#!/usr/bin/env python3
"""Index the reference library so people and Claude can find samples fast.

usage: python scripts/ref_index.py REFROOT
REFROOT/<style>/videos/<style>__<format>__<content>__<views>.<ext>   (no person names in file names)
  style   = a profile name (office-sitcom, story-vlog, ...)
  format  = the video's format inside the style (skit, brand-skit, challenge, kitchen-ops, ...)
  content = 2-6 word slug of what happens (xin-ve-som, kfc-my-vs-viet-nam)
  views   = 56.9M / 812K / na
Writes REFROOT/INDEX.json + INDEX.md (table per style: format, content, views, source code, length, cuts/min,
first spoken line) and REFROOT/<style>/analysis/_hooks.jpg (first 3 s of every sample, stacked).
Human fields (content description, source code k1/k2, video id) are kept from the previous INDEX.json;
the private source table lives in REFROOT/_sources/ and is never published.
Find samples with globs, e.g.  */videos/*__brand-skit__*   office-sitcom/videos/*__skit__*   */videos/*M.*
"""
import glob
import json
import os
import sys

ROOT = os.path.abspath(sys.argv[1])
IDX = os.path.join(ROOT, 'INDEX.json')
old = {r['file']: r for r in json.load(open(IDX, encoding='utf-8'))} if os.path.exists(IDX) else {}
rows = []
for v in sorted(glob.glob(os.path.join(ROOT, '*', 'videos', '*'))):
    rel = os.path.relpath(v, ROOT).replace('\\', '/')
    style = rel.split('/')[0]
    stem = os.path.splitext(os.path.basename(v))[0]
    parts = stem.split('__')
    if len(parts) != 4 or parts[0] != style:
        print('  ! name does not follow <style>__<format>__<content>__<views>:', rel)
        parts = [style, '?', stem, 'na']
    r = dict(old.get(rel, {}))
    r.update(file=rel, style=style, format=parts[1], views=parts[3])
    r.setdefault('content', parts[2].replace('-', ' '))
    r.setdefault('source', f'{style}/k?')
    r.setdefault('video_id', '')
    summ = json.load(open(os.path.join(ROOT, style, 'analysis', 'summary.json'), encoding='utf-8')) \
        if os.path.exists(os.path.join(ROOT, style, 'analysis', 'summary.json')) else {}
    s = summ.get(stem, {})
    r.update({k: s.get(k) for k in ('dur', 'avg_shot_s', 'cuts_per_min', 'cuts_first_5s', 'lufs')})
    trp = os.path.join(ROOT, style, 'work', 'transcript.json')
    tr = json.load(open(trp, encoding='utf-8')).get(stem) if os.path.exists(trp) else None
    r['first_line'] = tr['segs'][0]['t'][:90] if tr and tr['segs'] else r.get('first_line', '')
    rows.append(r)
json.dump(rows, open(IDX, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

L = ['# Thư viện video mẫu\n',
     'Tên file: `<style>__<format>__<nội-dung>__<view>.<đuôi>` - không chứa tên người. Tìm nhanh:',
     '`*/videos/*__brand-skit__*` (video lồng nhãn hàng), `office-sitcom/videos/*__skit__*`, `*/videos/*M.*` (triệu view).\n',
     'Mỗi style: `videos/`, `analysis/<tên>/` (hook.jpg = 3 giây đầu, sheet_NN.jpg, cuts.txt), `analysis/_hooks.jpg`',
     '(3 giây đầu của mọi mẫu), `analysis/summary.json` (số đo), `work/transcript.json` (lời thoại).',
     'Cột Nguồn = mã kênh (k1, k2…) để truy vết; bảng tra mã nằm ở `_sources/` (riêng tư, không chia sẻ).',
     'Tạo lại file này: `vse.py library <thư mục này>`.\n']
styles = sorted({r['style'] for r in rows})
for st in styles:
    rs = sorted([r for r in rows if r['style'] == st], key=lambda r: (r['source'], r['format'], r['file']))
    L += [f'## {st} ({len(rs)} mẫu)\n', '| File | Format | Nội dung | View | Nguồn | Dài | Cắt/phút | Câu mở đầu |',
          '|---|---|---|---|---|---|---|---|']
    for r in rs:
        L.append(f"| `{os.path.basename(r['file'])}` | {r['format']} | {r['content']} | {r['views']} | "
                 f"{r['source'].split('/')[-1]} | {round(r['dur']) if r.get('dur') else '?'} s | "
                 f"{r.get('cuts_per_min') if r.get('cuts_per_min') is not None else '?'} | {r['first_line'][:60]} |")
    L.append('')
open(os.path.join(ROOT, 'INDEX.md'), 'w', encoding='utf-8').write('\n'.join(L))

try:
    from PIL import Image, ImageDraw
    for st in styles:
        hooks = sorted(glob.glob(os.path.join(ROOT, st, 'analysis', '*', 'hook.jpg')))
        if not hooks:
            continue
        ims = [Image.open(h) for h in hooks]
        w = max(i.width for i in ims) // 2
        out = Image.new('RGB', (w + 10, sum(i.height // 2 + 18 for i in ims)), 'white')
        d, y = ImageDraw.Draw(out), 0
        for h, i in zip(hooks, ims):
            d.text((4, y + 2), os.path.basename(os.path.dirname(h)), fill='black')
            y += 16
            out.paste(i.resize((i.width // 2, i.height // 2)), (0, y))
            y += i.height // 2 + 2
        out.save(os.path.join(ROOT, st, 'analysis', '_hooks.jpg'), quality=85)
except ImportError:
    pass
print(f'{len(rows)} samples in {len(styles)} styles -> {os.path.join(ROOT, "INDEX.md")}')
