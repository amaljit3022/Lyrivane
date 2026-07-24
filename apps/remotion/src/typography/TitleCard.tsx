import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export interface TitleCardProps {
  title: string;
  artist: string;
  durationInFrames?: number;
}

export const TitleCard: React.FC<TitleCardProps> = ({
  title,
  artist,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 90 },
  });

  const opacity = interpolate(frame, [0, 15, 120, 150], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scale = interpolate(enterSpring, [0, 1], [0.92, 1.02]);
  const translateY = interpolate(enterSpring, [0, 1], [20, 0]);

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
        opacity,
        transform: `translateY(${translateY}px) scale(${scale})`,
        color: "#ffffff",
        fontFamily: "'Inter', system-ui, sans-serif",
      }}
    >
      <div
        style={{
          textTransform: "uppercase",
          letterSpacing: "0.2em",
          fontSize: "24px",
          color: "#f39c12",
          fontWeight: 600,
          marginBottom: "16px",
        }}
      >
        LYRIVANE STUDIO
      </div>
      <h1
        style={{
          fontSize: "84px",
          fontWeight: 900,
          margin: 0,
          letterSpacing: "-0.02em",
          textShadow: "0 10px 40px rgba(0,0,0,0.8)",
          textAlign: "center",
          width: "80%",
        }}
      >
        {title}
      </h1>
      <h2
        style={{
          fontSize: "36px",
          fontWeight: 400,
          color: "#b0bec5",
          marginTop: "20px",
          letterSpacing: "0.05em",
        }}
      >
        {artist}
      </h2>
    </AbsoluteFill>
  );
};
