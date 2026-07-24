import os
import math
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class EnergyMarker(BaseModel):
    ms: int
    rms_energy: float = Field(ge=0.0, le=1.0)
    is_beat: bool = False

class AudioAnalysisResult(BaseModel):
    bpm: float = 120.0
    duration_ms: int = 180000
    beats_ms: List[int] = Field(default_factory=list)
    energy_timeline: List[EnergyMarker] = Field(default_factory=list)
    overall_energy: float = 0.5

class AudioAnalysisService:
    """
    Extracts BPM, beat markers, RMS energy envelopes, and section energy for audio-reactive animation.
    """

    @classmethod
    def analyze_audio(cls, file_path: Path, duration_ms: int = 180000) -> AudioAnalysisResult:
        if not file_path.exists():
            return cls._generate_fallback_analysis(duration_ms)

        try:
            import librosa
            import numpy as np

            # Load audio file (mono, sr=22050 for fast processing)
            y, sr = librosa.load(str(file_path), sr=22050, mono=True)
            if len(y) == 0:
                return cls._generate_fallback_analysis(duration_ms)

            actual_duration_ms = int((len(y) / sr) * 1000)

            # 1. Estimate Tempo and Beat Frame Locations
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            bpm_val = float(np.atleast_1d(tempo)[0]) if len(np.atleast_1d(tempo)) > 0 else 120.0
            if bpm_val <= 0 or math.isnan(bpm_val):
                bpm_val = 120.0

            beat_times = librosa.frames_to_time(beat_frames, sr=sr)
            beats_ms = [int(t * 1000) for t in beat_times]

            # 2. RMS Energy calculation sampled every 100ms
            hop_length = int(sr * 0.1)  # 100ms windows
            rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
            max_rms = float(np.max(rms)) if len(rms) > 0 and np.max(rms) > 0 else 1.0
            norm_rms = (rms / max_rms).tolist()

            energy_timeline: List[EnergyMarker] = []
            beats_set = set(beats_ms)

            for i, val in enumerate(norm_rms):
                sample_ms = i * 100
                is_beat = any(abs(sample_ms - b) < 60 for b in beats_set)
                energy_timeline.append(EnergyMarker(
                    ms=sample_ms,
                    rms_energy=round(float(val), 3),
                    is_beat=is_beat
                ))

            overall_energy = round(float(np.mean(norm_rms)), 3) if len(norm_rms) > 0 else 0.5

            return AudioAnalysisResult(
                bpm=round(bpm_val, 1),
                duration_ms=actual_duration_ms,
                beats_ms=beats_ms,
                energy_timeline=energy_timeline,
                overall_energy=overall_energy
            )

        except Exception as e:
            print(f"Librosa audio analysis fallback: {e}")
            return cls._generate_fallback_analysis(duration_ms)

    @classmethod
    def _generate_fallback_analysis(cls, duration_ms: int) -> AudioAnalysisResult:
        """
        Generate deterministic beat grid and energy envelope when librosa isn't available.
        BPM = 120 -> beat every 500ms
        """
        bpm = 120.0
        beat_interval_ms = 500
        beats_ms = list(range(0, duration_ms, beat_interval_ms))

        energy_timeline: List[EnergyMarker] = []
        for ms in range(0, duration_ms, 100):
            is_beat = (ms % beat_interval_ms) < 100
            # Sine wave pseudo-energy variation
            rms = 0.4 + 0.4 * math.sin(ms / 2000.0)
            energy_timeline.append(EnergyMarker(
                ms=ms,
                rms_energy=round(rms, 3),
                is_beat=is_beat
            ))

        return AudioAnalysisResult(
            bpm=bpm,
            duration_ms=duration_ms,
            beats_ms=beats_ms,
            energy_timeline=energy_timeline,
            overall_energy=0.5
        )
