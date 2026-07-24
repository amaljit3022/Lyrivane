import os
import uuid
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json

from schemas.project import (
    ProjectCreateRequest,
    ProjectResponse,
    CanonicalTimeline,
    AudioMetadata,
    SectionTiming,
    LineTiming
)
from services.audio_service import AudioService
from services.lyrics_service import LyricsService
from services.alignment_service import AlignmentService
from services.template_service import TemplateService
from services.visual_intelligence import VisualIntelligenceService
from renderers.karaoke_renderer import KaraokeRendererAdapter
from renderers.remotion_renderer import RemotionRendererAdapter
from worker.celery_app import celery_app

app = FastAPI(
    title="LyricFlow Studio API",
    description="Automated Lyrical Video Creation Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECTS_DIR = Path(os.getenv("PROJECTS_DIR", "./projects")).resolve()
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

projects_db: Dict[str, Dict[str, Any]] = {}


class RenderRequest(BaseModel):
    renderer: str = "karaoke"
    template_id: str = "classic-two-line"
    resolution: str = "1080p"
    fps: int = 30
    codec: str = "h264"
    aspect_ratio: str = "16:9"
    motion_intensity: float = 0.5


SUPPORTED_RENDERERS = {"karaoke": KaraokeRendererAdapter, "remotion": RemotionRendererAdapter}


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "LyricFlow Studio API", "version": "1.0.0"}


@app.get("/api/v1/templates")
def list_templates(renderer: Optional[str] = None):
    return TemplateService.list_templates(renderer=renderer)


@app.get("/api/v1/projects/{project_id}/visual-plan")
def get_visual_plan(
    project_id: str, 
    style: str = "editorial-motion", 
    palette: str = "default", 
    aspect_ratio: str = "16:9",
    motion_intensity: float = 0.5
):
    project = projects_db.get(project_id, {})
    project_dir = PROJECTS_DIR / project_id
    audio_meta = project.get("audio_meta") or AudioMetadata(
        original_file=str(project_dir / "audio" / "original" / "song.mp3"),
        duration_ms=180000,
        sample_rate=44100,
        channels=2,
        title=project.get("title", "Untitled"),
        artist=project.get("artist", "Unknown")
    )

    if project.get("canonical_timeline"):
        timeline_dict = project["canonical_timeline"]
        if "audio" not in timeline_dict or timeline_dict["audio"] is None:
            timeline_dict["audio"] = audio_meta.model_dump()
        timeline = CanonicalTimeline(**timeline_dict)
    else:
        lines_raw = project.get("lines") or []
        timeline = CanonicalTimeline(
            project_id=project_id,
            title=project.get("title", "Untitled"),
            artist=project.get("artist", "Unknown"),
            audio=audio_meta,
            lines=[LineTiming(**l) for l in lines_raw]
        )

    plan = VisualIntelligenceService.generate_visual_plan(
        timeline=timeline,
        style=style,
        palette=palette,
        aspect_ratio=aspect_ratio,
        motion_intensity=motion_intensity
    )

    return plan.model_dump()



@app.post("/api/v1/projects", response_model=ProjectResponse)
def create_project(req: ProjectCreateRequest):
    import random
    import string
    import re
    
    title_slug = "".join(c if c.isalnum() else "-" for c in (req.title or "project").lower())
    title_slug = re.sub(r'-+', '-', title_slug).strip('-')[:20]
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    project_id = f"{title_slug}-{suffix}" if title_slug else f"proj-{suffix}"
    project_dir = PROJECTS_DIR / project_id
    (project_dir / "audio" / "original").mkdir(parents=True, exist_ok=True)
    (project_dir / "audio" / "working").mkdir(parents=True, exist_ok=True)
    (project_dir / "lyrics" / "source").mkdir(parents=True, exist_ok=True)
    (project_dir / "lyrics" / "timing").mkdir(parents=True, exist_ok=True)
    (project_dir / "renders").mkdir(parents=True, exist_ok=True)

    project_data = {
        "project_id": project_id,
        "title": req.title or "Untitled Song",
        "artist": req.artist or "Unknown Artist",
        "language": req.language or "en",
        "status": "created",
        "created_at": "2026-07-21T00:00:00Z",
        "has_audio": False,
        "has_lyrics": False,
        "audio_meta": None,
        "sections": [],
        "lines": [],
        "canonical_timeline": None
    }

    projects_db[project_id] = project_data
    return ProjectResponse(**project_data)


@app.get("/api/v1/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str):
    if project_id not in projects_db:
        dummy_project = {
            "project_id": project_id,
            "title": "Golden Stars",
            "artist": "Krittika",
            "language": "en",
            "status": "created",
            "created_at": "2026-07-21T00:00:00Z",
            "has_audio": True,
            "has_lyrics": True,
            "audio_meta": None,
            "sections": [],
            "lines": [],
            "sync_progress": None,
            "canonical_timeline": None
        }
        return ProjectResponse(**dummy_project)
        
    project = projects_db[project_id]
    
    # Check for progress if we are synchronizing
    if project.get("status") == "synchronizing":
        project_dir = PROJECTS_DIR / project_id
        timeline_file = project_dir / "timeline.json"
        progress_file = project_dir / "progress.json"
        
        if timeline_file.exists():
            with open(timeline_file, "r", encoding="utf-8") as f:
                timeline_data = json.load(f)
                
            audio_meta = project.get("audio_meta")
            # Apply AlignmentService to align Whisper's hallucinated timings back to user's precise lyrics
            aligned_lines = AlignmentService.align_user_lyrics_to_whisper(
                project.get("lines", []),
                timeline_data.get("lines", [])
            )
            
            timeline = CanonicalTimeline(
                project_id=project_id,
                title=project.get("title", "Untitled"),
                artist=project.get("artist", "Unknown"),
                audio=audio_meta,
                sections=[SectionTiming(**s) for s in project.get("sections", [])],
                lines=[LineTiming(**l) for l in aligned_lines],
                overall_confidence=0.95
            )
            project["canonical_timeline"] = timeline.model_dump()
            project["lines"] = [l.model_dump() for l in timeline.lines]
            project["status"] = "synchronized"
            project["sync_progress"] = {"message": "Synchronization complete!", "percent": 100}
            
        elif progress_file.exists():
            try:
                with open(progress_file, "r", encoding="utf-8") as f:
                    project["sync_progress"] = json.load(f)
                    
                # If the worker encountered a fatal error
                if project["sync_progress"].get("percent") == -1:
                    project["status"] = "error"
            except json.JSONDecodeError:
                pass
                
    return ProjectResponse(**project)


@app.post("/api/v1/projects/{project_id}/audio", response_model=ProjectResponse)
async def upload_audio(project_id: str, file: UploadFile = File(...)):
    project_dir = PROJECTS_DIR / project_id
    (project_dir / "audio" / "original").mkdir(parents=True, exist_ok=True)
    (project_dir / "audio" / "working").mkdir(parents=True, exist_ok=True)

    dest_path = project_dir / "audio" / "original" / file.filename
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    working_audio_path = project_dir / "audio" / "working" / f"{dest_path.stem}.wav"
    AudioService.extract_audio_from_video(dest_path, working_audio_path)

    audio_meta = AudioService.probe_audio(working_audio_path)
    audio_meta.original_file = str(dest_path)
    audio_meta.working_file = str(working_audio_path)

    if project_id not in projects_db:
        projects_db[project_id] = {
            "project_id": project_id,
            "title": audio_meta.title or "Golden Stars",
            "artist": audio_meta.artist or "Krittika",
            "language": "en",
            "status": "audio_uploaded",
            "created_at": "2026-07-21T00:00:00Z",
            "has_audio": True,
            "has_lyrics": False,
            "audio_meta": audio_meta,
            "sections": [],
            "lines": [],
            "canonical_timeline": None
        }
    else:
        project = projects_db[project_id]
        project["audio_meta"] = audio_meta
        project["has_audio"] = True
        if audio_meta.title:
            project["title"] = audio_meta.title
        if audio_meta.artist:
            project["artist"] = audio_meta.artist
        project["status"] = "audio_uploaded"

    return ProjectResponse(**projects_db[project_id])


@app.get("/api/v1/projects/{project_id}/audio")
def get_audio(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    project = projects_db[project_id]
    if not project.get("audio_meta") or not project["audio_meta"].working_file:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    audio_path = Path(project["audio_meta"].working_file)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file missing on disk")
        
    return FileResponse(
        path=audio_path,
        media_type="audio/wav"
    )



@app.post("/api/v1/projects/{project_id}/lyrics", response_model=ProjectResponse)
async def upload_lyrics(
    project_id: str,
    raw_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    content = ""
    if file:
        file_bytes = await file.read()
        content = file_bytes.decode("utf-8", errors="ignore")
    elif raw_text:
        content = raw_text
    else:
        raise HTTPException(status_code=400, detail="Provide raw_text or a file")

    if project_id not in projects_db:
        projects_db[project_id] = {
            "project_id": project_id,
            "title": "Golden Stars",
            "artist": "Krittika",
            "language": "en",
            "status": "lyrics_prepared",
            "created_at": "2026-07-21T00:00:00Z",
            "has_audio": False,
            "has_lyrics": True,
            "audio_meta": None,
            "sections": [],
            "lines": [],
            "canonical_timeline": None
        }

    project = projects_db[project_id]
    duration_ms = project["audio_meta"].duration_ms if project.get("audio_meta") else 180000

    sections, lines = LyricsService.process_raw_lyrics(content, total_duration_ms=duration_ms)

    project["sections"] = [s.model_dump() for s in sections]
    project["lines"] = [l.model_dump() for l in lines]
    project["has_lyrics"] = True
    project["status"] = "lyrics_prepared"

    project_dir = PROJECTS_DIR / project_id
    (project_dir / "lyrics" / "source").mkdir(parents=True, exist_ok=True)
    with open(project_dir / "lyrics" / "source" / "raw_lyrics.txt", "w", encoding="utf-8") as f:
        f.write(content)

    return ProjectResponse(**project)


@app.post("/api/v1/projects/{project_id}/synchronize", response_model=ProjectResponse)
def trigger_synchronization(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    
    project["status"] = "synchronizing"
    project["sync_progress"] = {"message": "Queued for alignment...", "percent": 0}
    
    # Dispatch to Celery worker on the alignment queue
    celery_app.send_task("worker.align_lyrics", args=[project_id], queue="alignment")

    return ProjectResponse(**project)


@app.post("/api/v1/projects/{project_id}/render")
def render_video(project_id: str, req: RenderRequest):
    project_dir = PROJECTS_DIR / project_id
    renders_dir = project_dir / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)

    output_video_path = renders_dir / "output.mp4"

    project = projects_db.get(project_id, {})
    audio_meta = project.get("audio_meta") or AudioMetadata(
        original_file=str(project_dir / "audio" / "original" / "song.mp3"),
        duration_ms=180000,
        sample_rate=44100,
        channels=2,
        title=project.get("title", "Untitled"),
        artist=project.get("artist", "Unknown")
    )

    if project.get("canonical_timeline"):
        timeline_dict = project["canonical_timeline"]
        if "audio" not in timeline_dict or timeline_dict["audio"] is None:
            timeline_dict["audio"] = audio_meta.model_dump()
        timeline = CanonicalTimeline(**timeline_dict)
    else:
        lines_raw = project.get("lines") or []
        timeline = CanonicalTimeline(
            project_id=project_id,
            title=project.get("title", "Untitled"),
            artist=project.get("artist", "Unknown"),
            audio=audio_meta,
            lines=[LineTiming(**l) for l in lines_raw]
        )

    renderer_class = SUPPORTED_RENDERERS.get(req.renderer)
    if renderer_class is None:
        raise HTTPException(status_code=422, detail=f"Unsupported renderer: {req.renderer}")
    renderer = renderer_class()
    validation = renderer.validate_project(
        timeline,
        req.template_id,
        {"aspect_ratio": req.aspect_ratio, "fps": req.fps, "resolution": req.resolution, "codec": req.codec},
    )
    resolved_template_id = validation["template_id"]
    rendered_path = renderer.render(
        timeline=timeline,
        template_id=resolved_template_id,
        settings={
            "resolution": req.resolution, 
            "fps": req.fps, 
            "codec": req.codec, 
            "aspect_ratio": req.aspect_ratio,
            "motion_intensity": req.motion_intensity
        },
        output_path=output_video_path
    )
    if not rendered_path.exists() or rendered_path.stat().st_size < 1000:
        raise HTTPException(status_code=500, detail="Renderer completed without producing a usable MP4 file")

    return {
        "status": "success",
        "project_id": project_id,
        "renderer": req.renderer,
        "template_id": resolved_template_id,
        "output_file": str(rendered_path),
        "download_url": f"/api/v1/projects/{project_id}/renders/download"
    }


@app.get("/api/v1/projects/{project_id}/renders/download")
def download_rendered_video(project_id: str):
    project_dir = PROJECTS_DIR / project_id
    output_dir = project_dir / "renders"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_video = output_dir / "output.mp4"

    if not output_video.exists() or output_video.stat().st_size < 1000:
        raise HTTPException(status_code=404, detail="No rendered video is available for this project")

    project = projects_db.get(project_id, {})
    title = project.get("title", "Untitled").replace(" ", "_")
    filename = f"{title}_lyricflow.mp4"
    
    return FileResponse(
        path=output_video,
        filename=filename,
        media_type="video/mp4"
    )
