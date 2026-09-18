import React from "react";
import { AbsoluteFill, Audio, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { resolveAudioSource } from "../audio/resolveAudioSource";

type GreenScreenWord = {
  text: string;
  start_ms: number;
  end_ms: number;
};

type GreenScreenLine = {
  id: string;
  start_ms: number;
  end_ms: number;
  words: GreenScreenWord[];
};

export type GreenScreenLyricsProps = {
  audioUrl?: string;
  lines: GreenScreenLine[];
  aspectRatio?: "16:9" | "9:16" | "1:1";
  keyColor?: string;
};

const KeyedWord: React.FC<{ word: GreenScreenWord; frame: number; fps: number }> = ({ word, frame, fps }) => {
  const start = Math.round((word.start_ms / 1000) * fps);
  const end = Math.max(start + 1, Math.round((word.end_ms / 1000) * fps));
  const localFrame = frame - start;
  const opacity = interpolate(localFrame, [-6, 0, end - start, end - start + 6], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const active = frame >= start && frame <= end;
  const progress = active ? interpolate(frame, [start, end], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;

  return (
    <span
      style={{
        display: "inline-block",
        opacity,
        transform: `translateY(${active ? Math.sin(progress * Math.PI) * -3 : 0}px) scale(${active ? 1.035 : 1})`,
        color: active ? "#fff200" : "#ffffff",
        margin: "0 .14em",
        fontWeight: active ? 900 : 800,
        WebkitTextStroke: "2px #000000",
        textShadow: "0 3px 0 #000000, 0 0 8px rgba(0,0,0,.9)",
        whiteSpace: "pre",
      }}
    >
      {word.text}
    </span>
  );
};

export const GreenScreenLyrics: React.FC<GreenScreenLyricsProps> = ({
  audioUrl,
  lines,
  aspectRatio = "16:9",
  keyColor = "#00ff00",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const now = (frame / fps) * 1000;
  const current = lines.find((line) => now >= line.start_ms && now <= line.end_ms);
  const padding = aspectRatio === "9:16" ? "14vh 8vw" : aspectRatio === "1:1" ? "10vh 8vw" : "8vh 7vw";

  return (
    <AbsoluteFill
      style={{
        backgroundColor: keyColor,
        color: "#ffffff",
        fontFamily: "Inter, Arial, sans-serif",
        overflow: "hidden",
      }}
    >
      {audioUrl && <Audio src={resolveAudioSource(audioUrl)} />}
      <AbsoluteFill style={{ padding, justifyContent: "center", alignItems: "center" }}>
        <div
          style={{
            width: "100%",
            maxWidth: "1700px",
            textAlign: "center",
            fontSize: aspectRatio === "9:16" ? "clamp(42px, 7vw, 96px)" : "clamp(48px, 5vw, 104px)",
            lineHeight: 1.08,
            letterSpacing: "-.02em",
          }}
        >
          {(current?.words || []).map((word, index) => (
            <KeyedWord key={`${current?.id}-${index}`} word={word} frame={frame} fps={fps} />
          ))}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};