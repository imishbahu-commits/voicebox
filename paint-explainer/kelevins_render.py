#!/usr/bin/env python3
"""Render a Kelevins-style explainer cut from recorded narration + key art.

Style facts used here come from the full transcript of "Historical Myths That
Turned Out To Be Real" (@Kelevins): one beat of narration = one claim with
receipts, no intro, no sign-off beyond a one-line subscribe. So the edit
pattern this renderer implements is:

  * audio drives everything — visuals are timed to measured clip durations
  * one artwork per beat, pushed in slowly (Ken Burns) — his footage is
    simple shots, so the motion has to do the work
  * burned-in captions, one chunk at a time, upper case, hard cut on beat
  * bottom gradient for caption legibility, thin progress bar at the bottom
  * chapter chip per entry (his uploads publish chapters; we bake ours in)

Usage
-----
  python3 kelevins_render.py --beats beats.json --audio-dir audio --art-dir art --out video.mp4

beats.json:
  [{"narration": "text of clip 1", "art": "art_1.png", "title": "01 · The myth"}, ...]
Narration files must be named n01.wav, n02.wav, ... matching beat order.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import shutil
import subprocess
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1280, 720, 30
PRE_SIZE = (int(W * 1.35), int(H * 1.35))
MAX_ZOOM = 1.22
GOLD = (232, 190, 96)
INK = (9, 13, 20)
WHITE = (245, 246, 248)
MUSIC = 0.13
DIP = 0.55  # music level while narration is in


# ────────────────────────────── audio ──────────────────────────────
def read_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as w:
        rate, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        raw = np.frombuffer(w.readframes(n), dtype="<i2")
    data = raw.reshape(-1, ch).mean(axis=1) if ch > 1 else raw
    return data.astype(np.float32) / 32768.0, rate


def write_wav(path: Path, data: np.ndarray, rate: int) -> None:
    peak = float(np.max(np.abs(data))) or 1.0
    pcm = (np.clip(data / max(peak, 1e-6), -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())


def silence(seconds: float, rate: int) -> np.ndarray:
    return np.zeros(max(0, int(seconds * rate)), dtype=np.float32)


def tone_bed(seconds: float, rate: int, root: float = 55.0) -> np.ndarray:
    """Low drone + slow tremolo + filtered noise: the 'quiet sea' under him."""
    n = int(seconds * rate)
    t = np.arange(n, dtype=np.float32) / rate
    pad = np.zeros(n, dtype=np.float32)
    for mult, amp in ((1.0, 1.0), (1.5, 0.5), (2.0, 0.28)):
        f = root * mult
        env = 0.5 - 0.5 * np.cos(2 * np.pi * t / (2 * seconds))
        pad += amp * env * np.sin(2 * np.pi * f * t)
    pad *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * t)
    rng = np.random.default_rng(4)
    noise = rng.standard_normal(n).astype(np.float32)
    k = max(3, int(rate * 0.05))
    kernel = np.hanning(k)
    kernel /= kernel.sum()
    noise = np.convolve(noise, kernel, mode="same")
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * 0.045 * t - 1.0)
    return (0.75 * pad / (np.max(np.abs(pad)) or 1) + 0.35 * noise / (np.max(np.abs(noise)) or 1)) * swell


def perc_tick(seconds_idx: list[float], total: float, rate: int) -> np.ndarray:
    """Wood tick at each beat start + a swell into every beat (his cuts land)."""
    n = int(total * rate)
    out = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(9)
    for b in seconds_idx:
        i = int(b * rate)
        if i >= n:
            continue
        m = min(int(0.12 * rate), n - i)
        env = np.exp(-np.arange(m) / (0.03 * rate), dtype=np.float32)
        out[i:i + m] += env * np.sin(2 * np.pi * 880 * np.arange(m) / rate) * 0.25
        s = min(int(0.9 * rate), n - i)
        senv = np.linspace(0, 1, s, dtype=np.float32) ** 2 * np.exp(-np.arange(s) / (0.5 * rate))
        out[i:i + s] += senv * rng.standard_normal(s).astype(np.float32) * 0.06
    return out


def duck(bed: np.ndarray, voice: np.ndarray, rate: int) -> np.ndarray:
    """Sidechain-lite: smooth voice envelope pulls the music down."""
    n = min(len(bed), len(voice))
    env = np.abs(voice[:n])
    k = int(rate * 0.25)
    kernel = np.ones(k) / k
    env = np.convolve(env, kernel, mode="same")
    env = np.clip(env / (np.max(env) or 1), 0, 1)
    gain = np.ones(len(bed), dtype=np.float32)
    gain[:n] = DIP + (1 - DIP) * (1 - env)
    return bed * gain


# ───────────────────────────── captions ─────────────────────────────
def chunks(text: str, min_words: int, max_words: int) -> list[str]:
    words, out, cur = text.split(), [], ""
    for w in words:
        cur = f"{cur} {w}".strip()
        if len(cur.split()) >= (min_words if not out else min_words) and len(cur.split()) >= max_words:
            out.append(cur)
            cur = ""
        elif len(cur.split()) >= max_words:
            out.append(cur)
            cur = ""
    if cur:
        if out and len(cur.split()) < min_words:
            out[-1] = f"{out[-1]} {cur}"
        else:
            out.append(cur)
    return out


def split_time(text: str, dur: float, min_w: int, max_w: int, lead: float, tail: float):
    cs = chunks(text, min_w, max_w)
    weights = np.array([max(1, len(c)) for c in cs], dtype=np.float64)
    span = max(0.2, dur - lead - tail)
    offs = lead + span * np.concatenate(([0.0], np.cumsum(weights[:-1] / weights.sum())))
    edges = list(offs + span * (np.cumsum(weights) / weights.sum()) * 0)
    # end time of each chunk = start of next (or end of speech)
    starts = list(offs)
    ends = starts[1:] + [lead + span + tail]
    return cs, starts, ends


# ────────────────────────────── frames ──────────────────────────────
def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for d in ("/usr/local/lib/python3.11/dist-packages/PIL/fonts", "/usr/share/fonts/truetype/dejavu"):
        p = Path(d) / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def stage(img: Image.Image) -> Image.Image:
    """Pre-size once so every frame is a cheap crop + resize."""
    iw, ih = img.size
    scale = max(PRE_SIZE[0] / iw, PRE_SIZE[1] / ih)
    return img.resize((int(iw * scale + 0.5), int(ih * scale + 0.5)), Image.LANCZOS)


def cover(big: Image.Image, zoom: float, dx: float, dy: float) -> Image.Image:
    """Crop the oversized stage with push-in (zoom) + drift (dx, dy in -1..1)."""
    bw, bh = big.size
    sw, sh = int(bw / zoom), int(bh / zoom)
    ox = int((bw - sw) * (0.5 + dx * 0.5) * 0.5)
    oy = int((bh - sh) * (0.5 + dy * 0.5) * 0.5)
    ox = max(0, min(bw - sw, ox))
    oy = max(0, min(bh - sh, oy))
    return big.crop((ox, oy, ox + sw, oy + sh)).resize((W, H), Image.BILINEAR)


def ease(t: float) -> float:
    return t * t * (3 - 2 * t)


def render(beats: list[dict], audio_dir: Path, art_dir: Path, out: Path,
           min_words: int = 5, max_words: int = 7) -> None:
    clips = []
    for i, b in enumerate(beats, start=1):
        f = audio_dir / b.get("file", f"n{i:02d}.wav")
        data, rate = read_wav(f)
        lead, tail = 0.12, 0.12
        cs, starts, ends = split_time(b["narration"], len(data) / rate, min_words, max_words, lead, tail)
        art = art_dir / b["art"] if not Path(b["art"]).is_absolute() else Path(b["art"])
        clips.append({
            "index": i, "audio": data, "rate": rate, "dur": len(data) / rate,
            "chunks": cs, "starts": starts, "ends": ends,
            "art": str(art), "title": b.get("title", ""),
        })

    pre_gap, post_gap = 0.35, 0.45
    t0 = 0.0
    for c in clips:
        c["start"] = t0 + pre_gap
        t0 = c["start"] + c["dur"] + post_gap
    total = t0 + 0.6

    # ── audio timeline ──
    rate = clips[0]["rate"]
    voice = silence(total, rate)
    for c in clips:
        i = int(c["start"] * rate)
        n = min(len(voice) - i, len(c["audio"]))
        voice[i:i + n] += c["audio"][:n]
    bed = MUSIC * tone_bed(total, rate) + 0.5 * perc_tick([c["start"] for c in clips], total, rate)
    master = duck(bed, voice, rate) + 1.0 * voice
    master = np.tanh(1.1 * master)

    # ── frame loop ──
    cfont, sfont, tfont = font("DejaVuSans-Bold.ttf", 30), font("DejaVuSans.ttf", 19), font("DejaVuSans-Bold.ttf", 21)
    prevfont = font("DejaVuSans.ttf", 20)
    stages: dict[int, Image.Image] = {}
    for c in clips:
        stages[c["index"]] = stage(Image.open(c["art"]).convert("RGB"))

    overlay = Image.new("L", (W, H), 0)
    od = ImageDraw.Draw(overlay)
    for y in range(H):
        od.line([(0, y), (W, y)], fill=int(215 * max(0.0, (y - H * 0.50)) / (H * 0.50)))
    overlay = overlay.filter(ImageFilter.GaussianBlur(20))
    shade = Image.new("RGBA", (W, H), (*INK, 255))

    frames_total = int(total * FPS)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    tmp_wav = out.with_suffix(".audio.wav")
    write_wav(tmp_wav, master[: int(total * rate)], rate)
    cmd = [
        ffmpeg, "-loglevel", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(tmp_wav), "-shortest",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None

    written = 0
    for b_i, c in enumerate(clips):
        big = stages[c["index"]]
        span = c["dur"] + pre_gap + post_gap
        for k in range(int(span * FPS)):
            tau = c["start"] - pre_gap + k / FPS
            rel = min(1.0, max(0.0, (tau - c["start"]) / max(c["dur"], 1e-6)))
            prog = ease(rel)
            zoom = 1.045 + (MAX_ZOOM - 1.045) * prog
            side = 1 if b_i % 2 == 0 else -1
            canvas = cover(big, zoom, side * (-0.34 + 0.68 * prog), -0.20 + 0.40 * prog).convert("RGBA")
            canvas.paste(shade, (0, 0), overlay)
            draw = ImageDraw.Draw(canvas)

            label = f"{c['index']:02d} / {len(clips):02d}"
            lw = draw.textlength(label, font=sfont)
            draw.rounded_rectangle((36, 32, 36 + 36 + int(lw), 70), 10, fill=(*INK, 150), outline=(*GOLD, 210), width=1)
            draw.text((54, 40), label, font=sfont, fill=GOLD)
            if c["title"]:
                draw.text((38, 82), c["title"], font=tfont, fill=(*WHITE, 205))

            if c["start"] <= tau <= c["start"] + c["dur"] + post_gap and c["chunks"]:
                ci = 0
                while ci < len(c["ends"]) - 1 and tau >= c["start"] + c["ends"][ci]:
                    ci += 1
                chunk_start = c["start"] + c["starts"][ci]
                appear = min(1.0, max(0.0, (tau - chunk_start) / 0.16))
                text = c["chunks"][ci].upper()
                tw = draw.textlength(text, font=cfont)
                x = int((W - tw) / 2)
                y = int(H - 116 + (1 - appear) * 12)
                for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
                    draw.text((x + ox, y + oy), text, font=cfont, fill=(*INK, int(235 * appear)))
                draw.text((x, y), text, font=cfont, fill=(*WHITE, int(255 * appear)))
                if ci > 0:
                    prev = c["chunks"][ci - 1].upper()
                    ptw = draw.textlength(prev, font=prevfont)
                    draw.text((int((W - ptw) / 2), y - 34), prev, font=prevfont, fill=(*WHITE, 70))

            p = min(1.0, max(0.0, tau / total))
            draw.rectangle((0, H - 5, int(W * p), H), fill=(*GOLD, 235))
            proc.stdin.write(canvas.convert("RGB").tobytes())
            written += 1
            if written % 600 == 0:
                print(f"  {written}/{frames_total} frames")

    for _ in range(int(0.6 * FPS)):
        proc.stdin.write(cover(big, MAX_ZOOM - 0.02, 0.02, 0.02).convert("RGB").tobytes())
        written += 1

    proc.stdin.close()
    stderr = proc.stderr.read().decode(errors="replace") if proc.stderr else ""
    if proc.wait():
        raise SystemExit("ffmpeg failed:\n" + stderr[-2000:])
    tmp_wav.unlink(missing_ok=True)

    json.dump({
        "video": str(out), "total_seconds": round(total, 2), "frames": written,
        "chapters": [{"start_s": round(c["start"], 2), "label": c["title"] or f"Entry {c['index']}"} for c in clips],
    }, open(out.with_suffix(".edl.json"), "w"), indent=2)
    print(f"wrote {out}  ({out.stat().st_size / 1e6:.1f} MB, {written} frames, {total:.1f}s)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beats", required=True, type=Path)
    ap.add_argument("--audio-dir", required=True, type=Path)
    ap.add_argument("--art-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--min-words", type=int, default=5)
    ap.add_argument("--max-words", type=int, default=7)
    a = ap.parse_args()
    beats = json.loads(a.beats.read_text())
    if a.out.parent.exists() is False:
        a.out.parent.mkdir(parents=True, exist_ok=True)
    render(beats, a.audio_dir, a.art_dir, a.out, a.min_words, a.max_words)


if __name__ == "__main__":
    raise SystemExit(main())
