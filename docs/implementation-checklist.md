# Implementation Checklist

Source of truth for the local AI content studio targeting an RTX 4060 Ti 8GB.

## Phase 1 — Runtime foundation

- [x] One FastAPI application, SQLite queue, and one serialized worker.
- [x] Replaceable model registry and one-active-model lifecycle.
- [x] Progress, cancellation, recovery, readable failures, and manifests.
- [x] Kokoro, faster-whisper, and Bark adapters.
- [x] Narration and social clip preparation workflows.
- [ ] Validate speech models on the target RTX 4060 Ti.

## Phase 2 — Image production

- [x] Sana 1.6B INT4 generation and sequential variations.
- [x] Seed, size, steps, guidance, and negative prompts.
- [x] SDXL inpainting with CPU offload and VAE tiling.
- [x] Replace the SVG route with queued model submission.
- [x] BiRefNet Lite, Real-ESRGAN NCNN, and Florence-2.
- [x] Complete thumbnail workflow with exact Pillow text.
- [ ] Validate real image inference and VRAM on the target machine.

## Phase 3 — Video production

- [x] Implement `video.ltx-q8` with 480p-first defaults.
- [x] Support text-to-video and image-to-video jobs.
- [x] Keep batch size one and short generated shots.
- [x] Add automatic OOM retry with lower resolution, frames, and steps.
- [x] Add an external Ada-optimized Q8 backend and a Diffusers fallback.
- [x] Implement a complete `youtube.ai-short` workflow.
- [x] Add still-image fallback when motion is unavailable.
- [x] Align scene duration to generated narration.
- [ ] Add optional frame interpolation.
- [ ] Add explicit human approval metadata for selected clips.
- [ ] Validate LTX on the target RTX 4060 Ti and record real generation times.

## Phase 4 — Music, sound, and expressive voices

- [x] Integrate ACE-Step 1.5 through its official local REST server.
- [x] Integrate Stable Audio Small-SFX through its local CLI.
- [x] Add Chatterbox Turbo and Multilingual V3.
- [x] Add revocable, reference-file-bound consent records.
- [x] Add reusable music, transition, notification, and SFX presets.
- [x] Add duration, loudness, and clipping-risk validation.

## Phase 5 — Creator workflows

- [x] Thumbnail generator.
- [x] AI Shorts generator.
- [ ] Faceless long-form video workflow.
- [ ] Documentary and history workflow.
- [ ] Storytelling and comic workflow.
- [ ] Product showcase workflow.
- [ ] Educational and tech tutorial workflow.
- [x] Podcast workflow.
- [ ] Long-video-to-social-clips workflow with highlight selection.

## Phase 6 — Reliability and usability

- [x] GPU capability and VRAM diagnostics.
- [x] Automatic local model timing and peak-memory benchmark records.
- [x] Add disk-space, FFmpeg, model availability, and cache readiness checks.
- [x] Add durable project runs and resumable model checkpoints.
- [x] Add dry-run-first project artifact and optional model-cache cleanup.
- [x] Protect active projects and configured cleanup roots.
- [x] Add standard-library unit tests for resume, cleanup, readiness, and presets.
- [ ] Add 8GB, 16GB, and 24GB benchmark presets.
- [ ] Add generated-output previews.
- [ ] Add full workflow integration tests using installed local models.
- [ ] Add a small local web interface after workflows stabilize.
