import os
import uuid
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

# In-memory store fallback for initial MVP phase
projects_db: Dict[str, Dict[str, Any]] = {}


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "LyricFlow Studio API", "version": "1.0.0"}


@app.post("/api/v1/projects", response_model=ProjectResponse)
def create_project(req: ProjectCreateRequest):
    project_id = str(uuid.uuid4())
    project_dir = PROJECTS_DIR / project_id
    (project_dir / "audio" / "original").mkdir(parents=True, exist_ok=True)
    (project_dir / "audio" / "working").mkdir(parents=True, exist_ok=True)
    (project_dir / "lyrics" / "source").mkdir(parents=True, exist_ok=True)
    (project_dir / "lyrics" / "timing").mkdir(parents=True, exist_ok=True)

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
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(**projects_db[project_id])


@app.post("/api/v1/projects/{project_id}/audio", response_model=ProjectResponse)
async def upload_audio(project_id: str, file: UploadFile = File(...)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project_dir = PROJECTS_DIR / project_id
    dest_path = project_dir / "audio" / "original" / file.filename

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    audio_meta = AudioService.probe_audio(dest_path)

    project = projects_db[project_id]
    project["audio_meta"] = audio_meta
    project["has_audio"] = True
    if audio_meta.title:
        project["title"] = audio_meta.title
    if audio_meta.artist:
        project["artist"] = audio_meta.artist

    project["status"] = "audio_uploaded"
    return ProjectResponse(**project)


@app.post("/api/v1/projects/{project_id}/lyrics", response_model=ProjectResponse)
async def upload_lyrics(
    project_id: str,
    raw_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    content = ""
    if file:
        file_bytes = await file.read()
        content = file_bytes.decode("utf-8", errors="ignore")
    elif raw_text:
        content = raw_text
    else:
        raise HTTPException(status_code=400, detail="Provide raw_text or a file")

    project = projects_db[project_id]
    duration_ms = project["audio_meta"].duration_ms if project.get("audio_meta") else 180000

    sections, lines = LyricsService.process_raw_lyrics(content, total_duration_ms=duration_ms)

    project["sections"] = [s.model_dump() for s in sections]
    project["lines"] = [l.model_dump() for l in lines]
    project["has_lyrics"] = True
    project["status"] = "lyrics_prepared"

    # Store raw lyrics
    project_dir = PROJECTS_DIR / project_id
    with open(project_dir / "lyrics" / "source" / "raw_lyrics.txt", "w", encoding="utf-8") as f:
        f.write(content)

    return ProjectResponse(**project)


@app.post("/api/v1/projects/{project_id}/synchronize", response_model=ProjectResponse)
def trigger_synchronization(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    if not project["has_audio"] or not project["has_lyrics"]:
        raise HTTPException(status_code=400, detail="Project requires both audio and lyrics before synchronization")

    audio_meta = project["audio_meta"]
    duration = audio_meta.duration_ms if audio_meta else 180000
    lines_raw = project["lines"]

    # Initial MVP automatic line timeline generation (evenly distributed across non-silent intervals)
    num_lines = len(lines_raw)
    line_timings = []

    if num_lines > 0:
        start_offset = 5000  # Start 5s into song
        usable_duration = duration - 10000
        slot_duration = usable_duration // num_lines if num_lines > 0 else 3000

        for idx, line_dict in enumerate(lines_raw):
            line_start = start_offset + (idx * slot_duration)
            line_end = line_start + min(slot_duration - 500, 4000)

            words = line_dict.get("words", [])
            num_words = len(words)
            word_timings = []

            if num_words > 0:
                word_slot = (line_end - line_start) // num_words
                for w_idx, w_dict in enumerate(words):
                    w_start = line_start + (w_idx * word_slot)
                    w_end = w_start + word_slot - 50
                    word_timings.append({
                        **w_dict,
                        "start_ms": w_start,
                        "end_ms": w_end,
                        "confidence": 0.95,
                        "source": "automatic"
                    })

            line_timings.append({
                **line_dict,
                "start_ms": line_start,
                "end_ms": line_end,
                "confidence": 0.94,
                "source": "automatic",
                "words": word_timings
            })

    timeline = CanonicalTimeline(
        project_id=project_id,
        title=project["title"],
        artist=project["artist"],
        audio=project["audio_meta"],
        sections=[SectionTiming(**s) for s in project["sections"]],
        lines=[LineTiming(**l) for l in line_timings],
        overall_confidence=0.94
    )

    project["canonical_timeline"] = timeline.model_dump()
    project["status"] = "synchronized"

    return ProjectResponse(**project)
