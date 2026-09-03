#!/usr/bin/env python3
"""
craiyon.py — Free image generation via Craiyon (formerly DALL·E mini).

No API key, no signup. Polls until the 9 images are ready and saves them.

Craiyon returns 9 images per prompt, ~1024x1024, slow (~30-90s).

Usage:
    python craiyon.py "a cat on the moon"
    python craiyon.py "astronaut riding a horse" --out ./out --prefix horse
"""
import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path


API_URL = "https://api.craiyon.com/v3"


def _post_json(url: str, payload: dict, timeout: int = 60) -> dict:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "craiyon-cli/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _get_json(url: str, timeout: int = 60) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "craiyon-cli/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def generate(
    prompt: str,
    out_dir: str = "output",
    prefix: str = "craiyon",
    timeout: int = 300,
    poll_interval: float = 4.0,
) -> list[str]:
    import base64

    print(f"[craiyon] submitting prompt: {prompt!r}")
    t0 = time.time()
    resp = _post_json(f"{API_URL}/generate", {"prompt": prompt}, timeout=timeout)
    if "images" not in resp:
        raise RuntimeError(f"Unexpected response: {resp}")
    images_b64 = resp["images"]
    print(f"[craiyon] got {len(images_b64)} images in {time.time() - t0:.1f}s, decoding...")

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    saved = []
    for i, b64 in enumerate(images_b64, 1):
        path = out / f"{prefix}_{i}.png"
        path.write_bytes(base64.b64decode(b64))
        saved.append(str(path.resolve()))
        print(f"[craiyon] saved {path.name} ({path.stat().st_size:,} bytes)")

    print(f"[craiyon] done in {time.time() - t0:.1f}s, {len(saved)} images at {out.resolve()}")
    return saved


def main():
    p = argparse.ArgumentParser(description="Free image generation via Craiyon (no key, no signup).")
    p.add_argument("prompt")
    p.add_argument("--out",    default="output", help="Output directory")
    p.add_argument("--prefix", default="craiyon", help="Filename prefix")
    p.add_argument("--timeout", type=int, default=300)
    args = p.parse_args()
    generate(args.prompt, args.out, args.prefix, args.timeout)


if __name__ == "__main__":
    main()
