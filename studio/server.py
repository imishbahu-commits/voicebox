#!/usr/bin/env python3
"""Voicebox Studio — review beat-based video projects in a browser.

Zero dependencies (stdlib only). Serves:

  /                       videos-only studio: every rendered MP4, playable
  /beats                  beat inspector (storyboard + per-beat voiceover)
  /api/videos             every rendered video across all projects
  /api/projects           project list + progress stats
  /api/beats/<project>    beats merged with their measured beat marks
  /media/<project>/...    audio clips and generated images

Run:
    python3 studio/server.py [--port 8000]

The preview player is the point: it plays each beat's narration audio while
showing that beat's visual, advancing on the measured beat marks — so you can
watch the cut before anything is rendered.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PROJECTS = os.path.join(REPO, "projects")

WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’-]*")
WORD_MIN, WORD_MAX = 12, 16
SEC_MIN, SEC_MAX = 2.0, 6.0

MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".mp3": "audio/mpeg",
    ".mp4": "video/mp4",
    ".m4a": "audio/mp4",
    ".webm": "video/webm",
    ".wav": "audio/wav",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


def wc(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def read_json(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def list_projects() -> list[dict]:
    out = []
    if not os.path.isdir(PROJECTS):
        return out
    for name in sorted(os.listdir(PROJECTS)):
        pdir = os.path.join(PROJECTS, name)
        beats_file = os.path.join(pdir, "beats.json")
        if not os.path.isfile(beats_file):
            continue
        data = read_json(beats_file) or {}
        beats = data.get("beats", [])

        audio_dir = os.path.join(pdir, "audio")
        img_dir = os.path.join(pdir, "images")
        audio = sorted(f for f in os.listdir(audio_dir)
                       if f.endswith(".mp3")) if os.path.isdir(audio_dir) else []
        images = sorted(f for f in os.listdir(img_dir)
                        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
                        ) if os.path.isdir(img_dir) else []

        marks = read_json(os.path.join(pdir, "beat_marks.json")) or {}
        mark_rows = marks.get("beats", [])

        words = [wc(b.get("narration") or b.get("spoken", "")) for b in beats]
        durs = [r.get("duration") for r in mark_rows if r.get("duration")]
        if not durs:
            durs = [b.get("duration") for b in beats if b.get("duration")]

        out.append({
            "name": name,
            "topic": data.get("topic", name),
            "format": data.get("format", ""),
            "status": data.get("status", ""),
            "source": data.get("source", ""),
            "beats": len(beats),
            "words_total": sum(words),
            "words_min": min(words) if words else 0,
            "words_max": max(words) if words else 0,
            "in_word_range": sum(1 for w in words if WORD_MIN <= w <= WORD_MAX),
            "audio_count": len(audio),
            "image_count": len(images),
            "measured": bool(marks.get("measured")),
            "total_duration": round(sum(durs), 2) if durs else 0,
            "median_duration": round(_median(durs), 2) if durs else 0,
            "outside_window": sum(1 for d in durs
                                  if d and not (SEC_MIN <= d <= SEC_MAX)),
            "renders": list_renders(pdir, name),
        })
    return out


def list_renders(pdir: str, name: str) -> list[dict]:
    """Rendered MP4s in <project>/video/, richest cut first.

    Each render writes a <name>.json sidecar next to the MP4, so the studio
    can report a real duration and beat range even though video/ is
    gitignored and the MP4 itself is never committed.
    """
    vdir = os.path.join(pdir, "video")
    if not os.path.isdir(vdir):
        return []
    out = []
    for fn in sorted(os.listdir(vdir)):
        if not fn.lower().endswith((".mp4", ".webm", ".m4v")):
            continue
        stem = os.path.splitext(fn)[0]
        meta = read_json(os.path.join(vdir, stem + ".json")) or {}
        contact = stem + "_contact.jpg"
        out.append({
            "file": fn,
            "url": meta.get("url") or f"media/{name}/video/{fn}",
            "bytes": meta.get("bytes") or os.path.getsize(os.path.join(vdir, fn)),
            "duration": meta.get("duration"),
            "beats": meta.get("beats") or [],
            "beat_count": meta.get("beat_count"),
            "part": meta.get("part"),
            "width": meta.get("width"),
            "height": meta.get("height"),
            "fps": meta.get("fps"),
            "rendered_at": meta.get("rendered_at"),
            "project": name,
            "contact": (f"media/{name}/video/{contact}"
                        if os.path.isfile(os.path.join(vdir, contact)) else None),
        })
    # longest cut first, then newest
    out.sort(key=lambda e: (-len(e["beats"]), -(e["duration"] or 0), e["file"]))
    return out


def list_all_videos() -> list[dict]:
    """Every rendered video across every project, for the videos-only studio."""
    out = []
    for p in list_projects():
        for v in p.get("renders", []):
            row = dict(v)
            row["topic"] = p.get("topic", p["name"])
            out.append(row)
    return out


def _median(xs):
    if not xs:
        return 0.0
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def project_beats(name: str) -> dict:
    pdir = os.path.join(PROJECTS, name)
    data = read_json(os.path.join(pdir, "beats.json")) or {}
    beats = data.get("beats", [])
    marks = read_json(os.path.join(pdir, "beat_marks.json")) or {}
    mark_by_id = {r.get("id"): r for r in marks.get("beats", [])}

    audio_dir = os.path.join(pdir, "audio")
    img_dir = os.path.join(pdir, "images")
    have_audio = set(os.listdir(audio_dir)) if os.path.isdir(audio_dir) else set()
    have_img = set(os.listdir(img_dir)) if os.path.isdir(img_dir) else set()

    rows = []
    for b in beats:
        bid = b.get("id")
        narration = b.get("narration") or b.get("spoken", "")
        mk = mark_by_id.get(bid, {})
        audio_file = f"beat{bid:02d}.mp3"
        img_file = f"beat{bid:02d}.png"
        rows.append({
            "id": bid,
            "part": b.get("part"),
            "narration": narration,
            "visual": b.get("visual") or b.get("scene", ""),
            "label": b.get("label", ""),
            "transition": b.get("transition", "cut"),
            "words": wc(narration),
            "start": mk.get("start"),
            "end": mk.get("end"),
            "duration": mk.get("duration") or b.get("duration"),
            "frame_in": mk.get("frame_in"),
            "frame_out": mk.get("frame_out"),
            "audio": (f"media/{name}/audio/{audio_file}"
                      if audio_file in have_audio else None),
            "image": (f"media/{name}/images/{img_file}"
                      if img_file in have_img else None),
        })
    return {
        "project": name,
        "topic": data.get("topic", name),
        "renders": list_renders(pdir, name),
        "fps": data.get("fps", 60),
        "total_duration": marks.get("total_duration"),
        "measured": marks.get("measured", False),
        "beats": rows,
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    def _json(self, obj, code=200, head_only=False):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", MIME[".json"])
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def _fail(self, msg, code=404, head_only=False):
        self._json({"error": msg}, code, head_only)

    def do_GET(self):
        self._route(head_only=False)

    def do_HEAD(self):
        # browsers issue HEAD probes before playing media
        self._route(head_only=True)

    def _route(self, head_only: bool):
        path = self.path.split("?", 1)[0]

        if path == "/" or path == "/index.html" or path in ("/videos", "/videos.html"):
            return self._serve_file(os.path.join(HERE, "videos.html"), ".html",
                                    head_only)
        if path == "/beats" or path == "/beats.html":
            return self._serve_file(os.path.join(HERE, "index.html"), ".html",
                                    head_only)
        if path == "/api/videos":
            return self._json({"videos": list_all_videos()}, 200, head_only)
        if path == "/api/projects":
            return self._json({"projects": list_projects()}, 200, head_only)
        if path.startswith("/api/beats/"):
            name = os.path.basename(path[len("/api/beats/"):])
            if not re.fullmatch(r"[A-Za-z0-9._-]+", name or ""):
                return self._fail("bad project name", 400, head_only)
            if not os.path.isfile(os.path.join(PROJECTS, name, "beats.json")):
                return self._fail("no such project", 404, head_only)
            return self._json(project_beats(name), 200, head_only)
        if path.startswith("/media/"):
            rel = path[len("/media/"):]
            if ".." in rel or rel.startswith("/"):
                return self._fail("bad path", 400, head_only)
            full = os.path.join(PROJECTS, rel)
            if not os.path.isfile(full):
                return self._fail("not found", 404, head_only)
            return self._serve_file(full, os.path.splitext(full)[1].lower(),
                                    head_only)
        if path.startswith("/projects/"):
            rel = path[len("/projects/"):]
            if ".." in rel:
                return self._fail("bad path", 400, head_only)
            full = os.path.join(REPO, "projects", rel)
            if os.path.isfile(full):
                return self._serve_file(full, os.path.splitext(full)[1].lower(),
                                        head_only)
            return self._fail("not found", 404, head_only)
        return self._fail("not found", 404, head_only)

    def _serve_file(self, full: str, ext: str, head_only: bool = False):
        """Serve a file with HTTP Range support so audio can seek."""
        try:
            size = os.path.getsize(full)
            fh = open(full, "rb")
        except OSError:
            return self._fail("not found", 404, head_only)

        start, end, code = 0, size - 1, 200
        rng = self.headers.get("Range")
        if rng and rng.startswith("bytes="):
            spec = rng[6:].split(",")[0].strip()
            if "-" in spec:
                a, b = spec.split("-", 1)
                try:
                    if a:
                        start = int(a)
                    if b:
                        end = min(int(b), size - 1)
                except ValueError:
                    start, end = 0, size - 1
            if start >= size or start > end:
                fh.close()
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return
            code = 206

        length = end - start + 1
        self.send_response(code)
        self.send_header("Content-Type", MIME.get(ext, "application/octet-stream"))
        self.send_header("Content-Length", str(length))
        self.send_header("Accept-Ranges", "bytes")
        if code == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if head_only:
            fh.close()
            return
        try:
            fh.seek(start)
            left = length
            while left > 0:
                chunk = fh.read(min(65536, left))
                if not chunk:
                    break
                self.wfile.write(chunk)
                left -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            fh.close()


def main():
    ap = argparse.ArgumentParser(description="Voicebox Studio server")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    projects = list_projects()
    print(f"Voicebox Studio on http://{args.host}:{args.port}")
    for p in projects:
        print(f"  {p['name']:<24} {p['beats']:>4} beats  "
              f"audio {p['audio_count']:>3}/{p['beats']:<4} "
              f"images {p['image_count']:>3}/{p['beats']:<4} "
              f"{p['total_duration']:>6.1f}s")
    if not projects:
        print("  (no projects found in projects/)")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
