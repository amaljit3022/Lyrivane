import pytest
from schemas.project import AudioMetadata, SectionTiming, LineTiming, WordTiming, SectionType
from alignment.forced_aligner import ForcedAligner


def test_forced_aligner_timestamps():
    audio = AudioMetadata(
        original_file="song.mp3",
        duration_ms=180000,
        sample_rate=44100,
        channels=2
    )

    sections = [SectionTiming(type=SectionType.VERSE, display_label="Verse 1", start_ms=0, end_ms=180000)]

    words = [
        WordTiming(display_text="Golden", alignment_text="golden", start_ms=0, end_ms=0),
        WordTiming(display_text="stars", alignment_text="stars", start_ms=0, end_ms=0)
    ]

    lines = [
        LineTiming(display_text="Golden stars", alignment_text="golden stars", start_ms=0, end_ms=0, words=words)
    ]

    aligned_lines = ForcedAligner.align_lyrics(audio, sections, lines)

    assert len(aligned_lines) == 1
    line = aligned_lines[0]
    assert line.start_ms > 0
    assert line.end_ms > line.start_ms
    assert len(line.words) == 2
    assert line.words[0].start_ms == line.start_ms
    assert line.words[1].end_ms <= line.end_ms
