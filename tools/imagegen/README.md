# Free Unlimited Image Generation — Pollinations.ai + Craiyon

Pure-Python, **zero install** (uses only the standard library). No API key, no signup, no rate limits, no payment. Works on any machine with Python 3.8+ (including a Raspberry Pi, a Chromebook with Linux, a phone with Termux, a free-tier cloud VM, etc.).

## Files

| File | Purpose |
|---|---|
| `pollinations.py` | Pollinations.ai client — 1 image per call, dozens of free models (FLUX, SDXL, SD3, DALL·E 3, …) |
| `craiyon.py`      | Craiyon client — 9 images per call, slower, lower quality, but truly unlimited |
| `genimg.py`       | Unified CLI: pick backend, prompt, get image(s) |
| `batch_doodle.py` | Generates a full 9-frame doodle-explainer storyboard from a preset script |

## Quick start

```bash
# Single image, FLUX, 1024x1024
python genimg.py polli "a cat on the moon"

# Doodle-explainer style, 1280x720
python genimg.py polli "stick figure cutting chair, cartoon comedy" --width 1280 --height 720

# 9 images at once via Craiyon
python genimg.py craiyon "astronaut riding a horse" --out ./out

# Full 9-frame storyboard (writes ./frames/frame_01.png ... frame_09.png)
python batch_doodle.py
```

## Pollinations options

```bash
python pollinations.py "prompt" \
    --out shot.png \
    --width 1280 --height 720 \
    --model flux-dev \
    --seed 42 \
    --negative "blurry, low quality, extra limbs"
```

Models: `flux` (default, fast), `flux-dev` (slower, better), `sdxl`, `sd3`, `sd3.5`, `playground`, `dalle`, `kandinsky`, `anydark`.

## Craiyon options

```bash
python craiyon.py "prompt" --out ./out --prefix myshot
```

Returns 9 images. Takes 30–90 seconds.

## Programmatic use

```python
import sys; sys.path.insert(0, "/path/to/this/folder")
import pollinations, craiyon

# One image
pollinations.generate("a cyberpunk city at night", "city.png", 1280, 720, "flux", seed=7)

# Nine at once
paths = craiyon.generate("a cyberpunk city at night", "./out", "city")
```

## Notes

- **No PC?** Run these on a free cloud VM (Google Colab, Kaggle, Lightning.ai, Vast.ai free tier, or any always-free-tier server). The image bytes are saved to disk wherever you run them.
- **No shell access in the current sandbox**, so I couldn't live-test these here. The code is stdlib-only and syntactically clean. If you hit any issue, paste the error and I'll fix it.
- **Quality:** Pollinations + FLUX gives near-SOTA free results. Craiyon is noticeably lower fidelity (it's a smaller model) but genuinely unlimited with no key.
- **For your doodle-explainer use case:** `batch_doodle.py` already has a 9-scene script in Henry-Stickmin-flavor style. Run it, then drop the frames into CapCut (phone) or any editor and add TTS (Edge browser "Read Aloud", or the TTSMaker app) for a complete explainer video — all free, all on phone.
