import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { bundle } from "@remotion/bundler";
import { getCompositions, renderMedia } from "@remotion/renderer";

const [entryPoint, compositionId, outputLocation, propsFlag, propsPath, codec] = process.argv.slice(2);

if (!entryPoint || !compositionId || !outputLocation || propsFlag !== "--props" || !propsPath || !codec) {
  throw new Error("Usage: render_with_progress.mjs <entry> <composition> <output> --props <props.json> <codec>");
}

const emit = (event) => {
  process.stdout.write(`${JSON.stringify(event)}\n`);
};

const inputProps = JSON.parse(await fs.readFile(path.resolve(propsPath), "utf8"));
const serveUrl = await bundle({
  entryPoint: path.resolve(entryPoint),
  onProgress: (progress) => emit({ type: "bundle", progress }),
});

const compositions = await getCompositions(serveUrl, { inputProps });
const composition = compositions.find((candidate) => candidate.id === compositionId);
if (!composition) {
  throw new Error(`Composition not found: ${compositionId}`);
}

await renderMedia({
  composition,
  serveUrl,
  codec,
  outputLocation: path.resolve(outputLocation),
  inputProps,
  concurrency: 1,
  overwrite: true,
  logLevel: "error",
  onProgress: (progress) => emit({
    type: "render",
    progress: progress.progress,
    renderedFrames: progress.renderedFrames,
    encodedFrames: progress.encodedFrames,
    totalFrames: composition.durationInFrames,
  }),
});

emit({ type: "stitch", progress: 1 });
