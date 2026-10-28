#!/usr/bin/env python3
"""Step 5: render a vertical (9:16) video from an edit plan.

usage:
  python scripts/render.py PROJECT plans/NAME.json all       # lint -> pieces -> final -> review copy (resumable)
  python scripts/render.py PROJECT plans/NAME.json pieces [START END]   # encode pieces only
  python scripts/render.py PROJECT plans/NAME.json final     # concat + captions + SFX + loudness
  python scripts/render.py PROJECT plans/NAME.json ass       # rebuild captions only (check timing)
  python scripts/render.py PROJECT plans/NAME.json review    # 540p copy for a listener (output/review/)

Pieces are cached in work/build/pieces/<hash>.mp4, keyed by everything that changes the picture or the
piece audio - edit a plan freely, only changed pieces re-render (captions, big text and SFX are applied
in `final`). With VSE_BUDGET set, `all`/`pieces` stop in time, print CONTINUE and exit 3: run again.
See docs/edit-plan.md for every field.
"""
import hashlib
import json
import math
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import FONTS, MODELS, SFX, clip_key, find_file, load_json, load_prefs, merged_style, out_of_time, project_paths, stop_for_now  # noqa: E402
import faces  # noqa: E402
import make_overlays  # noqa: E402

P = project_paths(sys.argv[1])
plan_path = sys.argv[2] if os.path.isabs(sys.argv[2]) else os.path.join(P['root'], sys.argv[2])
plan = load_json(plan_path)
STYLE = merged_style(plan)          # my-style preferences < plan.style
WORDS = {k.lower(): v for k, v in (load_prefs().get('words') or {}).items()}   # your caption spellings
W, H, FPS = 1080, 1920, 30
YEL = STYLE.get('caption_highlight', '&H0000D4FF&')  # ASS BGR of #FFD400
WORK = os.path.join(P['work'], 'build', plan['name'])
os.makedirs(WORK, exist_ok=True)
TR = load_json(os.path.join(P['work'], 'transcript.json'), {})
SPEEDLINES, PAPER = make_overlays.ensure()


def sfx_level(path, _cache={}):
    """(peak dBFS, time of the loudest 50 ms in s) of an SFX file - stock SFX vary by 30+ dB and many
    start with a lead-in (whooshes peak ~0.7 s in), so levels and timing are normalised on the peak."""
    if path not in _cache:
        r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', '8000', '-f', 's16le', '-'],
                           capture_output=True)
        x = [int.from_bytes(r.stdout[i:i + 2], 'little', signed=True) for i in range(0, len(r.stdout) - 1, 2)]
        best, best_i = 0.0, 0
        for i in range(0, len(x), 400):
            w = x[i:i + 400]
            rms = (sum(v * v for v in w) / max(len(w), 1)) ** 0.5
            if rms > best:
                best, best_i = rms, i
        peak = max((abs(v) for v in x), default=1) / 32768
        _cache[path] = (20 * math.log10(max(peak, 1e-6)), best_i / 8000)
    return _cache[path]


PIECES = os.path.join(P['work'], 'build', 'pieces')
os.makedirs(PIECES, exist_ok=True)
RENDER_VERSION = 11   # bump when render_piece changes its output
PIECE_KEYS = ('clip', 'a', 'b', 'va', 'zoom', 'fx', 'transition', 'vol', 'denoise', 'tint', 'image', 'audio', 'fit',
              'move', 'move_amt', 'move_at',
              'grade')
TINTS = {   # quick colour looks for a piece (reaction punch-ins, flashbacks)
    'pink': 'colorbalance=rs=0.38:gs=-0.10:bs=0.26:rm=0.28:gm=-0.05:bm=0.16,eq=saturation=1.1:brightness=0.05',
    'warm': 'colorbalance=rs=0.10:bs=-0.10,eq=saturation=1.1',
    'cool': 'colorbalance=rs=-0.08:bs=0.12',
    'bw': 'hue=s=0,eq=contrast=1.15',
}
# one look for the whole video (pro editors: "same colour across clips"; CapCut course: one filter layer at
# 70-80 %, never stack two). style.look = name below, "none", or a .cube file (style.look_mix 0-1, default 0.8)
LOOKS = {
    'clean': 'eq=contrast=1.05,vibrance=intensity=0.10',
    'warm': 'eq=contrast=1.05,vibrance=intensity=0.10,colorbalance=rm=0.04:bm=-0.04:rh=0.03:bh=-0.03',
    'cool': 'eq=contrast=1.05,vibrance=intensity=0.08,colorbalance=rm=-0.03:bm=0.04',
    'film': "eq=contrast=1.04:saturation=0.92,curves=all='0/0.05 0.5/0.5 1/0.96',noise=alls=4:allf=t",
    'none': '',
}
# speech clean-up (all 3 pro editors heard background noise). RNNoise (arnndn, model "leavened-quisling":
# voice incl. laughter vs general noise) removes crowd/room noise that FFT denoising cannot - measured on the
# barber footage: speech-to-noise gap +10..20 dB. Gemini listening: 80-100 % muffles outdoor voices, swallows off-mic
# replies and clips soft word endings -> light = 60 % on every piece with speech (true = light); "strong" = 100 %
# only for very noisy takes; `denoise: false` keeps the room sound.
RNN = os.path.join(MODELS, 'rnnoise-lq.rnnn')


def denoise_filter(mode):
    if os.path.exists(RNN):
        return f"highpass=f=80,arnndn=m='{RNN}':mix={0.6 if mode == 'light' else 1.0}"
    return 'highpass=f=80,afftdn=nr=10:nf=-30:tn=1' if mode == 'light' else 'highpass=f=90,afftdn=nf=-28'


def denoise_mode(p):
    d = p.get('denoise')
    if d is None:   # b-roll without captions keeps its natural ambience unless asked
        d = STYLE.get('denoise', 'light') if p.get('style', 'normal') != 'none' else False
    # true = 'light' (older plans used true for the mild FFT denoise; full RNNoise only when asked for by name)
    return 'strong' if d == 'strong' else ('light' if d is True or d == 'light' else None)


_COLOR = os.path.join(P['work'], 'build', 'color.json')
_color = load_json(_COLOR, {})


def clip_color(clip):
    """{hdr, yavg} of a clip, measured once (keyframes only - fast even on 4K HEVC) and cached in work/build"""
    k = os.path.relpath(clip, P['raw'])
    if k not in _color:
        r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                            'stream=color_transfer', '-of', 'csv=p=0', clip], capture_output=True, text=True)
        trc = r.stdout.strip().split(',')[0]
        hdr = trc in ('arib-std-b67', 'smpte2084')
        r = subprocess.run(['ffmpeg', '-v', 'error', '-skip_frame', 'nokey', '-i', clip, '-vf',
                            f"{HDR_VF + ',' if hdr else ''}scale=270:-2,signalstats,"
                            'metadata=print:key=lavfi.signalstats.YAVG:file=-', '-an', '-f', 'null', '-'],
                           capture_output=True, text=True)
        ys = [float(m) for m in re.findall(r'YAVG=([\d.]+)', r.stdout)]
        au = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index',
                             '-of', 'csv=p=0', clip], capture_output=True, text=True).stdout.strip()
        _color[k] = {'hdr': hdr, 'yavg': round(sum(ys) / len(ys), 1) if ys else None, 'audio': bool(au)}
        with open(_COLOR, 'w') as f:
            json.dump(_color, f, indent=1)
    return _color[k]


# iPhone HLG / PQ -> SDR Rec.709 (CapCut course: always deliver SDR Rec.709; HDR looks washed out once uploaded)
HDR_VF = ('zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,'
          'zscale=t=bt709:m=bt709:r=tv,format=yuv420p')


def grade_for(p):
    """per-clip exposure match: gamma that moves the clip's mean luma part of the way to the target
    (style.exposure_target, default 0.45 of the 16-235 range; style.color_match false = off).
    One fixed value per clip - per-frame normalisation flickers."""
    if 'grade' in p:          # manual override: gamma (1.1 = brighter), or null = leave the clip as shot
        return p['grade']
    if not STYLE.get('color_match', True):
        return None
    c = clip_color(find_file(P['raw'], p['clip']))
    if not c.get('yavg'):
        return None
    m = min(max((c['yavg'] - 16) / 219, 0.05), 0.95)
    t = STYLE.get('exposure_target', 0.45)
    t = m + STYLE.get('exposure_strength', 0.7) * (t - m)
    g = min(max(math.log(m) / math.log(t), 0.8), 1.35)
    return round(g, 2) if abs(g - 1) >= 0.03 else None




def qdur(p):
    """piece length rounded to whole frames - every timing (captions, SFX, chunks, audio length) uses this, so picture,
    sound and text cannot drift apart over many pieces (unrounded -t cuts + AAC priming drifted 0.4 s in 50 s)"""
    return max(round((p['b'] - p['a']) * FPS), 1) / FPS


def cont(x, y):
    """y continues x in the same take with no gap (a zoom jump cut mid-sentence)"""
    return x['clip'] == y['clip'] and abs(x['b'] - y['a']) < 0.02 and 'va' not in x and 'va' not in y


def piece_path(i):
    ps = plan['pieces']
    d = {k: ps[i].get(k) for k in PIECE_KEYS}
    d.update(fi=i > 0 and cont(ps[i - 1], ps[i]), fo=i + 1 < len(ps) and cont(ps[i], ps[i + 1]), v=RENDER_VERSION,
             grade=grade_for(ps[i]), look=STYLE.get('look', 'clean'), dn=denoise_mode(ps[i]),
             rnn=os.path.exists(RNN), mv=motion_for(i, ps[i]), aim=aim_for(ps[i]), mix=STYLE.get('look_mix'))
    lk = STYLE.get('look', 'clean')
    if lk.endswith('.cube') and os.path.exists(find_file(P['root'], lk)):
        d['cube'] = os.path.getmtime(find_file(P['root'], lk))
    h = hashlib.md5(json.dumps(d, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]
    return os.path.join(PIECES, h + '.mov')   # h264 + PCM audio: no AAC priming samples between pieces


def aim_for(p):
    """(x, y) of the main face for zooms, or None (centre, slightly above middle)"""
    return faces.main_face(_faces(p)) if STYLE.get('aim_faces', True) else None


def motion_for(i, p):
    """keyframed camera move of a piece: plan `move` = in | out | punch | none (`move_amt`, `move_at`), else
    style.motion "auto": punch-in on the big-text word, otherwise a slow push in / pull out alternating piece by piece
    (6 %, 5 % on b-roll) for pieces of 1.5 s+. style.motion "off" = static frames as before."""
    m = p.get('move')
    if m == 'none' or (m is None and STYLE.get('motion', 'auto') != 'auto'):
        return None
    dur = p['b'] - p['a']
    if m is None:
        if 'shake' in set(p.get('fx', [])) or p.get('transition') == 'zoom' or dur < 1.5:
            return None
        if p.get('big'):
            lines = [x for x in p['big'].split('\\N') if x.split()]
            first = _norm(lines[0].split()[0]) if lines else ''
            hit = next((w for w in words_for(p) if _norm(w[0]) == first), None)
            at = (hit[1] - p['a']) if hit else p.get('big_at', 0.05)
            return {'kind': 'punch', 'amt': 0.12, 'at': round(max(at - 0.1, 0), 2)}
        m = 'in' if i % 2 == 0 else 'out'
    amt = p.get('move_amt', 0.05 if p.get('style') == 'none' else (0.15 if m == 'punch' else 0.06))
    return {'kind': m, 'amt': amt, 'at': p.get('move_at', 0.0)}


def render_piece(i, p):
    out = piece_path(i)
    if os.path.exists(out):
        return
    a, b = p['a'], p['b']
    dur = b - a
    n = max(round(dur * FPS), 1)     # exact frame count of this piece (see qdur)
    va = p.get('va', a)
    fx = set(p.get('fx', []))
    z = p.get('zoom', 1.0)
    if 'shake' in fx:
        z = max(z, 1.08)
    clip = find_file(P['raw'], p['clip'])
    cmd = ['ffmpeg', '-nostdin', '-y', '-v', 'error', '-ss', f'{va:.3f}', '-t', f'{dur + 0.3:.3f}', '-i', clip]
    ain = '0:a'
    dn = denoise_mode(p)
    pre = min(0.5, a) if dn else 0.0  # pre-roll so the denoiser has learnt the noise before the cut
    if abs(va - a) > 0.01 or pre > 0:
        cmd += ['-ss', f'{a - pre:.3f}', '-t', f'{dur + pre + 0.3:.3f}', '-i', clip]
        ain = '1:a'
    n_in = 2 if ain == '1:a' else 1
    if not clip_color(clip).get('audio', True):   # silent clip (screen recording, timelapse): feed silence
        cmd += ['-f', 'lavfi', '-t', f'{dur + 0.3:.3f}', '-i', 'anullsrc=r=48000:cl=stereo']
        ain, pre, n_in = f'{n_in}:a', 0.0, n_in + 1
    vo = p.get('audio')   # voice-over / narration: picture from clip, sound from another file {file, a}
    if vo:
        vf = find_file(P['raw'], vo['file'])
        cmd += ['-ss', f"{vo.get('a', 0.0):.3f}", '-t', f'{dur + 0.3:.3f}', '-i', vf]
        ain, pre, n_in = f'{n_in}:a', 0.0, n_in + 1
    pre_vf = HDR_VF + ',' if clip_color(clip).get('hdr') else ''
    if p.get('fit') == 'blur':   # landscape clip in the 9:16 frame: whole picture over a blurred copy of itself
        g = [f'[0:v]{pre_vf}fps={FPS},split[f1][f2]',
             f'[f1]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=28:2,eq=brightness=-0.06[bg]',
             f'[f2]scale={W}:-2[fg]', '[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[b0]']
    else:
        g = [f'[0:v]{pre_vf}fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[b0]']
    # colour after scaling (cheap at 1080p): exposure match per clip, then the one look of the video
    gr = grade_for(p)
    lk = STYLE.get('look', 'clean')
    col = f'eq=gamma={gr},' if gr else ''
    if lk.endswith('.cube'):
        g.append(f"[b0]{col}split[lo][lg];[lg]lut3d='{find_file(P['root'], lk)}'[ll];"
                 f"[lo][ll]blend=all_mode=normal:all_opacity={STYLE.get('look_mix', 0.8)}[b]")
    else:
        g.append(f"[b0]{col}{LOOKS.get(lk, lk) + ',' if LOOKS.get(lk, lk) else ''}null[b]")
    sx = "18*sin(2*PI*t*11)*lt(t,0.6)" if 'shake' in fx else '0'
    sy = "14*cos(2*PI*t*9)*lt(t,0.6)" if 'shake' in fx else '0'
    mv = motion_for(i, p)
    tz = p.get('transition') == 'zoom'
    fc = aim_for(p) if (mv or tz or z > 1.001) else None
    fx_, fy_ = fc if fc else (0.5, None)
    if (mv or tz) and 'shake' not in fx:
        # keyframed zoom with easing (editors: "zoom in / zoom out, keyframe cho chuyển động mềm mại"): zoompan on a
        # 2x upscale (zoompan crops on whole pixels - at 1x a slow zoom shimmers), aimed at the main face
        ze = f'{z:.3f}'
        if mv:
            if mv['kind'] in ('in', 'out'):
                sm = f'st(0,min(on/{n},1));ld(0)*ld(0)*(3-2*ld(0))'
                f_ = f'({sm})' if mv['kind'] == 'in' else f'(1-({sm}))'
                ze = f"{z:.3f}*(1+{mv['amt']:.3f}*{f_})"
            else:   # punch: ease-out to +amt in 0.3 s at `at`, then hold
                k0, k1 = int(mv['at'] * FPS), max(int(0.3 * FPS), 1)
                ze = f"{z:.3f}*(1+{mv['amt']:.3f}*(1-pow(1-min(max((on-{k0})/{k1},0),1),2)))"
        if tz:   # zoom-in transition: starts 25 % in, eases out over 0.4 s
            ze = f"({ze})*(1+0.25*pow(max(0,1-on/{int(0.4 * FPS)}),2))"
        xe = f'min(max({fx_:.3f}*iw-iw/zoom/2,0),iw-iw/zoom)'
        ye = (f'min(max({fy_:.3f}*ih-0.38*ih/zoom,0),ih-ih/zoom)' if fy_ is not None else '(ih-ih/zoom)*0.40')
        esc = lambda e: e.replace(',', '\\,')
        g.append(f"[b]scale={2 * W}:{2 * H},zoompan=z='{esc(ze)}':x='{esc(xe)}':y='{esc(ye)}'"
                 f":d=1:s={W}x{H}:fps={FPS},setpts=PTS-STARTPTS[z]")
    elif z > 1.001:
        cx = f'{fx_:.3f}*iw-ow/2' if fc else '(iw-ow)/2'
        cy = f'{fy_:.3f}*ih-0.38*oh' if fy_ is not None else '(ih-oh)*0.40'
        g.append(f"[b]crop=w=iw/{z}:h=ih/{z}:x='clip({cx}+{sx},0,iw-ow)':y='clip({cy}+{sy},0,ih-oh)',"
                 f"scale={W}:{H}[z]")
    else:
        g.append('[b]null[z]')
    last = 'z'
    if 'speedlines' in fx:
        cmd += ['-loop', '1', '-t', f'{dur:.3f}', '-i', SPEEDLINES]
        g.append(f"[{last}][{n_in}:v]overlay=0:0:enable='lt(t,0.9)'[sl]")
        last, n_in = 'sl', n_in + 1
    if p.get('transition') == 'paper':
        cmd += ['-loop', '1', '-t', f'{dur:.3f}', '-i', PAPER]
        g.append(f"[{last}][{n_in}:v]overlay=x='W-(W+overlay_w)*t/0.45':y=0:enable='lt(t,0.46)'[pp]")
        last, n_in = 'pp', n_in + 1
    img = p.get('image')
    if img:   # picture-in-picture: app screenshot, product shot, meme image. {file, x, y, w, at, dur}
        f = find_file(P['root'], img['file'])
        if f.lower().endswith(('.mov', '.mp4', '.m4v', '.mkv', '.webm')):   # video PiP (facecam reaction)
            cmd += ['-ss', f"{img.get('ss', 0.0):.3f}", '-t', f'{dur:.3f}', '-i', f]
        else:
            cmd += ['-loop', '1', '-t', f'{dur:.3f}', '-i', f]
        iw = int(W * img.get('w', 0.7)) // 2 * 2
        at, until = img.get('at', 0.0), img.get('at', 0.0) + img.get('dur', dur)
        g.append(f"[{n_in}:v]scale={iw}:-2,format=rgba[im]")
        g.append(f"[{last}][im]overlay=x='{img.get('x', 0.5)}*W-overlay_w/2':y='{img.get('y', 0.35)}*H-overlay_h/2'"
                 f":enable='between(t,{at:.2f},{until:.2f})'[ov]")
        last, n_in = 'ov', n_in + 1
    tail = 'fade=t=in:st=0:d=0.3:color=white,' if p.get('transition') == 'flash' else ''
    if p.get('tint'):
        tail += TINTS.get(p['tint'], p['tint']) + ','
    # clone the last frame if the clip ends early, so the piece always has exactly n frames
    g.append(f'[{last}]{tail}tpad=stop_mode=clone:stop_duration=0.5,trim=end_frame={n},format=yuv420p[vout]')
    af = 'aresample=48000,'
    if dn:  # rumble + broadband hiss/rustle/room-noise reduction (light on every piece, strong on request)
        af += f'{denoise_filter(dn)},aresample=48000,atrim=start={pre:.3f},asetpts=PTS-STARTPTS,'
    if p.get('vol'):      # dB, e.g. +5 for a quiet second speaker, -6 for noisy b-roll
        af += f"volume={p['vol']}dB,"
    # contiguous cut in the same take (zoom jump): near-instant fades, a 50 ms dip is audible mid-sentence
    ps = plan['pieces']
    fi = 0.01 if i > 0 and cont(ps[i - 1], p) else 0.05
    fo = 0.01 if i + 1 < len(ps) and cont(p, ps[i + 1]) else 0.06
    dq = n / FPS
    g.append(f'[{ain}]{af}aformat=sample_rates=48000:channel_layouts=stereo,afade=t=in:d={fi},'
             f'afade=t=out:st={max(dq - fo, 0):.3f}:d={fo},apad,atrim=end_sample={n * 48000 // FPS}[aout]')
    # both streams are trimmed inside the graph (-frames:v would stop the muxer before the last audio is written)
    cmd += ['-filter_complex', ';'.join(g), '-map', '[vout]', '-map', '[aout]',
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-g', '60',
            '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '2', out + '.part.mov']
    subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL)
    os.replace(out + '.part.mov', out)   # never leave a half-written piece in the cache


def words_for(p):
    """captions for a piece; with a voice-over (piece.audio) the words come from that file's transcript"""
    vo = p.get('audio')
    if not vo:
        return _words(p)
    a0 = vo.get('a', 0.0)
    q = dict(p, clip=vo['file'], a=a0, b=a0 + p['b'] - p['a'])
    return [(t, s - a0 + p['a'], e - a0 + p['a']) for t, s, e in _words(q)]


def _words(p):
    """[(text, t_clip_start, t_clip_end)] for a piece; 'fix' replaces ASR words 1:1, '_' hides a word."""
    if p.get('style', 'normal') == 'none':
        return []
    segs = TR.get(clip_key(p['clip']), {}).get('segs', [])
    asr = [w for s in segs for w in s['words'] if p['a'] - 0.05 <= w['s'] < p['b']]
    toks = p['fix'].split() if p.get('fix') else [WORDS.get(w['w'].lower(), w['w']).upper() for w in asr]
    res = []
    if asr and len(toks) == len(asr):
        for k, (t, w) in enumerate(zip(toks, asr)):
            e = asr[k + 1]['s'] if k + 1 < len(asr) else min(w['s'] + 0.6, p['b'])
            res.append((t, max(w['s'], p['a']), e))
    else:  # word count differs: spread evenly over the spoken span
        if p.get('fix') and asr:
            print(f"  ! {p['clip']} {p['a']}-{p['b']}: fix has {len(toks)} words, ASR has {len(asr)} -> even timing")
        s0 = max(asr[0]['s'], p['a']) if asr else p['a'] + 0.1
        e0 = min((asr[-1]['s'] + 0.4) if asr else p['b'] - 0.1, p['b'])
        n = len(toks)
        res = [(t, s0 + (e0 - s0) * k / n, s0 + (e0 - s0) * (k + 1) / n) for k, t in enumerate(toks)]
    key = clip_key(p['clip'])
    lag = STYLE.get('caption_lag', 0.2)
    res = [(t, word_onset(key, s, e), e + lag) for t, s, e in res]
    for k in range(1, len(res)):   # onset snapping can reorder neighbours -> overlapping events stack up in libass
        t, s, e = res[k]
        s = max(s, res[k - 1][1] + 0.06)
        res[k] = (t, s, max(e, s + 0.08))
    return [(t.replace('+', ' '), s, e) for t, s, e in res if t != '_']  # '+' joins words on one ASR token


_db = {}


def word_onset(key, s, e):
    """when a word's caption appears (clip time). ASR word starts run ~50 ms early (median; a quarter are 0.2 s+
    early) -> captions appeared before the word was heard. Snap to the audible onset: first 10 ms frame within
    [s-0.05, s+0.3] that rises 8 dB above the quietest point of the 150 ms before it (else s + 0.05)."""
    if key not in _db:
        f = os.path.join(P['work'], 'audio', key + '.wav')
        _db[key] = None
        if os.path.exists(f):
            import wave
            import numpy as np
            with wave.open(f) as w:
                sr = w.getframerate()
                x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
            hop = sr // 100
            n = len(x) // hop
            _db[key] = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    # + caption_lag: a pro editor asked for text to land ~0.2 s AFTER the word is heard - text that arrives first
    # tells the punchline before it is said ("người ta biết trước mình nói gì, mất hay")
    d, lag = _db[key], STYLE.get('caption_lag', 0.2)
    on = s + 0.05   # ASR starts run ~50 ms early (median)
    if d is not None:
        i0, i1 = int((s - 0.05) * 100), int((s + 0.3) * 100)
        if i0 >= 15 and i1 < len(d):
            for i in range(i0, i1):
                if d[i] > d[i - 15:i].min() + 8 and d[i] > -45:
                    on = max(i / 100, s - 0.05)
                    break
    return on + lag


SPEAKERS = plan.get('speakers', {})   # {"NV1": "#7CFF4F", "Sếp": "#FF3B3B"} - caption colour by speaker


def ass_color(hexrgb):
    h = hexrgb.lstrip('#')
    return f'&H00{h[4:6]}{h[2:4]}{h[0:2]}&'.upper().replace('&H00', '&H00', 1)


def ts(t):
    t = max(t, 0)
    return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'


# text animation kit - one entrance per role for the whole video (editors: 1-2 fixed in/out animations, not many):
# big text + teaser lines pop in (scale 135/112 % -> 100 %), the title fades. Keywords (*WORD) are yellow.
POP = '{\\fscx112\\fscy112\\t(0,120,\\fscx100\\fscy100)}'
HIDE, SHOW = '{\\alpha&HFF&}', '{\\alpha&H00&}'


def reveal(toks, j):
    """words 0..j visible, later words transparent: the line keeps its final layout but a word only shows once it is
    spoken (editors: "the text jumps up before I say the word"). style.caption_reveal false = whole chunk at once."""
    if not STYLE.get('caption_reveal', True):
        return ' '.join(toks).replace(' \\N ', '\\N')
    out = []
    for k, t in enumerate(toks):
        if t == '\\N':
            out.append(t)
        elif k > j:
            out.append(HIDE + t + SHOW)
        else:
            out.append(t)
    return ' '.join(out).replace(' \\N ', '\\N')


FACES = faces.FaceCache(os.path.join(P['work'], 'build', 'faces.json'))


def _faces(p):
    """face boxes (fractions of the 9:16 frame) of a piece; [] without opencv / model"""
    va = p.get('va', p['a'])
    f = find_file(P['raw'], p['clip'])
    fb = FACES.get(f, va, va + p['b'] - p['a'], p.get('fit'), key=os.path.relpath(f, P['raw']))
    return [b for b in fb if b[2] >= 0.06]   # people far in the background do not matter


def piece_faces(p):
    """faces that text must avoid; [] when style.avoid_faces is false"""
    return _faces(p) if STYLE.get('avoid_faces', True) else []


def band(style, lines=1, size=None):
    """vertical extent (fractions of H) of a text style - must match the Style lines in build_ass"""
    cap = STYLE.get('caption_size', 76)
    if style == 'Cap':
        mv = STYLE.get('caption_margin_v', 470)
        return (H - mv - 1.3 * cap * lines) / H, (H - mv) / H
    if style == 'CapTop':
        return 330 / H, (330 + 1.3 * cap * lines) / H
    if style == 'Teaser':
        mv = STYLE.get('teaser_margin_v', 520)
        return (H - mv - 110 * lines) / H, (H - mv) / H
    if style == 'TeaserTop':
        return 330 / H, (330 + 110 * lines) / H
    if style == 'Big':
        mv = STYLE.get('big_margin_v', 360)
        return mv / H, (mv + 1.1 * (size or 170) * lines) / H
    if style == 'BigLow':
        return (H - 640 - 1.1 * (size or 170) * lines) / H, (H - 640) / H
    return 0, 0


def place(p, normal, alt, lines=1, size=None):
    """keep text off faces (pro editor: the hook line sat on the guest's face): the alternative position when a face
    crosses the normal one and not the alternative. An explicit caption_pos in the plan always wins."""
    fb = piece_faces(p)
    if fb and faces.overlaps(fb, *band(normal, lines, size)) and not faces.overlaps(fb, *band(alt, lines, size)):
        return alt
    return normal


def _norm(w):
    return re.sub(r'[^\w]', '', w.lstrip('*')).upper()


def build_ass(path):
    cap_size = STYLE.get('caption_size', 76)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Be Vietnam Pro ExtraBold,{cap_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,7,0,2,60,60,{STYLE.get('caption_margin_v', 470)},1
Style: CapTop,Be Vietnam Pro ExtraBold,{cap_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,7,0,8,60,60,330,1
Style: Teaser,Be Vietnam Pro Black,88,{YEL},{YEL},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,8,0,2,50,50,{STYLE.get('teaser_margin_v', 520)},1
Style: Big,Be Vietnam Pro Black,170,{YEL},{YEL},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,11,0,8,40,40,{STYLE.get('big_margin_v', 360)},1
Style: TeaserTop,Be Vietnam Pro Black,88,{YEL},{YEL},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,8,0,8,50,50,330,1
Style: BigLow,Be Vietnam Pro Black,170,{YEL},{YEL},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,11,0,2,40,40,640,1
Style: Title,Be Vietnam Pro Black,74,{YEL},{YEL},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,7,0,8,50,50,{STYLE.get('title_margin_v', 230)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev, sfx, T = [], [], 0.0
    for p in plan['pieces']:
        off = T - p['a']
        dur = qdur(p)
        n_ev = len(ev)
        ws = words_for(p) if STYLE.get('captions', True) else []   # style.captions false: no subtitles (finish in CapCut)
        if p.get('style') == 'teaser' and ws:
            # chunks: break on pauses > 0.45 s (only once >= 3 words) or at 9 words; no lone word
            chunks, cur = [], []
            for w in ws:
                if cur and (len(cur) >= 9 or (len(cur) >= 3 and w[1] - cur[-1][1] > 0.45)):
                    chunks.append(cur)
                    cur = []
                cur.append(w)
            if cur:
                if len(cur) <= 2 and chunks and len(chunks[-1]) + len(cur) <= 11:   # no 1-2 word tail ("ĐẮC NHẤT")
                    chunks[-1] += cur
                else:
                    chunks.append(cur)
            def tw(x):   # teaser text is all yellow already; '*' keyword marks are just dropped
                return x.lstrip('*')
            tsty = place(p, 'Teaser', 'TeaserTop', lines=2)
            for ci, ch in enumerate(chunks):
                toks = [tw(w[0]) for w in ch]
                br = (len(ch) + 1) // 2 if len(ch) > 4 else None
                if br:
                    toks = toks[:br] + ['\\N'] + toks[br:]
                end = min(ch[-1][2] + 0.15, p['b'])
                if ci + 1 < len(chunks):
                    end = min(end, chunks[ci + 1][0][1])
                for j, w in enumerate(ch):   # one event per spoken word: the line fills in as it is said
                    jj = j + (1 if br and j >= br else 0)
                    st = w[1]
                    en = ch[j + 1][1] if j + 1 < len(ch) else end
                    ev.append((0, st + off, max(en, st + 0.08) + off, tsty, (POP if j == 0 else '') + reveal(toks, jj)))
        elif ws:
            style = ('CapTop' if p['caption_pos'] == 'top' else 'Cap') if p.get('caption_pos') else \
                place(p, 'Cap', 'CapTop', lines=2 if STYLE.get('caption_mode') == 'static' else 1)
            base = ass_color(SPEAKERS.get(p.get('speaker'), '#FFFFFF'))   # caption colour per speaker
            hi = YEL if base == '&H00FFFFFF&' else '&H00FFFFFF&'

            def word(x, on):   # '*WORD' in fix = keyword, always yellow
                kw = x.startswith('*')
                t = x.lstrip('*')
                return (f'{{\\c{YEL if kw else hi}}}' + t + f'{{\\c{base}}}') if (on or kw) else t

            if STYLE.get('caption_mode', 'karaoke') == 'static':
                # sitcom style: a whole line (up to 6 words, 2 rows) in the speaker colour, keywords yellow
                chunks, cur = [], []
                for w in ws:
                    if cur and (len(cur) >= 6 or w[1] - cur[-1][1] > 0.6):
                        chunks.append(cur)
                        cur = []
                    cur.append(w)
                if cur:
                    chunks.append(cur)
                for ci, ch in enumerate(chunks):
                    toks = [word(x[0], False) for x in ch]
                    br = (len(toks) + 1) // 2 if len(toks) > 3 else None
                    if br:
                        toks = toks[:br] + ['\\N'] + toks[br:]
                    end = chunks[ci + 1][0][1] if ci + 1 < len(chunks) else min(ch[-1][2] + 0.2, p['b'])
                    for j, w in enumerate(ch):
                        jj = j + (1 if br and j >= br else 0)
                        en = ch[j + 1][1] if j + 1 < len(ch) else end
                        ev.append((0, w[1] + off, max(en, w[1] + 0.08) + off, style,
                                   f'{{\\c{base}}}' + reveal(toks, jj)))
            else:
                sizes = [3] * (len(ws) // 3) + ([len(ws) % 3] if len(ws) % 3 else [])
                if len(sizes) > 1 and sizes[-1] == 1:   # never a lone last word ("NGƯỜI Ạ" read as cut off): 3+1 -> 2+2
                    sizes[-2:] = [2, 2]
                cs = [sum(sizes[:k]) for k in range(len(sizes))]
                for c, sz in zip(cs, sizes):  # 3-word chunks, active word highlighted
                    ch = ws[c:c + sz]
                    for j, w in enumerate(ch):
                        parts = [word(x[0], k == j) for k, x in enumerate(ch)]
                        st = w[1] + off
                        en = (ch[j + 1][1] if j + 1 < len(ch) else w[2]) + off
                        ev.append((0, st, max(en, st + 0.08), style, f'{{\\c{base}}}' + reveal(parts, j)))
        # captions shifted by caption_lag must not spill into the next piece
        for k in range(n_ev, len(ev)):
            L, st, en, sty, txt = ev[k]
            st = min(st, T + dur - 0.12)
            ev[k] = (L, st, max(min(en, T + dur), st + 0.08), sty, txt)
        if p.get('big'):
            lines = p['big'].split('\\N')
            longest = max(len(x) for x in lines)
            fs = min(170, int(170 * 9 / max(longest, 1)))
            bsty = place(p, 'Big', 'BigLow', lines=len(lines), size=fs)
            pop = f'{{\\fs{fs}\\fscx135\\fscy135\\t(0,160,\\fscx100\\fscy100)}}'
            # big text follows the voice (editor: "TỰ CHỦ / TỰ DO / TỰ LO" jumped in before it was said, each line
            # should come when spoken): each line appears at the caption time of its first word; big_at overrides
            times, k = [], 0
            if 'big_at' not in p:
                spoken = [(_norm(w[0]), w[1]) for w in (ws or words_for(p))]
                for ln in lines:
                    first = _norm(ln.split()[0]) if ln.split() else ''
                    hit = next((i for i in range(k, len(spoken)) if spoken[i][0] == first), None)
                    if hit is None:
                        break
                    times.append(spoken[hit][1] + off)
                    k = hit + 1
            if not times:
                times = [T + p.get('big_at', 0.05)]
            end = min(times[-1] + 1.6, T + dur)
            for i, t0 in enumerate(times):
                shown = lines if i == len(times) - 1 else lines[:i + 1]   # last found line: everything left shows
                txt = '\\N'.join(shown + [HIDE + x + SHOW for x in lines[len(shown):]])
                t1 = times[i + 1] if i + 1 < len(times) else end
                t0 = min(t0, T + dur - 0.15)
                ev.append((1, t0, max(t1, t0 + 0.1), bsty, (pop if i == 0 else f'{{\\fs{fs}}}') + txt))
        for s in p.get('sfx', []):
            sfx.append((T + s.get('at', 0.0), s['name'], s.get('gain', -6)))
        T += dur
    ttl = plan.get('title')   # persistent headline / series name at the top: {"text", "from", "to"}
    if ttl:
        ev.append((2, ttl.get('from', 0.0), min(ttl.get('to', T), T), 'Title', '{\\fad(250,200)}' + ttl['text']))
    # subtitle events (layer 0) must hand over, not overlap: libass stacks overlapping lines one above the other, which
    # showed as two copies of the same caption. Each event ends where the next starts; a < 40 ms leftover is dropped.
    cap = sorted([e for e in ev if e[0] == 0], key=lambda e: e[1])
    fixed = []
    for k, e in enumerate(cap):
        L, st, en, sty, txt = e
        if k + 1 < len(cap) and cap[k + 1][1] < en:
            en = cap[k + 1][1]
        if en - st >= 0.04:
            fixed.append((L, st, en, sty, txt))
    ev = fixed + [e for e in ev if e[0] != 0]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(head)
        for layer, s, e, st, txt in ev:
            f.write(f'Dialogue: {layer},{ts(s)},{ts(e)},{st},,0,0,0,,{txt}\n')
    return T, sfx


def do_pieces(s=0, e=None):
    n = len(plan['pieces'])
    e = n if e is None else min(e, n)
    done = 0
    for i in range(s, e):   # paths are computed one by one: the first run measures faces/colour per clip
        p = plan['pieces'][i]
        if out_of_time(10 + 3 * (p['b'] - p['a'])):
            stop_for_now(f'{e - i} pieces left')
        if os.path.exists(piece_path(i)):
            done += 1
            continue
        render_piece(i, p)
        print('piece', i, 'ok', flush=True)
    print(f'{e - s} pieces ready ({done} were cached)', flush=True)


# optional voice compression before loudness (style.compress true). Off by default: on the barber test it lifted
# the background noise between words by ~4 dB
COMP = 'acompressor=threshold=-21dB:ratio=2.5:attack=8:release=180:makeup=1,' if STYLE.get('compress', False) else ''


def ffq(path):
    """a path inside single quotes of an ffmpeg concat list"""
    return path.replace("'", "'\\''")


CHUNK = 12   # seconds of video per burn-in chunk: each fits easily in one budgeted run, resumable


def do_final():
    """concat pieces -> captions burnt in CHUNK-second chunks (cached, resumable: on a 2-core VM a 80 s video
    takes ~3 min to encode, longer than one shell call) -> audio mix -> mux -> exact loudness"""
    lst = os.path.join(WORK, 'list.txt')
    with open(lst, 'w') as f:
        for i in range(len(plan['pieces'])):
            f.write(f"file '{ffq(piece_path(i))}'\n")
    tl = os.path.join(WORK, 'timeline.mov')
    ass = os.path.join(WORK, 'captions.ass')
    T, sfx = build_ass(ass)
    key = hashlib.md5((open(lst).read() + open(ass, encoding='utf-8').read()).encode()).hexdigest()[:10]
    if not os.path.exists(tl) or load_json(tl + '.key.json', {}).get('key') != key:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', tl],
                       check=True)
        with open(tl + '.key.json', 'w') as f:
            json.dump({'key': key}, f)
    out = os.path.join(P['output'], plan['name'] + '.mp4')
    full = hashlib.md5((key + json.dumps([sfx, plan.get('music'), STYLE.get('lufs'), COMP, RENDER_VERSION],
                                         sort_keys=True)).encode()).hexdigest()[:10]
    if os.path.exists(out) and load_json(out + '.key.json', {}).get('key') == full:
        print('final up to date', out, flush=True)
        return out
    cdir = os.path.join(WORK, 'chunks')
    os.makedirs(cdir, exist_ok=True)
    n = int(math.ceil(T / CHUNK - 1e-6))
    parts = []
    for k in range(n):
        c = os.path.join(cdir, f'{key}_{k:03d}.mp4')
        parts.append(c)
        if os.path.exists(c):
            continue
        if out_of_time(10 + 3.0 * CHUNK):
            stop_for_now(f'captions burnt in {k}/{n} chunks')
        s0 = k * CHUNK
        nf = int(round(min(CHUNK, T - s0) * FPS))
        # -copyts keeps the timeline clock so the ASS events line up; -frames keeps chunk joins frame-exact
        # run inside WORK with a relative subtitle path: ':' ',' or quotes in a project path would break the filter
        subprocess.run(['ffmpeg', '-nostdin', '-y', '-v', 'error', '-ss', f'{s0:.3f}', '-copyts', '-i', tl, '-an',
                        '-vf', f'ass=captions.ass:fontsdir={os.path.relpath(FONTS, WORK)},setpts=PTS-STARTPTS',
                        '-frames:v', str(nf),
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-g', '60', '-pix_fmt', 'yuv420p',
                        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
                        c + '.part.mp4'], check=True, cwd=WORK)
        os.replace(c + '.part.mp4', c)
        print(f'  chunk {k + 1}/{n} ok', flush=True)
    vid = os.path.join(WORK, 'video.mp4')
    with open(os.path.join(cdir, 'list.txt'), 'w') as f:
        f.writelines(f"file '{ffq(c)}'\n" for c in parts)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', os.path.join(cdir, 'list.txt'),
                    '-c', 'copy', vid], check=True)
    if out_of_time(15 + 0.5 * T):
        stop_for_now('video with captions done, audio mix next')
    cmd = ['ffmpeg', '-y', '-v', 'error', '-i', tl]
    # speech is loudness-normalised on its own first, so SFX never push the voice down
    graph = ['[0:a]' + COMP + 'loudnorm=I=-11:TP=-1.5:LRA=9,aresample=48000,aformat=channel_layouts=stereo[sp]']
    mix = ['[sp]']
    music = plan.get('music')   # {file, gain (dB, default -24), duck (true)} - a quiet bed under the dialogue
    if music:
        mf = find_file(P['root'], music['file'])
        cmd += ['-stream_loop', '-1', '-i', mf]
        graph[0] = '[0:a]' + COMP + 'loudnorm=I=-11:TP=-1.5:LRA=9,aresample=48000,aformat=channel_layouts=stereo,asplit[sp][key]'
        mg = music.get('gain', -24)
        graph.append(f'[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{T:.2f},'
                     f'afade=t=out:st={max(T - 1.5, 0):.2f}:d=1.5,volume={mg}dB[mu]')
        if music.get('duck', True):
            graph.append('[mu][key]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=350[mud]')
        else:
            graph.append('[key]anullsink;[mu]anull[mud]')
        mix.append('[mud]')
    n_in = 2 if music else 1
    for at, name, gain in sfx:
        f = os.path.join(SFX, name if name.endswith('.mp3') else f'sfx_{name}.mp3')
        if not os.path.exists(f):
            print('  ! missing sfx', f)
            continue
        peak_db, peak_t = sfx_level(f)
        cmd += ['-i', f]
        idx = n_in
        n_in += 1
        # normalise every SFX to 0 dBFS peak, then apply the plan gain; align the SFX *peak* with `at`
        start = at - peak_t
        trim = f'atrim=start={-start:.3f},asetpts=PTS-STARTPTS,' if start < 0 else ''
        ms = int(max(start, 0) * 1000)
        graph.append(f'[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,{trim}'
                     f'volume={gain - max(peak_db, -15):.1f}dB,adelay={ms}|{ms}[s{idx}]')  # max +15 dB boost
        mix.append(f'[s{idx}]')
    if len(mix) > 1:
        graph.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,aresample=192000,alimiter=limit=0.75:level=disabled,aresample=48000[a]")
    else:
        graph.append('[sp]anull[a]')
    aud = os.path.join(WORK, 'mix.m4a')
    cmd += ['-filter_complex', ';'.join(graph), '-map', '[a]', '-t', f'{T:.3f}',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', aud]
    subprocess.run(cmd, check=True)
    # second pass: hit the target loudness exactly (one-pass loudnorm + limiter lands 1-3 LU low)
    target = STYLE.get('lufs', -12)   # TikTok/Reels normalise to about -14; -12 keeps headroom for the limiter
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', aud, '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    m = re.findall(r'I:\s+(-?[\d.]+) LUFS', r)
    af = ['-c:a', 'copy']
    if m and abs(float(m[-1]) - target) > 0.5:
        af = ['-af', f'volume={target - float(m[-1]):.1f}dB,aresample=192000,alimiter=limit=0.75:level=disabled,'
              'aresample=48000', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000']
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', vid, '-i', aud, '-map', '0:v', '-map', '1:a', '-c:v', 'copy']
                   + af + ['-shortest', '-movflags', '+faststart', out + '.part.mp4'], check=True)
    os.replace(out + '.part.mp4', out)
    with open(out + '.key.json', 'w') as f:
        json.dump({'key': full}, f)
    print('final', out, round(T, 1), 's,', len(mix) - 1, 'sfx', flush=True)
    return out


def do_review():
    """540p, small enough for a listener (Gemini web, a phone) - see docs/gemini-review.md"""
    src = os.path.join(P['output'], plan['name'] + '.mp4')
    rdir = os.path.join(P['output'], 'review')
    os.makedirs(rdir, exist_ok=True)
    out = os.path.join(rdir, plan['name'] + '-review.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-vf', 'scale=540:-2', '-c:v', 'libx264', '-crf', '28',
                    '-preset', 'veryfast', '-c:a', 'aac', '-b:a', '128k', out + '.part.mp4'], check=True)
    os.replace(out + '.part.mp4', out)
    print('review copy', out, f'{os.path.getsize(out) / 1e6:.1f} MB')


mode = sys.argv[3]
if mode == 'pieces':
    do_pieces(int(sys.argv[4]) if len(sys.argv) > 4 else 0, int(sys.argv[5]) if len(sys.argv) > 5 else None)
elif mode == 'ass':
    T, sfx = build_ass(os.path.join(WORK, 'captions.ass'))
    print('timeline', round(T, 2), 's,', len(sfx), 'sfx')
elif mode == 'final':
    do_final()
elif mode == 'review':
    do_review()
elif mode == 'all':
    import planlint
    errs, _ = planlint.lint(sys.argv[1], plan_path, show_timeline=False)
    if errs:
        sys.exit('fix the plan errors above first')
    do_pieces()
    T = sum(p['b'] - p['a'] for p in plan['pieces'])
    do_final()
    if not out_of_time(5 + 0.5 * T):
        do_review()
else:
    sys.exit(__doc__)
