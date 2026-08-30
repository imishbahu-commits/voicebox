#!/usr/bin/env python3
"""beat_narrator.py — FoodCode-style beat narration for Voicebox.

Turns a narration script into per-beat assets an editor can cut to:

  * every beat is 12-16 spoken words
  * every beat is 2.0-6.0 s of real audio (median 3.6 s, measured from the
    Paint Explainer reference video)
  * every beat carries its own visual, so the cut list is derived from the
    voiceover instead of guessed

The voiceover is the boss: beat marks are measured from the audio that was
actually generated, never from an estimate.

Commands
--------
    split   narration.txt -> beats.json      (12-16 words per beat, visual slots)
    check   beats.json                       (pass/fail against the two rules)
    synth   beats.json                       (one audio file per beat)
    marks   beats.json                       (beat_marks.json/.csv/.edl)

Typical flow
------------
    python3 narration/beat_narrator.py split script.txt -o projects/myvid
    #   ... fill in the visual field for every beat ...
    python3 narration/beat_narrator.py check projects/myvid/beats.json
    python3 narration/beat_narrator.py synth projects/myvid/beats.json --backend voicebox
    python3 narration/beat_narrator.py marks projects/myvid/beats.json

Only the standard library is required. ``requests`` is used if present for the
voicebox backend, otherwise urllib is used.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict

# --------------------------------------------------------------------------
# The measured FoodCode / Paint Explainer rules
# --------------------------------------------------------------------------

WORD_MIN, WORD_MAX = 12, 16          # words of narration per beat
SEC_MIN, SEC_MAX = 2.0, 6.0          # seconds of audio per beat
MEDIAN_SEC = 3.6                     # measured median cut interval
TARGET_WPS = 14.0 / MEDIAN_SEC       # ~3.9 words/sec -> a 14-word beat ≈ 3.6 s
FPS = 60                             # render frame rate for beat marks
CHAPTER_PAUSE = 0.7                  # breath between sections

NARRATION_KEYS = ("narration", "spoken", "text", "line")
VISUAL_KEYS = ("visual", "scene", "shot", "image")
LABEL_KEYS = ("label", "title", "caption")

WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’\-]*")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
CLAUSE_SPLIT_RE = re.compile(r"(?<=[,;:—–])\s+")


# --------------------------------------------------------------------------
# Beat container
# --------------------------------------------------------------------------

@dataclass
class Beat:
    id: int
    narration: str = ""
    visual: str = ""
    label: str = ""
    transition: str = "cut"      # cut | revealing | disappearing | switching
    part: int | None = None
    duration: float | None = None     # planned / estimated
    actual: float | None = None       # measured from generated audio
    audio: str | None = None
    source_hint: str = "ai"

    @property
    def words(self) -> int:
        return len(WORD_RE.findall(self.narration))

    @property
    def ok_words(self) -> bool:
        return WORD_MIN <= self.words <= WORD_MAX

    @property
    def ok_seconds(self) -> bool:
        if self.actual is None:
            return True
        return SEC_MIN <= self.actual <= SEC_MAX

    @property
    def estimate(self) -> float:
        """Estimated spoken duration at the reference delivery rate."""
        return round(self.words / TARGET_WPS, 2)


def estimate_duration(narration: str) -> float:
    """Estimated seconds to speak `narration` at the FoodCode delivery rate."""
    return round(len(WORD_RE.findall(narration)) / TARGET_WPS, 2)


# --------------------------------------------------------------------------
# Loading / saving beats
# --------------------------------------------------------------------------

def _first(d: dict, keys, default=""):
    for k in keys:
        v = d.get(k)
        if v:
            return v
    return default


def load_beats(path: str) -> tuple[list[Beat], dict]:
    """Load a beats file. Understands both the youtube-script and the
    FoodCode (projects/foodcode-*) shapes."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        raw = data.get("beats", [])
        meta = {k: v for k, v in data.items() if k != "beats"}
    else:
        raw, meta = data, {}

    beats = []
    for i, b in enumerate(raw, 1):
        beats.append(Beat(
            id=b.get("id", i),
            narration=_first(b, NARRATION_KEYS),
            visual=_first(b, VISUAL_KEYS),
            label=_first(b, LABEL_KEYS),
            transition=b.get("transition", "cut"),
            part=b.get("part"),
            duration=b.get("duration"),
            actual=b.get("actual") or b.get("actual_duration"),
            audio=b.get("audio"),
            source_hint=b.get("source_hint", "ai"),
        ))
    return beats, meta


def save_beats(path: str, beats: list[Beat], meta: dict | None = None):
    meta = meta or {}
    out = dict(meta)
    out["beats"] = [asdict(b) for b in beats]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------
# split — narration text -> beats of 12-16 words
# --------------------------------------------------------------------------

def wc(text: str) -> int:
    """Spoken word count (punctuation excluded)."""
    return len(WORD_RE.findall(text))


def split_to_beats(text: str, min_w: int = WORD_MIN,
                   max_w: int = WORD_MAX) -> list[Beat]:
    """Split narration into beats of 12-16 words.

    Sentences are kept whole wherever they fit. A sentence is only broken at a
    clause boundary, and only chopped mid-sentence as a last resort (a long
    run-on with no commas) — a beat that ends mid-clause reads badly once it is
    cut to its own image.

    Short fragments ("Not a spice. Not an acid.") merge with a neighbour when
    the result still fits under `max_w`; when it does not they are left as
    short beats so `check` flags them for a rewrite instead of silently
    mangling the sentence to hit the number.
    """
    atoms: list[str] = []
    for sentence in SENTENCE_SPLIT_RE.split(text.strip()):
        sentence = sentence.strip()
        if not sentence:
            continue
        if wc(sentence) > max_w:
            atoms.extend(_chunk_sentence(sentence, min_w, max_w))
        else:
            atoms.append(sentence)

    raw: list[str] = []
    cur: list[str] = []
    cur_w = 0
    for atom in atoms:
        aw = wc(atom)
        if cur_w + aw <= max_w:
            cur.append(atom)
            cur_w += aw
        else:
            if cur:
                raw.append(" ".join(cur))
            cur, cur_w = [atom], aw
    if cur:
        raw.append(" ".join(cur))

    raw = _merge_short(raw, min_w, max_w)
    raw = _split_long(raw, min_w, max_w)

    return [Beat(id=i, narration=line, duration=estimate_duration(line))
            for i, line in enumerate(raw, 1)]


def _chunk_sentence(sentence: str, min_w: int, max_w: int) -> list[str]:
    """Break one over-long sentence into <= max_w chunks at clause boundaries."""
    clauses = [c.strip() for c in CLAUSE_SPLIT_RE.split(sentence) if c.strip()]
    if len(clauses) <= 1:
        return _chop_words(sentence, max_w)
    out: list[str] = []
    cur: list[str] = []
    cur_w = 0
    for c in clauses:
        cw = wc(c)
        if cur_w + cw <= max_w:
            cur.append(c)
            cur_w += cw
        elif cur_w >= min_w:
            out.append(" ".join(cur))
            cur, cur_w = [c], cw
        else:
            # short leading clause + over-long clause: chop the two together so
            # the leading clause is not orphaned into a sub-2 s crumb beat.
            whole = " ".join(cur + [c]) if cur else c
            out.extend(_chop_words(whole, max_w) if wc(whole) > max_w else [whole])
            cur, cur_w = [], 0
    if cur:
        out.append(" ".join(cur))
    return [o for o in out if o.strip()]


def _chop_words(text: str, max_w: int) -> list[str]:
    words = text.split()
    return [" ".join(words[i:i + max_w]) for i in range(0, len(words), max_w)]


def _merge_short(raw: list[str], min_w: int, max_w: int) -> list[str]:
    """Merge a beat under min_w into a neighbour if the result still fits."""
    if not raw:
        return raw
    out: list[str] = []
    for line in raw:
        if out and wc(line) < min_w and wc(out[-1]) + wc(line) <= max_w:
            out[-1] = f"{out[-1]} {line}"
            continue
        out.append(line)
    if len(out) >= 2 and wc(out[-1]) < min_w and \
            wc(out[-2]) + wc(out[-1]) <= max_w:
        out[-2] = f"{out[-2]} {out[-1]}"
        out.pop()
    return out


def _split_long(raw: list[str], min_w: int, max_w: int) -> list[str]:
    """Safety net: split anything still over max_w, clause boundary first."""
    out: list[str] = []
    for line in raw:
        while wc(line) > max_w:
            pieces = [p.strip() for p in CLAUSE_SPLIT_RE.split(line) if p.strip()]
            if len(pieces) > 1:
                take, acc = [], 0
                for p in pieces:
                    pw = wc(p)
                    if take and acc + pw > max_w:
                        break
                    take.append(p)
                    acc += pw
                if take and acc >= min_w:
                    out.append(" ".join(take).strip())
                    line = " ".join(pieces[len(take):]).strip()
                    continue
            words = line.split()
            cut = min(max_w, max(min_w, len(words) - max_w) or max_w)
            out.append(" ".join(words[:cut]))
            line = " ".join(words[cut:])
        if line:
            out.append(line)
    return out


def beats_from_txt(path: str) -> list[Beat]:
    """Load a `NN|narration` beats.txt file (the foodcode-pineapple format)."""
    lines = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").strip()
            if not line:
                continue
            if "|" in line:
                line = line.split("|", 1)[1].strip()
            lines.append(line)
    return split_to_beats(" ".join(lines))


# --------------------------------------------------------------------------
# check — validate against the two rules
# --------------------------------------------------------------------------

def check(beats: list[Beat]) -> tuple[list[str], dict]:
    issues: list[str] = []
    words = [b.words for b in beats]
    total = sum(b.actual or b.duration or b.estimate for b in beats)

    for b in beats:
        if b.words < WORD_MIN:
            issues.append(f"beat {b.id}: {b.words} words (< {WORD_MIN}) — too short, "
                          f"merges into a sub-2s cut")
        elif b.words > WORD_MAX:
            issues.append(f"beat {b.id}: {b.words} words (> {WORD_MAX}) — splits into "
                          f"two beats, each needs its own image")
        if b.actual is not None and not (SEC_MIN <= b.actual <= SEC_MAX):
            issues.append(f"beat {b.id}: {b.actual:.2f}s outside {SEC_MIN}-{SEC_MAX}s")
        if not b.visual:
            issues.append(f"beat {b.id}: no visual described (1 beat = 1 image)")

    stats = {
        "beats": len(beats),
        "words_total": sum(words),
        "words_min": min(words) if words else 0,
        "words_max": max(words) if words else 0,
        "words_mean": round(sum(words) / len(words), 1) if words else 0,
        "in_word_range": sum(1 for w in words if WORD_MIN <= w <= WORD_MAX),
        "missing_visual": sum(1 for b in beats if not b.visual),
        "total_seconds": round(total, 2),
        "median_seconds": round(_median([b.actual or b.duration or b.estimate
                                         for b in beats]), 2),
    }
    return issues, stats


def _median(xs: list[float]) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


# --------------------------------------------------------------------------
# audio duration probing
# --------------------------------------------------------------------------

def _find_ffmpeg() -> str | None:
    """Locate ffprobe or ffmpeg.

    Order: $VOICEBOX_FFMPEG / $FFMPEG, then PATH, then an importable
    imageio-ffmpeg, then an imageio-ffmpeg binary sitting in a nearby venv
    (the doodle-explainer-video checkout installs one). Exact durations need a
    real decoder; the built-in MP3/WAV reader is the fallback.
    """
    for var in ("VOICEBOX_FFMPEG", "FFMPEG", "FFPROBE"):
        exe = os.environ.get(var)
        if exe and os.path.exists(exe):
            return exe
    for name in ("ffprobe", "ffmpeg"):
        exe = shutil.which(name)
        if exe:
            return exe
    try:
        import imageio_ffmpeg  # noqa
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    # os.walk, not glob: the binary usually lives in a hidden .venv, and glob
    # refuses to descend into dot-directories.
    here = os.path.dirname(os.path.abspath(__file__))
    skip = {".git", "node_modules", "__pycache__", "target", "dist", "build"}
    for root in (os.path.dirname(here), os.path.dirname(os.path.dirname(here)),
                 os.getcwd()):
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in skip]
            if os.path.basename(dirpath) != "binaries":
                continue
            if os.path.basename(os.path.dirname(dirpath)) != "imageio_ffmpeg":
                continue
            for fn in sorted(filenames):
                if fn.startswith("ffmpeg-"):
                    hit = os.path.join(dirpath, fn)
                    if os.path.isfile(hit) and os.access(hit, os.X_OK):
                        return hit
    return None


def probe_duration(path: str) -> float | None:
    """Duration in seconds. Tries ffprobe/ffmpeg, then a stdlib MP3/WAV read."""
    exe = _find_ffmpeg()
    if exe:
        try:
            cmd = [exe, "-v", "error", "-show_entries", "format=duration",
                   "-of", "default=nw=1:nk=1", path]
            if os.path.basename(exe).startswith("ffprobe"):
                out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            else:                      # ffmpeg binary: read the header banner
                out = subprocess.run([exe, "-i", path],
                                     capture_output=True, text=True, timeout=60)
                m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", out.stderr)
                if m:
                    h, mi, se = m.groups()
                    return int(h) * 3600 + int(mi) * 60 + float(se)
                return None
            if out.returncode == 0 and out.stdout.strip():
                return float(out.stdout.strip())
        except Exception:
            pass
    return _duration_stdlib(path)


def _duration_stdlib(path: str) -> float | None:
    """Minimal WAV / MP3 duration reader (no third-party deps)."""
    try:
        with open(path, "rb") as f:
            head = f.read(4)
            if head == b"RIFF":
                return _wav_duration(f)
            if head[:3] == b"ID3":
                f.seek(0)
                return _mp3_duration(f, skip_id3=True)
            f.seek(0)
            return _mp3_duration(f, skip_id3=False)
    except Exception:
        return None


def _wav_duration(f) -> float | None:
    data = f.read()
    if data[8:12] != b"WAVE":
        return None
    pos, byte_rate, data_len = 12, None, 0
    while pos + 8 <= len(data):
        cid = data[pos:pos + 4]
        size = int.from_bytes(data[pos + 4:pos + 8], "little")
        body = data[pos + 8:pos + 8 + size]
        if cid == b"fmt " and size >= 16:
            byte_rate = int.from_bytes(body[8:12], "little")
        elif cid == b"data":
            data_len = size
        pos += 8 + size + (size & 1)
    if byte_rate:
        return round(data_len / byte_rate, 3)
    return None


# bitrate tables keyed by the layer bits of the frame header:
#   1 = Layer III, 2 = Layer II, 3 = Layer I   (0 is reserved)
_BR_V1 = {
    3: [0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448],
    2: [0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384],
    1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
}
_BR_V2 = {
    3: [0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256],
    2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
    1: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
}
# version bits -> (sample rate table, is_mpeg1)
_RATES = {
    3: [44100, 48000, 32000],   # MPEG-1
    2: [22050, 24000, 16000],   # MPEG-2
    0: [11025, 12000, 8000],    # MPEG-2.5
}


def _mp3_header(data: bytes, i: int):
    """Parse an MP3 frame header.

    Returns (ver, layer, bitrate_kbps, rate, samples_per_frame, frame_len)
    or None when the bytes at `i` are not a valid header.
    """
    if i + 4 > len(data):
        return None
    if data[i] != 0xFF or (data[i + 1] & 0xE0) != 0xE0:
        return None
    ver = (data[i + 1] >> 3) & 0x03
    layer = (data[i + 1] >> 1) & 0x03
    br_idx = (data[i + 2] >> 4) & 0x0F
    sr_idx = (data[i + 2] >> 2) & 0x03
    pad = (data[i + 2] >> 1) & 0x01           # padding lives in byte 2
    if ver == 1 or layer == 0 or br_idx in (0, 15) or sr_idx == 3:
        return None
    table = (_BR_V1 if ver == 3 else _BR_V2).get(layer)
    if not table:
        return None
    br = table[br_idx]
    rate = _RATES[ver][sr_idx]
    if layer == 3:                             # Layer I
        spf = 384
        flen = (12 * br * 1000 // rate + pad) * 4
    else:
        spf = 1152 if (layer == 2 or ver == 3) else 576
        # MPEG-2/2.5 pack half as many bytes per frame as MPEG-1
        coeff = 144 if ver == 3 else 72
        flen = coeff * br * 1000 // rate + pad
    return ver, layer, br, rate, spf, max(flen, 4)


def _mp3_duration(f, skip_id3: bool) -> float | None:
    data = f.read()
    start = 0
    if skip_id3 and data[:3] == b"ID3":
        size = ((data[6] & 0x7F) << 21) | ((data[7] & 0x7F) << 14) \
            | ((data[8] & 0x7F) << 7) | (data[9] & 0x7F)
        start = 10 + size
    n = len(data)

    i = start
    rate = spf = 0
    while i + 4 <= n:                          # find the first valid frame
        hdr = _mp3_header(data, i)
        if hdr is None:
            i += 1
            continue
        ver, _layer, _br, rate, spf, _flen = hdr
        mono = ((data[i + 3] >> 6) & 0x03) == 3
        # side-info size before the Xing/Info tag
        off = i + 4 + ((17 if mono else 32) if ver == 3 else (9 if mono else 17))
        if data[off:off + 4] in (b"Xing", b"Info"):
            flags = int.from_bytes(data[off + 4:off + 8], "big")
            if flags & 0x1:                    # frame count present -> exact
                cnt = int.from_bytes(data[off + 8:off + 12], "big")
                return round(cnt * spf / rate, 3)
        break
    if not rate:
        return None

    frames = 0
    while i + 4 <= n:                          # walk the frames
        hdr = _mp3_header(data, i)
        if hdr is None:
            i += 1
            continue
        frames += 1
        i += hdr[5]
    if frames:
        return round(frames * spf / rate, 3)
    return None


# --------------------------------------------------------------------------
# synth — one audio file per beat
# --------------------------------------------------------------------------

VOICEBOX_DEFAULT = "http://127.0.0.1:17493"


class VoiceboxClient:
    """Thin client over the Voicebox REST API (backend/app.py)."""

    def __init__(self, base: str = VOICEBOX_DEFAULT, timeout: float = 60.0):
        self.base = base.rstrip("/")
        self.timeout = timeout
        try:
            import requests  # noqa
            self._requests = True
        except ImportError:
            self._requests = False

    def _req(self, method: str, path: str, payload=None, raw=False):
        url = f"{self.base}{path}"
        if self._requests:
            import requests  # noqa
            r = requests.request(method, url, json=payload, timeout=self.timeout)
            r.raise_for_status()
            return r.content if raw else r.json()
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        if data:
            req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = resp.read()
            return body if raw else json.loads(body.decode())

    def profiles(self):
        return self._req("GET", "/profiles")

    def generate(self, profile_id: str, text: str, language="en", engine=None,
                 **kw) -> str:
        payload = {"profile_id": profile_id, "text": text, "language": language}
        if engine:
            payload["engine"] = engine
        payload.update(kw)
        return self._req("POST", "/generate", payload)["id"]

    def status(self, gen_id: str) -> dict:
        return self._req("GET", f"/generate/{gen_id}/status")

    def audio(self, gen_id: str) -> bytes:
        return self._req("GET", f"/audio/{gen_id}", raw=True)

    def wait(self, gen_id: str, poll: float = 1.0, limit: float = 900.0) -> dict:
        end = time.time() + limit
        while time.time() < end:
            st = self.status(gen_id)
            s = str(st.get("status", "")).lower()
            if s in ("completed", "complete", "done", "success"):
                return st
            if s in ("failed", "error", "cancelled", "canceled"):
                raise RuntimeError(f"generation {gen_id} failed: {st}")
            time.sleep(poll)
        raise TimeoutError(f"generation {gen_id} timed out")


def synth_voicebox(beats: list[Beat], outdir: str, profile_id: str,
                   base: str, engine=None, language="en", limit=0) -> int:
    os.makedirs(outdir, exist_ok=True)
    client = VoiceboxClient(base)
    todo = [b for b in beats if b.narration][:limit or len(beats)]
    done = 0
    for b in todo:
        dest = os.path.join(outdir, f"beat{b.id:02d}.mp3")
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            b.audio = dest
            b.actual = probe_duration(dest) or b.actual
            done += 1
            continue
        gen = client.generate(profile_id, b.narration, language=language,
                              engine=engine)
        client.wait(gen)
        with open(dest, "wb") as f:
            f.write(client.audio(gen))
        b.audio = dest
        b.actual = probe_duration(dest)
        done += 1
        print(f"  [{done}/{len(todo)}] beat {b.id:02d} "
              f"{b.actual or 0:.2f}s  {b.words}w", flush=True)
    return done


def synth_arena(beats: list[Beat], outdir: str) -> str:
    """Emit a manifest for the agent's generate_speech tool.

    Voicebox's local engines need several GB of model weights and a GPU; when
    that is not available this manifest is what the agent reads to synthesise
    each beat with the built-in high-quality voices instead. The beat numbering
    and durations come back through `marks`.
    """
    os.makedirs(outdir, exist_ok=True)
    man = {
        "backend": "arena-generate-speech",
        "outdir": outdir,
        "rules": {"words": [WORD_MIN, WORD_MAX], "seconds": [SEC_MIN, SEC_MAX]},
        "note": ("One generate_speech call per beat, saved as "
                 "beatNN.mp3. Max 10 clips per turn. Then run `marks`."),
        "beats": [{"id": b.id, "words": b.words, "file": f"beat{b.id:02d}.mp3",
                   "text": b.narration, "visual": b.visual} for b in beats],
    }
    path = os.path.join(outdir, "tts_manifest.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=2, ensure_ascii=False)
    for b in beats:                      # one text file per beat, easy to read
        with open(os.path.join(outdir, f"beat{b.id:02d}.txt"), "w",
                  encoding="utf-8") as f:
            f.write(b.narration)
    return path


# --------------------------------------------------------------------------
# fit — time-stretch each beat into the 2-6 s window (pitch preserved)
# --------------------------------------------------------------------------

def _atempo_chain(ratio: float) -> str:
    """atempo accepts 0.5-2.0 per filter, so chain them for bigger ratios."""
    parts: list[str] = []
    r = ratio
    while r > 2.0:
        parts.append("atempo=2.0")
        r /= 2.0
    while r < 0.5:
        parts.append("atempo=0.5")
        r /= 0.5
    parts.append(f"atempo={r:.4f}")
    return ",".join(parts)


def fit_beats(beats: list[Beat], audiodir: str, target_wps: float = TARGET_WPS,
              dry: bool = False) -> list[dict]:
    """Retime each beat's audio so it lands inside SEC_MIN-SEC_MAX.

    Uses ffmpeg's atempo so the pitch is untouched — this is the same move an
    editor makes when a read runs long, just applied per beat.

    `target_wps` is the delivery rate to aim for. The default (14 words / 3.6 s
    ~= 3.9 wps) centres the median beat on the measured 3.6 s reference. A TTS
    voice that reads at ~2.3 wps will be sped up ~1.7x at that setting; pass a
    lower value (2.7 is the slowest that still keeps a 16-word beat under 6 s)
    for a more natural read at the cost of a higher median.
    """
    exe = _find_ffmpeg()
    if not exe:
        raise SystemExit(
            "fit needs ffmpeg (atempo filter). Install imageio-ffmpeg, put "
            "ffmpeg on PATH, or set VOICEBOX_FFMPEG.")

    report: list[dict] = []
    for b in beats:
        if not b.audio:
            cand = os.path.join(audiodir, f"beat{b.id:02d}.mp3")
            if os.path.exists(cand):
                b.audio = cand
        if not b.audio or not os.path.exists(b.audio):
            continue
        measured = probe_duration(b.audio)
        if not measured:
            continue

        target = min(SEC_MAX, max(SEC_MIN, b.words / target_wps))
        ratio = measured / target
        row = {"id": b.id, "words": b.words, "before": round(measured, 2),
               "target": round(target, 2), "ratio": round(ratio, 3),
               "wps_before": round(b.words / measured, 2),
               "wps_after": round(b.words / target, 2)}

        if 0.98 <= ratio <= 1.02:
            row["action"] = "ok"
            row["after"] = round(measured, 2)
            b.actual = measured
            report.append(row)
            continue

        row["action"] = "speed-up" if ratio > 1 else "slow-down"
        if dry:
            row["after"] = round(measured / ratio, 2)
        else:
            # keep the untouched read so a beat can be re-fit at a different
            # pace later without regenerating the TTS
            orig_dir = os.path.join(audiodir, "original")
            orig = os.path.join(orig_dir, f"beat{b.id:02d}.mp3")
            if not os.path.exists(orig):
                os.makedirs(orig_dir, exist_ok=True)
                shutil.copy2(b.audio, orig)
            tmp = f"{b.audio}.fit.mp3"
            try:
                subprocess.run(
                    [exe, "-y", "-v", "error", "-i", b.audio,
                     "-filter:a", _atempo_chain(ratio),
                     "-c:a", "libmp3lame", "-q:a", "2", tmp],
                    capture_output=True, timeout=300)
            except Exception as exc:            # noqa: BLE001
                row["action"] = f"failed: {exc}"
                report.append(row)
                continue
            if os.path.exists(tmp) and os.path.getsize(tmp) > 0:
                os.replace(tmp, b.audio)
                b.actual = probe_duration(b.audio)
                row["after"] = round(b.actual or 0, 2)
            else:
                row["action"] = "ffmpeg produced no output"
                row["after"] = round(measured, 2)
        report.append(row)
    return report


# --------------------------------------------------------------------------
# marks — measured cut list
# --------------------------------------------------------------------------

def build_marks(beats: list[Beat], project: str = "project") -> dict:
    t = 0.0
    rows = []
    for b in beats:
        dur = b.actual or b.duration or b.estimate
        start, end = t, t + dur
        rows.append({
            "id": b.id,
            "start": round(start, 3),
            "end": round(end, 3),
            "duration": round(dur, 3),
            "frame_in": int(round(start * FPS)),
            "frame_out": int(round(end * FPS)),
            "frames": int(round(dur * FPS)),
            "words": b.words,
            "wps": round(b.words / dur, 2) if dur else 0,
            "ok_words": b.ok_words,
            "ok_seconds": SEC_MIN <= dur <= SEC_MAX,
            "visual": b.visual,
            "label": b.label,
            "transition": b.transition,
            "audio": b.audio or f"audio/beat{b.id:02d}.mp3",
            "narration": b.narration,
        })
        t = end
    measured = [b.actual for b in beats if b.actual]
    return {
        "project": project,
        "fps": FPS,
        "rules": {"words": [WORD_MIN, WORD_MAX], "seconds": [SEC_MIN, SEC_MAX],
                  "median_target": MEDIAN_SEC},
        "total_duration": round(t, 3),
        "median_duration": round(_median([b.actual or b.duration or b.estimate
                                          for b in beats]), 3),
        "measured": bool(measured),
        "beats": rows,
    }


def write_marks(marks: dict, outdir: str):
    os.makedirs(outdir, exist_ok=True)
    p_json = os.path.join(outdir, "beat_marks.json")
    with open(p_json, "w", encoding="utf-8") as f:
        json.dump(marks, f, indent=2, ensure_ascii=False)

    p_csv = os.path.join(outdir, "beat_marks.csv")
    with open(p_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["beat", "start", "end", "duration", "frames", "words",
                    "wps", "transition", "label", "visual", "audio"])
        for r in marks["beats"]:
            w.writerow([r["id"], r["start"], r["end"], r["duration"], r["frames"],
                        r["words"], r["wps"], r["transition"], r["label"],
                        r["visual"], r["audio"]])

    p_edl = os.path.join(outdir, "beat_marks.edl")
    with open(p_edl, "w", encoding="utf-8") as f:
        f.write(f"TITLE: {marks['project']}\nFCM: NON-DROP FRAME\n\n")
        for i, r in enumerate(marks["beats"], 1):
            f.write(f"{i:03d}  AX       V     C        "
                    f"{_tc(r['frame_in'])} {_tc(r['frame_out'])} "
                    f"{_tc(r['frame_in'])} {_tc(r['frame_out'])}\n")
            f.write(f"* FROM CLIP NAME: {r['label'] or r['visual'][:40]}\n")
            f.write(f"* VISUAL: {r['visual']}\n")
            f.write(f"* NARRATION: {r['narration']}\n\n")
    return p_json, p_csv, p_edl


def _tc(frames: int) -> str:
    fps = FPS
    h = frames // (3600 * fps)
    m = (frames // (60 * fps)) % 60
    s = (frames // fps) % 60
    fr = frames % fps
    return f"{h:02d}:{m:02d}:{s:02d}:{fr:02d}"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _print_report(issues: list[str], stats: dict, beats: list[Beat],
                  show_rows: bool):
    print(f"beats            {stats['beats']}")
    print(f"words            total {stats['words_total']}  "
          f"min {stats['words_min']}  max {stats['words_max']}  "
          f"mean {stats['words_mean']}")
    print(f"in {WORD_MIN}-{WORD_MAX} words    {stats['in_word_range']}"
          f"/{stats['beats']}")
    print(f"missing visual   {stats['missing_visual']}")
    print(f"duration         total {stats['total_seconds']}s  "
          f"median {stats['median_seconds']}s (target {MEDIAN_SEC}s)")
    if show_rows:
        print()
        print(f"{'beat':>4} {'w':>3} {'sec':>6} {'visual':<34} narration")
        for b in beats:
            d = b.actual or b.duration or b.estimate
            flag = "" if b.ok_words else " !"
            vis = (b.visual or b.label or "-")[:34]
            print(f"{b.id:>4} {b.words:>3} {d:>6.2f} {vis:<34} "
                  f"{b.narration[:60]}{flag}")
    print()
    if issues:
        print(f"{len(issues)} issue(s):")
        for i in issues[:40]:
            print(f"  - {i}")
        if len(issues) > 40:
            print(f"  ... and {len(issues) - 40} more")
    else:
        print("OK — every beat is 12-16 words, 2-6 s, and has a visual.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="beat_narrator",
        description="FoodCode-style beat narration for Voicebox "
                    f"({WORD_MIN}-{WORD_MAX} words, {SEC_MIN}-{SEC_MAX}s per beat).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("split", help="split narration into 12-16 word beats")
    p.add_argument("input", help="plain narration text, beats.txt, or .md")
    p.add_argument("-o", "--out", default=".", help="project directory")
    p.add_argument("--name", default="beats.json")
    p.add_argument("--min-words", type=int, default=WORD_MIN)
    p.add_argument("--max-words", type=int, default=WORD_MAX)
    p.add_argument("--keep-visuals", help="existing beats.json to copy "
                                          "visual/label/part from")

    p = sub.add_parser("check", help="validate beats against the two rules")
    p.add_argument("beats")
    p.add_argument("--rows", action="store_true")

    p = sub.add_parser("synth", help="generate one audio file per beat")
    p.add_argument("beats")
    p.add_argument("--backend", choices=["voicebox", "arena"], default="arena")
    p.add_argument("--base", default=VOICEBOX_DEFAULT, help="voicebox API base URL")
    p.add_argument("--profile", help="voicebox profile id (voicebox backend)")
    p.add_argument("--engine", help="qwen | qwen_custom_voice | kokoro | ...")
    p.add_argument("--language", default="en")
    p.add_argument("--out", help="audio directory (default: <project>/audio)")
    p.add_argument("--limit", type=int, default=0, help="only first N beats")

    p = sub.add_parser("fit", help="retime each beat into the 2-6 s window")
    p.add_argument("beats")
    p.add_argument("--audio-dir", help="where beatNN.mp3 lives (default: audio)")
    p.add_argument("--target-wps", type=float, default=TARGET_WPS,
                   help=f"delivery rate to aim for (default {TARGET_WPS:.2f} "
                        f"= 14 words / 3.6 s). 2.7 is the slowest that still "
                        f"fits a 16-word beat inside 6 s.")
    p.add_argument("--dry-run", action="store_true",
                   help="report what would change without touching audio")

    p = sub.add_parser("marks", help="build the measured cut list")
    p.add_argument("beats")
    p.add_argument("--out", help="output directory (default: project dir)")
    p.add_argument("--audio-dir", help="where beatNN.mp3 lives (default: audio)")

    args = ap.parse_args(argv)

    if args.cmd == "split":
        text = open(args.input, encoding="utf-8").read()
        if args.input.endswith(".json"):
            beats, meta = load_beats(args.input)
            beats = split_to_beats(" ".join(b.narration for b in beats),
                                   args.min_words, args.max_words)
        else:
            beats = beats_from_txt(args.input) if "|" in text[:200] \
                else split_to_beats(text, args.min_words, args.max_words)
            meta = {}
        if args.keep_visuals and os.path.exists(args.keep_visuals):
            old, ometa = load_beats(args.keep_visuals)
            for b, o in zip(beats, old):
                b.visual, b.label, b.part = o.visual, o.label, o.part
            meta.update(ometa)
        os.makedirs(args.out, exist_ok=True)
        path = os.path.join(args.out, args.name)
        save_beats(path, beats, meta)
        issues, stats = check(beats)
        print(f"{len(beats)} beats -> {path}")
        _print_report(issues, stats, beats, show_rows=False)
        return 0

    if args.cmd == "check":
        beats, _ = load_beats(args.beats)
        issues, stats = check(beats)
        _print_report(issues, stats, beats, show_rows=args.rows)
        return 1 if issues else 0

    if args.cmd == "synth":
        beats, meta = load_beats(args.beats)
        outdir = args.out or os.path.join(os.path.dirname(
            os.path.abspath(args.beats)), "audio")
        if args.backend == "voicebox":
            if not args.profile:
                ap.error("--profile is required with --backend voicebox")
            synth_voicebox(beats, outdir, args.profile, args.base,
                           args.engine, args.language, args.limit)
        else:
            path = synth_arena(beats, outdir)
            print(f"tts manifest -> {path}")
            print(f"{len(beats)} beats ready to synthesise "
                  f"(10 clips per turn; resume with --limit).")
        save_beats(args.beats, beats, meta)
        return 0

    if args.cmd == "fit":
        beats, meta = load_beats(args.beats)
        pdir = os.path.dirname(os.path.abspath(args.beats))
        adir = args.audio_dir or os.path.join(pdir, "audio")
        rows = fit_beats(beats, adir, args.target_wps, args.dry_run)
        if not rows:
            print(f"no audio found in {adir} — run `synth` first.")
            return 1
        print(f"{'beat':>4} {'w':>3} {'before':>7} {'target':>7} {'after':>7} "
              f"{'x':>6} {'wps':>5} -> {'wps':>5}  action")
        for r in rows:
            print(f"{r['id']:>4} {r['words']:>3} {r['before']:>7.2f} "
                  f"{r['target']:>7.2f} {r.get('after', 0):>7.2f} "
                  f"{r['ratio']:>6.2f} {r['wps_before']:>5.2f} -> "
                  f"{r['wps_after']:>5.2f}  {r['action']}")
        changed = sum(1 for r in rows if r["action"] not in ("ok",))
        print(f"\n{len(rows)} beat(s) processed, {changed} retimed"
              f"{' (dry run — nothing written)' if args.dry_run else ''}")
        if not args.dry_run:
            save_beats(args.beats, beats, meta)
        return 0

    if args.cmd == "marks":
        beats, meta = load_beats(args.beats)
        pdir = os.path.dirname(os.path.abspath(args.beats))
        adir = args.audio_dir or os.path.join(pdir, "audio")
        for b in beats:
            cand = os.path.join(adir, f"beat{b.id:02d}.mp3")
            if os.path.exists(cand):
                b.audio = os.path.relpath(cand, pdir)
                b.actual = probe_duration(cand) or b.actual
        marks = build_marks(beats, meta.get("project",
                                            os.path.basename(pdir)))
        outdir = args.out or pdir
        j, c, e = write_marks(marks, outdir)
        bad = [r for r in marks["beats"] if not r["ok_seconds"]]
        print(f"total {marks['total_duration']}s  "
              f"median {marks['median_duration']}s  "
              f"{len(marks['beats'])} beats")
        print(f"measured from audio: {marks['measured']}")
        if bad:
            print(f"{len(bad)} beat(s) outside {SEC_MIN}-{SEC_MAX}s: "
                  + ", ".join(str(r["id"]) for r in bad[:20]))
        print(f"  {j}\n  {c}\n  {e}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
