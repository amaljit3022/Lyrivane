import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import os

TEMPLATES_DIR = Path(os.getenv("TEMPLATES_DIR", "/app/templates")).resolve()
if not TEMPLATES_DIR.exists():
    # template_service.py -> services -> api -> apps -> project root
    TEMPLATES_DIR = (Path(__file__).resolve().parents[3] / "templates").resolve()

class TemplateService:
    """
    Service for scanning, loading, and validating template manifests.
    """

    @classmethod
    def list_templates(cls, renderer: Optional[str] = None) -> List[Dict[str, Any]]:
        templates = []
        if not TEMPLATES_DIR.exists():
            return templates

        seen_ids = set()
        # Manifests are the catalog contract. Sort paths so UI order is stable
        # across Windows, Linux containers, and packaged builds.
        for renderer_dir in sorted(TEMPLATES_DIR.iterdir(), key=lambda path: path.name.lower()):
            if not renderer_dir.is_dir():
                continue
            if renderer and renderer_dir.name != renderer:
                continue

            for t_dir in sorted(renderer_dir.iterdir(), key=lambda path: path.name.lower()):
                manifest_file = t_dir / "manifest.json"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                        if not isinstance(manifest, dict) or not manifest.get("id"):
                            raise ValueError("manifest must be an object with an id")
                        if manifest.get("id") in seen_ids:
                            raise ValueError(f"duplicate template id: {manifest['id']}")
                        manifest.setdefault("renderer", renderer_dir.name)
                        manifest.setdefault("supported_aspect_ratios", ["16:9", "9:16", "1:1"])
                        manifest.setdefault("timing_support", ["line"])
                        seen_ids.add(manifest["id"])
                        templates.append(manifest)
                    except Exception as e:
                        print(f"Error loading template manifest {manifest_file}: {e}")

        return templates

    @classmethod
    def get_template(cls, template_id: str) -> Optional[Dict[str, Any]]:
        for t in cls.list_templates():
            if t.get("id") == template_id:
                return t
        return None
