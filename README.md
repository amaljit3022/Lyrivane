# LyricFlow Studio (Lyrivane)

> *Let every word move with the music.*  
> A Krittika Labs Project.

LyricFlow Studio is a local-first, open-source application designed to transform audio tracks and user-supplied lyrics into professional lyric videos with **99.9% targeted automation**.

## 🌟 Key Features

- **Automated Lyrics-to-Audio Alignment**: Advanced forced alignment hierarchy using wav2vec2 CTC alignment, selective refinement, Demucs vocal stem isolation, and ASR fallbacks.
- **Dual Text Representation**: Preserves exact user display formatting (spelling, capitalization, punctuation, line breaks) while utilizing a normalized representation for alignment mapping.
- **Multi-Engine Renderer Architecture**:
  1. **Fast Karaoke**: Low-overhead FFmpeg & ASS subtitle rendering for rapid 1080p generation.
  2. **Creative Remotion**: Modern React/TypeScript animated typography and social templates.
  3. **Cinematic Blender**: 3D typography, volumetric lighting, and particle environments.
- **Decoupled Visual Iteration**: Visual tweaks (renderers, templates, fonts, colors, aspect ratios) never trigger audio resynchronization.
- **Optional Waveform Editor**: Manual correction fallback under `Advanced -> Edit Lyrics or Timing`.
- **Central lyric presentation**: The export fallback uses a centered lyric panel, active-word highlighting, and previous/next lyric context so the final MP4 matches the preview intent.
- **Safe rendering fallback**: A Remotion failure cannot produce a silent or blank video; FFmpeg/ASS rendering preserves lyrics and the original soundtrack.

## 🚀 Quick Start (Docker)

```bash
# Start Core Application (Postgres, Redis, API, Frontend, Alignment Workers)
docker compose up --build

# Enable Remotion Profile
docker compose --profile remotion up --build

# Enable Blender Profile
docker compose --profile blender up --build
```

The API image includes the Linux browser libraries required by Remotion. If the
image was created before those dependencies were added, rebuild the API image:

```bash
docker compose build api
docker compose up -d api alignment-worker frontend
```

The application is local-first. Uploaded audio and generated videos remain in
`projects/<project-id>/` and are intentionally excluded from Git.

## 📁 Repository Structure

- `apps/api`: Python FastAPI backend, audio ingestion, lyrics normalization, and worker services.
- `apps/web`: Next.js 14 web interface with 5-stage workflow stepper.
- `packages/alignment`: Forced alignment algorithms and quality validation.
- `templates/`: Engine-specific video rendering templates.
- `projects/`: Local project files, cached stems, and rendered video outputs.
- `docs/RENDERING_AND_SYNC.md`: Synchronization, renderer, design, and troubleshooting notes.

## 📄 License

Open-source core licensed under MIT / Apache 2.0.
