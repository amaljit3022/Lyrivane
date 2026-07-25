from schemas.project import AudioMetadata, CanonicalTimeline
from renderers.karaoke_renderer import KaraokeRendererAdapter
from renderers.remotion_renderer import RemotionRendererAdapter
from services.template_service import TemplateService


def test_manifest_catalog_contains_only_real_remotion_templates():
    templates = TemplateService.list_templates(renderer="remotion")
    ids = {template["id"] for template in templates}
    assert {"neon-orbit", "paper-bloom", "signal-noir"}.issubset(ids)
    assert all(template["renderer"] == "remotion" for template in templates)


def test_renderers_reject_unsupported_aspect_ratio():
    timeline = CanonicalTimeline(
        project_id="contract-test",
        audio=AudioMetadata(original_file="song.mp3", duration_ms=1000),
        lines=[],
    )
    for renderer, template_id in [
        (KaraokeRendererAdapter(), "classic-two-line"),
        (RemotionRendererAdapter(), "neon-orbit"),
    ]:
        result = renderer.validate_project(timeline, template_id, {"aspect_ratio": "2:1"})
        assert result["status"] == "invalid"
