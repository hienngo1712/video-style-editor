#!/usr/bin/env python3
"""Build dist/video-style-editor-skill.zip from the skill folder (for "Upload skill" in Claude / a GitHub release).

usage: python tools/build_skill_zip.py
Packs plugins/video-style-editor/skills/video-style-editor as video-style-editor/..., without caches, and checks that
no media, model or personal file slipped in.
"""
import hashlib
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'plugins', 'video-style-editor', 'skills', 'video-style-editor')
OUT = os.path.join(ROOT, 'dist', 'video-style-editor-skill.zip')
BLOCK = ('.mp4', '.mov', '.m4v', '.mkv', '.webm', '.wav', '.mp3', '.m4a', '.onnx', '.rnnn', '.ttf', '.jpg', '.png',
         '.heic', '.pyc')


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    files = []
    for root, dirs, fs in os.walk(SRC):
        dirs[:] = sorted(d for d in dirs if d not in ('__pycache__', '.git', 'work', 'output'))
        for f in sorted(fs):
            p = os.path.join(root, f)
            if f.lower().endswith(BLOCK):
                sys.exit(f'refusing to pack {os.path.relpath(p, ROOT)} - media/model/personal files stay out of the skill')
            files.append(p)
    with zipfile.ZipFile(OUT + '.part', 'w', zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, os.path.join('video-style-editor', os.path.relpath(p, SRC)))
    os.replace(OUT + '.part', OUT)
    with zipfile.ZipFile(OUT) as z:
        bad = [i.filename for i in z.infolist()
               if hashlib.md5(z.read(i)).digest() != hashlib.md5(
                   open(os.path.join(SRC, i.filename.split('/', 1)[1]), 'rb').read()).digest()]
    if bad:
        sys.exit(f'zip does not match the source: {bad}')
    print(f'{OUT}: {len(files)} files, {os.path.getsize(OUT) / 1024:.0f} KB')


if __name__ == '__main__':
    main()
