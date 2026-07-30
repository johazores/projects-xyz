# Roadmap

## Foundation — complete

- [x] Review and simplify the original repository
- [x] Establish consistent audio, image, and video projects
- [x] Add CLI, configuration, providers, output management, logging, and retries
- [x] Add a lightweight FastAPI entry point
- [x] Add provider and model discovery

## Practical local workflows — complete

- [x] Add faster-whisper transcription
- [x] Add TXT transcripts and SRT subtitles
- [x] Add spoken-audio enhancement
- [x] Add image prompt presets
- [x] Add image prompt-file batching
- [x] Add local background removal
- [x] Add video resize presets
- [x] Add frame extraction and manifests
- [x] Add project-based API output grouping
- [x] Add API capability discovery

## Next useful integrations

- [ ] Add a tested Piper voice provider for narration and game voice lines
- [ ] Add a tested ComfyUI image provider using saved workflow JSON
- [ ] Add image-to-image through ComfyUI or Diffusers
- [ ] Add local image upscaling through a tested provider
- [ ] Add audio prompt batches for NPC lines and sound effects
- [ ] Add generation metadata sidecars
- [ ] Add reusable rembg sessions for large folder batches

## Later, only when needed

- [ ] Add asynchronous polling for a real video provider
- [ ] Reuse selected local models in-process when startup time becomes a measured problem
- [ ] Add a small local web interface after the API stabilizes
- [ ] Add an asset index only if folders become difficult to manage
- [ ] Add selective GitHub Actions only during stabilization
