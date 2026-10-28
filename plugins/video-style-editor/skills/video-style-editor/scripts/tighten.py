#!/usr/bin/env python3
"""Cut filler sounds ("ờ", "ừm", a lone "à"/"ừ") and dead air out of a plan's pieces.

usage: python scripts/tighten.py PROJECT plans/IN.json [plans/OUT.json] [--gap 0.45] [--dry]
  writes OUT (default plans/IN-tight.json) where every speaking piece is split around its fillers and long pauses,
  so the video plays straight through (pro editor: "cắt hết những phần ừ, à, phần thừa -> video liền mạch, người ta
  xem không muốn dừng"). Then `vse.py lint` the new plan and render it as usual.

What it does per piece (b-roll without captions, voice-over pieces and J/L cuts are left alone):
- filler = always "ờ ờm ừm ơ ư ầ hừm"; "à ừ ừa" only when said on their own (a pause on both sides) - inside a
  sentence "năm 2022 à" they are words. A word you hid with "_" in `fix` that is one of those sounds is cut too.
- pause = a gap > --gap s between two words is shortened to ~0.2 s.
- sound without a word = the ASR often drops "ờ"/"ừm" altogether: a gap of 0.25 s+ between two words that is
  clearly voiced is listed for you to check with `vse.py inspect`; --sounds cuts them too (it may also cut a word
  the ASR missed - listen first).
- the new pieces alternate zoom (1.0 / 1.12) so a cut inside one take reads as a deliberate jump cut; `fix`, SFX,
  big text and the transition follow the words they belong to.
"""
import argparse
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import clip_key, load_json, load_prefs, project_paths, save_json  # noqa: E402

HARD = {'ờ', 'ờm', 'ừm', 'ơ', 'ư', 'ầ', 'hừm', 'ừm', 'hửm', 'ê'}
SOFT = {'à', 'ừ', 'ừa', 'ờ', 'ạ'}
LEAD, TAIL = 0.06, 0.10      # keep this much before a word's start / after its end at a cut


def words_in(TR, clip, a, b):
    segs = TR.get(clip_key(clip), {}).get('segs', [])
    return [w for s in segs for w in s['words'] if a - 0.05 <= w['s'] < b]


_db = {}


def voiced(P, clip, s0, s1):
    """mean level of [s0, s1] above the clip's quiet floor (dB), or None without audio"""
    k = clip_key(clip)
    if k not in _db:
        f = os.path.join(P['work'], 'audio', k + '.wav')
        _db[k] = None
        if os.path.exists(f):
            with wave.open(f) as w:
                sr = w.getframerate()
                x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
            hop = sr // 100
            n = len(x) // hop
            d = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
            _db[k] = (d, float(np.percentile(d, 10)))
    if _db[k] is None:
        return None
    d, floor = _db[k]
    seg = d[int(s0 * 100):int(s1 * 100)]
    return float(np.mean(seg)) - floor if len(seg) else None


def tighten_piece(TR, p, gap_max, stats, P=None, sounds=False):
    if p.get('style') == 'none' or p.get('audio') or 'va' in p:
        return [p]
    a, b = p['a'], p['b']
    ws = words_in(TR, p['clip'], a, b)
    if len(ws) < 2:
        return [p]
    fix = p['fix'].split() if p.get('fix') and len(p['fix'].split()) == len(ws) else None
    cut_word = []
    for k, w in enumerate(ws):
        t = w['w'].lower()
        gb = w['s'] - ws[k - 1]['e'] if k else 1.0
        ga = ws[k + 1]['s'] - w['e'] if k + 1 < len(ws) else 1.0
        hidden = fix is not None and fix[k] == '_'
        cut_word.append(t in HARD or (t in SOFT and gb > 0.12 and ga > 0.12) or (hidden and t in HARD | SOFT))
    # regions to remove (clip time)
    cuts = []
    kept = [k for k in range(len(ws)) if not cut_word[k]]
    if not kept:
        return [p]
    for k in range(len(ws)):
        if cut_word[k]:
            prev = max([j for j in kept if j < k], default=None)
            nxt = min([j for j in kept if j > k], default=None)
            s0 = ws[prev]['e'] + TAIL if prev is not None else a
            s1 = ws[nxt]['s'] - LEAD if nxt is not None else b
            if s1 - s0 > 0.05:
                cuts.append([s0, s1])
                stats['fillers'] += 1
    for j0, j1 in zip(kept, kept[1:]):
        g0, g1 = ws[j0]['e'], ws[j1]['s']
        lv = voiced(P, p['clip'], g0 + 0.05, g1 - 0.05) if P and g1 - g0 >= 0.35 else None
        if lv is not None and lv > 14:   # sound in the gap but no word: an "ờ" the ASR dropped (or a missed word)
            stats['sounds'].append(f"{os.path.basename(p['clip'])} {g0:.2f}-{g1:.2f} (+{lv:.0f} dB)")
            if sounds:
                cuts.append([g0 + TAIL, g1 - LEAD])
            continue
        if g1 - g0 > gap_max:
            cuts.append([g0 + TAIL, g1 - LEAD])
            stats['pauses'] += 1
    if not cuts:
        return [p]
    cuts.sort()
    merged = [cuts[0]]
    for c in cuts[1:]:
        if c[0] <= merged[-1][1] + 0.05:
            merged[-1][1] = max(merged[-1][1], c[1])
        else:
            merged.append(c)
    segs, t = [], a
    for c0, c1 in merged:
        c0, c1 = max(c0, a), min(c1, b)
        if c0 - t > 0.05:
            segs.append([t, c0])
        t = max(t, c1)
    if b - t > 0.05:
        segs.append([t, b])
    # drop slivers without a kept word
    out_segs = []
    for s0, s1 in segs:
        has = [k for k in kept if s0 - 0.05 <= ws[k]['s'] < s1]
        if has or s1 - s0 >= 0.35:
            out_segs.append([round(s0, 3), round(s1, 3)])
    stats['removed'] += (b - a) - sum(s1 - s0 for s0, s1 in out_segs)
    if len(out_segs) <= 1 and out_segs == [[a, b]]:
        return [p]
    big_first = None
    if p.get('big'):
        bw = p['big'].split('\\N')[0].split()
        big_first = bw[0].upper().strip('*') if bw else None
    z0 = p.get('zoom', 1.0)
    res = []
    for n, (s0, s1) in enumerate(out_segs):
        q = {k: v for k, v in p.items() if k not in ('a', 'b', 'fix', 'sfx', 'big', 'big_at', 'transition', 'zoom',
                                                     'image', 'move', 'move_at', 'move_amt')}
        q['a'], q['b'] = s0, s1
        q['zoom'] = z0 if n % 2 == 0 else (1.12 if z0 < 1.05 else 1.0)
        if n == 0:   # one-off moments stay on the first piece
            for k in ('transition', 'move', 'move_at', 'move_amt'):
                if k in p:
                    q[k] = p[k]
        win = words_in(TR, p['clip'], s0, s1)
        if fix or any(cut_word[ws.index(w)] for w in win if w in ws):
            toks = []
            for w in win:
                k = ws.index(w) if w in ws else None
                if k is None or cut_word[k]:
                    toks.append('_')
                else:
                    toks.append(fix[k] if fix else w['w'].upper())
            q['fix'] = ' '.join(toks)
        res.append(q)
    # big text goes with the piece that says its first word (else the first piece)
    if p.get('big'):
        tgt = 0
        for n, q in enumerate(res):
            if big_first and any(w['w'].upper() == big_first for w in words_in(TR, p['clip'], q['a'], q['b'])):
                tgt = n
                break
        res[tgt]['big'] = p['big']
        if 'big_at' in p and tgt == 0:
            res[tgt]['big_at'] = p['big_at']
    # a picture-in-picture keeps its moment: it goes to the piece where it starts, shortened to that piece
    if p.get('image'):
        img = p['image']
        t = a + img.get('at', 0.0)
        tgt = next((n for n, q in enumerate(res) if q['a'] <= t < q['b']), None)
        if tgt is None:
            tgt = next((n for n, q in enumerate(res) if q['a'] > t), len(res) - 1)
        at = max(t - res[tgt]['a'], 0.0)
        res[tgt]['image'] = dict(img, at=round(at, 2), dur=round(min(img.get('dur', 99), res[tgt]['b'] - res[tgt]['a'] - at), 2))
    # SFX keep their moment in the speech
    for s in p.get('sfx', []):
        t = a + s.get('at', 0.0)
        tgt, at = len(res) - 1, None
        for n, q in enumerate(res):
            if t < q['a']:
                tgt, at = n, 0.0
                break
            if q['a'] <= t < q['b']:
                tgt, at = n, t - q['a']
                break
        if at is None:
            at = max(res[tgt]['b'] - res[tgt]['a'] - 0.1, 0.0)
        res[tgt].setdefault('sfx', []).append(dict(s, at=round(at, 2)))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('plan')
    ap.add_argument('out', nargs='?')
    ap.add_argument('--gap', type=float, default=(load_prefs().get('pacing') or {}).get('tighten_gap', 0.45),
                    help='shorten pauses longer than this (s); default from my-style pacing.tighten_gap')
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--sounds', action='store_true', help='also cut voiced gaps without a word (listen first)')
    a = ap.parse_args()
    P = project_paths(a.project)
    src = a.plan if os.path.isabs(a.plan) else os.path.join(P['root'], a.plan)
    plan = load_json(src)
    TR = load_json(os.path.join(P['work'], 'transcript.json'), {})
    stats = {'fillers': 0, 'pauses': 0, 'removed': 0.0, 'sounds': []}
    before = sum(p['b'] - p['a'] for p in plan['pieces'])
    pieces = []
    for p in plan['pieces']:
        pieces += tighten_piece(TR, p, a.gap, stats, P, a.sounds)
    after = sum(p['b'] - p['a'] for p in pieces)
    print(f"{len(plan['pieces'])} -> {len(pieces)} pieces, {stats['fillers']} fillers + {stats['pauses']} long pauses cut, "
          f"{before:.1f}s -> {after:.1f}s")
    if stats['sounds']:
        how = 'cut' if a.sounds else 'kept - check with vse.py inspect, re-run with --sounds to cut'
        print(f"{len(stats['sounds'])} voiced gaps without a word ({how}):")
        for x in stats['sounds']:
            print('  ', x)
    if a.dry:
        return
    out = a.out or os.path.splitext(a.plan)[0] + '-tight.json'
    out = out if os.path.isabs(out) else os.path.join(P['root'], out)
    name = os.path.splitext(os.path.basename(out))[0]
    save_json(dict(plan, name=name, pieces=pieces), out)
    print('->', out, '(now: vse.py lint, then render)')


if __name__ == '__main__':
    main()
