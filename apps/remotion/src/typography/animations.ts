import { interpolate, spring } from "remotion";

export interface AnimationFrameContext {
  localFrame: number;
  wordLocalStart: number;
  wordLocalEnd: number;
  fps: number;
}

export function computeWordAnimations(
  ctx: AnimationFrameContext,
  enterPreset: string = "fade-up",
  activePreset?: string | null,
  exitPreset: string = "fade"
) {
  const { localFrame, wordLocalStart, wordLocalEnd, fps } = ctx;

  // 1. Entry Animation Progress
  const enterSpring = spring({
    frame: localFrame - wordLocalStart,
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  let opacity = 1;
  let translateY = 0;
  let translateX = 0;
  let scale = 1;
  let blurPx = 0;
  let rotateDeg = 0;

  // Compute Entry
  switch (enterPreset) {
    case "scale-pop":
      scale = interpolate(enterSpring, [0, 1], [0.3, 1.05]);
      opacity = interpolate(localFrame, [wordLocalStart - 4, wordLocalStart], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      break;

    case "blur-focus":
      opacity = interpolate(localFrame, [wordLocalStart - 6, wordLocalStart + 2], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      blurPx = interpolate(enterSpring, [0, 1], [16, 0]);
      break;

    case "slide-in":
      translateX = interpolate(enterSpring, [0, 1], [-40, 0]);
      opacity = interpolate(localFrame, [wordLocalStart - 4, wordLocalStart], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      break;

    case "drop":
      translateY = interpolate(enterSpring, [0, 1], [-50, 0]);
      opacity = interpolate(localFrame, [wordLocalStart - 4, wordLocalStart], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      break;

    case "cascade":
      translateY = interpolate(enterSpring, [0, 1], [25, 0]);
      scale = interpolate(enterSpring, [0, 1], [0.8, 1]);
      opacity = interpolate(localFrame, [wordLocalStart - 4, wordLocalStart], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      break;

    case "fade-up":
    default:
      translateY = interpolate(enterSpring, [0, 1], [30, 0]);
      opacity = interpolate(localFrame, [wordLocalStart - 4, wordLocalStart], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      break;
  }

  // 2. Active Animation
  if (activePreset && localFrame >= wordLocalStart && localFrame <= wordLocalEnd) {
    const activeFrame = localFrame - wordLocalStart;

    switch (activePreset) {
      case "breathe":
        scale *= 1 + Math.sin(activeFrame / 10) * 0.05;
        break;
      case "pulse":
      case "heartbeat":
        scale *= 1 + Math.sin(activeFrame / 6) * 0.12;
        break;
      case "vibrate":
        translateX += (Math.sin(activeFrame * 3) * 3);
        translateY += (Math.cos(activeFrame * 3) * 3);
        break;
      case "wave":
      case "float":
        translateY += Math.sin(activeFrame / 8) * 8;
        break;
      case "glow-pulse":
        scale *= 1 + Math.sin(activeFrame / 8) * 0.06;
        break;
    }
  }

  // 3. Exit Animation
  if (localFrame > wordLocalEnd - 6) {
    const exitProgress = interpolate(
      localFrame,
      [wordLocalEnd - 6, wordLocalEnd + 6],
      [0, 1],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );

    switch (exitPreset) {
      case "dissolve":
      case "blur":
        opacity = 1 - exitProgress;
        blurPx += exitProgress * 14;
        break;
      case "drop":
        translateY += exitProgress * 40;
        opacity = 1 - exitProgress;
        break;
      case "scatter":
        scale *= 1 - exitProgress * 0.4;
        rotateDeg += exitProgress * 15;
        opacity = 1 - exitProgress;
        break;
      case "fade":
      default:
        opacity = 1 - exitProgress;
        break;
    }
  }

  return {
    opacity,
    transform: `translate(${translateX}px, ${translateY}px) scale(${scale}) rotate(${rotateDeg}deg)`,
    filter: blurPx > 0.5 ? `blur(${blurPx}px)` : "none",
  };
}
