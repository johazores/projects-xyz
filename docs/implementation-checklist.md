# Implementation Checklist

This checklist is the source of truth for turning the application into a practical local AI content studio for an RTX 4060 Ti 8GB.

## Phase 1 — Runtime foundation

- [x] Keep one root FastAPI application.
- [x] Add a configuration-backed model registry.
- [x] Add replaceable model adapter contracts.
- [x] Add a persistent SQLite job store.
- [x] Add one serialized local GPU worker.
- [x] Add job progress, errors, cancellation, and restart recovery.
- [x] Add one-active-model lifecycle management.
- [x] Add explicit model unload support.
- [x] Add artifact and workflow manifests.
- [x] Add model discovery endpoints.
- [x] Add workflow discovery endpoints.
- [x] Add a queued Kokoro adapter.
- [x] Add a queued persistent faster-whisper adapter.
- [x] Add a queued persistent Bark adapter.
- [x] Add `youtube.narration` workflow.
- [x] Add `youtube.social-clip-prep` workflow.
- [ ] Validate Kokoro, Bark, and large-v3-turbo on the target RTX 4060 Ti machine.
- [ ] Record real timings and peak VRAM in a local benchmark document.

## Phase 2 — Image production

- [ ] Implement `image.sana-1.5-int4` using the official quantized runtime.
- [ ] Add image seed, size, steps, guidance, and negative prompt fields.
- [ ] Add sequential image variation jobs with batch size one.
- [ ] Implement `image.sdxl-inpaint` with CPU offload and VAE tiling.
- [ ] Replace the SVG prompt-card provider as the default image route.
- [ ] Add BiRefNet background removal adapter.
- [ ] Add tiled Real-ESRGAN upscaling adapter.
- [ ] Add Florence-2 captioning and OCR.
- [ ] Implement `youtube.thumbnail` workflow.
- [ ] Add exact text composition through Pillow or SVG instead of diffusion-generated text.

## Phase 3 — Video production

- [ ] Implement `video.ltx-q8` with 480p-first defaults.
- [ ] Support text-to-video and image-to-video jobs.
- [ ] Limit generated shots to short clips and batch size one.
- [ ] Add automatic OOM retry with lower frames or resolution.
- [ ] Add optional frame interpolation.
- [ ] Add selected-frame and selected-clip approval metadata.
- [ ] Implement `youtube.ai-short` workflow.
- [ ] Add a still-image-heavy fallback when video generation is unavailable.

## Phase 4 — Music, sound, and expressive voices

- [ ] Implement ACE-Step 1.5 using INT8 and CPU offload.
- [ ] Implement Stable Audio small SFX generation.
- [ ] Add Chatterbox as an optional expressive and multilingual TTS provider.
- [ ] Add consent records for every cloned voice.
- [ ] Add music-loop, ambience, transition, and game-SFX presets.
- [ ] Add loudness, clipping, and target-duration validation.

## Phase 5 — Complete creator workflows

- [ ] Thumbnail generator.
- [ ] AI Shorts generator.
- [ ] Faceless video workflow.
- [ ] Documentary and history workflow.
- [ ] Storytelling and comic workflow.
- [ ] Product showcase workflow.
- [ ] Educational and tech tutorial workflow.
- [ ] Podcast workflow.
- [ ] Long-video-to-social-clips workflow with automatic highlight selection.

## Phase 6 — Reliability and usability

- [ ] Add project records and resumable workflow steps.
- [ ] Add cleanup commands for old artifacts and model caches.
- [ ] Add disk-space and model-download checks.
- [ ] Add GPU capability and VRAM detection.
- [ ] Add benchmark presets for 8GB, 16GB, and 24GB GPUs.
- [ ] Add generated-output previews.
- [ ] Add a small local web interface only after the API workflows are stable.
- [ ] Add unit tests for adapters, registry, job recovery, and cancellation.
- [ ] Add integration tests for every implemented workflow.
