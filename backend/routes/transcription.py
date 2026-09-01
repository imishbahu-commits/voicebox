"""Transcription endpoints."""

import asyncio
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from .. import models
from ..services import transcribe
from ..services.task_queue import create_background_task
from ..utils.media import extract_audio_from_video, is_video_file
from ..utils.tasks import get_task_manager

router = APIRouter()

UPLOAD_CHUNK_SIZE = 8 * 1024 * 1024  # 8MB, keeps large video uploads efficient
MAX_UPLOAD_SIZE = 250 * 1024 * 1024  # 250MB

ALLOWED_AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".webm", ".opus"}


@router.post("/transcribe", response_model=models.TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str | None = Form(None),
    model: str | None = Form(None),
):
    """Transcribe an audio file or the audio track from a reference video."""
    uploaded_ext = Path(file.filename or "").suffix.lower()
    is_video = is_video_file(file.filename, file.content_type)
    file_suffix = uploaded_ext if uploaded_ext in ALLOWED_AUDIO_EXTS or is_video else ".wav"

    if file.size is not None and file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {MAX_UPLOAD_SIZE // (1024 * 1024)} MB)",
        )

    with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=False) as tmp:
        total_size = 0
        while chunk := await file.read(UPLOAD_CHUNK_SIZE):
            total_size += len(chunk)
            if total_size > MAX_UPLOAD_SIZE:
                Path(tmp.name).unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large (max {MAX_UPLOAD_SIZE // (1024 * 1024)} MB)",
                )
            tmp.write(chunk)
        tmp_path = tmp.name

    extracted_path: str | None = None
    stt_path = tmp_path
    try:
        from ..utils.audio import load_audio, save_audio
        from ..backends import WHISPER_HF_REPOS

        if is_video:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_tmp:
                extracted_path = audio_tmp.name
            try:
                await asyncio.to_thread(extract_audio_from_video, tmp_path, extracted_path)
            except RuntimeError as e:
                raise HTTPException(status_code=503, detail=str(e)) from e
            stt_path = extracted_path

        audio, sr = await asyncio.to_thread(load_audio, stt_path)
        duration = len(audio) / sr

        # The STT backend (mlx_audio.stt -> miniaudio) only decodes
        # WAV/FLAC/MP3/Vorbis, so browser recordings uploaded as WebM/Opus
        # fail with "unsupported file format" (issue: web-mode dictation).
        # librosa already decoded the file above (it falls back to
        # audioread/ffmpeg for exotic containers), so re-encode that PCM to a
        # temp WAV and hand *that* to Whisper. WAV inputs pass through
        # unchanged.
        if file_suffix != ".wav" and not is_video:
            stt_path = f"{tmp_path}.stt.wav"
            await asyncio.to_thread(save_audio, audio, stt_path, sr)

        whisper_model = transcribe.get_whisper_model()
        model_size = model if model else whisper_model.model_size

        valid_sizes = list(WHISPER_HF_REPOS.keys())
        if model_size not in valid_sizes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model size '{model_size}'. Must be one of: {', '.join(valid_sizes)}",
            )

        already_loaded = whisper_model.is_loaded() and whisper_model.model_size == model_size
        if not already_loaded and not whisper_model._is_model_cached(model_size):
            progress_model_name = f"whisper-{model_size}"
            task_manager = get_task_manager()

            async def download_whisper_background():
                try:
                    await whisper_model.load_model_async(model_size)
                    task_manager.complete_download(progress_model_name)
                except Exception as e:
                    task_manager.error_download(progress_model_name, str(e))

            task_manager.start_download(progress_model_name)
            create_background_task(download_whisper_background())

            raise HTTPException(
                status_code=202,
                detail={
                    "message": f"Whisper model {model_size} is being downloaded. Please wait and try again.",
                    "model_name": progress_model_name,
                    "downloading": True,
                },
            )

        text = await whisper_model.transcribe(stt_path, language, model_size)

        return models.TranscriptionResponse(
            text=text,
            duration=duration,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)
        if stt_path != tmp_path and stt_path != extracted_path:
            Path(stt_path).unlink(missing_ok=True)
        if extracted_path:
            Path(extracted_path).unlink(missing_ok=True)
