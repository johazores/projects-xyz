# Usage

## Start the studio

```bash
python -m pip install -r requirements.txt
python -m app
```

Open `http://127.0.0.1:8000/docs`.

## Local runtime

```text
submit job
→ save it in SQLite
→ run it on the single worker
→ unload the previous heavyweight model
→ load the requested model
→ record progress, timing, and VRAM
→ write artifacts and a manifest
```

Only one GPU-heavy model is active at a time.

## Inspect hardware and benchmarks

```bash
curl http://127.0.0.1:8000/system
curl http://127.0.0.1:8000/system/gpu
curl http://127.0.0.1:8000/system/benchmarks
```

Benchmarks are stored locally in `data/benchmarks.jsonl`. Prompts and script text are not copied into benchmark records.

## Install video support

Install a CUDA-enabled PyTorch build first, then:

```bash
python -m pip install -r requirements-video.txt
```

### External Q8 backend

The fastest RTX 4060-class text-to-video path uses a separate patched Q8 environment. Configure:

```text
LTX_Q8_REPO_PATH=C:/models/q8-ltx-video
LTX_Q8_PYTHON=C:/models/q8-ltx-video/.venv/Scripts/python.exe
```

The folder must contain `inference.py`. This backend is text-to-video only and follows the seed behavior of that external script.

### Diffusers backend

When the Q8 environment is not configured, the adapter uses official Diffusers pipelines. It supports text-to-video and image-to-video with:

- FP8 layerwise storage when supported
- BF16 computation
- VAE tiling
- group or model CPU offloading
- automatic retry at 512×288, 49 frames, and fewer steps after a CUDA out-of-memory error

The default 8GB profile is 576×320, 65 frames, 20 steps, and batch size one. Real timing and peak VRAM depend on the installed versions and are recorded automatically.

## Direct queued image generation

```bash
curl -X POST http://127.0.0.1:8000/image/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a cinematic local AI workstation",
    "project": "demo",
    "count": 2,
    "width": 1024,
    "height": 576,
    "seed": 42
  }'
```

`/image/generate-batch` creates one queued job per prompt. The former SVG prompt-card path has been removed.

## Direct LTX video generation

Text-to-video:

```bash
curl -X POST http://127.0.0.1:8000/video/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "slow cinematic camera movement through a local AI studio",
    "project": "video-test",
    "width": 576,
    "height": 320,
    "num_frames": 65,
    "steps": 20
  }'
```

Image-to-video uses the same endpoint with `input_path`. The external Q8 backend is bypassed for image-to-video, so the Diffusers backend is required.

## AI Short workflow

```bash
curl -X POST http://127.0.0.1:8000/workflows/youtube.ai-short \
  -H "Content-Type: application/json" \
  -d '{
    "script": "This entire short was prepared using local open-source models.",
    "project": "local-short",
    "scenes": [
      {
        "prompt": "a developer using a powerful local AI workstation",
        "text": "Local generation starts with a script"
      },
      {
        "prompt": "a vertical video timeline filled with images and subtitles",
        "text": "The application assembles the final video"
      }
    ],
    "use_motion": true,
    "fallback_to_stills": true,
    "burn_subtitles": false
  }'
```

Pipeline:

```text
Kokoro or Bark narration
→ normalized audio and measured duration
→ sequential Sana scene images
→ optional LTX image-to-video per scene
→ automatic still-image fallback
→ vertical FFmpeg normalization and concatenation
→ optional faster-whisper subtitles
→ narration mux
→ optional subtitle burn-in
→ final MP4 and manifest
```

A failed LTX scene disables motion for the remaining scenes and continues with still images when fallback is enabled.

## Inspect jobs

```bash
curl http://127.0.0.1:8000/jobs
curl http://127.0.0.1:8000/jobs/JOB_ID
curl -X DELETE http://127.0.0.1:8000/jobs/JOB_ID
curl -X POST http://127.0.0.1:8000/models/unload
```

Cancellation is cooperative. A running model call or FFmpeg process reaches its next checkpoint before cancellation completes.

## RTX 4060 Ti rules

- Keep diffusion and video batch size at one.
- Generate video at 480p-class resolution first.
- Prefer short motion clips and assemble longer videos with FFmpeg.
- Keep `fallback_to_stills` enabled for daily production.
- Leave 0.5–1GB VRAM headroom.
- Use benchmark history from the actual target machine instead of assumed timings.
