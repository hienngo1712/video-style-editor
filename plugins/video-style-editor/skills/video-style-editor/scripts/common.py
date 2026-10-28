"""Shared paths and helpers for video-style-editor scripts.

Project layout (one folder per editing job, kept out of git):
    <project>/raw/      original footage (any sub-folders)
    <project>/work/     generated: audio/, transcript.json, audio_events.json, thumbs/, build/, check/
    <project>/plans/    edit plans written by Claude (JSON)
    <project>/output/   final videos
"""
import json
import os
import re
import subprocess
import unicodedata

# SKILL = folder that contains SKILL.md (code, profiles, docs - replaced on every plugin update)
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES = os.path.join(SKILL, 'profiles')
SFX_MANIFEST = os.path.join(SKILL, 'assets', 'sfx', 'manifest.json')
# DATA = downloaded / generated assets that must survive plugin updates.
# Override with the VSE_HOME environment variable.
DATA = os.path.abspath(os.path.expanduser(os.environ.get('VSE_HOME', '~/.video-style-editor')))
MODELS = os.path.join(DATA, 'models')
FONTS = os.path.join(DATA, 'fonts')
SFX = os.path.join(DATA, 'sfx')
OVERLAYS = os.path.join(DATA, 'overlays')
# MYSTYLE = the user's own taste (preferences.yaml, journal.md) - created by `vse.py style init`, edited over time
MYSTYLE = os.path.join(DATA, 'my-style')


def load_prefs():
    """<VSE_HOME>/my-style/preferences.yaml as a dict ({} when missing, unreadable or PyYAML is not installed)"""
    p = os.path.join(MYSTYLE, 'preferences.yaml')
    if not os.path.exists(p):
        return {}
    try:
        import yaml
        with open(p, encoding='utf-8') as f:
            d = yaml.safe_load(f) or {}
        return d if isinstance(d, dict) else {}
    except Exception as e:  # noqa: BLE001
        print(f'  ! my-style/preferences.yaml not used: {e}')
        return {}


def merged_style(plan):
    """style of a render: built-in defaults < my-style preferences < the plan's own style block"""
    return {**(load_prefs().get('style') or {}), **(plan.get('style') or {})}

VIDEO_EXT = ('.mov', '.mp4', '.m4v', '.mkv', '.webm')
AUDIO_EXT = ('.m4a', '.mp3', '.wav', '.aac')


def slug(s):
    s = unicodedata.normalize('NFKD', s).replace('đ', 'd').replace('Đ', 'D')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def clip_key(rel_path):
    """'Chuyển văn phòng/IMG_9662.MOV' -> 'chuyen-van-phong_IMG_9662'"""
    rel_path = unicodedata.normalize('NFC', rel_path.replace('\\', '/'))
    folder, name = os.path.split(rel_path)
    stem = os.path.splitext(name)[0]
    return f"{slug(folder)}_{stem}" if folder else stem


def project_paths(project):
    p = os.path.abspath(project)
    d = {k: os.path.join(p, k) for k in ('raw', 'work', 'plans', 'output')}
    d['root'] = p
    for k in ('work', 'plans', 'output'):
        os.makedirs(d[k], exist_ok=True)
    return d


def list_media(raw_dir, exts=VIDEO_EXT + AUDIO_EXT):
    out = []
    for root, _, files in os.walk(raw_dir):
        for f in sorted(files):
            if f.lower().endswith(exts):
                out.append(os.path.relpath(os.path.join(root, f), raw_dir).replace('\\', '/'))
    return sorted(out)


def ffprobe(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', path],
                       capture_output=True, text=True)
    return json.loads(r.stdout or '{}')


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


# ---- time budget -------------------------------------------------------------------------------
# Some hosts (Claude Cowork) kill a shell command after ~3 min. Set VSE_BUDGET=150 there: long steps
# then save their progress, print CONTINUE and exit with code 3 - run the same command again.
import time  # noqa: E402

_T0 = time.time()
BUDGET = float(os.environ.get('VSE_BUDGET', '0') or 0)
EXIT_CONTINUE = 3


def out_of_time(next_cost=0.0):
    """True when the time budget (VSE_BUDGET seconds, 0 = unlimited) would be exceeded."""
    return BUDGET > 0 and time.time() - _T0 + next_cost > BUDGET


def stop_for_now(what):
    print(f'CONTINUE: time budget reached ({what}). Progress is saved - run the same command again.')
    raise SystemExit(EXIT_CONTINUE)


# ---- audio helpers ---------------------------------------------------------------------------
def load_wav(path):
    """16 kHz mono wav -> float32 numpy array."""
    import wave
    import numpy as np
    with wave.open(path) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def frame_db(x, hop=800):
    """RMS level in dBFS per hop (800 samples = 50 ms at 16 kHz)."""
    import numpy as np
    n = len(x) // hop
    if n == 0:
        return np.array([-99.0])
    f = x[:n * hop].reshape(n, hop)
    return 20 * np.log10(np.sqrt((f ** 2).mean(axis=1)) + 1e-6)


def noise_floor(db):
    import numpy as np
    return float(np.percentile(db, 15))


def load_wav_checked(path, expected_dur=None, tries=4):
    """load_wav, but re-read when the file looks shorter than the clip: on some mounted folders a file
    that was just written can briefly read back truncated. Returns None if it stays short."""
    for k in range(tries):
        x = load_wav(path)
        if not expected_dur or len(x) / 16000 >= expected_dur - 0.3:
            return x
        time.sleep(1.5 * (k + 1))
    print(f'  ! {os.path.basename(path)} reads {len(x) / 16000:.1f}s, clip is {expected_dur}s - skipped, run again')
    return None


def find_file(base, rel):
    """base/rel, tolerating NFC/NFD differences in Vietnamese file names (macOS and Windows disagree)."""
    p = rel if os.path.isabs(rel) else os.path.join(base, rel)
    if os.path.exists(p):
        return p
    for form in ('NFC', 'NFD'):
        q = unicodedata.normalize(form, p)
        if os.path.exists(q):
            return q
    # walk component by component, comparing normalised names
    cur = base if not os.path.isabs(rel) else os.sep
    for part in rel.replace('\\', '/').split('/'):
        if not part:
            continue
        want = unicodedata.normalize('NFC', part)
        try:
            hit = next((n for n in os.listdir(cur) if unicodedata.normalize('NFC', n) == want), None)
        except OSError:
            return p
        if hit is None:
            return p
        cur = os.path.join(cur, hit)
    return cur
