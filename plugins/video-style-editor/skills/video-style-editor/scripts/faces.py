#!/usr/bin/env python3
"""Where are the faces in a piece? Used by render.py to keep text off faces and to aim zooms at them.

Editors' notes (10/2026): a teaser line sat on the guest's face; zoom in on the face of the person being talked about.
Detection: OpenCV's YuNet face detector (models/face_detection_yunet_2023mar.onnx, MIT, from opencv_zoo - fetched by
setup_assets.py; OpenCV 5 no longer ships Haar cascades, they are only a fallback for OpenCV 4), 3 frames per piece,
run on the picture exactly as the piece frames it (9:16 crop). Boxes are fractions of the 1080x1920 frame.
Cached in work/build/faces.json.
"""
import json
import os
import subprocess

import numpy as np

from common import MODELS

_ld = os.environ.get('LD_LIBRARY_PATH')
try:
    import cv2
except ImportError:  # no opencv: placement falls back to the fixed layout
    cv2 = None
# opencv-python's import puts its bundled lib64 on LD_LIBRARY_PATH; every ffmpeg started afterwards then loads those
# libraries and runs ~20x slower (measured: 0.4 s -> 9 s per frame). Put the variable back.
if _ld is None:
    os.environ.pop('LD_LIBRARY_PATH', None)
else:
    os.environ['LD_LIBRARY_PATH'] = _ld

FW, FH = 360, 640
YUNET = os.path.join(MODELS, 'face_detection_yunet_2023mar.onnx')
_det = None


def _detector():
    """('yunet', det) | ('haar', [cascades]) | (None, None)"""
    global _det
    if _det is None:
        _det = (None, None)
        if cv2 is not None and os.path.exists(YUNET) and hasattr(cv2, 'FaceDetectorYN'):
            try:
                _det = ('yunet', cv2.FaceDetectorYN.create(YUNET, '', (FW, FH), 0.75, 0.3, 50))
            except Exception as e:  # noqa: BLE001  (half-downloaded model: run setup_assets.py again)
                print('  ! face model not usable:', e)
        if _det[0] is None and cv2 is not None and hasattr(cv2, 'CascadeClassifier'):
            d = cv2.data.haarcascades
            _det = ('haar', [cv2.CascadeClassifier(os.path.join(d, n)) for n in
                             ('haarcascade_frontalface_default.xml', 'haarcascade_profileface.xml')])
    return _det


def _frame(clip, t, fit):
    """one frame as the piece shows it, FWxFH BGR"""
    vf = (f'scale={FW}:{FH}:force_original_aspect_ratio=decrease,pad={FW}:{FH}:(ow-iw)/2:(oh-ih)/2' if fit == 'blur'
          else f'scale={FW}:{FH}:force_original_aspect_ratio=increase,crop={FW}:{FH}')
    r = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{t:.2f}', '-i', clip, '-frames:v', '1', '-vf',
                        vf + ',format=bgr24', '-f', 'rawvideo', '-'], capture_output=True, stdin=subprocess.DEVNULL)
    if len(r.stdout) != FW * FH * 3:
        return None
    return np.frombuffer(r.stdout, dtype=np.uint8).reshape(FH, FW, 3)


def detect(clip, t0, t1, fit=None):
    """[(x, y, w, h)] fractions of the frame, merged over 3 frames of [t0, t1]"""
    kind, det = _detector()
    if kind is None:
        return []
    boxes = []
    for f in (0.2, 0.5, 0.8):
        img = _frame(clip, t0 + (t1 - t0) * f, fit)
        if img is None:
            continue
        if kind == 'yunet':
            _, found = det.detect(img)
            for r in (found if found is not None else []):
                boxes.append((r[0] / FW, r[1] / FH, r[2] / FW, r[3] / FH))
        else:
            g = cv2.equalizeHist(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
            for k, c in enumerate(det):
                for flip in ((False, True) if k == 1 else (False,)):
                    im = cv2.flip(g, 1) if flip else g
                    for (x, y, w, h) in c.detectMultiScale(im, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30)):
                        boxes.append(((FW - x - w if flip else x) / FW, y / FH, w / FW, h / FH))
    # one box per face: merge detections of the same face over the 3 frames (people move a little)
    keep = []
    for b in sorted(boxes, key=lambda b: -b[2] * b[3]):
        if not any(abs(k[0] - b[0]) < 0.08 and abs(k[1] - b[1]) < 0.06 for k in keep):
            keep.append(tuple(round(float(v), 3) for v in b))
    return keep


class FaceCache:
    def __init__(self, path):
        self.path = path
        try:
            with open(path) as f:
                self.d = json.load(f)
        except (OSError, ValueError):
            self.d = {}

    def get(self, clip, t0, t1, fit=None, key=None):
        k = f'{key or os.path.basename(clip)}|{t0:.2f}|{t1:.2f}|{fit or ""}'
        if k not in self.d:
            if _detector()[0] is None:   # nothing to detect with: do not cache "no faces" for later runs
                return []
            self.d[k] = detect(clip, t0, t1, fit)
            with open(self.path, 'w') as f:
                json.dump(self.d, f)
        return [tuple(b) for b in self.d[k]]


def overlaps(boxes, y0, y1, pad=0.02):
    """does any face box cross the horizontal band [y0, y1] (fractions of the frame height)?"""
    return any(b[1] - pad < y1 and b[1] + b[3] + pad > y0 for b in boxes)


def main_face(boxes):
    """centre (x, y) of the largest face, or None"""
    if not boxes:
        return None
    b = max(boxes, key=lambda b: b[2] * b[3])
    return b[0] + b[2] / 2, b[1] + b[3] / 2
