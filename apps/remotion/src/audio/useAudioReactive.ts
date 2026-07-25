import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export interface AudioAnalysisProps {
  bpm?: number;
  beats_ms?: number[];
  energy_timeline?: Array<{ ms: number; rms_energy: number; is_beat: boolean }>;
  overall_energy?: number;
}

export function useAudioReactive(audioAnalysis?: AudioAnalysisProps) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const currentMs = (frame / fps) * 1000;
  const beatsMs = audioAnalysis?.beats_ms || [];

  // 1. Calculate closest beat timestamp
  let isNearBeat = false;
  let framesSinceLastBeat = 999;

  for (const bMs of beatsMs) {
    const beatFrame = Math.round((bMs / 1000) * fps);
    const diff = frame - beatFrame;
    if (diff >= 0 && diff < framesSinceLastBeat) {
      framesSinceLastBeat = diff;
    }
    if (Math.abs(currentMs - bMs) < 60) {
      isNearBeat = true;
    }
  }

  // Fallback synthetic beat every 500ms (120 BPM) if beats_ms is empty
  if (beatsMs.length === 0) {
    const synthBeatFrame = 15; // every 15 frames @ 30fps
    framesSinceLastBeat = frame % synthBeatFrame;
    isNearBeat = framesSinceLastBeat === 0;
  }

  // 2. Beat Pulse Scale (bump to 1.1x on beat, decaying back to 1.0 over 5 frames)
  const beatScale = interpolate(
    framesSinceLastBeat,
    [0, 2, 5],
    [1.08, 1.04, 1.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 3. Camera Bump Scale (subtle 1.03x camera zoom bump on beat)
  const cameraBump = interpolate(
    framesSinceLastBeat,
    [0, 3, 6],
    [1.03, 1.01, 1.0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // 4. Current RMS Energy Level
  let currentEnergy = audioAnalysis?.overall_energy || 0.5;
  if (audioAnalysis?.energy_timeline && audioAnalysis.energy_timeline.length > 0) {
    const timelineIdx = Math.floor(currentMs / 100);
    if (timelineIdx >= 0 && timelineIdx < audioAnalysis.energy_timeline.length) {
      currentEnergy = audioAnalysis.energy_timeline[timelineIdx].rms_energy;
    }
  }

  return {
    isNearBeat,
    beatScale,
    cameraBump,
    currentEnergy,
    bpm: audioAnalysis?.bpm || 120,
  };
}
