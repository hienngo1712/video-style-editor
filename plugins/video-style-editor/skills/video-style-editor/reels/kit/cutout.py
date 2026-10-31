#!/usr/bin/env python3
"""Cut the speaker out of a clip: RobustVideoMatting (ONNX, on the CPU) -> VP9 webm with an alpha channel.

    python reels/kit/cutout.py <clip.mp4> <out.webm> [--model mobilenetv3|resnet50]

The webm lines up frame for frame with the clip, so a layout can put graphics BEHIND the speaker (background video,
then the graphics, then this cutout on top). mobilenetv3 is the default: fast and good on a clean talking head;
resnet50 is slower and cleaner around hair and hands. Models download on first use into <VSE_HOME>/models/.
RobustVideoMatting is by Shanchuan Lin et al. (GPL-3.0): https://github.com/PeterL1n/RobustVideoMatting

Changed from the original kit: resumable. The matte is computed in chunks (the model's recurrent state is saved
between them) into grey-scale mask pieces; when the time budget (VSE_BUDGET) runs out it stops with CONTINUE
and the next run carries on. The last step merges clip + mask into the alpha webm.
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT.parents[1] / 'scripts'))
from common import MODELS, out_of_time, stop_for_now  # noqa: E402

URL = 'https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_{}_fp32.onnx'
CHUNK = 60  # frames per resumable piece


def model_path(name):
    p = Path(MODELS) / f'rvm_{name}_fp32.onnx'
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        print(f'downloading the {name} matting model (one time)...', flush=True)
        tmp = p.with_suffix('.part')
        try:
            urllib.request.urlretrieve(URL.format(name), tmp)
        except Exception:  # noqa: BLE001 - urllib may not use the proxy; curl does
            subprocess.run(['curl', '-fsSL', '-o', str(tmp), URL.format(name)], check=True)
        tmp.rename(p)
    return p


def probe(clip):
    s = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries',
                                            'stream=width,height,r_frame_rate,nb_read_packets', '-of', 'json', str(clip)]))['streams'][0]
    a, b = s['r_frame_rate'].split('/')
    return s['width'], s['height'], float(a) / float(b), int(s.get('nb_read_packets') or 0)


def cutout(clip, out, model='mobilenetv3', ratio=0.25):
    import onnxruntime as ort
    out = Path(out)
    w, h, fps, n = probe(clip)
    parts = out.with_name(out.stem + '.parts')
    parts.mkdir(exist_ok=True)
    state_f = parts / 'state.npz'
    done = 0
    rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
    if state_f.exists():
        st = np.load(state_f)
        done = int(st['done'])
        rec = [st[f'r{i}'] for i in range(4)]
    sess = None
    t0, ran = time.time(), 0
    while done < n:
        k = min(CHUNK, n - done)
        if out_of_time(k * 0.6 + 5):
            stop_for_now(f'cutout {done}/{n} frames')
        if sess is None:
            opts = ort.SessionOptions()
            sess = ort.InferenceSession(str(model_path(model)), opts, providers=['CPUExecutionProvider'])
        ss = ['-ss', f'{(done - 0.5) / fps:.6f}'] if done else []
        dec = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', *ss, '-i', str(clip), '-frames:v', str(k), '-f', 'rawvideo',
                                '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
        piece = parts / f'{done:06d}.mkv'
        enc = subprocess.Popen(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'gray', '-s', f'{w}x{h}',
                                '-r', f'{fps:.6f}', '-i', '-', '-c:v', 'ffv1', str(piece)], stdin=subprocess.PIPE)
        size, got = w * h * 3, 0
        dr = np.array([ratio], np.float32)
        new = rec
        while got < k:
            buf = dec.stdout.read(size)
            if len(buf) < size:
                break
            rgb = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
            src = (rgb.astype(np.float32) / 255).transpose(2, 0, 1)[None]
            fgr, pha, *new = sess.run(None, {'src': src, 'r1i': new[0], 'r2i': new[1], 'r3i': new[2], 'r4i': new[3],
                                             'downsample_ratio': dr})
            enc.stdin.write((np.clip(pha[0, 0], 0, 1) * 255).astype(np.uint8).tobytes())
            got += 1
        enc.stdin.close()
        enc.wait()
        dec.stdout.close()
        dec.wait()
        if enc.returncode or got == 0:
            sys.exit('ffmpeg could not write the cutout mask')
        rec = new
        done += got
        ran += got
        np.savez(state_f, done=done, **{f'r{i}': rec[i] for i in range(4)})
        print(f'  cutout {done}/{n} frames  {(time.time() - t0) / ran:.2f}s/frame', flush=True)
        if got < k:
            break
    pieces = sorted(parts.glob('*.mkv'))
    lst = parts / 'list.txt'
    lst.write_text(''.join(f"file '{p.name}'\n" for p in pieces))
    if out_of_time(n * 0.15 + 10):
        stop_for_now('cutout: alpha webm still to encode')
    print('  encoding the alpha webm ...', flush=True)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', str(clip), '-f', 'concat', '-safe', '0', '-i', str(lst),
                    '-filter_complex', '[1:v]format=gray[m];[0:v][m]alphamerge,format=yuva420p[v]', '-map', '[v]', '-an',
                    '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', '-b:v', '0', '-crf', '22', '-deadline', 'realtime',
                    '-cpu-used', '8', '-row-mt', '1', '-auto-alt-ref', '0', str(out)], check=True, stdin=subprocess.DEVNULL)
    for p in list(parts.iterdir()) + [parts]:   # a Cowork folder may refuse deletes: leftovers are harmless
        try:
            p.rmdir() if p.is_dir() else p.unlink()
        except OSError:
            pass
    print(f'wrote {out}  ({done} frames)')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('clip')
    ap.add_argument('out')
    ap.add_argument('--model', default='mobilenetv3', choices=['mobilenetv3', 'resnet50'])
    ap.add_argument('--ratio', type=float, default=0.25, help='downsample ratio (0.25 suits 1080x1920)')
    a = ap.parse_args()
    cutout(a.clip, a.out, a.model, a.ratio)
