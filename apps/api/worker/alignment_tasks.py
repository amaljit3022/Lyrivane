import os
import json
import time
from pathlib import Path
import torch
from worker.celery_app import celery_app
import whisper_timestamped as whisper

# Monkey-patch torch.hub.load to trust the silero-vad repo (required in newer PyTorch)
_original_hub_load = torch.hub.load
def _patched_hub_load(repo_or_dir, model, *args, **kwargs):
    if "silero-vad" in repo_or_dir:
        kwargs['trust_repo'] = True
    return _original_hub_load(repo_or_dir, model, *args, **kwargs)
torch.hub.load = _patched_hub_load

from schemas.project import CanonicalTimeline, LineTiming, WordTiming, SectionTiming

PROJECTS_DIR = Path(os.getenv("PROJECTS_DIR", "./projects")).resolve()

# Load the model lazily
_model = None

def get_whisper_model():
    global _model
    if _model is None:
        # 'tiny' or 'base' is good for fast alignment, but user wants accuracy. 
        # 'base' is a good middle ground for CPU.
        _model = whisper.load_model("base", device="cpu")
    return _model

def update_progress(project_id: str, message: str, percent: int):
    project_dir = PROJECTS_DIR / project_id
    progress_file = project_dir / "progress.json"
    with open(progress_file, "w", encoding="utf-8") as f:
        json.dump({"message": message, "percent": percent}, f)

@celery_app.task(name="worker.align_lyrics")
def align_lyrics(project_id: str):
    try:
        project_dir = PROJECTS_DIR / project_id
        
        update_progress(project_id, "Loading AI model...", 10)
        model = get_whisper_model()
        
        # Read the raw lyrics from the project
        lyrics_file = project_dir / "lyrics" / "source" / "raw_lyrics.txt"
        if not lyrics_file.exists():
            update_progress(project_id, "Error: Lyrics file not found.", -1)
            return
            
        with open(lyrics_file, "r", encoding="utf-8") as f:
            raw_lyrics = f.read().strip()
            
        # Find the working audio file
        audio_dir = project_dir / "audio" / "working"
        audio_files = list(audio_dir.glob("*.wav"))
        if not audio_files:
            update_progress(project_id, "Error: Audio file not found.", -1)
            return
            
        audio_path = str(audio_files[0])
        
        update_progress(project_id, "Transcribing and aligning audio with Whisper...", 30)
        
        # We can pass the raw lyrics as initial prompt to guide the transcriber and prevent looping
        result = whisper.transcribe(
            model, 
            audio_path, 
            language="en", 
            vad="silero:v4.0",
            condition_on_previous_text=False,
            initial_prompt=raw_lyrics[:1000] # Provide up to first 1000 chars as context
        )
        
        update_progress(project_id, "Processing aligned timestamps...", 80)
        
        line_timings = []
        # Fallback to evenly distributing if transcription failed completely
        if not result.get("segments"):
            update_progress(project_id, "Error: Transcription failed to find segments.", -1)
            return
            
        for seg_idx, segment in enumerate(result["segments"]):
            words = segment.get("words", [])
            word_timings = []
            
            for w in words:
                word_timings.append({
                    "id": f"w-{seg_idx}-{w['text']}",
                    "display_text": w["text"].strip(),
                    "alignment_text": w["text"].strip().lower(),
                    "start_ms": int(w["start"] * 1000),
                    "end_ms": int(w["end"] * 1000),
                    "confidence": w.get("confidence", 0.95),
                    "source": "automatic"
                })
                
            line_timings.append({
                "id": f"l-{seg_idx}",
                "section_id": "verse",
                "display_text": segment["text"].strip(),
                "alignment_text": segment["text"].strip().lower(),
                "start_ms": int(segment["start"] * 1000),
                "end_ms": int(segment["end"] * 1000),
                "confidence": 0.95,
                "source": "automatic",
                "words": word_timings
            })
            
        # Write the aligned timeline to timeline.json so the API can read it
        timeline_data = {
            "lines": line_timings
        }
        
        with open(project_dir / "timeline.json", "w", encoding="utf-8") as f:
            json.dump(timeline_data, f)
            
        update_progress(project_id, "Synchronization complete!", 100)
        
    except Exception as e:
        update_progress(project_id, f"Error: {str(e)}", -1)
        print(f"Alignment error: {e}")
