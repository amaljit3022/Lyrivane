from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from schemas.project import CanonicalTimeline


class RendererAdapter(ABC):
    """
    Abstract Renderer Adapter Contract.
    All rendering engines (Fast Karaoke, Creative Remotion, Cinematic Blender)
    must implement this common plugin interface.
    """

    @abstractmethod
    def list_templates(self) -> List[Dict[str, Any]]:
        """Return available engine templates and manifest specifications."""
        raise NotImplementedError

    @abstractmethod
    def validate_project(
        self,
        timeline: CanonicalTimeline,
        template_id: str,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate timeline and user settings against template requirements."""
        raise NotImplementedError

    @abstractmethod
    def create_preview(
        self,
        timeline: CanonicalTimeline,
        template_id: str,
        settings: Dict[str, Any],
        output_path: Path,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Path:
        """Create interactive browser-compatible preview asset or draft snippet."""
        raise NotImplementedError

    @abstractmethod
    def render(
        self,
        timeline: CanonicalTimeline,
        template_id: str,
        settings: Dict[str, Any],
        output_path: Path,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Path:
        """Render high-resolution final video with audio multiplexing."""
        raise NotImplementedError

    @abstractmethod
    def cancel(self, job_id: str) -> None:
        """Cancel an active render job."""
        raise NotImplementedError
