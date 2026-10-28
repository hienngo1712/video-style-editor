#!/usr/bin/env python3
"""Generate our own overlay graphics (no third-party assets):
<VSE_HOME>/overlays/speedlines.png  radial speed lines, transparent centre (1080x1920)
<VSE_HOME>/overlays/paper.png       white torn-paper sheet with jagged left edge + shadow (1400x1920)
usage: python scripts/make_overlays.py   (render.py calls it automatically if missing)
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OVERLAYS as OUT  # noqa: E402
W, H = 1080, 1920


def speedlines(path, seed=7):
    rnd = random.Random(seed)
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = W / 2, H * 0.45
    for _ in range(140):
        a = rnd.uniform(0, 2 * math.pi)
        r0 = rnd.uniform(0.38, 0.55) * H
        r1 = 1.3 * H
        width = rnd.uniform(0.004, 0.012)
        pts = [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)),
               (cx + r1 * math.cos(a - width), cy + r1 * math.sin(a - width)),
               (cx + r1 * math.cos(a + width), cy + r1 * math.sin(a + width))]
        d.polygon(pts, fill=(255, 255, 255, rnd.randint(150, 230)))
    im.save(path)


def paper(path, seed=3):
    rnd = random.Random(seed)
    PW = 1400
    im = Image.new('RGBA', (PW, H), (0, 0, 0, 0))
    edge = []
    x = 90
    for y in range(0, H + 24, 24):
        x = max(30, min(150, x + rnd.randint(-28, 28)))
        edge.append((x, y))
    poly = edge + [(PW, H), (PW, 0)]
    shadow = Image.new('RGBA', (PW, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).polygon([(px - 14, py) for px, py in edge] + [(PW, H), (PW, 0)], fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    im.alpha_composite(shadow)
    sheet = Image.new('RGBA', (PW, H), (0, 0, 0, 0))
    ImageDraw.Draw(sheet).polygon(poly, fill=(246, 244, 238, 255))
    # fibres along the tear
    dd = ImageDraw.Draw(sheet)
    for px, py in edge:
        for _ in range(3):
            dd.line([(px, py), (px - rnd.randint(4, 14), py + rnd.randint(-10, 10))], fill=(255, 255, 255, 200), width=2)
    im.alpha_composite(sheet)
    im.save(path)


def ensure():
    os.makedirs(OUT, exist_ok=True)
    p1, p2 = os.path.join(OUT, 'speedlines.png'), os.path.join(OUT, 'paper.png')
    if not os.path.exists(p1):
        speedlines(p1)
    if not os.path.exists(p2):
        paper(p2)
    return p1, p2


if __name__ == '__main__':
    print(ensure())
