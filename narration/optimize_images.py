#!/usr/bin/env python3
"""Shrink generated doodle PNGs without visible quality loss.

Doodle frames are flat-color art on a pure white background, so they quantise
extremely well: indexing to a small adaptive palette typically cuts file size
by 80-90% with no perceptible change. Without this, a 145-beat project costs
~130 MB of PNG and bloats the repository.

Usage:
    python3 narration/optimize_images.py projects/foodcode-tomato/images
    python3 narration/optimize_images.py <dir> --colors 96 --max-size 1400 --dry-run

Requires Pillow (the repo's .tools venv has it):
    python3 -m venv .tools/venv && .tools/venv/bin/pip install Pillow imageio-ffmpeg
"""

from __future__ import annotations

import argparse
import os
import sys

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required. Install it into the repo's .tools venv:\n"
             "  python3 -m venv .tools/venv && "
             ".tools/venv/bin/pip install Pillow imageio-ffmpeg")

EXTS = (".png", ".jpg", ".jpeg", ".webp")


def human(n: int) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def already_optimized(path: str, colors: int) -> bool:
    """True if this PNG looks like our own output.

    Generated art arrives as RGB/RGBA; optimise_images.py writes a small
    palettised PNG. Re-quantising our own output on every batch would
    re-encode part 1 twelve more times over the life of a project for no
    gain, so those files are skipped unless --force is given.
    """
    try:
        with Image.open(path) as im:
            if im.format != "PNG" or im.mode != "P":
                return False
            pal = im.getpalette()
            if not pal:
                return False
            return len(pal) // 3 <= max(colors, 16) * 2
    except Exception:
        return False


def optimize_one(path: str, colors: int, max_size: int | None,
                 dry: bool) -> tuple[int, int]:
    before = os.path.getsize(path)
    im = Image.open(path)

    if max_size and max(im.size) > max_size:
        scale = max_size / max(im.size)
        im = im.resize((max(1, round(im.width * scale)),
                        max(1, round(im.height * scale))), Image.LANCZOS)

    # Flatten onto white so any alpha edge does not force a 32-bit PNG.
    if im.mode in ("RGBA", "LA", "P") and ("transparency" in im.info
                                           or im.mode in ("RGBA", "LA")):
        rgba = im.convert("RGBA")
        bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, rgba).convert("RGB")
    else:
        im = im.convert("RGB")

    quant = im.quantize(colors=colors, method=Image.MEDIANCUT,
                        dither=Image.NONE)
    if dry:
        quant.info["__dry__"] = True
        # still measure by encoding to memory
        import io
        buf = io.BytesIO()
        quant.save(buf, "PNG", optimize=True)
        return before, buf.tell()

    tmp = f"{path}.opt"
    quant.save(tmp, "PNG", optimize=True)
    os.replace(tmp, path)
    return before, os.path.getsize(path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("directory", help="folder of beat images")
    ap.add_argument("--colors", type=int, default=96,
                    help="palette size (default 96; flat art needs very few)")
    ap.add_argument("--max-size", type=int, default=1400,
                    help="downscale so the longest edge is at most this (0 = off)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="re-optimise even PNGs this tool already wrote")
    args = ap.parse_args()

    d = args.directory
    if not os.path.isdir(d):
        sys.exit(f"not a directory: {d}")

    files = sorted(f for f in os.listdir(d)
                   if f.lower().endswith(EXTS) and not f.endswith(".opt"))
    if not files:
        sys.exit(f"no images in {d}")

    total_before = total_after = 0
    for f in files:
        p = os.path.join(d, f)
        if not args.force and already_optimized(p, args.colors):
            b = a = os.path.getsize(p)
            print(f"  {f:<24} {human(b):>9}  skip (already optimised)")
            total_before += b
            total_after += a
            continue
        b, a = optimize_one(p, args.colors, args.max_size or None, args.dry_run)
        total_before += b
        total_after += a
        pct = (1 - a / b) * 100 if b else 0
        print(f"  {f:<16} {human(b):>9} -> {human(a):>9}  -{pct:.0f}%")

    saved = (1 - total_after / total_before) * 100 if total_before else 0
    verb = "would be" if args.dry_run else "now"
    print(f"\n{len(files)} images: {human(total_before)} -> "
          f"{human(total_after)} ({verb} -{saved:.0f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
