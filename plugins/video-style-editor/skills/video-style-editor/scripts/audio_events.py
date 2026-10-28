#!/usr/bin/env python3
"""Step 3: "ears" for Claude - non-speech sound events + loudness peaks.

usage: python scripts/audio_events.py PROJECT [--model mini|base] [--force]   (resumable, like transcribe.py)
writes work/audio_events.json:
  {key: {events: [{t, label, p}], peaks: [{t, db}]}}
- events: AudioSet tags (laughter, thump, music, applause...) from a CED model, 2 s window / 1 s hop.
  Treat as hints: Vietnamese speech is sometimes tagged as "Mantra", rustling as animals.
- peaks: 0.5 s windows at least 8 dB above the clip median = shouting / exclamations.
"""
import glob
import os
import sys
import wave

import numpy as np
import sherpa_onnx

sys.path.insert(0, os.path.dirname(__file__))
from common import MODELS, load_wav_checked, load_json, out_of_time, project_paths, save_json, stop_for_now  # noqa: E402

P = project_paths(sys.argv[1])
size = sys.argv[sys.argv.index('--model') + 1] if '--model' in sys.argv else 'mini'
M = os.path.join(MODELS, f'sherpa-onnx-ced-{size}-audio-tagging-2024-04-19')
tagger = sherpa_onnx.AudioTagging(sherpa_onnx.AudioTaggingConfig(
    model=sherpa_onnx.AudioTaggingModelConfig(ced=f'{M}/model.int8.onnx', num_threads=os.cpu_count() or 2),
    labels=f'{M}/class_labels_indices.csv', top_k=5))

IGNORE = {'Speech', 'Male speech, man speaking', 'Female speech, woman speaking', 'Narration, monologue',
          'Conversation', 'Inside, small room', 'Inside, large room or hall', 'Speech synthesizer',
          'Child speech, kid speaking', 'Mantra', 'Chant'}

OUT = os.path.join(P['work'], 'audio_events.json')
CLIPS = load_json(os.path.join(P['work'], 'clips.json'), {})
out = {} if '--force' in sys.argv else load_json(OUT, {})
todo = [p for p in sorted(glob.glob(os.path.join(P['work'], 'audio', '*.wav'))) if os.path.basename(p)[:-4] not in out and not p.endswith('.part.wav')]
for p in todo:
    if out_of_time(20):
        save_json(out, OUT)
        stop_for_now(f'{len(todo) - todo.index(p)} clips left')
    x = load_wav_checked(p, CLIPS.get(os.path.basename(p)[:-4], {}).get('dur'))
    if x is None:
        continue
    ev = []
    for t in np.arange(0, max(len(x) / 16000 - 1, 0.1), 1.0):
        s = tagger.create_stream()
        s.accept_waveform(16000, x[int(t * 16000):int((t + 2) * 16000)])
        ev += [{'t': float(t), 'label': e.name, 'p': round(e.prob, 2)} for e in tagger.compute(s)
               if e.name not in IGNORE and e.prob > 0.3]
    win = 8000
    db = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + win] ** 2)) + 1e-6) for i in range(0, len(x), win)])
    med = float(np.median(db)) if len(db) else -60
    peaks = [{'t': round(i * 0.5, 1), 'db': round(float(v), 1)} for i, v in enumerate(db) if v > med + 8]
    key = os.path.basename(p)[:-4]
    out[key] = {'events': ev, 'peaks': peaks, 'median_db': round(med, 1)}
    save_json(out, OUT)
    print(key, '|', ', '.join(f"{e['t']:.0f}s {e['label']}" for e in ev)[:300], flush=True)
save_json(out, OUT)
print('events ->', OUT)
