#!/usr/bin/env python3
"""Reel layouts (from claude-editing-skills by Artem Novitckii, MIT) - one clip -> one designed 9:16 reel.

  vse.py reel setup                          install HyperFrames + GSAP + Chromium (npm) into $VSE_HOME/reels-runtime
  vse.py reel check                          what is installed
  vse.py reel list                           the layouts and what each one makes
  vse.py reel words <video> [--start S] [--end E]   words with times, one line per breath group ([ends ...])
  vse.py reel frame <video> <t> <out.jpg>    one 9:16 frame with a y ruler (read eyes / chin)
  vse.py reel sheet <video.mp4> <out.jpg>    contact sheet with the Instagram safe zone in red
  vse.py reel build <layout> <spec.json>     cut, (cut out the speaker), render, sheet - resumable (exit 3 = run again)

Each layout's spec, steps and taste rules: reels/<layout>/GUIDE.md. Overview: docs/reels.md.
"""
import os
import subprocess
import sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REELS = os.path.join(SKILL, 'reels')
KIT = os.path.join(REELS, 'kit')
LAYOUTS = {
    'trial-reels': 'one clip -> 3 different-looking reels to A/B test (title + karaoke | post header + punch-ins | pixel stat in a frame)',
    'behind-the-person': 'speaker cut out in front of a panel (post grid, bar chart, screenshot); chest words; profile card counts up',
    'explainer': 'speaker low in a rounded panel, head breaking out; before -> after cards with an arrow, or a numbered list on top',
    'split-screen': 'visuals on the top half (step badge, headline, window: grid pick / screenshot / checklist), speaker below',
    'ranking-list': 'S-to-F tier table on the chest; each item pops when named and drops into its tier on the verdict',
    'storytelling': '3 cards across the top + black-box title + subtitle, all at once, over one take; TikTok captions',
}


def py(script, args):
    return subprocess.call([sys.executable, script] + args)


if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help', 'help'):
    sys.exit(__doc__)
cmd, args = sys.argv[1], sys.argv[2:]
if cmd in ('setup', 'check'):
    sys.exit(py(os.path.join(KIT, 'runtime.py'), [cmd]))
if cmd == 'list':
    for k, v in LAYOUTS.items():
        print(f'  {k:18} {v}')
    print('\nguide: reels/<layout>/GUIDE.md')
    sys.exit(0)
if cmd in ('words', 'frame', 'sheet'):
    sys.exit(py(os.path.join(KIT, 'reel.py'), [cmd] + args))
if cmd == 'transcribe':
    sys.exit(py(os.path.join(KIT, 'transcribe.py'), args))
if cmd == 'build':
    if len(args) < 2 or args[0] not in LAYOUTS:
        sys.exit('usage: vse.py reel build <layout> <spec.json>\nlayouts: ' + ', '.join(LAYOUTS))
    sys.exit(py(os.path.join(REELS, args[0], 'build.py'), args[1:]))
sys.exit(__doc__)
