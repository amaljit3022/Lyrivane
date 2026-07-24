import React from "react";
import { AbsoluteFill } from "remotion";
import { WordRenderer, WordCompositionProps } from "./WordRenderer";
import { useAudioReactive, AudioAnalysisProps } from "../audio/useAudioReactive";

export interface LineCompositionProps {
  id: string;
  start_ms: number;
  end_ms: number;
  words: WordCompositionProps[];
  layout_type?: string;
  anchor?: string;
}

export interface LayoutEngineProps {
  line: LineCompositionProps;
  aspectRatio?: "16:9" | "9:16" | "1:1";
  templateBaseSize?: number;
  accentColor?: string;
  audioAnalysis?: AudioAnalysisProps;
}

export const LayoutEngine: React.FC<LayoutEngineProps> = ({
  line,
  aspectRatio = "16:9",
  templateBaseSize = 64,
  audioAnalysis,
}) => {
  const reactive = useAudioReactive(audioAnalysis);
  const layoutType = line.layout_type || "center";

  // Aspect ratio responsive container bounds
  let containerWidth = "85%";
  let baseSize = templateBaseSize;

  if (aspectRatio === "9:16") {
    containerWidth = "92%";
    baseSize = Math.round(templateBaseSize * 0.9);
  } else if (aspectRatio === "1:1") {
    containerWidth = "88%";
    baseSize = Math.round(templateBaseSize * 0.95);
  }

  // Layout Styles
  let flexAlign = "center";
  let flexJustify = "center";
  let flexDirection: "row" | "column" = "row";
  let gap = "20px";

  switch (layoutType) {
    case "editorial-left":
      flexAlign = "flex-start";
      flexJustify = "flex-start";
      break;

    case "asymmetric-stack":
      flexDirection = "column";
      flexAlign = "flex-start";
      gap = "14px";
      break;

    case "vertical-stack":
      flexDirection = "column";
      flexAlign = "center";
      gap = "16px";
      break;

    case "full-screen-keyword":
      baseSize = Math.round(baseSize * 1.5);
      flexAlign = "center";
      flexJustify = "center";
      break;

    case "scattered":
      flexAlign = "center";
      flexJustify = "space-around";
      gap = "28px";
      break;

    case "center":
    default:
      flexAlign = "center";
      flexJustify = "center";
      break;
  }

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: aspectRatio === "9:16" ? "120px 40px" : "60px",
        transform: `scale(${reactive.cameraBump})`,
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection,
          flexWrap: flexDirection === "row" ? "wrap" : "nowrap",
          justifyContent: flexJustify,
          alignItems: flexAlign,
          gap,
          width: containerWidth,
          maxWidth: aspectRatio === "9:16" ? "980px" : "1500px",
          textAlign: layoutType === "editorial-left" ? "left" : "center",
        }}
      >
        {line.words.map((word, j) => (
          <WordRenderer
            key={j}
            word={{
              ...word,
              baseFontSize: word.baseFontSize || baseSize,
            }}
            lineStartMs={line.start_ms}
            audioAnalysis={audioAnalysis}
          />
        ))}
      </div>
    </AbsoluteFill>
  );
};
