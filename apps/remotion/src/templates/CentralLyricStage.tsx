import React from "react";
import { AbsoluteFill, Audio, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export type CentralWord = {
  text: string;
  start_ms: number;
  end_ms: number;
  importance?: number;
};

export type CentralLine = {
  id: string;
  display_text?: string;
  start_ms: number;
  end_ms: number;
  words: CentralWord[];
};

export type CentralStageProps = {
  audioUrl?: string;
  lines: CentralLine[];
  variant?: "aurora" | "glass" | "solar";
  aspectRatio?: "16:9" | "9:16" | "1:1";
};

const palettes = {
  aurora: { accent: "#8cf6ff", accent2: "#dca7ff", bg: "#090b1a", glow: "rgba(112, 232, 255, .32)" },
  glass: { accent: "#b8a7ff", accent2: "#6fffe9", bg: "#080b18", glow: "rgba(164, 143, 255, .3)" },
  solar: { accent: "#ffe28a", accent2: "#ff8e6e", bg: "#140b0a", glow: "rgba(255, 155, 67, .32)" },
};

const Word: React.FC<{ word: CentralWord; frame: number; fps: number; palette: typeof palettes.aurora }> = ({ word, frame, fps, palette }) => {
  const start = Math.round((word.start_ms / 1000) * fps);
  const end = Math.max(start + 1, Math.round((word.end_ms / 1000) * fps));
  const local = frame - start;
  const opacity = interpolate(local, [-8, 0, Math.min(12, end - start), end - start + 8], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const scale = interpolate(local, [-8, 0, 10], [0.92, 1, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const active = frame >= start && frame <= end;
  const progress = active ? interpolate(frame, [start, end], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;
  return (
    <span style={{
      display: "inline-block", opacity, transform: `translateY(${active ? Math.sin(progress * Math.PI) * -3 : 0}px) scale(${scale})`,
      color: active ? palette.accent : "#eef2ff", margin: "0 .16em", fontWeight: active ? 800 : 650,
      textShadow: active ? `0 0 18px ${palette.glow}, 0 0 42px ${palette.glow}` : "0 2px 16px rgba(0,0,0,.45)",
      whiteSpace: "pre",
    }}>{word.text}</span>
  );
};

export const CentralLyricStage: React.FC<CentralStageProps> = ({ audioUrl, lines, variant = "aurora", aspectRatio = "16:9" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const now = (frame / fps) * 1000;
  const palette = palettes[variant];
  const activeIndex = lines.findIndex((line) => now >= line.start_ms && now <= line.end_ms);
  const currentIndex = activeIndex >= 0 ? activeIndex : -1;
  const current = currentIndex >= 0 ? lines[currentIndex] : undefined;
  const previous = currentIndex > 0 ? lines[currentIndex - 1] : undefined;
  const next = currentIndex >= 0 ? lines[currentIndex + 1] : lines.find((line) => now < line.start_ms);
  const panel = variant === "glass" ? "rgba(22, 26, 57, .54)" : variant === "solar" ? "rgba(49, 20, 12, .3)" : "rgba(13, 18, 45, .28)";
  const yPadding = aspectRatio === "9:16" ? "18vh 7vw" : "10vh 6vw";

  return (
    <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 46%, ${palette.glow} 0%, transparent 36%), linear-gradient(140deg, ${palette.bg}, #05060d 72%)`, color: "#f8fbff", fontFamily: "Inter, system-ui, sans-serif", overflow: "hidden" }}>
      {audioUrl && <Audio src={audioUrl} />}
      <AbsoluteFill style={{ padding: yPadding, justifyContent: "center", alignItems: "center" }}>
        <div style={{ width: "min(88vw, 1500px)", textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", gap: "clamp(18px, 3vh, 42px)" }}>
          <div style={{ minHeight: "1.4em", color: "rgba(230,238,255,.28)", fontSize: "clamp(20px, 2.2vw, 42px)", fontWeight: 500, filter: "blur(1px)", transform: "translateY(-8px)" }}>{previous?.display_text || ""}</div>
          <div style={{ position: "relative", width: "100%", padding: "clamp(20px, 3vw, 48px) clamp(24px, 5vw, 100px)", borderRadius: variant === "glass" ? 34 : 18, background: panel, border: `1px solid ${palette.accent}33`, boxShadow: `0 0 70px ${palette.glow}, inset 0 0 40px rgba(255,255,255,.035)`, backdropFilter: variant === "glass" ? "blur(18px)" : "blur(5px)" }}>
            <div style={{ position: "absolute", left: "12%", right: "12%", top: 0, height: 2, background: `linear-gradient(90deg, transparent, ${palette.accent}, ${palette.accent2}, transparent)`, boxShadow: `0 0 20px ${palette.accent}` }} />
            <div style={{ fontSize: "clamp(34px, 5vw, 92px)", lineHeight: 1.1, letterSpacing: "-.025em", wordBreak: "normal" }}>
              {(current?.words || []).map((word, index) => <Word key={`${current?.id}-${index}`} word={word} frame={frame} fps={fps} palette={palette} />)}
            </div>
          </div>
          <div style={{ minHeight: "1.4em", color: "rgba(230,238,255,.18)", fontSize: "clamp(18px, 1.8vw, 34px)", fontWeight: 500, filter: "blur(5px)", transform: "translateY(8px)" }}>{next?.display_text || ""}</div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
