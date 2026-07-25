import React from "react";
import { AbsoluteFill, Audio, Sequence, useVideoConfig } from "remotion";
import { LayoutEngine } from "../typography/LayoutEngine";
import { WordCompositionProps } from "../typography/WordRenderer";
import { AudioAnalysisProps } from "../audio/useAudioReactive";
import { resolveAudioSource } from "../audio/resolveAudioSource";

export type LineTiming = {
  id: string;
  start_ms: number;
  end_ms: number;
  words: WordCompositionProps[];
  layout_type?: string;
};

export type WhisperingProps = {
  audioUrl?: string;
  lines: LineTiming[];
  aspectRatio?: "16:9" | "9:16" | "1:1";
  audioAnalysis?: AudioAnalysisProps;
};

export const WhisperingWind: React.FC<WhisperingProps> = ({
  audioUrl,
  lines,
  aspectRatio = "16:9",
  audioAnalysis,
}) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #0b132b 0%, #1c2541 50%, #3a506b 100%)",
        color: "#edf2f4",
        fontFamily: "'Quicksand', 'Nunito', system-ui, sans-serif",
      }}
    >
      {audioUrl && <Audio src={resolveAudioSource(audioUrl)} />}

      {lines.map((line, i) => {
        const startFrame = Math.round((line.start_ms / 1000) * fps);
        const endFrame = Math.round((line.end_ms / 1000) * fps);
        const durationInFrames = Math.max(1, endFrame - startFrame);

        const styledWords = line.words.map((w) => ({
          ...w,
          active_preset: w.active_preset || "wave",
          enter_preset: w.enter_preset || "cascade",
        }));

        return (
          <Sequence
            key={line.id || i}
            from={startFrame}
            durationInFrames={durationInFrames}
          >
            <LayoutEngine
              line={{
                ...line,
                words: styledWords,
                layout_type: line.layout_type || "asymmetric-stack",
              }}
              aspectRatio={aspectRatio}
              templateBaseSize={60}
              audioAnalysis={audioAnalysis}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
