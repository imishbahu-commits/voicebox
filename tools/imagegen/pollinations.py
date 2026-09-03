#!/usr/bin/env python3
"""
pollinations.py — Unlimited free image generation via Pollinations.ai.

No API key, no signup, no rate limit. Just HTTP.

Usage:
    python pollinations.py "a cat on the moon"
    python pollinations.py "a cat on the moon" --out cat.png --width 1024 --height 1024 --model flux
    python pollinations.py --seed 42 --negative "blurry, low quality" "astronaut riding a horse"

Models (all free on Pollinations):
    flux        FLUX.1-schnell  (default, fast, high quality)
    flux-dev    FLUX.1-dev      (slower, more detailed)
    sdxl        Stable Diffusion XL
    sd3         Stable Diffusion 3
    sd3.5       Stable Diffusion 3.5
    playground  Playground v2.5
    dalle       DALL·E 3 (via Pollinations proxy)
    kandinsky   Kandinsky
    anydark     AnyDark
"""
import argparse
import sys
import urllib.parse
import urllib.request
from pathlib import Path
import time


# Each entry: (model id used in URL, supports negative_prompt)
MODELS = {
    "flux":        ("flux",            True),
    "flux-dev":    ("flux-dev",        True),
    "sdxl":        ("sdxl",            True),
    "sd3":         ("sd3",             False),
    "sd3.5":       ("sd3.5",           False),
    "playground":  ("playground-v2.5", True),
    "dalle":       ("dalle",           False),
    "kandinsky":   ("kandinsky",       False),
    "anydark":     ("anydark",         True),
}


def generate(
    prompt: str,
    out_path: str = "output.png",
    width: int = 1024,
    height: int = 1024,
    model: str = "flux",
    seed: int | None = None,
    negative: str | None = None,
    nologo: bool = True,
    enhance: bool = False,
    timeout: int = 180,
) -> str:
    if model not in MODELS:
        raise ValueError(f"Unknown model: {model}. Choose from: {list(MODELS)}")
    model_id, supports_negative = MODELS[model]

    params = {
        "width":  width,
        "height": height,
        "model":  model_id,
        "nologo": "true" if nologo else "false",
        "enhance":"true" if enhance else "false",
    }
    if seed is not None:
        params["seed"] = seed
    if negative and supports_negative:
        params["negative_prompt"] = negative

    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt) + "?" + urllib.parse.quote(urllib.parse.urlencode(params), safe="=&")
    print(f"[pollinations] GET {url[:120]}{'...' if len(url) > 120 else ''}")

    req = urllib.request.Request(url, headers={"User-Agent": "pollinations-cli/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()

    if len(data) < 500:
        raise RuntimeError(f"Got tiny response ({len(data)} bytes) — prompt likely rejected. Body: {data[:200]!r}")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(f"[pollinations] saved {len(data):,} bytes -> {out.resolve()}")
    return str(out.resolve())


def main():
    p = argparse.ArgumentParser(description="Unlimited free images via Pollinations.ai (no key, no signup).")
    p.add_argument("prompt", help="Text prompt")
    p.add_argument("--out", default="output.png", help="Output file path")
    p.add_argument("--width",  type=int, default=1024)
    p.add_argument("--height", type=int, default=1024)
    p.add_argument("--model",  default="flux", choices=list(MODELS))
    p.add_argument("--seed",   type=int, default=None, help="Seed for reproducibility")
    p.add_argument("--negative", default=None, help="Negative prompt (model-dependent)")
    p.add_argument("--enhance", action="store_true", help="Let Pollinations enhance the prompt")
    p.add_argument("--keep-logo", action="store_true", help="Keep Pollinations watermark")
    p.add_argument("--timeout", type=int, default=180)
    args = p.parse_args()

    t0 = time.time()
    out = generate(
        args.prompt, args.out, args.width, args.height,
        args.model, args.seed, args.negative,
        nologo=not args.keep_logo, enhance=args.enhance, timeout=args.timeout,
    )
    print(f"[pollinations] done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
