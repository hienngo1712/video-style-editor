#!/usr/bin/env python3
"""Your personal editing style: the part of the skill that learns from you, day by day.

usage:
  python scripts/mystyle.py init                       create <VSE_HOME>/my-style/ from templates/my-style
  python scripts/mystyle.py show                       preferences + rules + recent feedback (Claude reads this first)
  python scripts/mystyle.py note "TEXT" [--project P] [--video NAME] [--at 0:12] [--tag captions] [--by editor]
                                                       log one piece of feedback in journal.md + feedback.jsonl
  python scripts/mystyle.py learn PROJECT plans/A.json plans/B.json
                                                       what changed between Claude's plan (A) and the corrected one (B):
                                                       logged, plus suggested preference updates
  python scripts/mystyle.py stats                      which topics get the most feedback (where to improve first)
  python scripts/mystyle.py set KEY VALUE              one preference, dotted key, YAML value
                                                       (style.caption_size 88 | sfx.banned '["laughtrack_424"]' | onboarded 2026-10-28)
  python scripts/mystyle.py rule "TEXT"                add a plain-language rule
  python scripts/mystyle.py word "asr spelling" "Correct"   caption spelling you always want
  python scripts/mystyle.py brief                      path + text of brief.md (the user's portrait in words)

Files (in <VSE_HOME>/my-style/, never inside the plugin, so updates keep them):
  preferences.yaml   style defaults for every render, SFX likes/bans, pacing, caption spellings, rules
  brief.md           who the user is: channel, audience, goals, tone, likes / dislikes (written after onboarding)
  journal.md         human-readable feedback log
  feedback.jsonl     the same, one JSON object per line (for stats)
Tags: captions, text, audio, sfx, music, cut, pacing, motion, color, story, teaser, other.
"""
import argparse
import datetime
import json
import os
import shutil
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import MYSTYLE, SKILL, load_json, load_prefs, project_paths  # noqa: E402

HEADER = ("# My editing style - written by `vse.py style ...` and by hand. What each key means:\n"
          "# templates/my-style/preferences.yaml in the skill, docs/personalize.md, docs/onboarding.md.\n"
          "# Priority when rendering: built-in defaults < this file < the style block of one plan.\n")


def save_prefs(d):
    import yaml
    os.makedirs(MYSTYLE, exist_ok=True)
    p = os.path.join(MYSTYLE, 'preferences.yaml')
    if os.path.exists(p):
        shutil.copy(p, p + '.bak')   # one step of undo
    with open(p + '.part', 'w', encoding='utf-8') as f:
        f.write(HEADER + '\n' + yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=110))
    os.replace(p + '.part', p)


def _need():
    if not os.path.exists(os.path.join(MYSTYLE, 'preferences.yaml')):
        init()


def set_pref(key, value):
    import yaml
    _need()
    d = load_prefs()
    try:
        v = yaml.safe_load(value)
    except yaml.YAMLError:
        v = value
    cur = d
    parts = key.split('.')
    for k in parts[:-1]:
        if not isinstance(cur.get(k), dict):
            cur[k] = {}
        cur = cur[k]
    old = cur.get(parts[-1])
    cur[parts[-1]] = v
    save_prefs(d)
    print(f'{key}: {json.dumps(old, ensure_ascii=False, default=str)} -> {json.dumps(v, ensure_ascii=False, default=str)}')


def add_rule(text):
    _need()
    d = load_prefs()
    rules = d.get('rules') or []
    if text not in rules:
        rules.append(text)
    d['rules'] = rules
    save_prefs(d)
    print(f'rule {len(rules)}: {text}')


def add_word(asr, correct):
    _need()
    d = load_prefs()
    w = d.get('words') or {}
    w[asr.lower()] = correct
    d['words'] = w
    save_prefs(d)
    print(f'caption spelling: "{asr.lower()}" -> "{correct}"')


def brief():
    _need()
    p = os.path.join(MYSTYLE, 'brief.md')
    if not os.path.exists(p):
        shutil.copy(os.path.join(TEMPLATE, 'brief.md'), p)
    print(p)
    print(open(p, encoding='utf-8').read())

TEMPLATE = os.path.join(SKILL, 'templates', 'my-style')
TAGS = ('captions', 'text', 'audio', 'sfx', 'music', 'cut', 'pacing', 'motion', 'color', 'story', 'teaser', 'other')


def init(force=False):
    os.makedirs(MYSTYLE, exist_ok=True)
    for f in os.listdir(TEMPLATE):
        dst = os.path.join(MYSTYLE, f)
        if force or not os.path.exists(dst):
            shutil.copy(os.path.join(TEMPLATE, f), dst)
            print('created', dst)
        else:
            print('kept   ', dst)


def _log(entry):
    os.makedirs(MYSTYLE, exist_ok=True)
    if not os.path.exists(os.path.join(MYSTYLE, 'journal.md')):
        init()
    with open(os.path.join(MYSTYLE, 'feedback.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False, default=str) + '\n')
    where = '/'.join(x for x in (entry.get('project'), entry.get('video')) if x)
    if entry.get('at'):
        where += f" @ {entry['at']}"
    line = (f"- [{entry['date']}] [{where or '-'}] ({entry.get('tag', 'other')}, {entry.get('by', 'user')}) "
            f"{entry['text']}" + (f" -> {entry['fix']}" if entry.get('fix') else ''))
    with open(os.path.join(MYSTYLE, 'journal.md'), 'a', encoding='utf-8') as f:
        f.write(line + '\n')
    print('logged:', line)


def note(a):
    tag = a.tag if a.tag in TAGS else 'other'
    _log({'date': datetime.date.today().isoformat(), 'text': a.text, 'project': a.project, 'video': a.video,
          'at': a.at, 'tag': tag, 'by': a.by, 'fix': a.fix})


def entries():
    p = os.path.join(MYSTYLE, 'feedback.jsonl')
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p, encoding='utf-8'):
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out


def show():
    if not os.path.exists(os.path.join(MYSTYLE, 'preferences.yaml')):
        print(f'no personal style yet ({MYSTYLE}) - run: vse.py style init')
        return
    pr = load_prefs()
    print(f'# my-style ({MYSTYLE})')
    if not pr.get('onboarded'):
        print('!! NOT ONBOARDED - before the first video, interview the user (docs/onboarding.md), then '
              '`style set onboarded <date>`')
    bp = os.path.join(MYSTYLE, 'brief.md')
    if os.path.exists(bp):
        txt = [ln for ln in open(bp, encoding='utf-8').read().splitlines() if ln.strip() and not ln.startswith('<!--')]
        print('brief:')
        for ln in txt[:25]:
            print('  ' + ln)
    print('default profile:', pr.get('default_profile', '-'), '| language:', pr.get('language', '-'))
    print('style:', json.dumps(pr.get('style', {}), ensure_ascii=False, default=str))
    print('sfx:', json.dumps(pr.get('sfx', {}), ensure_ascii=False, default=str))
    print('pacing:', json.dumps(pr.get('pacing', {}), ensure_ascii=False, default=str))
    if pr.get('words'):
        print('caption spellings:', json.dumps(pr['words'], ensure_ascii=False, default=str))
    print('rules:')
    for r in pr.get('rules') or []:
        print('  -', r)
    es = entries()
    if es:
        print(f'recent feedback ({len(es)} total):')
        for e in es[-12:]:
            print(f"  [{e['date']}] ({e.get('tag')}) {e['text']}" + (f" -> {e['fix']}" if e.get('fix') else ''))
        c = Counter(e.get('tag', 'other') for e in es)
        print('most feedback on:', ', '.join(f'{t} {n}' for t, n in c.most_common(5)))


def stats():
    es = entries()
    if not es:
        print('no feedback logged yet')
        return
    by = defaultdict(list)
    for e in es:
        by[e.get('tag', 'other')].append(e)
    for t, lst in sorted(by.items(), key=lambda kv: -len(kv[1])):
        print(f'{t}: {len(lst)}')
        for e in lst[-3:]:
            print(f"   [{e['date']}] {e['text'][:110]}")


def _match(before, after):
    """pair pieces of two plans by clip + overlapping time"""
    used, pairs = set(), []
    for i, p in enumerate(before):
        best, bo = None, 0.0
        for j, q in enumerate(after):
            if j in used or q['clip'] != p['clip']:
                continue
            ov = min(p['b'], q['b']) - max(p['a'], q['a'])
            if ov > bo:
                best, bo = j, ov
        if best is not None:
            used.add(best)
            pairs.append((i, best))
    return pairs, [i for i in range(len(before)) if i not in {x for x, _ in pairs}], \
        [j for j in range(len(after)) if j not in used]


def learn(project, fa, fb):
    P = project_paths(project)
    A = load_json(fa if os.path.isabs(fa) else os.path.join(P['root'], fa))
    B = load_json(fb if os.path.isabs(fb) else os.path.join(P['root'], fb))
    notes, sugg = [], []
    sa, sb = A.get('style', {}), B.get('style', {})
    for k in sorted(set(sa) | set(sb)):
        if sa.get(k) != sb.get(k):
            notes.append(f'style.{k}: {sa.get(k)} -> {sb.get(k)}')
            sugg.append(f'style.{k}: {json.dumps(sb.get(k), ensure_ascii=False, default=str)}')
    ma, mb = A.get('music') or {}, B.get('music') or {}
    if ma.get('gain') != mb.get('gain') and ma and mb:
        notes.append(f"music gain {ma.get('gain')} -> {mb.get('gain')} dB")
    pa, pb = A['pieces'], B['pieces']
    pairs, gone, new = _match(pa, pb)
    trims, gains, words = [], [], Counter()
    for i, j in pairs:
        p, q = pa[i], pb[j]
        da, db = q['a'] - p['a'], q['b'] - p['b']
        if abs(da) > 0.04 or abs(db) > 0.04:
            trims.append((da, db))
        for k in ('zoom', 'vol', 'denoise', 'transition', 'big', 'move', 'tint', 'caption_pos', 'style'):
            if p.get(k) != q.get(k):
                notes.append(f"piece {i} ({os.path.basename(p['clip'])}) {k}: {p.get(k)} -> {q.get(k)}")
        sp = {s['name']: s.get('gain') for s in p.get('sfx', [])}
        sq = {s['name']: s.get('gain') for s in q.get('sfx', [])}
        for n in set(sp) | set(sq):
            if n not in sq:
                notes.append(f'piece {i}: SFX {n} removed')
            elif n not in sp:
                notes.append(f'piece {i}: SFX {n} added ({sq[n]} dB)')
            elif sp[n] != sq[n] and sp[n] is not None and sq[n] is not None:
                gains.append(sq[n] - sp[n])
        fp, fq = (p.get('fix') or '').split(), (q.get('fix') or '').split()
        if fp and fq and len(fp) == len(fq):
            for x, y in zip(fp, fq):
                if x != y and '_' not in (x, y):
                    words[(x.lower().strip('*'), y.strip('*'))] += 1
    for i in gone:
        notes.append(f"piece {i} ({os.path.basename(pa[i]['clip'])} {pa[i]['a']}-{pa[i]['b']}) dropped")
    for j in new:
        notes.append(f"new piece ({os.path.basename(pb[j]['clip'])} {pb[j]['a']}-{pb[j]['b']})")
    if trims:
        ha = sum(t[0] for t in trims) / len(trims)
        hb = sum(t[1] for t in trims) / len(trims)
        notes.append(f'{len(trims)} cuts moved: start {ha:+.2f} s, end {hb:+.2f} s on average')
        if ha > 0.05 or hb < -0.05:
            sugg.append('rules: "Cắt sát hơn: bỏ khoảng thừa đầu/cuối câu."')
    if gains:
        g = sum(gains) / len(gains)
        notes.append(f'{len(gains)} SFX gain changes, {g:+.1f} dB on average')
        if abs(g) >= 2 and len(gains) >= 2:
            sugg.append(f"sfx.default_gain: {round(load_prefs().get('sfx', {}).get('default_gain', -12) + g)}")
    for (x, y), n in words.most_common(10):
        notes.append(f'caption "{x}" -> "{y}"' + (f' (x{n})' if n > 1 else ''))
        sugg.append(f'words: "{x}": "{y}"')
    ta = sum(p['b'] - p['a'] for p in pa)
    tb = sum(p['b'] - p['a'] for p in pb)
    notes.append(f'length {ta:.1f} s -> {tb:.1f} s, pieces {len(pa)} -> {len(pb)}')
    print(f'# {os.path.basename(fa)} -> {os.path.basename(fb)}')
    for n in notes:
        print(' -', n)
    if sugg:
        print('suggested my-style updates (ask the user, then edit preferences.yaml):')
        for s in dict.fromkeys(sugg):
            print('   ', s)
    _log({'date': datetime.date.today().isoformat(), 'tag': 'other', 'by': 'learn',
          'project': os.path.basename(os.path.abspath(project)), 'video': B.get('name'),
          'text': f'edits {os.path.basename(fa)} -> {os.path.basename(fb)}: ' + '; '.join(notes[:12])})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    i = sub.add_parser('init')
    i.add_argument('--force', action='store_true', help='overwrite with the template (loses your edits)')
    sub.add_parser('show')
    sub.add_parser('stats')
    n = sub.add_parser('note')
    n.add_argument('text')
    for k in ('project', 'video', 'at', 'fix'):
        n.add_argument('--' + k)
    n.add_argument('--tag', default='other', help=', '.join(TAGS))
    n.add_argument('--by', default='user')
    st = sub.add_parser('set')
    st.add_argument('key')
    st.add_argument('value')
    ru = sub.add_parser('rule')
    ru.add_argument('text')
    wo = sub.add_parser('word')
    wo.add_argument('asr')
    wo.add_argument('correct')
    sub.add_parser('brief')
    le = sub.add_parser('learn')
    le.add_argument('project')
    le.add_argument('before')
    le.add_argument('after')
    a = ap.parse_args()
    if a.cmd == 'init':
        init(a.force)
    elif a.cmd == 'show':
        show()
    elif a.cmd == 'stats':
        stats()
    elif a.cmd == 'note':
        note(a)
    elif a.cmd == 'set':
        set_pref(a.key, a.value)
    elif a.cmd == 'rule':
        add_rule(a.text)
    elif a.cmd == 'word':
        add_word(a.asr, a.correct)
    elif a.cmd == 'brief':
        brief()
    else:
        learn(a.project, a.before, a.after)


if __name__ == '__main__':
    main()
