"""Helpers for turning uploaded reference videos into TTS-ready audio."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

VIDEO_EXTENSIONS = frozenset({
    ".avi",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".webm",
    ".wmv",
})


def is_video_file(filename: str | None, content_type: str | None = None) -> bool:
    """Return whether an upload should be treated as a video container."""
    normalized_content_type = (content_type or "").lower()
    if normalized_content_type.startswith("audio/"):
        # MediaRecorder commonly produces audio/webm, which must stay on the
        # normal audio validation path rather than going through video input.
        return False
    if normalized_content_type.startswith("video/"):
        return True
    return Path(filename or "").suffix.lower() in VIDEO_EXTENSIONS


def _find_ffmpeg() -> str | None:
    """Find a system FFmpeg binary, then try the pip-provided fallback."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg

    # ``imageio-ffmpeg`` ships a self-contained binary on supported platforms.
    # Keep this import lazy so audio-only installations do not need the extra
    # package and the API can still start when FFmpeg is unavailable.
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError, OSError):
        return None


def extract_audio_from_video(
    video_path: str | Path,
    audio_path: str | Path,
    *,
    max_seconds: int = 30,
) -> None:
    """Extract the first short audio segment from a video for voice cloning.

    Reference voices only need a clean speech segment. Limiting extraction to
    ``max_seconds`` avoids decoding an entire long video and keeps uploads fast
    even when a user accidentally selects a full recording. The normal sample
    validator subsequently enforces the two-to-thirty-second requirement.

    The output is mono, 24 kHz, signed 16-bit PCM WAV, which is accepted by all
    of Voicebox's cloning engines.
    """
    ffmpeg = _find_ffmpeg()
    if not ffmpeg:
        raise RuntimeError(
            "Video uploads require FFmpeg. Install FFmpeg and make sure it is on PATH, "
            "or install the imageio-ffmpeg Python package."
        )

    source = str(video_path)
    destination = str(audio_path)
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-i",
        source,
        "-map",
        "0:a:0?",
        "-t",
        str(max_seconds),
        "-vn",
        "-sn",
        "-dn",
        "-ac",
        "1",
        "-ar",
        "24000",
        "-c:a",
        "pcm_s16le",
        "-y",
        destination,
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired as e:
        raise ValueError("Video audio extraction timed out after 180 seconds") from e
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "unknown FFmpeg error"
        raise ValueError(f"Could not extract an audio track from this video: {detail}")

    if not Path(destination).is_file() or Path(destination).stat().st_size == 0:
        raise ValueError("This video does not contain a usable audio track")
