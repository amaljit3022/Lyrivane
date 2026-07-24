# Rendering and synchronization notes

## Current pipeline

1. The user-provided lyrics are parsed into canonical lines and words while preserving display text.
2. Whisper is used only to obtain timestamp anchors from the working WAV file.
3. `AlignmentService` maps the supplied lyrics to those anchors using normalized words and a monotonic dynamic-programming alignment.
4. The canonical timeline is used by both preview and final rendering.
5. Remotion is attempted first. If its Linux browser/runtime is unavailable, the lyric-capable FFmpeg/ASS renderer is used.

The calculation/alignment code remains independent of the web UI. The final renderer receives the already-aligned timeline and must never re-run synchronization.

## Implemented renderer matrix

| Engine | Status | Templates exposed in the UI |
|---|---|---|
| FFmpeg/ASS Karaoke | Implemented | Central Aurora, Minimal Dark |
| Remotion | Implemented | Aurora Pulse, Glass Halo, Solar Flare, Editorial Motion, Cinematic Fade, Whispering Wind |
| Blender | Not implemented | Hidden until a real renderer, manifest, and export test exist |

The UI only lists engines and templates that have a backend implementation. A
template is considered real only when its manifest, renderer mapping, and export
path agree on the same ID. Resolution, aspect ratio, FPS, and codec settings are
passed into the renderer; they are not presentation-only controls.

## Repeated-chorus protection

The earlier global `SequenceMatcher` approach could match a repeated phrase much later in the song. In the observed failure, the timeline jumped from approximately 171 seconds to 336.9 seconds.

The current mapper uses:

- monotonic user-word to Whisper-word alignment;
- exact and fuzzy normalized-word scores;
- penalties for skipped user and Whisper words;
- preserved ordering across repeated phrases;
- bounded word and line durations in the final repair pass.

This allows multiple supplied lyric lines to share one Whisper segment when Whisper combines them or misses low-energy words, without selecting a later chorus.

## Central lyric design

The central export presentation is intentionally restrained and readable:

- centered primary lyric line;
- cyan active-word highlighting with a dark outline;
- previous lyric above and next lyric below at reduced opacity;
- dark central panel for contrast;
- no full-width vector drawing layer, because that layer caused visible background banding/flicker in FFmpeg/libass output.

Remotion templates live in `apps/remotion/src/templates/` and their metadata lives in `templates/remotion/`. The current catalog includes Aurora Pulse, Glass Halo, Solar Flare, Editorial Motion, Cinematic Fade, Whispering Wind, plus the future-ready Neon Orbit, Paper Bloom, and Signal Noir designs. The FFmpeg fallback is implemented in `apps/api/renderers/karaoke_renderer.py` so a failed Remotion environment still produces a useful lyric video.

Template manifests are the discovery contract for both engines. They declare supported aspect ratios and timing support; the API rejects unsupported renderer, codec, FPS, resolution, or aspect-ratio combinations before a render starts. Karaoke keeps only renderer-specific ASS style defaults in Python while its names, descriptions, and supported formats come from the manifest.

Rendering is asynchronous. `POST /api/v1/projects/{project_id}/render` returns a job ID immediately; the web client polls `/render-status/{job_id}` until `completed` or `failed`. The progress bar is driven only by that job state. Remotion audio is copied temporarily into `apps/remotion/public/render-assets/` and resolved with `staticFile()` so container paths are never mistaken for browser URLs.

The web preview is a template-aware lightweight preview. It uses the same template IDs and visual language as the Remotion compositions while keeping the synchronized timeline in the browser; the final export still uses the authoritative Remotion renderer.

## Renderer runtime requirements

Remotion needs both JavaScript native packages and a headless Chrome runtime. The API Dockerfile installs the required Debian browser libraries. The API container also needs the Linux Rspack optional dependency; do not reuse a Windows-only `node_modules` tree for a Linux container.

If Remotion fails, inspect the API logs. The renderer records the actual failure and then invokes the lyric-capable fallback. A blank color-only fallback is deliberately not used.

## Verification commands

```bash
# Python alignment tests
$env:PYTHONPATH='apps/api'
pytest -q apps/api/tests/test_alignment_service.py

# Remotion checks
cd apps/remotion
npm run lint
npm run build

# Inspect an exported file
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_type,codec_name projects/<id>/renders/output.mp4
```

For a visual check, extract a frame at a known lyric timestamp with FFmpeg and verify the central text, previous/next context, and absence of background flicker.

## Known operational note

The source project storage is local and intentionally ignored by Git. Do not commit uploaded audio, generated MP4 files, timelines containing user media paths, or smoke-test media.
