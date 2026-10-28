#!/usr/bin/env python3
"""Step 1 for a new project: inventory clips, extract audio, make contact sheets.

usage: python scripts/prepare.py PROJECT
writes: work/clips.json, work/audio/<key>.wav, work/thumbs/sheet_XX.jpg
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import AUDIO_EXT, VIDEO_EXT, clip_key, ffprobe, list_media, out_of_time, project_paths, save_json, stop_for_now  # noqa: E402

P = project_paths(sys.argv[1])
clips = {}
for rel in list_media(P['raw']):
    src = os.path.join(P['raw'], rel)
    j = ffprobe(src)
    v = [s for s in j.get('streams', []) if s.get('codec_type') == 'video']
    info = {'path': rel, 'dur': round(float(j.get('format', {}).get('duration', 0)), 2),
            'created': j.get('format', {}).get('tags', {}).get('creation_time', '')[:19]}
    if v:
        rot = next((sd['rotation'] for sd in v[0].get('side_data_list', []) if 'rotation' in sd), 0)
        w, h = v[0]['width'], v[0]['height']
        if abs(int(rot)) == 90:
            w, h = h, w
        info.update(w=w, h=h, fps=v[0].get('r_frame_rate'), codec=v[0].get('codec_name'))
    info['audio'] = any(s.get('codec_type') == 'audio' for s in j.get('streams', []))
    clips[clip_key(rel)] = info
save_json(clips, os.path.join(P['work'], 'clips.json'))
print(f"{len(clips)} clips, {sum(c['dur'] for c in clips.values()):.0f}s total")

# audio 16 kHz mono for ASR / audio analysis
adir = os.path.join(P['work'], 'audio')
os.makedirs(adir, exist_ok=True)
for key, c in clips.items():
    out = os.path.join(adir, key + '.wav')
    if not os.path.exists(out):
        if out_of_time(10):
            stop_for_now('extracting audio')
        src = ['-i', os.path.join(P['raw'], c['path'])] if c.get('audio', True) else \
            ['-f', 'lavfi', '-t', str(max(c['dur'], 0.1)), '-i', 'anullsrc=r=16000:cl=mono']   # silent clip
        subprocess.run(['ffmpeg', '-nostdin', '-y', '-v', 'error'] + src +
                       ['-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', out + '.part.wav'], check=True)
        os.replace(out + '.part.wav', out)
print('audio ok')

# contact sheets: 4 frames per clip, 2 clips per row, 10 clips per sheet
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit('pip install pillow to build contact sheets')
tdir = os.path.join(P['work'], 'thumbs')
os.makedirs(tdir, exist_ok=True)
vids = [k for k, c in clips.items() if c['path'].lower().endswith(VIDEO_EXT)]
for k in vids:
    c = clips[k]
    for i in range(4):
        out = os.path.join(tdir, f'{k}_{i}.jpg')
        if not os.path.exists(out):
            if out_of_time(5):
                stop_for_now('making thumbnails')
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f"{c['dur'] * (i + 0.5) / 4:.2f}",
                            '-i', os.path.join(P['raw'], c['path']), '-frames:v', '1',
                            '-vf', 'scale=180:320:force_original_aspect_ratio=decrease,pad=180:320:(ow-iw)/2:(oh-ih)/2',
                            '-q:v', '5', out])
font = ImageFont.load_default()
for s in range(0, len(vids), 10):
    group = vids[s:s + 10]
    rows = (len(group) + 1) // 2
    im = Image.new('RGB', (2 * 730 + 10, rows * 350 + 10), 'white')
    d = ImageDraw.Draw(im)
    for i, k in enumerate(group):
        x0, y0 = 10 + (i % 2) * 730, 10 + (i // 2) * 350
        d.text((x0, y0 + 5), f"{k}  ({clips[k]['dur']}s)", fill='black', font=font)
        for f in range(4):
            p = os.path.join(tdir, f'{k}_{f}.jpg')
            if os.path.exists(p):
                im.paste(Image.open(p), (x0 + f * 180, y0 + 28))
    im.save(os.path.join(tdir, f'sheet_{s // 10 + 1:02d}.jpg'), quality=80)
print('thumbs ok ->', tdir)
