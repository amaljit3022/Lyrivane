import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { computeWordAnimations } from "./animations";
import { useAudioReactive, AudioAnalysisProps } from "../audio/useAudioReactive";

export interface WordCompositionProps {
  text: string;
  start_ms: number;
  end_ms: number;
  importance?: number;
  style?: {
    font_family?: string;
    font_size_mult?: number;
    font_weight?: number;
    color?: string;
    gradient?: string;
    opacity?: number;
    rotation_deg?: number;
    letter_spacing_em?: number;
    glow_color?: string;
    stroke_color?: string;
    stroke_width_px?: number;
    text_transform?: string;
  };
  enter_preset?: string;
  active_preset?: string;
  exit_preset?: string;
  baseFontSize?: number;
}

export const WordRenderer: React.FC<{
  word: WordCompositionProps;
  lineStartMs: number;
  audioAnalysis?: AudioAnalysisProps;
}> = ({ word, lineStartMs, audioAnalysis }) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const reactive = useAudioReactive(audioAnalysis);

  const startFrame = Math.round((lineStartMs / 1000) * fps);
  const wordStartFrame = Math.round((word.start_ms / 1000) * fps);
  const wordEndFrame = Math.round((word.end_ms / 1000) * fps);

  const localFrame = frame - startFrame;
  const wordLocalStart = wordStartFrame - startFrame;
  const wordLocalEnd = wordEndFrame - startFrame;

  const anim = computeWordAnimations(
    { localFrame, wordLocalStart, wordLocalEnd, fps },
    word.enter_preset || "fade-up",
    word.active_preset,
    word.exit_preset || "fade"
  );

  const wStyle = word.style || {};
  const baseSize = word.baseFontSize || 64;
  const sizeMult = wStyle.font_size_mult || 1.0;
  const computedFontSize = Math.round(baseSize * sizeMult);

  const textTransform = (wStyle.text_transform as any) || (word.importance && word.importance >= 0.8 ? "uppercase" : "none");

  // Audio-reactive beat pulse on high importance words
  let transformStr = anim.transform;
  if (word.importance && word.importance >= 0.8) {
    transformStr += ` scale(${reactive.beatScale})`;
  }

  const cssStyle: React.CSSProperties = {
    opacity: anim.opacity * (wStyle.opacity ?? 1.0),
    transform: transformStr,
    filter: anim.filter,
    fontSize: `${computedFontSize}px`,
    fontWeight: wStyle.font_weight || 700,
    fontFamily: wStyle.font_family || "inherit",
    letterSpacing: wStyle.letter_spacing_em ? `${wStyle.letter_spacing_em}em` : "normal",
    textTransform,
    color: wStyle.color || "inherit",
    display: "inline-block",
  };

  if (wStyle.gradient) {
    cssStyle.background = wStyle.gradient;
    cssStyle.WebkitBackgroundClip = "text";
    cssStyle.WebkitTextFillColor = "transparent";
  }

  if (wStyle.glow_color) {
    const glowMultiplier = 20 * reactive.currentEnergy;
    cssStyle.textShadow = `0 0 ${glowMultiplier}px ${wStyle.glow_color}, 0 0 ${glowMultiplier * 2}px ${wStyle.glow_color}`;
  }

  if (wStyle.stroke_color && wStyle.stroke_width_px) {
    cssStyle.WebkitTextStroke = `${wStyle.stroke_width_px}px ${wStyle.stroke_color}`;
  }

  return <span style={cssStyle}>{word.text}</span>;
};
