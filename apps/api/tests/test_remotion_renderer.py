import pytest
from pathlib import Path
from schemas.project import CanonicalTimeline, AudioMetadata, LineTiming, WordTiming
from renderers.remotion_renderer import RemotionRendererAdapter


def test_remotion_props_generation(tmp_path):
    audio = AudioMetadata(original_file="song.mp3", duration_ms=60000)
    words = [WordTiming(display_text="Remotion", alignment_text="remotion", start_ms=1000, end_ms=2000)]
    lines = [LineTiming(display_text="Remotion Text", alignment_text="remotion text", start_ms=1000, end_ms=3000, words=words)]

    timeline = CanonicalTimeline(project_id="test-remotion", audio=audio, lines=lines)
    renderer = RemotionRendererAdapter()

    preview_json = tmp_path / "remotion_props.json"
    result_path = renderer.create_preview(timeline, "cinematic-minimal", {"fps": 30}, preview_json)

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "cinematic-minimal" in content
    assert "Remotion Text" in content
