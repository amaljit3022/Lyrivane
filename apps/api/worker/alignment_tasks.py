import json
import os
from pathlib import Path

import torch
import whisper_timestamped as whisper
from celery.utils.log import get_task_logger

from worker.celery_app import celery_app
from schemas.project import AudioMetadata
from services.alignment_service import AlignmentService
from services.audio_service import AudioService
from services.lyrics_service import LyricsService

# Monkey-patch torch.hub.load to trust the silero-vad repo when other tasks use it.
_original_hub_load = torch.hub.load


def _patched_hub_load(repo_or_dir, model, *args, **kwargs):
    if "silero-vad" in repo_or_dir:
        kwargs["trust_repo"] = True
    return _original_hub_load(repo_or_dir, model, *args, **kwargs)


torch.hub.load = _patched_hub_load

PROJECTS_DIR = Path(os.getenv("PROJECTS_DIR", "./projects")).resolve()
logger = get_task_logger(__name__)
_model = None


def get_whisper_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base", device="cpu")
    return _model


def update_progress(project_id: str, message: str, percent: int):
    progress_file = PROJECTS_DIR / project_id / "progress.json"
    with progress_file.open("w", encoding="utf-8") as handle:
        json.dump({"message": message, "percent": percent}, handle)


def _find_audio(project_dir: Path) -> Path | None:
    audio_files = sorted((project_dir / "audio" / "working").glob("*.wav"))
    return audio_files[0] if audio_files else None


def _transcribe(model, audio_path: Path):
    """Use Whisper only for word anchors; do not let it replace user lyrics."""
    # The previous silero-VAD pass was dropping the opening sung verse. A no-VAD
    # pass keeps low-energy vocals available for text alignment. We also avoid
    # initial_prompt because it can cause repeated/hallucinated lyric text.
    return whisper.transcribe(
        model,
        str(audio_path),
        language="en",
        vad=False,
        condition_on_previous_text=False,
    )


def _whisper_lines(result: dict) -> list[dict]:
    lines = []
    for seg_idx, segment in enumerate(result.get("segments", [])):
        word_timings = []
        for word_idx, word in enumerate(segment.get("words", [])):
            text = str(word.get("text", "")).strip()
            if not text:
                continue
            word_timings.append({
                "id": f"w-{seg_idx}-{word_idx}",
                "display_text": text,
                "alignment_text": text.lower(),
                "start_ms": int(float(word["start"]) * 1000),
                "end_ms": int(float(word["end"]) * 1000),
                "confidence": float(word.get("confidence", 0.0) or 0.0),
                "source": "automatic",
            })
        if not word_timings:
            continue
        lines.append({
            "id": f"l-{seg_idx}",
            "section_id": "verse",
            "display_text": str(segment.get("text", "")).strip(),
            "alignment_text": str(segment.get("text", "")).strip().lower(),
            "start_ms": word_timings[0]["start_ms"],
            "end_ms": word_timings[-1]["end_ms"],
            "confidence": 0.0,
            "source": "automatic",
            "words": word_timings,
        })
    return lines


@celery_app.task(name="worker.align_lyrics")
def align_lyrics(project_id: str):
    try:
        project_dir = PROJECTS_DIR / project_id
        update_progress(project_id, "Loading AI model...", 10)
        model = get_whisper_model()

        lyrics_file = project_dir / "lyrics" / "source" / "raw_lyrics.txt"
        audio_path = _find_audio(project_dir)
        if not lyrics_file.exists():
            update_progress(project_id, "Error: Lyrics file not found.", -1)
            return
        if audio_path is None:
            update_progress(project_id, "Error: Audio file not found.", -1)
            return

        raw_lyrics = lyrics_file.read_text(encoding="utf-8").strip()
        audio_meta: AudioMetadata = AudioService.probe_audio(audio_path)
        _, user_lines = LyricsService.process_raw_lyrics(raw_lyrics, audio_meta.duration_ms)
        if not user_lines:
            update_progress(project_id, "Error: No lyric lines found.", -1)
            return

        update_progress(project_id, "Transcribing audio for word timestamps...", 30)
        result = _transcribe(model, audio_path)
        whisper_lines = _whisper_lines(result)
        if not whisper_lines:
            update_progress(project_id, "Error: Transcription produced no word timestamps.", -1)
            return

        update_progress(project_id, "Aligning supplied lyrics to audio timestamps...", 80)
        user_line_dicts = [line.model_dump(mode="json") for line in user_lines]
        repaired_whisper = AlignmentService.repair_whisper_timestamps(whisper_lines)
        aligned_lines = AlignmentService.align_user_lyrics_to_whisper(user_line_dicts, repaired_whisper)

        timeline_data = {
            "schema_version": "1.0",
            "alignment_mode": "user_lyrics_mapped_to_whisper_word_timestamps",
            "lines": aligned_lines,
        }
        (project_dir / "timeline.json").write_text(
            json.dumps(timeline_data, ensure_ascii=False), encoding="utf-8"
        )
        update_progress(project_id, "Synchronization complete!", 100)
    except Exception as exc:
        logger.exception("Alignment error for %s", project_id)
        update_progress(project_id, f"Error: {exc}", -1)
