#!/usr/bin/env python3
"""Learn a style from reference videos (run once per style). Resumable (VSE_BUDGET).

usage: python scripts/analyze_reference.py REFDIR
REFDIR/videos/*.(mp4|webm|mov) ->
  REFDIR/analysis/<name>/cuts.txt, audio.log, frames/ (1 every 2 s), sheet_NN.jpg (8x3 = 48 s each),
                         hook.jpg (first 3 s at 3 fps - the hook decides retention), first10.jpg (0-10 s, 2 fps),
                         onsets.txt (sharp sound hits = likely SFX)
  REFDIR/analysis/summary.json   duration, cuts, avg shot, cuts in the first 5 s, first cut, motion in the first
                                 second, silences, LUFS, sound hits, share of cuts that carry a sound hit
  REFDIR/notes.txt (optional, written by the user): what they love / would skip in these videos - read it first.
  REFDIR/work/audio/<name>.wav + work/clips.json, so `vse.py transcribe REFDIR` / `events REFDIR` work too.
Name files <style>__<format>__<content>__<views>.mp4 (no person names) - see ref_index.py / vse.py library.
Claude then reads sheets + hook + summary + transcript and writes profiles/<style>.yaml.
"""
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import frame_db, load_wav, out_of_time, save_json, stop_for_now  # noqa: E402


def onsets(wav):
    """times of sharp sound hits (a 50 ms frame 9+ dB above the loudest of the 4 before it) - SFX, claps, slams"""
    try:
        db = frame_db(load_wav(wav))
    except Exception:  # noqa: BLE001
        return []
    out, last = [], -9.0
    for i in range(4, len(db)):
        if db[i] - max(db[i - 4:i]) > 9 and db[i] > -35 and i * 0.05 - last > 0.3:
            out.append(round(i * 0.05, 2))
            last = i * 0.05
    return out


def hook_motion(mkv):
    """mean frame-to-frame change in the first second (0 = still picture, 10+ = lots of movement)"""
    r = subprocess.run(['ffmpeg', '-v', 'info', '-t', '1', '-i', mkv, '-an', '-vf',
                        'scale=72:128,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-',
                        '-f', 'null', '-'], capture_output=True, text=True)
    ys = [float(x) for x in re.findall(r'YAVG=([\d.]+)', r.stdout)]
    return round(sum(ys) / len(ys), 1) if ys else None

def probe_dur(path):
    """duration in s; browser recordings (webm) often have none in the header -> decode to find it"""
    if not os.path.exists(path):
        return 0.0
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        r = subprocess.run(['ffmpeg', '-i', path, '-map', '0:a:0', '-f', 'null', '-'], capture_output=True, text=True).stderr
        t = re.findall(r'time=(\d+):(\d+):([\d.]+)', r)
        return int(t[-1][0]) * 3600 + int(t[-1][1]) * 60 + float(t[-1][2]) if t else 0.0


REF = os.path.abspath(sys.argv[1])
if os.path.exists(os.path.join(REF, 'notes.txt')):
    print('notes.txt (the user\'s own words - read before writing the style):')
    print(open(os.path.join(REF, 'notes.txt'), encoding='utf-8', errors='replace').read().strip()[:2000])
else:
    print('no notes.txt: ask the user what they love / would skip in these videos and save it as REFDIR/notes.txt')
SUM = os.path.join(REF, 'analysis', 'summary.json')
summary = json.load(open(SUM)) if os.path.exists(SUM) else {}
WAV = os.path.join(REF, 'work', 'audio')
os.makedirs(WAV, exist_ok=True)
clips = {}
done_now = 0
for v in sorted(glob.glob(os.path.join(REF, 'videos', '*'))):
    name = os.path.splitext(os.path.basename(v))[0]
    D = os.path.join(REF, 'analysis', name)
    dur = probe_dur(os.path.join(D, 'video.mkv')) or probe_dur(v)
    clips[name] = {'path': os.path.relpath(v, REF), 'dur': round(dur, 2)}
    if name in summary and os.path.exists(os.path.join(D, 'hook.jpg')):
        continue
    if done_now and out_of_time(20 + dur * 0.5):   # always finish at least one video per run
        save_json(summary, SUM)
        save_json(clips, os.path.join(REF, 'work', 'clips.json'))
        stop_for_now(f'analysing {name}')
    os.makedirs(os.path.join(D, 'frames'), exist_ok=True)
    mkv = os.path.join(D, 'video.mkv')
    if not os.path.exists(mkv):  # remux fixes missing duration in browser recordings
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', v, '-c', 'copy', mkv], check=True)
    r = subprocess.run(['ffmpeg', '-v', 'info', '-i', mkv, '-an', '-vf',
                        "scale=144:256,select='gt(scene,0.10)',showinfo", '-f', 'null', '-'],
                       capture_output=True, text=True)
    cuts = [float(x) for x in re.findall(r'pts_time:([0-9.]+)', r.stderr)]
    merged, last = [], -9
    for c in cuts:  # merge detections closer than 0.7 s (motion blur, transitions)
        if c - last > 0.7:
            merged.append(c)
            last = c
    with open(os.path.join(D, 'cuts.txt'), 'w') as f:
        f.write('\n'.join(f'{c:.2f}' for c in merged))
    a = subprocess.run(['ffmpeg', '-v', 'info', '-i', mkv, '-vn', '-af', 'silencedetect=n=-32dB:d=0.35,ebur128',
                        '-f', 'null', '-'], capture_output=True, text=True).stderr
    with open(os.path.join(D, 'audio.log'), 'w') as f:
        f.write(a)
    lufs = re.findall(r'I:\s+(-?[0-9.]+) LUFS', a)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', mkv, '-vf', 'fps=1/2,scale=288:512', '-q:v', '5',
                    os.path.join(D, 'frames', 'f_%04d.jpg')])
    n = len(glob.glob(os.path.join(D, 'frames', 'f_*.jpg')))
    for k in range(0, n, 24):
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', '1', '-start_number', str(k + 1),
                        '-i', os.path.join(D, 'frames', 'f_%04d.jpg'), '-frames:v', '1',
                        '-vf', 'scale=144:256,tile=8x3:padding=2', os.path.join(D, f'sheet_{k // 24 + 1:02d}.jpg')])
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-t', '3', '-i', mkv, '-vf', 'fps=3,scale=216:384,tile=9x1:padding=2',
                    '-frames:v', '1', os.path.join(D, 'hook.jpg')])
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-t', '10', '-i', mkv, '-vf', 'fps=2,scale=144:256,tile=10x2:padding=2',
                    '-frames:v', '1', os.path.join(D, 'first10.jpg')])
    wav = os.path.join(WAV, name + '.wav')
    if not os.path.exists(wav):
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', mkv, '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le',
                        wav], check=True)
    hits = onsets(wav)
    with open(os.path.join(D, 'onsets.txt'), 'w') as f:
        f.write('\n'.join(f'{h:.2f}' for h in hits))
    on_cut = sum(1 for c in merged if any(abs(c - h) <= 0.15 for h in hits))
    summary[name] = {'dur': round(dur, 1), 'cuts': len(merged),
                     'avg_shot_s': round(dur / (len(merged) + 1), 2),
                     'cuts_first_5s': sum(1 for c in merged if c < 5),
                     'cuts_per_min': round(len(merged) / max(dur, 1) * 60, 1),
                     'first_cut_s': round(merged[0], 2) if merged else None,
                     'hook_motion': hook_motion(mkv),
                     'silences': a.count('silence_end'), 'lufs': float(lufs[-1]) if lufs else None,
                     'sound_hits': len(hits), 'cuts_with_hit': round(on_cut / len(merged), 2) if merged else None}
    print(name, summary[name], flush=True)
    save_json(summary, SUM)
    done_now += 1
save_json(clips, os.path.join(REF, 'work', 'clips.json'))
save_json(summary, SUM)
print('summary ->', SUM)
