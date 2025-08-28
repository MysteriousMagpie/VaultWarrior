#!/usr/bin/env python3
"""Generate application icon assets from the source SVG.

Outputs PNG sizes (32,64,128,256,512) into desktop/src-tauri/icons/ and an ICNS/ICO file if pillow & icnsutil available.

Run: python scripts/gen_icons.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import subprocess

SIZES = [32,64,128,256,512]
ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / 'desktop' / 'src-tauri' / 'icons' / 'logo.svg'
OUT = ROOT / 'desktop' / 'src-tauri' / 'icons'

FAIL_MSG = "Install cairosvg and pillow: pip install cairosvg pillow"

def ensure_tools():
    try:
        import cairosvg  # type: ignore
    except Exception:
        print("cairosvg missing. " + FAIL_MSG, file=sys.stderr)
        return False
    try:
        from PIL import Image  # type: ignore
    except Exception:
        print("pillow missing. " + FAIL_MSG, file=sys.stderr)
        return False
    return True


def render_pngs():
    import cairosvg  # type: ignore
    OUT.mkdir(parents=True, exist_ok=True)
    for sz in SIZES:
        target = OUT / f"icon-{sz}.png"
        cairosvg.svg2png(url=str(SVG), write_to=str(target), output_width=sz, output_height=sz)
        print("wrote", target)


def compose_icns():
    # Use iconutil on macOS if available
    if sys.platform != 'darwin':
        return
    iconset = OUT / 'AppIcon.iconset'
    iconset.mkdir(exist_ok=True)
    from shutil import copyfile
    for sz in SIZES:
        src = OUT / f'icon-{sz}.png'
        if not src.exists():
            continue
        # macOS expects both 1x and 2x for some sizes
        name = f'icon_{sz}x{sz}.png'
        copyfile(src, iconset / name)
    # try iconutil
    try:
        subprocess.check_call(['iconutil', '-c', 'icns', str(iconset), '-o', str(OUT / 'app.icns')])
        print('wrote', OUT / 'app.icns')
    except Exception as e:
        print('iconutil failed', e)


def compose_ico():
    try:
        from PIL import Image  # type: ignore
    except Exception:
        return
    imgs = []
    for sz in SIZES:
        p = OUT / f'icon-{sz}.png'
        if p.exists():
            imgs.append(Image.open(p))
    if not imgs:
        return
    ico = OUT / 'app.ico'
    imgs[0].save(ico, sizes=[(im.width, im.height) for im in imgs])
    print('wrote', ico)


def main():
    if not SVG.exists():
        print('SVG not found', SVG, file=sys.stderr); return 1
    if not ensure_tools():
        return 1
    render_pngs()
    compose_icns()
    compose_ico()
    print('Done.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
