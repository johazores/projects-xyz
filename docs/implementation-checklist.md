# Implementation Checklist

This checklist is the source of truth for the local AI content studio targeting an RTX 4060 Ti 8GB.

## Phase 1 — Runtime foundation

- [x] One root FastAPI application.
- [x] Configuration-backed model registry and replaceable adapters.
- [x] Persistent SQLite jobs and one serialized GPU worker.
- [x] Progress, cancellation, readable failures, and restart recovery.
- [x] One-active-model lifecycle and explicit unload support.
- [x] Artifact and workflow manifests.
- [x] Model and workflow discovery endpoints.
- [x] Kokoro, faster-whisper, and Bark adapters.
- [x] `youtube.narration` workflow.
- [x] `youtube.social-clip-prep` workflow.
- [ ] Validate speech models on the target RTX 4060 Ti.
- [ ] Record real timings and peak VRAM.

## Phase 2 — Image production

- [x] Implement `image.sana-1.6b-int4` using the official Nunchaku runtime.
- [x] Add seed, size, steps, guidance, and negative prompt controls.
- [x] Generate image variations sequentially with batch size one.
- [x] Implement `image.sdxl-inpaint` with CPU offload and VAE tiling.
- [ ] Replace the old synchronous SVG image route with queued model submission.
- [x] Add BiRefNet Lite background removal.
- [x] Add tiled Real-ESRGAN NCNN upscaling.
- [x] Add Florence-2 captioning and OCR support.
- [x] Implement `youtube.thumbnail` workflow.
- [x] Add exact text composition through Pillow.
- [x] Save candidates, scores, seeds, selected source, and manifest.
- [ ] Validate every real image model on the target RTX 4060 Ti.
- [ ] Record model load time, generation time, and peak VRAM.

## Phase 3 — Video production

- [ ] Implement `video.ltx-q8` with 480p-first defaults.
- [ ] Support text-to-video and image-to-video jobs.
- [ ] Limit generated shots to short clips and batch size one.
- [ ] Add automatic OOM retry with fewer frames or lower resolution.
- [ ] Add optional frame interpolation.
- [ ] Add selected-frame and selected-clip approval metadata.
- [ ] Implement `youtube.ai-short` workflow.
- [ ] Add a still-image fallback when video generation is unavailable.

## Phase 4 — Music, sound, and expressive voices

- [ ] Implement ACE-Step 1.5 using INT8 and CPU offload.
- [ ] Implement Stable Audio small SFX generation.
- [ ] Add Chatterbox as an optional expressive and multilingual TTS provider.
- [ ] Add consent records for every cloned voice.
- [ ] Add music-loop, ambience, transition, and game-SFX presets.
- [ ] Add loudness, clipping, and target-duration validation.

## Phase 5 — Creator workflows

- [x] Thumbnail generator.
- [ ] AI Shorts generator.
- [ ] Faceless video workflow.
- [ ] Documentary and history workflow.
- [ ] Storytelling and comic workflow.
- [ ] Product showcase workflow.
- [ ] Educational and tech tutorial workflow.
- [ ] Podcast workflow.
- [ ] Long-video-to-social-clips workflow with highlight selection.

## Phase 6 — Reliability and usability

- [ ] Add resumable project workflow steps.
- [ ] Add cleanup commands for artifacts and model caches.
- [ ] Add disk-space and model-download checks.
- [ ] Add GPU capability and VRAM detection.
- [ ] Add benchmark presets for 8GB, 16GB, and 24GB GPUs.
- [ ] Add generated-output previews.
- [ ] Add a small local web interface after API workflows stabilize.
- [ ] Add unit tests for adapters, registry, recovery, and cancellation.
- [ ] Add integration tests for every implemented workflow.
