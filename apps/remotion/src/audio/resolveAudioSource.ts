import { staticFile } from "remotion";

/** Resolve a staged Remotion public asset without breaking browser/API URLs. */
export const resolveAudioSource = (source?: string): string | undefined => {
  if (!source) return undefined;
  if (/^(https?:|file:|data:)/i.test(source)) return source;
  return staticFile(source.replace(/^\/+/, ""));
};
