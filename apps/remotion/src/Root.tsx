import "./index.css";
import { CalculateMetadataFunction, Composition } from "remotion";
import { LyrivaneComposition, LyrivaneProps } from "./Composition";

const defaultProps: LyrivaneProps = {
  lines: [
    {
      id: "line-1",
      start_ms: 1000,
      end_ms: 3000,
      words: [
        { text: "Lyrivane", start_ms: 1000, end_ms: 1500, importance: 0.9, enter_preset: "scale-pop" },
        { text: "Visual", start_ms: 1600, end_ms: 2200, importance: 0.7 },
        { text: "Engine", start_ms: 2300, end_ms: 3000, importance: 1.0, enter_preset: "blur-focus" },
      ],
    },
  ],
  template_id: "aurora-pulse",
  aspect_ratio: "16:9",
  resolution: "1080p",
};

const calculateMetadata: CalculateMetadataFunction<LyrivaneProps> = ({ props }) => {
  const ratio = props.aspect_ratio || "16:9";
  const baseHeight = props.resolution === "4K" ? 2160 : props.resolution === "1440p" ? 1440 : 1080;
  let width = Math.round(baseHeight * 16 / 9);
  let height = baseHeight;

  if (ratio === "9:16") {
    width = 1080;
    height = 1920;
  } else if (ratio === "1:1") {
    width = 1080;
    height = 1080;
  }

  // Calculate duration from last line end_ms if available
  let maxMs = 5000;
  if (props.lines && props.lines.length > 0) {
    const lastLine = props.lines[props.lines.length - 1];
    if (lastLine.end_ms) {
      maxMs = Math.max(maxMs, lastLine.end_ms + 1000);
    }
  }

  const fps = props.fps || 30;
  const durationInFrames = Math.max(60, Math.round((maxMs / 1000) * fps));

  return {
    width,
    height,
    fps,
    durationInFrames,
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="LyrivaneComposition"
        component={LyrivaneComposition}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        defaultProps={defaultProps}
        calculateMetadata={calculateMetadata}
      />
    </>
  );
};
