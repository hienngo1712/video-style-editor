#!/usr/bin/env python3
"""video-style-editor - one entry point for every step.

  python vse.py doctor [--fix]                    check / install Python packages, models, fonts, SFX
  python vse.py analyze  PROJECT                  prepare + transcribe + events (resumable)
  python vse.py inspect  PROJECT CLIP [S E]       words + loudness strip + pauses of one clip
  python vse.py style    init|show|note|learn|stats     your personal style: preferences + feedback journal
  python vse.py tighten  PROJECT plans/X.json [OUT] cut fillers (ờ, ừm, lone à/ừ) + long pauses -> plans/X-tight.json
  python vse.py lint     PROJECT plans/X.json     timeline + plan errors/warnings (before rendering)
  python vse.py render   PROJECT plans/X.json [all|pieces|final|ass|review]   (default all, resumable)
  python vse.py check    PROJECT plans/X.json     contact sheet + loudness + warnings of the output
  python vse.py reference REFDIR                  analyse reference videos to learn a new style
  python vse.py library  REFROOT                  rebuild the sample index (INDEX.md / INDEX.json / _hooks.jpg)
  python vse.py overlays                           (re)build paper / speedline overlays

Environment: VSE_HOME = data folder (models, fonts, SFX), VSE_BUDGET = seconds per command
(set 150 in Claude Cowork). Exit code 3 = time budget reached, progress saved - run the same command again.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = {'doctor': 'doctor.py', 'prepare': 'prepare.py', 'transcribe': 'transcribe.py', 'events': 'audio_events.py',
         'inspect': 'inspect_clip.py', 'lint': 'planlint.py', 'render': 'render.py', 'check': 'check.py',
         'reference': 'analyze_reference.py', 'library': 'ref_index.py', 'overlays': 'make_overlays.py', 'setup': 'setup_assets.py',
         'tighten': 'tighten.py', 'style': 'mystyle.py'}


def run(script, args):
    return subprocess.call([sys.executable, os.path.join(HERE, script)] + args)


if len(sys.argv) < 2 or sys.argv[1] not in STEPS and sys.argv[1] != 'analyze':
    sys.exit(__doc__)
cmd, args = sys.argv[1], sys.argv[2:]
if cmd == 'analyze':
    for step in ('prepare.py', 'transcribe.py', 'audio_events.py'):
        rc = run(step, args)
        if rc:
            sys.exit(rc)
    print('analyze done: look at work/thumbs/sheet_*.jpg, read work/transcript.json and work/audio_events.json')
elif cmd == 'render' and len(args) == 2:
    sys.exit(run('render.py', args + ['all']))
else:
    sys.exit(run(STEPS[cmd], args))
