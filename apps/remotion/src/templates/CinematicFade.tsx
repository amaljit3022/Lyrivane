import React from "react";
import { AbsoluteFill, Audio, Sequence, useVideoConfig } from "remotion";
import { LayoutEngine } from "../typography/LayoutEngine";
import { WordCompositionProps } from "../typography/WordRenderer";
import { AudioAnalysisProps } from "../audio/useAudioReactive";

export type LineTiming = {
  id: string;
  start_ms: number;
  end_ms: number;
  words: WordCompositionProps[];
  layout_type?: string;
};

export type CinematicProps = {
  audioUrl?: string;
  lines: LineTiming[];
  aspectRatio?: "16:9" | "9:16" | "1:1";
  audioAnalysis?: AudioAnalysisProps;
};

export const CinematicFade: React.FC<CinematicProps> = ({
  audioUrl,
  lines,
  aspectRatio = "16:9",
  audioAnalysis,
}) => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill
      style={{
        background: "radial-gradient(circle at center, #1e1e2f 0%, #0a0a12 100%)",
        color: "#e2e8f0",
        fontFamily: "'Georgia', 'Times New Roman', serif",
      }}
    >
      {audioUrl && <Audio src={audioUrl} />}

      {lines.map((line, i) => {
        const startFrame = Math.round((line.start_ms / 1000) * fps);
        const endFrame = Math.round((line.end_ms / 1000) * fps);
        const durationInFrames = Math.max(1, endFrame - startFrame);

        const styledWords = line.words.map((w) => ({
          ...w,
          enter_preset: w.enter_preset || "blur-focus",
          exit_preset: w.exit_preset || "blur",
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
                layout_type: line.layout_type || "center",
              }}
              aspectRatio={aspectRatio}
              templateBaseSize={64}
              audioAnalysis={audioAnalysis}
            />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
