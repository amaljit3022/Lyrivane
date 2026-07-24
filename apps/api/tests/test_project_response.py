from schemas.project import AudioMetadata, LineTiming, ProjectResponse, WordTiming


def test_project_response_exposes_preview_inputs():
    line = LineTiming(
        display_text="Preview line",
        alignment_text="preview line",
        start_ms=1000,
        end_ms=2000,
        words=[WordTiming(display_text="Preview", alignment_text="preview", start_ms=1000, end_ms=1500)],
    )
    response = ProjectResponse(
        project_id="preview-test",
        title="Preview",
        artist="Test",
        language="en",
        status="synchronized",
        created_at="2026-07-24T00:00:00Z",
        has_audio=True,
        has_lyrics=True,
        audio_meta=AudioMetadata(original_file="song.wav", working_file="song.wav", duration_ms=2000),
        lines=[line],
    )
    assert response.audio_meta is not None
    assert response.audio_meta.duration_ms == 2000
    assert response.lines[0].display_text == "Preview line"
