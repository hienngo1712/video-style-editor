#!/usr/bin/env python3
"""Step 6: QA a rendered video.

usage: python scripts/check.py PROJECT plans/NAME.json
- work/check/NAME_sheet.jpg : a frame every 1.5 s - look at captions, big text, framing, transitions
- loudness of the output (target about -12 LUFS integrated, true peak below -1 dBTP) and its length
- the plan warnings from planlint.py (clipped cuts, level jumps, SFX on words)
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_json, project_paths  # noqa: E402
import planlint  # noqa: E402

P = project_paths(sys.argv[1])
plan_path = sys.argv[2] if os.path.isabs(sys.argv[2]) else os.path.join(P['root'], sys.argv[2])
plan = load_json(plan_path)
out = os.path.join(P['output'], plan['name'] + '.mp4')
if not os.path.exists(out):
    sys.exit(f'not rendered yet: {out}')
cdir = os.path.join(P['work'], 'check')
os.makedirs(cdir, exist_ok=True)
sheet = os.path.join(cdir, plan['name'] + '_sheet.jpg')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', out, '-vf', 'fps=1/1.5,'
                # TikTok UI zones: text must stay between the red lines and left of the right button column
                'drawbox=x=0:y=ih*0.10:w=iw:h=6:color=red@0.9:t=fill,drawbox=x=0:y=ih*0.78:w=iw:h=6:color=red@0.9:t=fill,'
                'drawbox=x=iw*0.88:y=ih*0.45:w=6:h=ih*0.33:color=red@0.9:t=fill,'
                'scale=180:320,tile=9x5:padding=2',
                '-frames:v', '1', sheet])
print('sheet ->', sheet)
r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', out, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
I = re.findall(r'I:\s+(-?[\d.]+) LUFS', r)
TP = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)
D = re.findall(r'Duration: (\d+):(\d+):([\d.]+)', r)
dur = int(D[0][1]) * 60 + float(D[0][2]) if D else 0
print(f'output: {dur:.1f}s, {I[-1] if I else "?"} LUFS, true peak {TP[-1] if TP else "?"} dBTP')
# exposure across the video: mean luma every 1.5 s (16-235); big jumps between neighbours = unmatched clips
r = subprocess.run(['ffmpeg', '-v', 'error', '-i', out, '-vf', 'fps=1/1.5,scale=270:-2,signalstats,'
                    'metadata=print:key=lavfi.signalstats.YAVG:file=-', '-an', '-f', 'null', '-'],
                   capture_output=True, text=True)
ys = [float(v) for v in re.findall(r'YAVG=([\d.]+)', r.stdout)]
if ys:
    jumps = [(i * 1.5, ys[i] - ys[i - 1]) for i in range(1, len(ys)) if abs(ys[i] - ys[i - 1]) > 25]
    print(f'luma: mean {sum(ys) / len(ys):.0f}, min {min(ys):.0f}, max {max(ys):.0f} (16-235, ~110-125 is a good mean); '
          + (f'{len(jumps)} jumps >25: ' + ', '.join(f'{t:.0f}s {d:+.0f}' for t, d in jumps[:8]) if jumps else 'no big jumps'))
# captions: overlapping subtitle events show as two stacked copies of a line
ass = os.path.join(P['work'], 'build', plan['name'], 'captions.ass')
if os.path.exists(ass):
    def _t(x):
        h, m, s = x.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)
    ev = sorted((_t(l.split(',')[1]), _t(l.split(',')[2])) for l in open(ass, encoding='utf-8')
                if l.startswith('Dialogue: 0,'))
    ov = [a for a, b in zip(ev, ev[1:]) if b[0] < a[1] - 0.01]
    print(f'captions: {len(ev)} events, {len(ov)} overlapping' + (' <- fix before publishing' if ov else ''))
planlint.lint(sys.argv[1], plan_path, show_timeline=False)
