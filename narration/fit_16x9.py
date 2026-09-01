#!/usr/bin/env python3
"""fit_16x9.py — force every beat image onto a true 16:9 canvas.

Image generators return whatever aspect they feel like (1024x1024 one time,
1400x764 the next). The video frame is 16:9, so every beat image has to be
16:9 too or the framing jumps between cuts.

This never crops and never squashes. It extends the short side with a soft
backdrop built from the image itself — a blurred, zoomed copy of the picture
faded towards white — so a white doodle stays white and a coloured scene
bleeds out instead of getting a hard bar.

    .tools/venv/bin/python narration/fit_16x9.py projects/myvid/images
    .tools/venv/bin/python narration/fit_16x9.py projects/myvid/images --dry-run

Files already within 1% of 16:9 are left alone.
"""

from __future__ import annotations

import argparse
import os
import sys

TARGET = 16 / 9
TOL = 0.01

try:
    from PIL import Image, ImageFilter
except ImportError:
    sys.exit("Pillow is required. Use .tools/venv/bin/python (see narration/rebuild.sh)")


def make_backdrop(im: Image.Image, w: int, h: int) -> Image.Image:
    """Blurred, cover-scaled copy of the image, faded towards white."""
    src = im.convert("RGB")
    sr, tr = src.width / src.height, w / h
    if sr > tr:                      # source is wider: match height
        nh = h
        nw = max(1, int(round(src.width * h / src.height)))
    else:
        nw = w
        nh = max(1, int(round(src.height * w / src.width)))
    bg = src.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    bg = bg.crop((left, top, left + w, top + h))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=max(w, h) // 26))
    # keep it pale: doodle art reads best on a near-white field
    return Image.blend(bg, Image.new("RGB", (w, h), (255, 255, 255)), 0.45)


def fit(path: str, dry_run: bool = False) -> tuple[str, tuple[int, int], tuple[int, int]]:
    im = Image.open(path)
    orig = im.size
    w, h = orig
    if abs((w / h) - TARGET) <= TOL * TARGET:
        return ("ok", orig, orig)

    if w / h > TARGET:               # too wide -> add top and bottom
        nw, nh = w, int(round(w / TARGET))
    else:                            # too tall -> add left and right
        nh, nw = h, int(round(h * TARGET))

    canvas = make_backdrop(im, nw, nh)
    fg = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
    canvas.paste(fg, ((nw - fg.width) // 2, (nh - fg.height) // 2),
                 fg if fg.mode == "RGBA" else None)

    if not dry_run:
        canvas.convert("RGB").save(path)
    return ("resized", orig, (nw, nh))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir", help="directory of beat images")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(args.dir):
        sys.exit(f"no such directory: {args.dir}")

    files = sorted(f for f in os.listdir(args.dir)
                   if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")))
    if not files:
        sys.exit("no images found")

    changed = 0
    for fn in files:
        p = os.path.join(args.dir, fn)
        status, before, after = fit(p, args.dry_run)
        ar = after[0] / after[1]
        flag = "ok     " if status == "ok" else "RESIZED"
        if status != "ok":
            changed += 1
        print(f"  {flag} {fn:<16} {before[0]}x{before[1]} -> "
              f"{after[0]}x{after[1]}  ({ar:.3f})")

    print(f"\n{len(files)} image(s), {changed} converted to 16:9"
          + (" (dry run)" if args.dry_run else ""))


if __name__ == "__main__":
    main()
