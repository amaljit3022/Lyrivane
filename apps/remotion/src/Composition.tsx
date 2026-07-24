import React from "react";
import { Sequence } from "remotion";
import { EditorialMotion } from "./templates/EditorialMotion";
import { CinematicFade } from "./templates/CinematicFade";
import { WhisperingWind } from "./templates/WhisperingWind";
import { WordCompositionProps } from "./typography/WordRenderer";
import { AudioAnalysisProps } from "./audio/useAudioReactive";
import { TitleCard } from "./typography/TitleCard";
import { AuroraPulse } from "./templates/AuroraPulse";
import { GlassHalo } from "./templates/GlassHalo";
import { SolarFlare } from "./templates/SolarFlare";

export type LineTiming = {
  id: string;
  start_ms: number;
  end_ms: number;
  words: WordCompositionProps[];
  layout_type?: string;
};

export type LyrivaneProps = {
  title?: string;
  artist?: string;
  audioUrl?: string;
  lines: LineTiming[];
  template_id?: string;
  aspect_ratio?: "16:9" | "9:16" | "1:1";
  resolution?: "1080p" | "1440p" | "4K";
  fps?: number;
  audio_analysis?: AudioAnalysisProps;
};

export const LyrivaneComposition: React.FC<LyrivaneProps> = (props) => {
  const templateId = props.template_id || "aurora-pulse";
  const aspectRatio = props.aspect_ratio || "16:9";

  const renderTemplate = () => {
    switch (templateId) {
      case "aurora-pulse":
        return <AuroraPulse audioUrl={props.audioUrl} lines={props.lines} aspectRatio={aspectRatio} />;
      case "glass-halo":
        return <GlassHalo audioUrl={props.audioUrl} lines={props.lines} aspectRatio={aspectRatio} />;
      case "solar-flare":
        return <SolarFlare audioUrl={props.audioUrl} lines={props.lines} aspectRatio={aspectRatio} />;
      case "cinematic-fade":
      case "cinematic-minimal":
        return (
          <CinematicFade
            audioUrl={props.audioUrl}
            lines={props.lines}
            aspectRatio={aspectRatio}
            audioAnalysis={props.audio_analysis}
          />
        );
      case "whispering-wind":
        return (
          <WhisperingWind
            audioUrl={props.audioUrl}
            lines={props.lines}
            aspectRatio={aspectRatio}
            audioAnalysis={props.audio_analysis}
          />
        );
      case "editorial-motion":
      default:
        return (
          <EditorialMotion
            audioUrl={props.audioUrl}
            lines={props.lines}
            aspectRatio={aspectRatio}
            audioAnalysis={props.audio_analysis}
          />
        );
    }
  };

  const showTitleCard = Boolean(props.title && props.title !== "Untitled");

  return (
    <>
      {showTitleCard && (
        <Sequence durationInFrames={120}>
          <TitleCard title={props.title || "Untitled"} artist={props.artist || "Unknown Artist"} />
        </Sequence>
      )}
      {renderTemplate()}
    </>
  );
};
