#!/usr/bin/env python3
"""Check (and fix what it can) everything the skill needs. Run it first on a new machine.

usage: python scripts/doctor.py [--fix]
--fix  pip-installs missing Python packages and runs setup_assets.py for missing models/fonts/SFX.
"""
import importlib
import importlib.util
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, FONTS, MODELS, SFX, SFX_MANIFEST, load_json  # noqa: E402

fix = '--fix' in sys.argv
ok = True


def report(name, good, hint=''):
    global ok
    ok &= good
    print(f"  [{'ok' if good else '!!'}] {name}" + ('' if good else f'  -> {hint}'))


print('video-style-editor doctor')
print('  data folder:', DATA)
report(f'python {sys.version.split()[0]}', sys.version_info >= (3, 10), 'Python 3.10+ required')
for tool in ('ffmpeg', 'ffprobe'):
    report(tool, shutil.which(tool) is not None, 'install FFmpeg and add it to PATH (https://ffmpeg.org/download.html)')

missing = []
for mod, pkg in (('sherpa_onnx', 'sherpa-onnx'), ('numpy', 'numpy'), ('PIL', 'pillow'), ('cv2', 'opencv-python-headless'), ('yaml', 'pyyaml')):
    try:
        importlib.import_module(mod)
    except ImportError:
        missing.append(pkg)
if missing and fix:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', *missing])
    missing = [p for m, p in (('sherpa_onnx', 'sherpa-onnx'), ('numpy', 'numpy'), ('PIL', 'pillow'), ('cv2', 'opencv-python-headless'), ('yaml', 'pyyaml'))
               if importlib.util.find_spec(m) is None]
report('python packages', not missing, f'pip install {" ".join(missing)}  (or run doctor.py --fix)')

need = {
    'ASR model': os.path.isdir(os.path.join(MODELS, 'sherpa-onnx-zipformer-vi-2025-04-20')),
    'VAD model': os.path.exists(os.path.join(MODELS, 'silero_vad.onnx')),
    'denoise model (RNNoise)': os.path.exists(os.path.join(MODELS, 'rnnoise-lq.rnnn')),
    'face model (YuNet)': os.path.exists(os.path.join(MODELS, 'face_detection_yunet_2023mar.onnx')),
    'audio-tagging model': any(n.startswith('sherpa-onnx-ced-') for n in os.listdir(MODELS)) if os.path.isdir(MODELS) else False,
    'fonts': os.path.exists(os.path.join(FONTS, 'BeVietnamPro-Black.ttf')),
}
man = load_json(SFX_MANIFEST, [])
have = [s for s in man if os.path.exists(os.path.join(SFX, s['file']))]
need[f'SFX {len(have)}/{len(man)}'] = len(have) == len(man)
if not all(need.values()) and fix:
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'setup_assets.py')])
    return_code = subprocess.run([sys.executable, __file__]).returncode
    sys.exit(return_code)
for k, v in need.items():
    report(k, v, 'python scripts/setup_assets.py')
print('ready' if ok else 'not ready - see the hints above')
sys.exit(0 if ok else 1)
