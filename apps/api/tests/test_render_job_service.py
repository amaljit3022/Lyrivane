import pytest
from services.render_job_service import RenderJobService


def test_render_job_lifecycle():
    job = RenderJobService.create_job("job-123", "proj-456", "karaoke", "classic-two-line")
    assert job.status == "queued"
    assert job.progress_percentage == 0

    updated = RenderJobService.update_progress("job-123", 50, "Rendering frames...", "processing")
    assert updated is not None
    assert updated.progress_percentage == 50
    assert updated.status == "processing"

    fetched = RenderJobService.get_job("job-123")
    assert fetched.progress_percentage == 50
