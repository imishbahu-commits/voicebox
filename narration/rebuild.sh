#!/usr/bin/env bash
# rebuild.sh — restore everything the sandbox can wipe, then re-cut the videos.
#
# Two things live outside git and therefore vanish on an environment reset:
#   .tools/venv   Pillow + ffmpeg   (gitignored)
#   projects/*/video/              (gitignored build output)
#
# Everything else — beats, audio, images, beat marks — is committed, so this
# script can rebuild the whole picture from the repo alone.
#
#   ./narration/rebuild.sh                      # all projects, all ready parts
#   ./narration/rebuild.sh foodcode-tomato      # one project
#   ./narration/rebuild.sh foodcode-tomato 1    # one part
#
set -euo pipefail

cd "$(dirname "$0")/.."
REPO="$PWD"
PROJECT="${1:-}"
PART="${2:-}"

# ---------------------------------------------------------------- 1. tooling
VENV="$REPO/.tools/venv"
PYTHON="$VENV/bin/python"

if [ ! -x "$PYTHON" ]; then
  echo ">> building .tools/venv (Pillow + ffmpeg)"
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q --disable-pip-version-check Pillow imageio-ffmpeg
fi

if ! "$PYTHON" -c "import PIL, imageio_ffmpeg" 2>/dev/null; then
  echo ">> repairing .tools/venv"
  rm -rf "$VENV"
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q --disable-pip-version-check Pillow imageio-ffmpeg
fi

FFMPEG="$("$PYTHON" -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")"
export VOICEBOX_FFMPEG="$FFMPEG"
echo ">> ffmpeg  $FFMPEG"
echo ">> pillow  $("$PYTHON" -c 'import PIL; print(PIL.__version__)')"

# --------------------------------------------------------------- 2. targets
if [ -n "$PROJECT" ]; then
  PROJECTS=("$PROJECT")
else
  mapfile -t PROJECTS < <(cd projects && ls -d */ 2>/dev/null | tr -d '/' || true)
fi

if [ "${#PROJECTS[@]}" -eq 0 ]; then
  echo "no projects in projects/"
  exit 0
fi

# --------------------------------------------------------------- 3. render
for P in "${PROJECTS[@]}"; do
  DIR="$REPO/projects/$P"
  [ -f "$DIR/beats.json" ] || continue

  if [ -n "$PART" ]; then
    PARTS=("$PART")
  else
    # Only render parts whose beats are complete: a part with a missing clip
    # or image would silently produce a short video.
    mapfile -t PARTS < <("$PYTHON" - "$DIR" <<'PY'
import json, os, sys
d = sys.argv[1]
data = json.load(open(os.path.join(d, "beats.json")))
beats = data["beats"] if isinstance(data, dict) else data
by_part = {}
for b in beats:
    by_part.setdefault(b.get("part") or 1, []).append(b["id"])
for part in sorted(by_part):
    ids = by_part[part]
    ok = all(os.path.exists(os.path.join(d, "audio", f"beat{i:02d}.mp3")) and
             os.path.exists(os.path.join(d, "images", f"beat{i:02d}.png"))
             for i in ids)
    if ok:
        print(part)
PY
)
  fi

  [ "${#PARTS[@]}" -eq 0 ] && { echo "== $P: no complete parts yet"; continue; }

  for N in "${PARTS[@]}"; do
    echo "== $P part $N"
    "$PYTHON" narration/render_video.py "projects/$P" --part "$N"
  done
done

echo
echo ">> done. Start the studio with:"
echo "   python3 studio/server.py --host 0.0.0.0 --port 8000"
