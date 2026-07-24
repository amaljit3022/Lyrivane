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

export type EditorialProps = {
  audioUrl?: string;
  lines: LineTiming[];
  aspectRatio?: "16:9" | "9:16" | "1:1";
  audioAnalysis?: AudioAnalysisProps;
};

export const EditorialMotion: React.FC<EditorialProps> = ({
  audioUrl,
  lines,
  aspectRatio = "16:9",
  audioAnalysis,
}) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0d0d0d",
        color: "#f5f5f5",
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
      }}
    >
      {audioUrl && <Audio src={resolveAudioSource(audioUrl)} />}

      {lines.map((line, i) => {
        const startFrame = Math.round((line.start_ms / 1000) * fps);
        const endFrame = Math.round((line.end_ms / 1000) * fps);
        const durationInFrames = Math.max(1, endFrame - startFrame);

        return (
          <Sequence
            key={line.id || i}
            from={startFrame}
            durationInFrames={durationInFrames}
          >
            <LayoutEngine
              line={{
                ...line,
                layout_type: line.layout_type || (i % 2 === 0 ? "editorial-left" : "center"),
              }}
              aspectRatio={aspectRatio}
              templateBaseSize={68}
              audioAnalysis={audioAnalysis}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
