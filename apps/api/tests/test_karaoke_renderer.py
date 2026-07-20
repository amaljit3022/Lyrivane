import pytest
from pathlib import Path
from schemas.project import CanonicalTimeline, AudioMetadata, LineTiming, WordTiming
from renderers.karaoke_renderer import KaraokeRendererAdapter


def test_karaoke_ass_subtitle_generation(tmp_path):
    audio = AudioMetadata(original_file="song.mp3", duration_ms=60000)
    words = [
        WordTiming(display_text="Golden", alignment_text="golden", start_ms=10000, end_ms=10500),
        WordTiming(display_text="stars", alignment_text="stars", start_ms=10550, end_ms=11000)
    ]
    lines = [
        LineTiming(display_text="Golden stars", alignment_text="golden stars", start_ms=10000, end_ms=12000, words=words)
    ]

    timeline = CanonicalTimeline(project_id="test-render", audio=audio, lines=lines)
    renderer = KaraokeRendererAdapter()

    ass_path = tmp_path / "test.ass"
    renderer.generate_ass_subtitles(timeline, renderer.TEMPLATES[0], ass_path)

    assert ass_path.exists()
    content = ass_path.read_text(encoding="utf-8")
    assert "[Script Info]" in content
    assert "Style: Karaoke" in content
    assert "\\k" in content
    assert "Golden" in content
