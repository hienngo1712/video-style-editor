#!/usr/bin/env python3
"""Download models, fonts and sound effects that are NOT stored in git.

usage: python scripts/setup_assets.py [--models] [--fonts] [--sfx] [--ced base|mini]
(no flag = everything)

- Models come from k2-fsa/sherpa-onnx GitHub releases (Apache-2.0), plus the RNNoise speech-denoise model
  "leavened-quisling" from GregorR/rnnoise-models (README: model data is not subject to copyright) and the YuNet
  face detector from opencv/opencv_zoo (MIT) used to keep text off faces and aim zooms.
- Fonts: Be Vietnam Pro from google/fonts (SIL OFL 1.1).
- SFX: Mixkit free sound effects (Mixkit Sound Effects Free License). The licence forbids
  redistributing the files inside a tool/template, so each user downloads them locally.
  If direct download is blocked on your network, open the URLs in assets/sfx/manifest.json
  in a browser and save them into the SFX folder printed below.
"""
import argparse
import os
import sys
import tarfile
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from common import FONTS, MODELS, SFX, SFX_MANIFEST, load_json  # noqa: E402

GH = 'https://github.com/k2-fsa/sherpa-onnx/releases/download'
MODEL_FILES = {
    'asr': f'{GH}/asr-models/sherpa-onnx-zipformer-vi-2025-04-20.tar.bz2',
    'vad': f'{GH}/asr-models/silero_vad.onnx',
    'ced-mini': f'{GH}/audio-tagging-models/sherpa-onnx-ced-mini-audio-tagging-2024-04-19.tar.bz2',
    'ced-base': f'{GH}/audio-tagging-models/sherpa-onnx-ced-base-audio-tagging-2024-04-19.tar.bz2',
}
RNN_URL = ('https://raw.githubusercontent.com/GregorR/rnnoise-models/master/'
           'leavened-quisling-2018-08-31/lq.rnnn')
YUNET_URL = ('https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/'
             'face_detection_yunet_2023mar.onnx')
FONT_URL = 'https://raw.githubusercontent.com/google/fonts/main/ofl/bevietnampro/'
FONT_FILES = ['BeVietnamPro-ExtraBold.ttf', 'BeVietnamPro-Black.ttf', 'OFL.txt']


def fetch(url, dest):
    if os.path.exists(dest):
        print('  ok (cached)', os.path.basename(dest))
        return True
    try:
        print('  downloading', url)
        urllib.request.urlretrieve(url, dest + '.part')
        os.replace(dest + '.part', dest)
        return True
    except Exception as e:  # noqa: BLE001
        print('  FAILED', e)
        return False


def models(ced):
    os.makedirs(MODELS, exist_ok=True)
    for key in ('asr', 'vad', f'ced-{ced}'):
        url = MODEL_FILES[key]
        dest = os.path.join(MODELS, os.path.basename(url))
        if url.endswith('.tar.bz2'):
            folder = dest[:-8]
            if os.path.isdir(folder):
                print('  ok (cached)', os.path.basename(folder))
                continue
            if fetch(url, dest):
                with tarfile.open(dest) as t:
                    t.extractall(MODELS)
                try:
                    os.remove(dest)
                except OSError:
                    print('  (could not delete', os.path.basename(dest), '- remove it manually)')
        else:
            fetch(url, dest)
    fetch(RNN_URL, os.path.join(MODELS, 'rnnoise-lq.rnnn'))   # speech denoise used by render.py
    fetch(YUNET_URL, os.path.join(MODELS, 'face_detection_yunet_2023mar.onnx'))   # faces.py


def fonts():
    os.makedirs(FONTS, exist_ok=True)
    for f in FONT_FILES:
        fetch(FONT_URL + f, os.path.join(FONTS, f))


def sfx():
    os.makedirs(SFX, exist_ok=True)
    man = load_json(SFX_MANIFEST, [])
    missing = []
    for s in man:
        if not fetch(s['url'], os.path.join(SFX, s['file'])):
            missing.append(s)
    if missing:
        print(f'\n{len(missing)} SFX could not be downloaded here. Open these URLs in a browser and save into {SFX}:')
        for s in missing:
            print(f"  {s['file']:28s} {s['url']}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--models', action='store_true')
    ap.add_argument('--fonts', action='store_true')
    ap.add_argument('--sfx', action='store_true')
    ap.add_argument('--ced', default='mini', choices=['mini', 'base'])
    a = ap.parse_args()
    everything = not (a.models or a.fonts or a.sfx)
    if a.models or everything:
        print('[models]'); models(a.ced)
    if a.fonts or everything:
        print('[fonts]'); fonts()
    if a.sfx or everything:
        print('[sfx]'); sfx()
