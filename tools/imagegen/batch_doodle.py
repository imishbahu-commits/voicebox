#!/usr/bin/env python3
"""
batch_doodle.py — Generate N doodle-explainer style frames in one go.
Uses Pollinations.ai (FLUX). Adjust prompts to taste.

Usage:
    python batch_doodle.py                  # uses default 9-frame story
    python batch_doodle.py --frames 12      # custom count
    python batch_doodle.py --out ./my_shot
    python batch_doodle.py --model flux-dev # better quality
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import pollinations  # noqa: E402

STYLE = (
    "2D cartoon animation frame, flat colors, thick black outlines, "
    "simple white round head stick figure character, brown spiky hair, "
    "expressive eyes, Newgrounds flash animation style, "
    "16:9 widescreen, clean vector look, "
)

DEFAULT_FRAMES = [
    "a stick figure with mischievous grin holding a handsaw next to a wooden chair, dim room, single hanging light bulb, dramatic lighting",
    "the same stick figure looking proud at the same wooden chair",
    "the same stick figure in a bright room looking at the same chair, but now the chair is broken with stuffing coming out, comedic",
    "the same stick figure scratching his head, broken chair in background, comedic cartoon",
    "the same stick figure running away from a chair that has come to life, exaggerated motion lines, cartoon comedy",
    "the same stick figure hiding behind a door, only eyes visible, peeking at the chair",
    "the same stick figure cautiously approaching the broken chair with a toolbox, determined look",
    "the same stick figure happily sitting on a newly repaired chair, holding a thumbs up, sparkles around",
    "the same stick figure and a now-anthropomorphic chair sharing tea, wholesome cartoon ending, title card style",
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--frames", type=int, default=len(DEFAULT_FRAMES))
    p.add_argument("--out",    default="./frames", help="Output directory")
    p.add_argument("--width",  type=int, default=1280)
    p.add_argument("--height", type=int, default=720)
    p.add_argument("--model",  default="flux", choices=list(pollinations.MODELS))
    p.add_argument("--negative", default="photo, realistic, 3d render, blurry, low quality, deformed, extra limbs")
    p.add_argument("--seed",   type=int, default=1234)
    p.add_argument("--custom-prompt", default=None, help="Override: use this single prompt for all frames")
    args = p.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.custom_prompt:
        prompts = [args.custom_prompt] * args.frames
    else:
        prompts = DEFAULT_FRAMES[: args.frames]
        if args.frames > len(DEFAULT_FRAMES):
            extras = [f"the same stick figure in scene {i}, doodle explainer cartoon, comedic"
                      for i in range(len(DEFAULT_FRAMES) + 1, args.frames + 1)]
            prompts += extras

    for i, scene in enumerate(prompts, 1):
        full_prompt = STYLE + scene
        out_path = out / f"frame_{i:02d}.png"
        print(f"\n=== frame {i}/{len(prompts)} ===")
        try:
            pollinations.generate(
                full_prompt, str(out_path),
                args.width, args.height,
                args.model, args.seed + i, args.negative,
            )
        except Exception as e:
            print(f"  !! frame {i} failed: {e}", file=sys.stderr)

    print(f"\nAll frames attempted in {out.resolve()}")


if __name__ == "__main__":
    main()
