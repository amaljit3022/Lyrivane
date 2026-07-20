import pytest
from schemas.project import (
    CanonicalTimeline,
    AudioMetadata,
    SectionTiming,
    LineTiming,
    WordTiming,
    SectionType
)


def test_canonical_timeline_serialization():
    audio = AudioMetadata(
        original_file="song.mp3",
        duration_ms=120000,
        sample_rate=44100,
        channels=2
    )

    words = [
        WordTiming(display_text="Hello", alignment_text="hello", start_ms=1000, end_ms=1500)
    ]

    lines = [
        LineTiming(display_text="Hello World", alignment_text="hello world", start_ms=1000, end_ms=2500, words=words)
    ]

    sections = [
        SectionTiming(type=SectionType.VERSE, display_label="Verse 1", start_ms=0, end_ms=120000)
    ]

    timeline = CanonicalTimeline(
        project_id="test-id",
        audio=audio,
        sections=sections,
        lines=lines
    )

    dumped = timeline.model_dump()
    assert dumped["schema_version"] == "1.0"
    assert dumped["project_id"] == "test-id"
    assert len(dumped["lines"]) == 1
    assert dumped["lines"][0]["words"][0]["display_text"] == "Hello"
