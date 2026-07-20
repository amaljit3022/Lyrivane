import pytest
from schemas.project import CanonicalTimeline, AudioMetadata, LineTiming, WordTiming
from alignment.quality_validator import QualityValidator


def test_quality_validator_clean():
    audio = AudioMetadata(original_file="song.mp3", duration_ms=60000)
    words = [WordTiming(display_text="Test", alignment_text="test", start_ms=5000, end_ms=5500)]
    lines = [LineTiming(display_text="Test line", alignment_text="test line", start_ms=5000, end_ms=7000, words=words)]

    timeline = CanonicalTimeline(project_id="test", audio=audio, lines=lines)
    diagnostics, confidence = QualityValidator.validate_timeline(timeline)

    assert confidence == 1.0
    assert len([d for d in diagnostics if d.severity == "error"]) == 0


def test_quality_validator_out_of_bounds():
    audio = AudioMetadata(original_file="song.mp3", duration_ms=10000)
    words = [WordTiming(display_text="Late", alignment_text="late", start_ms=12000, end_ms=15000)]
    lines = [LineTiming(display_text="Late line", alignment_text="late line", start_ms=12000, end_ms=15000, words=words)]

    timeline = CanonicalTimeline(project_id="test", audio=audio, lines=lines)
    diagnostics, confidence = QualityValidator.validate_timeline(timeline)

    assert confidence == 0.0
    assert any(d.code == "OUT_OF_BOUNDS_TIMING" for d in diagnostics)
