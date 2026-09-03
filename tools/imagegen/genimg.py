#!/usr/bin/env python3
"""
genimg.py — Unified CLI: pick backend, prompt, get image(s).

Backends:
    polli    Pollinations.ai  — unlimited, no signup, FLUX/SDXL/etc.
    craiyon  Craiyon          — unlimited, no signup, 9 images/prompt, slow

Examples:
    python genimg.py polli "a cat on the moon"
    python genimg.py polli "astronaut on horse" --model flux-dev --width 1280 --height 720 --seed 42
    python genimg.py craiyon "stick figure with saw cutting chair, cartoon"
    python genimg.py polli "doodle explainer scene" --out ./frames/shot1.png
    python genimg.py craiyon "neon city" --out ./frames --prefix scene

No installs required (uses only Python stdlib).
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import pollinations  # noqa: E402
import craiyon       # noqa: E402


def main():
    p = argparse.ArgumentParser(description="Unified free image generator (Pollinations + Craiyon).")
    p.add_argument("backend", choices=["polli", "craiyon"], help="Which backend to use")
    p.add_argument("prompt", help="Text prompt")
    p.add_argument("--out",    default="output.png" if True else "output", help="Output file (polli) or dir (craiyon)")
    p.add_argument("--prefix", default="craiyon",    help="Filename prefix (craiyon only)")
    p.add_argument("--width",  type=int, default=1024, help="(polli)")
    p.add_argument("--height", type=int, default=1024, help="(polli)")
    p.add_argument("--model",  default="flux",        help="(polli) flux|flux-dev|sdxl|sd3|sd3.5|playground|dalle|kandinsky|anydark")
    p.add_argument("--seed",   type=int, default=None, help="(polli) seed for reproducibility")
    p.add_argument("--negative", default=None,        help="(polli) negative prompt")
    p.add_argument("--enhance", action="store_true",  help="(polli) let backend enhance prompt")
    p.add_argument("--keep-logo", action="store_true",help="(polli) keep watermark")
    p.add_argument("--timeout", type=int, default=180)
    args = p.parse_args()

    if args.backend == "polli":
        out = args.out if args.out.endswith((".png", ".jpg", ".jpeg", ".webp")) else "output.png"
        pollinations.generate(
            args.prompt, out, args.width, args.height,
            args.model, args.seed, args.negative,
            nologo=not args.keep_logo, enhance=args.enhance, timeout=args.timeout,
        )
    else:  # craiyon
        craiyon.generate(args.prompt, args.out, args.prefix, args.timeout)


if __name__ == "__main__":
    main()
