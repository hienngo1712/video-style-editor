#!/usr/bin/env python3
"""Transcribe one clip offline (Vietnamese) with word timings, in the transcript format the reel kit reads.

    python reels/kit/transcribe.py <video> [--out file.json]

Replaces the original Groq Whisper step (no API key, nothing leaves the computer): the same sherpa-onnx Zipformer
+ Silero VAD models as `vse.py analyze`. The recogniser writes no punctuation, so every pause the VAD finds ends a
"sentence" (a "." is added to its last word): `reel.py words` prints one line per breath group and captions break
there. Writes {text, segments: [{start, end, text}], words: [{word, start, end}], duration, model}.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT.parents[1] / 'scripts'))
from common import MODELS, frame_db, noise_floor  # noqa: E402

MODEL = 'sherpa-onnx-zipformer-vi-2025-04-20'


def _audio(video):
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / 'a.raw'
        subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', str(video), '-vn', '-ac', '1', '-ar', '16000',
                        '-f', 's16le', str(wav)], check=True, stdin=subprocess.DEVNULL)
        return np.frombuffer(wav.read_bytes(), dtype=np.int16).astype(np.float32) / 32768


def _trim_ends(words, db, floor):
    """the ASR gives start times only; pull inflated word ends back to where the speech energy stops"""
    for w in words:
        if w['end'] - w['start'] <= 0.45:
            continue
        i0, i1 = int(w['start'] / 0.05), int(w['end'] / 0.05)
        loud = [i for i in range(i0, min(i1, len(db))) if db[i] > floor + 9]
        if loud:
            w['end'] = round(min(w['end'], max(w['start'] + 0.2, (loud[-1] + 1) * 0.05 + 0.08)), 3)


def transcribe(video, out=None, language=None):  # language kept for the original signature (Vietnamese model)
    import sherpa_onnx
    video = Path(video).resolve()
    out = Path(out) if out else video.with_name(video.stem + '.transcript.json')
    m = os.path.join(MODELS, MODEL)
    if not os.path.isdir(m):
        sys.exit(f'speech model missing ({m}): run `vse.py doctor --fix` first')
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=f'{m}/encoder-epoch-12-avg-8.onnx', decoder=f'{m}/decoder-epoch-12-avg-8.onnx',
        joiner=f'{m}/joiner-epoch-12-avg-8.onnx', tokens=f'{m}/tokens.txt',
        num_threads=os.cpu_count() or 2, decoding_method='modified_beam_search')
    cfg = sherpa_onnx.VadModelConfig()
    cfg.silero_vad.model = os.path.join(MODELS, 'silero_vad.onnx')
    cfg.silero_vad.min_silence_duration = 0.25
    cfg.silero_vad.min_speech_duration = 0.2
    cfg.silero_vad.max_speech_duration = 12
    cfg.sample_rate = 16000
    a = _audio(video)
    db = frame_db(a)
    floor = noise_floor(db)
    vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=max(60, int(len(a) / 16000) + 30))
    for i in range(0, len(a), cfg.silero_vad.window_size):
        vad.accept_waveform(a[i:i + cfg.silero_vad.window_size])
    vad.flush()
    words, segments = [], []
    while not vad.empty():
        s = vad.front
        vad.pop()
        st = s.start / 16000
        smp = np.array(s.samples, dtype=np.float32)
        stream = rec.create_stream()
        stream.accept_waveform(16000, smp)
        rec.decode_stream(stream)
        r = stream.result
        seg, cur = [], None
        for tok, ts in zip(r.tokens, r.timestamps):
            if tok.startswith(('▁', ' ')) or cur is None:
                if cur:
                    seg.append(cur)
                cur = {'word': tok.replace('▁', '').strip().lower(), 'start': round(st + ts, 3)}
            else:
                cur['word'] += tok.lower()
        if cur:
            seg.append(cur)
        seg = [w for w in seg if w['word']]
        if not seg:
            continue
        end = st + len(smp) / 16000
        for k, w in enumerate(seg):
            w['end'] = round(seg[k + 1]['start'] if k + 1 < len(seg) else end, 3)
        _trim_ends(seg, db, floor)
        seg[-1]['word'] += '.'
        words += seg
        segments.append({'start': round(st, 3), 'end': round(end, 3), 'text': ' '.join(w['word'] for w in seg)})
    data = {'text': ' '.join(s['text'] for s in segments), 'segments': segments, 'words': words,
            'duration': round(len(a) / 16000, 3), 'model': MODEL}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--out')
    x = ap.parse_args()
    p = transcribe(x.video, x.out)
    d = json.loads(p.read_text())
    print(f'wrote {p}  ({len(d["words"])} words)')
    for s in d['segments']:
        print(f'{s["start"]:7.2f}-{s["end"]:7.2f}  {s["text"]}')
