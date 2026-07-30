# Practical Toolkit Review

## Current architecture

The repository contains three independent CLI projects and one thin FastAPI project:

```text
CLI or API -> media project orchestration -> provider or local utility -> output
```

This remains a good fit for a personal local toolkit. Optional dependencies stay isolated, commands are easy to debug, and individual projects can evolve independently.

## Strengths

- shallow, beginner-friendly folders
- clear provider boundaries
- readable configuration dataclasses
- independent media projects
- local output management
- minimal FastAPI integration
- no required cloud infrastructure

## Main pain points before this phase

1. Audio could be generated and normalized, but there was no transcription or subtitle workflow.
2. Spoken recordings required multiple manual FFmpeg commands to clean up.
3. Image prompts were one-off and lacked reusable presets or batching.
4. Background removal required leaving the toolkit.
5. Video utilities were limited to a generation placeholder; common resizing and frame extraction were missing.
6. API outputs were grouped only by media type, making different videos and games harder to separate.
7. Provider discovery existed, but practical capabilities were not discoverable.

## Research-informed decisions

### Speech transcription

[faster-whisper](https://github.com/SYSTRAN/faster-whisper) supports local CPU/GPU execution, timestamped segments, VAD filtering, and progress reporting. A direct optional integration provides useful TXT and SRT output without introducing a transcription server or job system.

### Background removal

[rembg](https://github.com/danielgatis/rembg) supports local CPU/GPU execution and reusable model sessions. The first integration handles one file at a time; folder session reuse can be added when real batch usage justifies it.

### Audio and video processing

[FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html) already provide the reliable building blocks needed for loudness normalization, noise reduction, scaling, padding, and frame extraction. Reusing FFmpeg is simpler than adding separate Python media libraries.

### Local image generation

[Diffusers](https://huggingface.co/docs/diffusers/main/using-diffusers/batched_inference) supports batched prompts and image-to-image pipelines. [ComfyUI](https://docs.comfy.org/development/overview) exposes local workflows through an API. These are strong next providers, but the toolkit should integrate them rather than duplicate their model-loading and workflow systems.

## Implemented priorities

### Audio

- local faster-whisper transcription
- TXT transcript output
- SRT subtitle output
- spoken-audio enhancement with FFmpeg

### Image

- reusable prompt presets
- batch generation from a text file
- local background removal with rembg
- presets for thumbnails and common game assets

### Video

- aspect-safe resizing and padding
- YouTube, Shorts, square, and 720p presets
- frame extraction with a JSON manifest

### API and organization

- endpoints for the new practical operations
- project-based output folders
- capability discovery endpoint
- consistent operation metadata in responses

## Recommended next priorities

1. **Piper voice provider** for fast CPU-friendly voice lines and narration.
2. **ComfyUI image provider** using saved API workflow JSON files.
3. **Image-to-image and upscaling** through ComfyUI or Diffusers instead of custom model orchestration.
4. **Reusable rembg sessions for folder batches** after batch usage is confirmed.
5. **Audio generation batches** for NPC voice lines and sound-effect prompt lists.
6. **Generation metadata sidecars** containing prompt, preset, provider, model, and seed.
7. **A small local web page** only after CLI and API workflows stabilize.

## Features intentionally deferred

- database-backed asset catalog
- task queue and worker system
- authentication
- cloud deployment configuration
- multi-user projects
- complex inheritance-based provider frameworks
- automated GitHub Actions

These would add operational cost without improving the current personal workflow.
