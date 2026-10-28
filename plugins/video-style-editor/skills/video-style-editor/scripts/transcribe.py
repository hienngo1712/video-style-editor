#!/usr/bin/env python3
"""Step 2: Vietnamese speech-to-text with per-word timestamps (offline).

usage: python scripts/transcribe.py PROJECT [--force]
reads work/audio/*.wav, writes work/transcript.json:
  {key: {dur, segs: [{s, e, t, words: [{w, s, e}]}]}}
Model: sherpa-onnx Zipformer (Vietnamese) + Silero VAD (see setup_assets.py).
Resumable: clips already in transcript.json are skipped (--force redoes all); saves after every clip.
Word ends: the ASR gives start times only; a word's end = next word's start, which swallows pauses.
Ends longer than 0.45 s are trimmed to where the speech energy actually stops.
"""
import glob
import os
import sys
import wave

import numpy as np
import sherpa_onnx

sys.path.insert(0, os.path.dirname(__file__))
from common import MODELS, load_wav_checked, frame_db, load_json, noise_floor, out_of_time, project_paths, save_json, stop_for_now  # noqa: E402

P = project_paths(sys.argv[1])
M = os.path.join(MODELS, 'sherpa-onnx-zipformer-vi-2025-04-20')
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f'{M}/encoder-epoch-12-avg-8.onnx', decoder=f'{M}/decoder-epoch-12-avg-8.onnx',
    joiner=f'{M}/joiner-epoch-12-avg-8.onnx', tokens=f'{M}/tokens.txt',
    num_threads=os.cpu_count() or 2, decoding_method='modified_beam_search')

vcfg = sherpa_onnx.VadModelConfig()
vcfg.silero_vad.model = os.path.join(MODELS, 'silero_vad.onnx')
vcfg.silero_vad.min_silence_duration = 0.25
vcfg.silero_vad.min_speech_duration = 0.2
vcfg.silero_vad.max_speech_duration = 12
vcfg.sample_rate = 16000


def read(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


TR = os.path.join(P['work'], 'transcript.json')
CLIPS = load_json(os.path.join(P['work'], 'clips.json'), {})
out = {} if '--force' in sys.argv else load_json(TR, {})


def trim_ends(words, db, floor):
    """Pull inflated word ends back to the last 50 ms frame that is clearly louder than the noise."""
    for w in words:
        if w['e'] - w['s'] <= 0.45:
            continue
        i0, i1 = int(w['s'] / 0.05), int(w['e'] / 0.05)
        loud = [i for i in range(i0, min(i1, len(db))) if db[i] > floor + 9]
        if loud:
            w['e'] = round(min(w['e'], max(w['s'] + 0.2, (loud[-1] + 1) * 0.05 + 0.08)), 2)


todo = [p for p in sorted(glob.glob(os.path.join(P['work'], 'audio', '*.wav'))) if os.path.basename(p)[:-4] not in out and not p.endswith('.part.wav')]
print(f'{len(out)} clips already transcribed, {len(todo)} to go', flush=True)
for p in todo:
    if out_of_time(20):
        save_json(out, TR)
        stop_for_now(f'{len(todo) - todo.index(p)} clips left')
    a = load_wav_checked(p, CLIPS.get(os.path.basename(p)[:-4], {}).get('dur'))
    if a is None:
        continue
    db = frame_db(a)
    floor = noise_floor(db)
    vad = sherpa_onnx.VoiceActivityDetector(vcfg, buffer_size_in_seconds=600)
    ws = vcfg.silero_vad.window_size
    for i in range(0, len(a), ws):
        vad.accept_waveform(a[i:i + ws])
    vad.flush()
    segs = []
    while not vad.empty():
        s = vad.front
        vad.pop()
        st = s.start / 16000
        smp = np.array(s.samples, dtype=np.float32)
        stream = rec.create_stream()
        stream.accept_waveform(16000, smp)
        rec.decode_stream(stream)
        r = stream.result
        words, cur = [], None
        for tok, ts in zip(r.tokens, r.timestamps):
            if tok.startswith(('▁', ' ')) or cur is None:
                if cur:
                    words.append(cur)
                cur = {'w': tok.replace('▁', '').strip().lower(), 's': round(st + ts, 2)}
            else:
                cur['w'] += tok.lower()
        if cur:
            words.append(cur)
        end = st + len(smp) / 16000
        for k, w in enumerate(words):
            w['e'] = round(words[k + 1]['s'] if k + 1 < len(words) else end, 2)
        trim_ends(words, db, floor)
        if r.text.strip():
            segs.append({'s': round(st, 2), 'e': round(end, 2), 't': r.text.strip().lower(), 'words': words})
    key = os.path.basename(p)[:-4]
    out[key] = {'dur': round(len(a) / 16000, 2), 'segs': segs}
    save_json(out, TR)
    print(key, '|', ' / '.join(f"[{s['s']}-{s['e']}] {s['t']}" for s in segs), flush=True)
save_json(out, TR)
print('transcript ->', TR)
