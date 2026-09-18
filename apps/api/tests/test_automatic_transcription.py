import asyncio
import json

import pytest

from schemas.project import AudioMetadata
from services.audio_service import AudioService


def test_long_whisper_segments_are_chunked_into_readable_cards():
    pytest.importorskip("whisper_timestamped")
    from worker import alignment_tasks

    words = [
        {"text": token, "start": index * 0.4, "end": index * 0.4 + 0.3, "confidence": 0.8}
        for index, token in enumerate("through the jungle climb do be do be dumb dumb do be".split())
    ]

    lines = alignment_tasks._whisper_lines({"segments": [{"text": "", "words": words}]})

    assert len(lines) == 2
    assert all(len(line["words"]) <= 8 for line in lines)
    assert lines[0]["display_text"] == "through the jungle climb do be do be"
    assert lines[1]["display_text"] == "dumb dumb do be"

def test_blank_lyrics_are_transcribed_into_the_canonical_timeline(tmp_path, monkeypatch):
    pytest.importorskip("whisper_timestamped")
    from worker import alignment_tasks

    project_id = "auto-lyrics-test"
    project_dir = tmp_path / project_id
    audio_path = project_dir / "audio" / "working" / "song.wav"
    audio_path.parent.mkdir(parents=True)
    audio_path.write_bytes(b"test audio")

    monkeypatch.setattr(alignment_tasks, "PROJECTS_DIR", tmp_path)
    monkeypatch.setattr(alignment_tasks, "get_whisper_model", lambda: object())
    monkeypatch.setattr(
        alignment_tasks,
        "_transcribe",
        lambda model, path: {
            "segments": [
                {
                    "text": "Hello world",
                    "words": [
                        {"text": "Hello", "start": 0.1, "end": 0.6, "confidence": 0.9},
                        {"text": "world", "start": 0.65, "end": 1.1, "confidence": 0.85},
                    ],
                }
            ]
        },
    )
    monkeypatch.setattr(
        AudioService,
        "probe_audio",
        staticmethod(lambda path: AudioMetadata(original_file=str(path), duration_ms=2000)),
    )

    alignment_tasks.align_lyrics.run(project_id)

    timeline = json.loads((project_dir / "timeline.json").read_text(encoding="utf-8"))
    assert timeline["alignment_mode"] == "automatic_transcription"
    assert timeline["lines"][0]["display_text"] == "Hello world"
    assert timeline["lines"][0]["words"][0]["start_ms"] == 100


def test_blank_lyrics_endpoint_queues_transcription(tmp_path, monkeypatch):
    pytest.importorskip("celery")
    import main as api

    project_id = "blank-lyrics-endpoint"
    monkeypatch.setattr(api, "PROJECTS_DIR", tmp_path)
    api.projects_db.clear()
    api.projects_db[project_id] = {
        "project_id": project_id,
        "title": "Blank Lyrics",
        "artist": "Test",
        "language": "en",
        "status": "audio_uploaded",
        "created_at": "2026-07-26T00:00:00Z",
        "has_audio": True,
        "has_lyrics": False,
        "audio_meta": AudioMetadata(original_file="song.wav", duration_ms=2000),
        "sections": [],
        "lines": [],
        "canonical_timeline": None,
    }

    response = asyncio.run(api.upload_lyrics(project_id, raw_text="", file=None))

    assert response.status == "transcription_pending"
    assert response.has_lyrics is False
    assert (tmp_path / project_id / "lyrics" / "source" / "raw_lyrics.txt").read_text(encoding="utf-8") == ""