"""Integration coverage for reference-video uploads."""

import io
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parents[2]))

from backend import models  # noqa: E402
from backend.routes import profiles as profile_routes  # noqa: E402
from backend.utils.media import is_video_file  # noqa: E402


def test_audio_webm_is_not_misclassified_as_video():
    assert not is_video_file("recording.webm", "audio/webm")
    assert is_video_file("reference.webm", "video/webm")


@pytest.fixture
def video_upload_app(monkeypatch):
    """Mount the real profile route while replacing persistence and FFmpeg."""
    app = FastAPI()
    app.include_router(profile_routes.router)
    app.dependency_overrides[profile_routes.get_db] = lambda: None

    extracted = {}

    def fake_extract(video_path: str, audio_path: str) -> None:
        extracted["video_path"] = video_path
        extracted["video_bytes"] = Path(video_path).read_bytes()
        Path(audio_path).write_bytes(b"fake wav output")

    async def fake_add_sample(profile_id: str, audio_path: str, reference_text: str, db):
        extracted["audio_path"] = audio_path
        extracted["audio_exists_during_persistence"] = Path(audio_path).is_file()
        return models.ProfileSampleResponse(
            id="sample-id",
            profile_id=profile_id,
            audio_path="profiles/profile-id/sample-id.wav",
            reference_text=reference_text,
        )

    monkeypatch.setattr(profile_routes, "extract_audio_from_video", fake_extract)
    monkeypatch.setattr(profile_routes.profiles, "add_profile_sample", fake_add_sample)
    return app, extracted


def test_reference_video_is_streamed_extracted_and_cleaned(video_upload_app):
    app, extracted = video_upload_app
    client = TestClient(app)
    video_bytes = b"video bytes" * 1024

    response = client.post(
        "/profiles/profile-id/samples",
        files={"file": ("reference.mp4", io.BytesIO(video_bytes), "video/mp4")},
        data={"reference_text": "A short spoken reference."},
    )

    assert response.status_code == 200, response.text
    assert response.json()["profile_id"] == "profile-id"
    assert extracted["video_bytes"] == video_bytes
    assert Path(extracted["video_path"]).suffix == ".mp4"
    assert Path(extracted["audio_path"]).suffix == ".wav"
    assert extracted["audio_exists_during_persistence"]
    assert not Path(extracted["video_path"]).exists()
    assert not Path(extracted["audio_path"]).exists()
