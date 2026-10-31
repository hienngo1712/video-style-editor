#!/usr/bin/env python3
"""Node runtime for the reel layouts: HyperFrames (HTML + GSAP -> MP4), GSAP and a headless Chromium.

    python reels/kit/runtime.py setup     # install into ~/.cache/vse-reels-runtime (~250 MB), then check
    python reels/kit/runtime.py check     # print what is installed

Everything comes from the npm registry (registry.npmjs.org), which Claude Cowork's network allows even where
GitHub releases, Google storage or cdnjs are blocked: HyperFrames' own "browser ensure" download fails there,
so on Linux a Chromium build is taken from the @sparticuz/chromium package instead. On macOS / a machine with
Chrome, HyperFrames finds or downloads its browser itself.
"""
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT.parents[1] / 'scripts'))
from common import DATA  # noqa: E402

# Outside the shared folder on purpose: npm needs symlinks (node_modules/.bin), which a Cowork-mounted Windows folder
# does not support. Override with VSE_REELS_RUNTIME. Reinstalling takes ~30 s (`reel build` does it by itself).
RT = Path(os.path.expanduser(os.environ.get('VSE_REELS_RUNTIME', '~/.cache/vse-reels-runtime')))
HYPERFRAMES = 'hyperframes@0.8.34'
PACKAGES = [HYPERFRAMES, 'gsap@3.12.5'] + (['@sparticuz/chromium@153.0.0'] if platform.system() == 'Linux' else [])


def env():
    e = dict(os.environ)
    e.update(NODE_USE_ENV_PROXY='1', NODE_NO_WARNINGS='1',          # Node's own fetch honours HTTPS_PROXY
             ONNXRUNTIME_NODE_INSTALL_CUDA='skip', npm_config_onnxruntime_node_install_cuda='skip')
    b = browser(quiet=True)
    if b:
        e['HYPERFRAMES_BROWSER_PATH'] = b
    return e


def gsap_path():
    return RT / 'node_modules' / 'gsap' / 'dist' / 'gsap.min.js'


def hyperframes_cmd():
    b = RT / 'node_modules' / '.bin' / 'hyperframes'
    return [str(b)] if b.exists() else ['npx', '--yes', HYPERFRAMES]


def browser(quiet=False):
    """path of the Chromium HyperFrames should use, or None to let HyperFrames find / download one"""
    p = os.environ.get('HYPERFRAMES_BROWSER_PATH')
    if p and Path(p).exists():
        return p
    pkg = RT / 'node_modules' / '@sparticuz' / 'chromium'
    if platform.system() != 'Linux' or not pkg.exists() or not shutil.which('node'):
        return None
    js = "require('@sparticuz/chromium').default.executablePath().then(p=>console.log(p)).catch(e=>{console.error(e.message);process.exit(1)})"
    r = subprocess.run(['node', '-e', js], capture_output=True, text=True, cwd=str(RT))
    path = r.stdout.strip().splitlines()[-1] if r.returncode == 0 and r.stdout.strip() else ''
    if not path and not quiet:
        print('could not unpack Chromium:', r.stderr[-500:])
    return path or None


def ready():
    return (RT / 'node_modules' / '.bin' / 'hyperframes').exists() and gsap_path().exists()


def setup():
    if not shutil.which('npm'):
        sys.exit('Node.js / npm is missing: install Node.js 22+ (Claude Cowork already has it).')
    RT.mkdir(parents=True, exist_ok=True)
    if not (RT / 'package.json').exists():
        (RT / 'package.json').write_text('{"name": "vse-reels-runtime", "private": true}\n')
    if not ready():
        print('installing', ', '.join(PACKAGES), 'into', RT, flush=True)
        r = subprocess.run(['npm', 'install', '--no-audit', '--no-fund', '--prefix', str(RT), *PACKAGES], env=env())
        if r.returncode:
            sys.exit('npm install failed (see above). Is registry.npmjs.org reachable?')
    check()


def check():
    ok = ready()
    print(f"  [{'ok' if ok else '!!'}] HyperFrames + GSAP in {RT}")
    b = browser()
    if platform.system() == 'Linux':
        print(f"  [{'ok' if b else '!!'}] Chromium {b or '(missing: run reels/kit/runtime.py setup)'}")
        ok &= bool(b)
    else:
        print('  [ok] browser: HyperFrames finds or downloads Chrome itself')
    from_models = Path(DATA) / 'models' / 'rvm_mobilenetv3_fp32.onnx'
    print(f"  [{'ok' if from_models.exists() else '..'}] cutout model {'ready' if from_models.exists() else '(downloads on first cutout)'}")
    return ok


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if cmd == 'setup':
        setup()
    else:
        sys.exit(0 if check() else 1)
