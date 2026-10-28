#!/usr/bin/env python3
"""Look closely at one clip before choosing cut points.

usage: python scripts/inspect_clip.py PROJECT CLIP [START END]
CLIP = any part of the clip key or file name, e.g. 9677 or "IMG_9677".
prints the words with times, then a loudness strip: one character per 50 ms
    ' ' silence   '.' faint   ':' quiet speech   '|' speech   '#' loud
and the pauses (>= 0.2 s of silence) - the safe places to cut.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import frame_db, load_json, load_wav, noise_floor, project_paths  # noqa: E402

P = project_paths(sys.argv[1])
TR = load_json(os.path.join(P['work'], 'transcript.json'), {})
clips = load_json(os.path.join(P['work'], 'clips.json'), {})
keys = [k for k in clips if sys.argv[2].lower() in (k + ' ' + clips[k]['path']).lower()]
if len(keys) != 1:
    sys.exit(f'{len(keys)} clips match "{sys.argv[2]}": {keys[:10]}')
key = keys[0]
db = frame_db(load_wav(os.path.join(P['work'], 'audio', key + '.wav')))
floor = noise_floor(db)
s = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
e = float(sys.argv[4]) if len(sys.argv) > 4 else len(db) * 0.05
print(f"{key}  raw/{clips[key]['path']}  {clips[key]['dur']}s  noise {floor:.0f} dB")
for seg in TR.get(key, {}).get('segs', []):
    ws = [w for w in seg['words'] if s - 0.5 <= w['s'] <= e]
    if ws:
        print('  ' + ' '.join(f"{w['w']}@{w['s']:.2f}" for w in ws) + f"  (ends {ws[-1]['e']:.2f})")


def ch(v):
    d = v - floor
    return ' ' if d < 4 else '.' if d < 9 else ':' if d < 16 else '|' if d < 24 else '#'


i0, i1 = int(s / 0.05), min(len(db), int(e / 0.05) + 1)
for r in range(i0, i1, 100):   # 5 s per line
    line = ''.join(ch(db[i]) for i in range(r, min(r + 100, i1)))
    ruler = ''.join('^' if (i % 10 == 0) else ' ' for i in range(r, min(r + 100, i1)))
    print(f'{r * 0.05:6.1f}s {line}\n        {ruler}  (^ every 0.5 s)')
gaps, run = [], None
for i in range(i0, i1):
    if db[i] - floor < 5:
        run = i if run is None else run
    else:
        if run is not None and i - run >= 4:
            gaps.append((run * 0.05, i * 0.05))
        run = None
print('pauses:', ', '.join(f'{a:.2f}-{b:.2f}' for a, b in gaps) or 'none')
