import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from renderers.base_renderer import RendererAdapter
from schemas.project import CanonicalTimeline


logger = logging.getLogger(__name__)


class RemotionRendererAdapter(RendererAdapter):
    """
    Creative Remotion Rendering Engine Adapter.
    Uses React, TypeScript, and Remotion CLI / SSR bundler
    for fluid kinetic typography and animated video generation.
    """

    def list_templates(self) -> List[Dict[str, Any]]:
        from services.template_service import TemplateService
        return TemplateService.list_templates(renderer="remotion")

    def validate_project(
        self,
        timeline: CanonicalTimeline,
        template_id: str,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        templates = self.list_templates()
        valid_ids = [t.get("id") for t in templates]
        if template_id not in valid_ids:
            template_id = "aurora-pulse"
        template = next(t for t in templates if t.get("id") == template_id)
        aspect_ratio = settings.get("aspect_ratio", "16:9")
        if aspect_ratio not in template.get("supported_aspect_ratios", ["16:9", "9:16", "1:1"]):
            return {"status": "invalid", "message": f"Template {template_id} does not support {aspect_ratio}"}
        return {"status": "valid", "template_id": template_id}

    @staticmethod
    def prepare_remotion_props(timeline: CanonicalTimeline, template_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Convert canonical timeline to Remotion composition JSON props with Visual Intelligence."""
        from services.visual_intelligence import VisualIntelligenceService
        from services.audio_analysis_service import AudioAnalysisService

        audio_path = Path(timeline.audio.working_file or timeline.audio.original_file or "")
        audio_analysis = AudioAnalysisService.analyze_audio(audio_path, duration_ms=timeline.audio.duration_ms)

        aspect_ratio = settings.get("aspect_ratio", "16:9")
        resolution = settings.get("resolution", "1080p")
        visual_plan = VisualIntelligenceService.generate_visual_plan(
            timeline=timeline,
            style=template_id,
            aspect_ratio=aspect_ratio,
            motion_intensity=settings.get("motion_intensity", 0.5)
        )

        formatted_lines = []
        for line in timeline.lines:
            plan = visual_plan.line_plans.get(line.id)
            word_list = []
            
            for idx, w in enumerate(line.words):
                w_comp = plan.words[idx] if (plan and idx < len(plan.words)) else None
                
                word_data = {
                    "text": w.display_text,
                    "start_ms": w.start_ms,
                    "end_ms": w.end_ms,
                    "start_frame": int((w.start_ms / 1000.0) * settings.get("fps", 30)),
                    "end_frame": int((w.end_ms / 1000.0) * settings.get("fps", 30)),
                    "importance": w_comp.importance if w_comp else 0.5,
                    "enter_preset": w_comp.enter_preset if w_comp else "fade-up",
                    "active_preset": w_comp.active_preset if w_comp else None,
                    "exit_preset": w_comp.exit_preset if w_comp else "fade",
                    "style": w_comp.style.model_dump() if w_comp else {}
                }
                word_list.append(word_data)

            line_data = {
                "id": line.id,
                "display_text": line.display_text,
                "start_ms": line.start_ms,
                "end_ms": line.end_ms,
                "start_frame": int((line.start_ms / 1000.0) * settings.get("fps", 30)),
                "end_frame": int((line.end_ms / 1000.0) * settings.get("fps", 30)),
                "layout_type": plan.layout.type if plan else "center",
                "words": word_list
            }
            formatted_lines.append(line_data)

        # Prefer normalized WAV so Remotion does not need to decode an upload container.
        audio_file = timeline.audio.working_file or timeline.audio.original_file
        return {
            "title": timeline.title,
            "artist": timeline.artist,
            # Remotion components use camelCase props. Keep the snake_case key as
            # well for older preview consumers, but always provide the render key.
            "audioUrl": audio_file,
            "audio_url": audio_file,
            "duration_in_frames": int((timeline.audio.duration_ms / 1000.0) * settings.get("fps", 30)),
            "fps": settings.get("fps", 30),
            "resolution": resolution,
            "codec": settings.get("codec", "h264"),
            "template_id": template_id,
            "aspect_ratio": aspect_ratio,
            "lines": formatted_lines,
            "visual_plan": visual_plan.model_dump(),
            "audio_analysis": audio_analysis.model_dump()
        }

    @staticmethod
    def _stage_audio_asset(timeline: CanonicalTimeline, remotion_cwd: Path) -> tuple[Path, str]:
        source = Path(timeline.audio.working_file or timeline.audio.original_file or "")
        if not source.exists() or not source.is_file() or source.stat().st_size == 0:
            raise FileNotFoundError(f"Render audio file not found: {source}")

        asset_dir = remotion_cwd / "public" / "render-assets"
        asset_dir.mkdir(parents=True, exist_ok=True)
        suffix = source.suffix.lower() or ".wav"
        target = asset_dir / f"lyrivane-{timeline.project_id}{suffix}"
        shutil.copy2(source, target)
        return target, f"render-assets/{target.name}"

    def create_preview(
        self,
        timeline: CanonicalTimeline,
        template_id: str,
        settings: Dict[str, Any],
        output_path: Path,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Path:
        props = self.prepare_remotion_props(timeline, template_id, settings)
        props_path = output_path.with_suffix(".json")
        with open(props_path, "w", encoding="utf-8") as f:
            json.dump(props, f, indent=2)
        return props_path

    def render(
        self,
        timeline: CanonicalTimeline,
        template_id: str,
        settings: Dict[str, Any],
        output_path: Path,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Path:
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        remotion_cwd = Path(os.getenv("REMOTION_DIR", "/app/remotion"))
        if not remotion_cwd.exists():
            remotion_cwd = Path(__file__).resolve().parents[2] / "remotion"

        staged_audio: Path | None = None

        try:
            staged_audio, render_audio_url = self._stage_audio_asset(timeline, remotion_cwd)
            props = self.prepare_remotion_props(timeline, template_id, settings)
            props["audioUrl"] = render_audio_url
            props["audio_url"] = render_audio_url
            props_path = output_dir / "remotion_props.json"
            with open(props_path, "w", encoding="utf-8") as f:
                json.dump(props, f, indent=2)

            cmd = [
                "node", "scripts/render_with_progress.mjs",
                "src/index.ts",
                "LyrivaneComposition",
                str(output_path.resolve()),
                "--props", str(props_path.resolve()),
                "h265" if str(settings.get("codec", "h264")).lower() in {"h265", "hevc"} else "h264",
            ]
            process = subprocess.Popen(
                cmd,
                cwd=remotion_cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            output_lines: List[str] = []
            assert process.stdout is not None
            for raw_line in process.stdout:
                line = raw_line.strip()
                if not line:
                    continue
                output_lines.append(line)
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not progress_callback:
                    continue
                if event.get("type") == "bundle":
                    progress_callback(10, "Preparing Remotion composition...")
                elif event.get("type") == "render":
                    render_progress = max(0.0, min(1.0, float(event.get("progress", 0.0))))
                    percent = 10 + round(render_progress * 85)
                    frames = event.get("encodedFrames", event.get("renderedFrames", 0))
                    total = event.get("totalFrames")
                    frame_text = f" ({frames}/{total} frames)" if total else ""
                    progress_callback(percent, f"Rendering Remotion frames{frame_text}...")
                elif event.get("type") == "stitch":
                    progress_callback(96, "Encoding final video and audio...")

            return_code = process.wait()
            if return_code != 0:
                raise RuntimeError("\n".join(output_lines[-40:]) or "Remotion render process failed")
            if not output_path.exists() or output_path.stat().st_size < 1000:
                raise RuntimeError("Remotion completed without creating a usable MP4")
        except Exception as exc:
            logger.exception("Remotion render failed; using FFmpeg fallback: %s", exc)
            if progress_callback:
                progress_callback(96, "Remotion unavailable; using lyric-safe FFmpeg fallback...")
            # Keep lyrics and the original soundtrack in the fallback. A blank
            # color card is not a valid export for this application.
            from renderers.karaoke_renderer import KaraokeRendererAdapter
            fallback_path = KaraokeRendererAdapter().render(
                timeline, "classic-two-line", {}, output_path,
                progress_callback=progress_callback,
            )
            if not fallback_path.exists() or fallback_path.stat().st_size < 1000:
                raise RuntimeError("Lyric-capable fallback failed to produce an MP4")
        finally:
            if staged_audio and staged_audio.exists():
                staged_audio.unlink(missing_ok=True)

        return output_path

    def cancel(self, job_id: str) -> None:
        pass
