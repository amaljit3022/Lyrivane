import pytest
from pathlib import Path
from services.audio_service import AudioService
from schemas.project import AudioMetadata


def test_probe_audio_fallback(tmp_path):
    dummy_file = tmp_path / "test_song.mp3"
    dummy_file.write_text("fake audio binary data")

    meta = AudioService.probe_audio(dummy_file)

    assert isinstance(meta, AudioMetadata)
    assert meta.title == "Test Song"
    assert meta.artist == "Unknown Artist"
    assert meta.duration_ms > 0
