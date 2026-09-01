#!/usr/bin/env python3
"""render_video.py — cut Voicebox beat assets into a real MP4.

One beat = one image + one voice clip = one cut. The cut points come from
``beat_marks.json``, which is measured from the audio that was actually
generated, so picture and voice cannot drift apart.

    python3 narration/render_video.py projects/foodcode-tomato --part 1
    python3 narration/render_video.py projects/foodcode-tomato --beats 1-20

Pipeline per beat
-----------------
1. Pillow normalises the generated image onto a 16:9 canvas (pale mat, never
   squashed, slight headroom for the move).
2. ffmpeg turns it into a clip exactly as long as the beat's measured audio,
   with a slow push / pull / hold chosen from the measured FoodCode mix
   (~55% still, ~45% gentle move).
3. The beat's own audio is muxed into that clip, so every segment is
   inherently in sync.
4. Segments are concatenated with ``-c copy`` — no re-encode, no drift.

Requires ffmpeg (``$VOICEBOX_FFMPEG``, or the repo-local ``.tools/venv``
binary) and Pillow for the canvas work.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

FPS = 30
WIDTH = 1920
HEIGHT = 1080
HEADROOM = 1.15          # how much larger the canvas is than the frame
PAD = (247, 243, 234)    # pale warm mat, matches the doodle white
CRF = "20"
AUDIO_BITRATE = "192k"

# Measured FoodCode motion mix, applied on a 5-beat cycle:
#   hold, push in, hold, pull out, hold   ->  60% still / 40% move
MOTION_CYCLE = ("hold", "in", "hold", "out", "hold")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def find_ffmpeg(explicit: str | None = None) -> str:
    if explicit:
        return explicit
    for var in ("VOICEBOX_FFMPEG", "FFMPEG"):
        exe = os.environ.get(var)
        if exe and os.path.exists(exe):
            return exe
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hit = os.path.join(
        repo, ".tools", "venv", "lib", "python3.11", "site-packages",
        "imageio_ffmpeg", "binaries",
    )
    if os.path.isdir(hit):
        for fn in sorted(os.listdir(hit)):
            if fn.startswith("ffmpeg-"):
                return os.path.join(hit, fn)
    sys.exit("ffmpeg not found. Set VOICEBOX_FFMPEG=/path/to/ffmpeg")


def parse_range(spec: str | None, n: int) -> set[int]:
    """'1-10', '3', '1-5,9' -> a set of 1-based beat ids."""
    if not spec:
        return set(range(1, n + 1))
    out: set[int] = set()
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, b = chunk.split("-", 1)
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(chunk))
    return out


def ensure_pillow() -> None:
    """Re-exec inside the repo's tool venv if Pillow is missing here.

    The sandbox ships no Pillow and wipes everything outside the repo between
    turns, so .tools/venv is the only reliable place for imaging deps.
    """
    try:
        import PIL  # noqa: F401
        return
    except ImportError:
        pass
    if os.environ.get("VOICEBOX_RENDER_REEXEC"):
        sys.exit("Pillow is required. Install it with:  pip install Pillow")
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    py = os.path.join(repo, ".tools", "venv", "bin", "python")
    if os.path.exists(py):
        os.environ["VOICEBOX_RENDER_REEXEC"] = "1"
        os.execv(py, [py, os.path.abspath(__file__)] + sys.argv[1:])


def normalise_image(src: str, dst: str, w: int, h: int, pad) -> None:
    """Fit `src` onto a w x h canvas without distorting it."""
    from PIL import Image  # imported lazily: only needed when rendering

    im = Image.open(src)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        canvas = Image.new("RGBA", im.size, pad + (255,))
        canvas.alpha_composite(im)
        im = canvas.convert("RGB")
    else:
        im = im.convert("RGB")

    im.thumbnail((w, h), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h), pad)
    canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    canvas.save(dst, "JPEG", quality=94, optimize=True, progressive=False)


def write_contact_sheet(frames: list[str], out: str, cols: int = 5,
                       thumb_w: int = 480) -> None:
    """Grid of the beats that went into a render, so a part can be eyeballed
    without scrubbing the MP4."""
    from PIL import Image

    cols = max(1, min(cols, len(frames)))
    rows = (len(frames) + cols - 1) // cols
    tw = thumb_w
    th = int(round(tw * HEIGHT / WIDTH))
    sheet = Image.new("RGB", (cols * tw, rows * th), (255, 255, 255))
    for i, f in enumerate(frames):
        im = Image.open(f)
        im.thumbnail((tw, th), Image.LANCZOS)
        x = (i % cols) * tw + (tw - im.width) // 2
        y = (i // cols) * th + (th - im.height) // 2
        sheet.paste(im, (x, y))
    sheet.save(out, "JPEG", quality=82, optimize=True)


def build_filter(motion: str, frames: int, cw: int, ch: int,
                 out_w: int, out_h: int) -> str:
    """zoompan keeps one output frame per input frame (d=1), so `on` is the
    frame index and z can be expressed straight off it."""
    span = max(frames - 1, 1)
    rate = (HEADROOM - 1.0) / span
    if motion == "in":
        z = f"min(1+{rate:.6f}*on,{HEADROOM})"
    elif motion == "out":
        z = f"max({HEADROOM}-{rate:.6f}*on,1)"
    else:
        z = f"{HEADROOM}"
    return (
        f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d=1:s={cw}x{ch}:fps={FPS},"
        f"scale={out_w}:{out_h}:flags=lanczos,format=yuv420p"
    )


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit("ffmpeg failed:\n" + " ".join(cmd) + "\n" + proc.stderr[-4000:])


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> None:
    global FPS
    ensure_pillow()
    ap = argparse.ArgumentParser(description="Render Voicebox beats to MP4.")
    ap.add_argument("project", help="project directory, e.g. projects/foodcode-tomato")
    ap.add_argument("--part", type=int, help="render one part number from beats.json")
    ap.add_argument("--beats", help="beat range, e.g. 1-10 or 1-10,12")
    ap.add_argument("--out", help="output file (default <project>/video/partNN.mp4)")
    ap.add_argument("--fps", type=int, default=FPS)
    ap.add_argument("--width", type=int, default=WIDTH)
    ap.add_argument("--height", type=int, default=HEIGHT)
    ap.add_argument("--pad", default="%02x%02x%02x" % PAD, help="mat colour, hex")
    ap.add_argument("--motion", default="auto",
                    choices=("auto", "hold", "in", "out"),
                    help="force one move for every beat")
    ap.add_argument("--ffmpeg", help="explicit ffmpeg path")
    ap.add_argument("--keep", action="store_true", help="keep the segment cache")
    args = ap.parse_args()

    FPS = args.fps

    proj = os.path.abspath(args.project)
    name = os.path.basename(proj.rstrip("/"))
    marks_path = os.path.join(proj, "beat_marks.json")
    beats_path = os.path.join(proj, "beats.json")
    src = marks_path if os.path.exists(marks_path) else beats_path
    if not os.path.exists(src):
        sys.exit(f"no beat_marks.json or beats.json in {proj}")
    data = json.load(open(src))
    beats = data["beats"] if isinstance(data, dict) else data

    # beat_marks.json carries timings but not part numbers; beats.json carries
    # parts but not timings. Merge so --part works off either file.
    if os.path.exists(beats_path) and os.path.abspath(beats_path) != os.path.abspath(src):
        script = json.load(open(beats_path))
        script_beats = script["beats"] if isinstance(script, dict) else script
        parts = {b["id"]: b.get("part") for b in script_beats}
        for b in beats:
            b.setdefault("part", parts.get(b["id"]))

    want = parse_range(args.beats, len(beats))
    if args.part:
        want = {b["id"] for b in beats if b.get("part") == args.part}
        if not want:
            sys.exit(f"no beats found for part {args.part}")

    pad = tuple(int(args.pad[i:i + 2], 16) for i in (0, 2, 4))
    ffmpeg = find_ffmpeg(args.ffmpeg)

    selected = []
    for b in beats:
        if b["id"] not in want:
            continue
        audio = os.path.join(proj, b.get("audio") or f"audio/beat{b['id']:02d}.mp3")
        image = os.path.join(proj, "images", f"beat{b['id']:02d}.png")
        if not os.path.exists(audio):
            print(f"  skip beat {b['id']:>3}: no audio  ({os.path.relpath(audio, proj)})")
            continue
        if not os.path.exists(image):
            print(f"  skip beat {b['id']:>3}: no image  ({os.path.relpath(image, proj)})")
            continue
        dur = b.get("duration") or b.get("actual")
        if not dur:
            print(f"  skip beat {b['id']:>3}: no measured duration (run `marks`)")
            continue
        selected.append((b, audio, image, float(dur)))

    if not selected:
        sys.exit("nothing to render — every beat in range is missing audio or image")

    total = sum(s[3] for s in selected)
    print(f"{name}: {len(selected)} beat(s), {total:.2f}s "
          f"({total / 60:.2f} min) @ {args.width}x{args.height} {FPS}fps")

    tmp = os.path.join(proj, ".render")
    os.makedirs(os.path.join(tmp, "norm"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "seg"), exist_ok=True)

    cw = int(round(args.width * HEADROOM / 2) * 2)
    ch = int(round(args.height * HEADROOM / 2) * 2)
    segs = []

    for i, (b, audio, image, dur) in enumerate(selected):
        bid = b["id"]
        motion = args.motion
        if motion == "auto":
            motion = MOTION_CYCLE[i % len(MOTION_CYCLE)]
        norm = os.path.join(tmp, "norm", f"beat{bid:02d}.jpg")
        normalise_image(image, norm, cw, ch, pad)

        frames = max(int(round(dur * FPS)), 2)
        seg = os.path.join(tmp, "seg", f"beat{bid:02d}.mp4")
        cmd = [
            ffmpeg, "-y", "-v", "error",
            "-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", norm,
            "-i", audio,
            "-filter:v", build_filter(motion, frames, cw, ch, args.width, args.height),
            "-frames:v", str(frames),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", CRF,
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", "48000", "-ac", "2",
            "-t", f"{dur:.3f}",
            "-movflags", "+faststart",
            seg,
        ]
        run(cmd)
        segs.append(seg)
        print(f"  beat {bid:>3}  {dur:5.2f}s  {motion:<4}  {b.get('label', '')}")

    listfile = os.path.join(tmp, "concat.txt")
    with open(listfile, "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")

    out = args.out
    if not out:
        os.makedirs(os.path.join(proj, "video"), exist_ok=True)
        tag = f"part{args.part:02d}" if args.part else "cut"
        out = os.path.join(proj, "video", f"{tag}.mp4")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)

    run([ffmpeg, "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", listfile, "-c", "copy", "-movflags", "+faststart", out])

    size = os.path.getsize(out)
    print(f"\nwrote {out}  ({size / 1e6:.1f} MB, {total:.2f}s)")

    norm_frames = [os.path.join(tmp, "norm", f"beat{b['id']:02d}.jpg")
                   for b, _, _, _ in selected]
    contact = os.path.splitext(out)[0] + "_contact.jpg"
    write_contact_sheet(norm_frames, contact)
    print(f"wrote {contact}  ({os.path.getsize(contact) / 1e3:.0f} KB, "
          f"{len(norm_frames)} frames)")

    write_sidecar(out, proj, selected, total, contact, args)


def write_sidecar(out: str, proj: str, selected, total: float, contact: str,
                  args) -> str:
    """A <video>.json next to every MP4.

    The studio reads these instead of guessing, so a render can report its
    real duration, beat range and resolution even though video/ is gitignored
    and the MP4 is not in the repo.
    """
    import datetime

    data = {
        "project": os.path.basename(proj.rstrip("/")),
        "file": os.path.basename(out),
        "url": "media/%s/video/%s" % (os.path.basename(proj.rstrip("/")),
                                      os.path.basename(out)),
        "part": args.part,
        "beats": [b["id"] for b, _, _, _ in selected],
        "beat_count": len(selected),
        "duration": round(total, 2),
        "bytes": os.path.getsize(out),
        "width": args.width,
        "height": args.height,
        "fps": FPS,
        "contact": os.path.basename(contact),
        "rendered_at": datetime.datetime.now(datetime.timezone.utc)
                       .replace(microsecond=0).isoformat(),
    }
    path = os.path.splitext(out)[0] + ".json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
        f.write("\n")
    print(f"wrote {path}")
    return path

    if not args.keep:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
