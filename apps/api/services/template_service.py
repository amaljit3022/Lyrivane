import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import os

TEMPLATES_DIR = Path(os.getenv("TEMPLATES_DIR", "/app/templates")).resolve()
if not TEMPLATES_DIR.exists():
    TEMPLATES_DIR = (Path(__file__).parent.parent.parent / "templates").resolve()

class TemplateService:
    """
    Service for scanning, loading, and validating template manifests.
    """

    @classmethod
    def list_templates(cls, renderer: Optional[str] = None) -> List[Dict[str, Any]]:
        templates = []
        if not TEMPLATES_DIR.exists():
            return templates

        # Iterate over renderer subdirectories (e.g. remotion, karaoke, blender)
        for renderer_dir in TEMPLATES_DIR.iterdir():
            if not renderer_dir.is_dir():
                continue
            if renderer and renderer_dir.name != renderer:
                continue

            for t_dir in renderer_dir.iterdir():
                manifest_file = t_dir / "manifest.json"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
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
