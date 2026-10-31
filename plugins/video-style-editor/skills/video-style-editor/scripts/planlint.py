#!/usr/bin/env python3
"""Check an edit plan BEFORE rendering and print its timeline.

usage: python scripts/planlint.py PROJECT plans/NAME.json
prints
  timeline  output time of every piece (use it to map a reviewer's "0:37" to a piece), clip, a-b,
            zoom / vol, captions, big text, SFX
  ERROR     must fix: missing clip or SFX file, bad a/b, `fix` word count != ASR word count
  warn      look at it: word clipped at a cut, piece much quieter/louder than the rest (suggested `vol`),
            SFX peak landing on a word, same zoom on a jump cut, big text on a very short piece
exit code 1 when there are errors.
"""
import os
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SFX, SFX_MANIFEST, clip_key, find_file, frame_db, load_json, load_prefs, load_wav, noise_floor, project_paths  # noqa: E402

_audio = {}


def clip_db(P, key):
    if key not in _audio:
        path = os.path.join(P['work'], 'audio', key + '.wav')
        db = frame_db(load_wav(path)) if os.path.exists(path) else np.array([-99.0])
        _audio[key] = (db, noise_floor(db))
    return _audio[key]


def seg_db(db, s, e):
    """mean level (dB) of the 50 ms frames covering [s, e)"""
    i0, i1 = max(0, int(s / 0.05)), max(0, int(np.ceil(e / 0.05)))
    f = db[i0:i1]
    return float(np.mean(f)) if len(f) else -99.0


def lufs(wav, a, b):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', wav,
                        '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = re.findall(r'I:\s+(-?[\d.]+) LUFS', r)
    return float(m[-1]) if m else -99.0


def asr_words(TR, p):
    vo = p.get('audio')
    clip, a = (vo['file'], vo.get('a', 0.0)) if vo else (p['clip'], p['a'])
    b = a + p['b'] - p['a']
    segs = TR.get(clip_key(clip), {}).get('segs', [])
    return [w for s in segs for w in s['words'] if a - 0.05 <= w['s'] < b]


def fmt(t):
    return f'{int(t // 60)}:{t % 60:04.1f}'


def lint(project, plan_file, show_timeline=True):
    P = project_paths(project)
    plan = load_json(plan_file if os.path.isabs(plan_file) else os.path.join(P['root'], plan_file))
    TR = load_json(os.path.join(P['work'], 'transcript.json'), {})
    clips = load_json(os.path.join(P['work'], 'clips.json'), {})
    sfx_names = {s['file'][4:-4] for s in load_json(SFX_MANIFEST, [])}
    errors, warns, rows, levels = [], [], [], []
    said = []   # (piece index, tag, style, words) - to catch a line kept twice (two takes of the same sentence)
    pieces = plan['pieces']
    T = 0.0

    def cont(x, y):
        return x['clip'] == y['clip'] and abs(x['b'] - y['a']) < 0.02

    for i, p in enumerate(pieces):
        tag = f'piece {i:2d} ({fmt(T)})'
        key = clip_key(p['clip'])
        a, b = p['a'], p['b']
        dur = b - a
        if not os.path.exists(find_file(P['raw'], p['clip'])):
            errors.append(f'{tag}: clip not found: raw/{p["clip"]}')
        cd = clips.get(key, {}).get('dur')
        if dur <= 0 or a < 0 or (cd and b > cd + 0.15):
            errors.append(f'{tag}: bad a/b {a}-{b} (clip is {cd}s)')
        ws = asr_words(TR, p)
        style = p.get('style', 'normal')
        said.append((i, tag, style, [w['w'].lower() for w in ws]))
        if p.get('fix'):
            n = len(p['fix'].split())
            if n != len(ws):
                errors.append(f'{tag}: fix has {n} words, ASR has {len(ws)} in [{a - 0.05:.2f}, {b}): '
                              + ' '.join(w['w'] for w in ws) + "  -> use _ to hide, + to glue")
            cap = ' '.join(t.replace('+', ' ').lstrip('*') for t in p['fix'].split() if t != '_')
        else:
            cap = ' '.join(w['w'].upper() for w in ws)
        if style == 'none':
            cap = ''
        vo = p.get('audio')   # voice-over: sound checks run on the voice file, not on the picture clip
        if vo:
            key, a, b = clip_key(vo['file']), vo.get('a', 0.0), vo.get('a', 0.0) + dur
        db, floor = clip_db(P, key)
        # clipped words at non-contiguous cuts
        if not (i > 0 and cont(pieces[i - 1], p)):
            head = seg_db(db, a - 0.1, a)
            if head > floor + 10 and 'va' not in p:
                warns.append(f'{tag}: sound right before a={a} ({head:.0f} dB, noise {floor:.0f}) - word head clipped? '
                             f'(fine if it is a word you dropped on purpose)')
        if not (i + 1 < len(pieces) and cont(p, pieces[i + 1])):
            tail = seg_db(db, b, b + 0.1)
            if tail > floor + 10:
                warns.append(f'{tag}: sound right after b={b} ({tail:.0f} dB, noise {floor:.0f}) - word tail clipped?')
        # loudness of the piece (EBU R128 integrated, K-weighted) after its vol
        if style != 'none' and dur >= 0.5:
            lu = lufs(os.path.join(P['work'], 'audio', key + '.wav'), a, b)
            if lu > -60:
                levels.append((i, lu + p.get('vol', 0), floor, tag))
        # jump cut inside one take with the same zoom looks like a glitch
        if i > 0 and pieces[i - 1]['clip'] == p['clip'] and pieces[i - 1].get('zoom', 1.0) == p.get('zoom', 1.0) \
                and not p.get('transition') and 'va' not in p and 'va' not in pieces[i - 1]:
            warns.append(f'{tag}: same clip and same zoom as the previous piece - alternate 1.0 / 1.12')
        if p.get('audio') and not os.path.exists(find_file(P['raw'], p['audio']['file'])):
            errors.append(f'{tag}: voice-over file not found: raw/{p["audio"]["file"]}')
        if p.get('speaker') and p['speaker'] not in plan.get('speakers', {}):
            warns.append(f'{tag}: speaker "{p["speaker"]}" has no colour in plan.speakers - captions stay white')
        if p.get('image'):
            f = p['image'].get('file', '')
            if not os.path.exists(find_file(P['root'], f)):
                errors.append(f'{tag}: image not found: {f}')
        if p.get('tint') and p['tint'] not in ('pink', 'warm', 'cool', 'bw') and '=' not in p['tint']:
            errors.append(f'{tag}: unknown tint {p["tint"]} (pink, warm, cool, bw or an ffmpeg filter)')
        if p.get('big') and dur < 0.8:
            warns.append(f'{tag}: big text on a {dur:.2f}s piece - too short to read')
        if dur < 0.35:
            warns.append(f'{tag}: very short piece ({dur:.2f}s)')
        sx = []
        for s in p.get('sfx', []):
            if s['name'] not in sfx_names and not os.path.exists(os.path.join(SFX, f"sfx_{s['name']}.mp3")):
                errors.append(f'{tag}: unknown SFX {s["name"]} (see assets/sfx/manifest.json)')
            t = a + s.get('at', 0)
            on = [w for w in ws if w['s'] + 0.03 < t < min(w['e'], w['s'] + 0.45)]
            if on and s.get('gain', -6) > -16 and not s['name'].startswith(('pop', 'paper', 'whoosh')):
                warns.append(f'{tag}: {s["name"]} peaks on the word "{on[0]["w"]}" at gain {s.get("gain")} - '
                             'move it into a pause or go below -16')
            sx.append(f"{s['name']}@{s.get('at', 0)}{s.get('gain', -6):+}")
        rows.append(f"{i:2d} {fmt(T)}-{fmt(T + dur)} {os.path.basename(p['clip'])[:12]:12} {a:6.2f}-{b:6.2f} "
                    f"z{p.get('zoom', 1.0):<4} {('v%+g' % p['vol']) if p.get('vol') else '':5}"
                    f"{' dn' if p.get('denoise') else '   '} {style[:6]:6} "
                    + (f"[{p['big']}] " if p.get('big') else '') + (f"<{p['transition']}> " if p.get('transition') else '')
                    + cap[:70] + (('  ♪ ' + ' '.join(sx)) if sx else ''))
        T += dur
    if len(levels) >= 3:
        med = float(np.median([l for _, l, _, _ in levels]))
        for i, lv, floor, tag in levels:
            d = med - lv
            if abs(d) > 4:
                hint = ' + denoise (noisy take)' if d > 0 and floor > -45 and not pieces[i].get('denoise') else ''
                warns.append(f'{tag}: {lv - med:+.0f} LU vs the median piece -> try vol '
                             f'{pieces[i].get("vol", 0) + round(d * 0.7):+d}{hint} (a hint: let a listener confirm)')
    m = plan.get('music')
    if m and not os.path.exists(find_file(P['root'], m['file'])):
        errors.append(f"music file not found: {m['file']}")
    # pro-editor feedback (10/2026): repeated SFX sound monotonous; transitions only at the start feel flat
    # the same 4+ words in two body pieces = two takes of one line (teaser lines repeat on purpose)
    seen = {}
    for i, tag, style, ws in said:
        if style == 'teaser':
            continue
        for k in range(len(ws) - 3):
            g = ' '.join(ws[k:k + 4])
            j = seen.get(g)
            if j is not None and j[0] != i and not (j[0] == i - 1 and cont(pieces[j[0]], pieces[i])):
                warns.append(f'{tag}: says "{g}..." again (also {j[1]}) - two takes of one line? keep the cleanest '
                             'full take and tell the user which one you dropped')
                break
            seen.setdefault(g, (i, tag))
    from collections import Counter
    my = load_prefs().get('sfx') or {}
    mx = my.get('max_repeat', 2)
    for name, n in Counter(s['name'] for p in pieces for s in p.get('sfx', [])).items():
        if n > mx:
            warns.append(f'SFX {name} used {n}x - at most {mx}x per video, rotate variants (docs/editing-craft.md 3)')
        if name in (my.get('banned') or []):
            errors.append(f'SFX {name} is banned in your my-style/preferences.yaml')
    starts, t0 = [], 0.0
    for p in pieces:
        if p.get('transition'):
            starts.append(t0)
        t0 += p['b'] - p['a']
    if T > 45 and not [s for s in starts if 0.15 * T < s < 0.9 * T]:
        warns.append(f'{T:.0f}s video with no transition in the middle - add 1-3 (one kind, e.g. "zoom") '
                     'where the topic/section changes')
    for p in pieces:
        if p.get('transition') not in (None, 'paper', 'flash', 'zoom'):
            errors.append(f"unknown transition {p['transition']} (paper, flash, zoom)")
        if p.get('fit') not in (None, 'crop', 'blur'):
            errors.append(f"unknown fit {p['fit']} (crop, blur)")
    st = plan.get('style', {})
    lk = st.get('look', 'clean')
    if lk.endswith('.cube') and not os.path.exists(find_file(P['root'], lk)):
        errors.append(f'look file not found: {lk}')
    elif not lk.endswith('.cube') and lk not in ('clean', 'warm', 'cool', 'film', 'none') and '=' not in lk:
        errors.append(f'unknown look {lk} (clean, warm, cool, film, none, a .cube file or an ffmpeg filter)')
    mv = {**(load_prefs().get('style') or {}), **st}.get('caption_margin_v', 470)
    if not 380 <= mv <= 700:
        warns.append(f'caption_margin_v {mv}: outside the TikTok safe zone (380-700 px from the bottom, ~470 ideal)')
    teaser = sum(p['b'] - p['a'] for p in pieces if p.get('style') == 'teaser')
    if teaser > 15 or 0 < teaser < 4:
        warns.append(f'teaser is {teaser:.1f}s - keep it 5-15 s (2-4 lines)')
    if show_timeline:
        print(f"{plan['name']}: {len(pieces)} pieces, {T:.1f}s, teaser {teaser:.1f}s, "
              f"{sum(len(p.get('sfx', [])) for p in pieces)} SFX")
        print('\n'.join(rows))
    for e in errors:
        print('ERROR', e)
    for w in warns:
        print('warn ', w)
    print(f'{len(errors)} errors, {len(warns)} warnings')
    return errors, warns


if __name__ == '__main__':
    errs, _ = lint(sys.argv[1], sys.argv[2])
    sys.exit(1 if errs else 0)
