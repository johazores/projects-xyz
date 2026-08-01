# Usage

## Start the studio

```bash
python -m pip install -r requirements.txt
python -m app
```

Open `http://127.0.0.1:8000/docs`.

## Job lifecycle

```text
submit
→ saved in SQLite
→ single worker starts the job
→ previous heavyweight model is unloaded
→ required model is loaded
→ progress and artifacts are saved
→ job completes or fails with a readable error
```

Jobs survive application restarts. Only one GPU-heavy model is active at a time.

## Install image capabilities

```bash
python -m pip install -r requirements-image.txt
python -m pip install -r requirements-vision.txt
```

Install CUDA-enabled PyTorch separately. Install Nunchaku using the official wheel matching your Python, PyTorch, CUDA, and operating system. The package returned by plain `pip install nunchaku` is unrelated.

Set the optional Real-ESRGAN executable:

```text
REALESRGAN_NCNN_PATH=C:/tools/realesrgan/realesrgan-ncnn-vulkan.exe
```

## Thumbnail workflow

```bash
curl -X POST http://127.0.0.1:8000/workflows/youtube.thumbnail \
  -H "Content-Type: application/json" \
  -d '{
    "title": "BUILD AI VIDEOS LOCALLY",
    "prompt": "a creator inside a futuristic local AI video studio, dramatic lighting, clean composition, empty space on the left",
    "project": "local-ai-video",
    "count": 4,
    "width": 1024,
    "height": 576,
    "steps": 20,
    "guidance": 4.5,
    "seed": 42,
    "subject_path": "C:/photos/creator.png"
  }'
```

Process:

```text
Sana INT4 candidates, generated one at a time
→ optional Florence captions
→ deterministic visual and semantic scoring
→ optional Real-ESRGAN upscale
→ optional BiRefNet subject cutout
→ exact Pillow headline composition
→ candidate scores and workflow manifest
```

Florence and Real-ESRGAN are optional. The workflow continues with deterministic visual scoring or normal resizing when they are unavailable. BiRefNet is required only when `subject_path` is supplied.

## Direct queued image jobs

Sana generation:

```bash
curl -X POST http://127.0.0.1:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "model",
    "target": "image.sana-1.6b-int4",
    "payload": {
      "prompt": "a clean technology thumbnail background",
      "project": "thumbnail-test",
      "count": 2,
      "seed": 100
    }
  }'
```

SDXL inpainting:

```bash
curl -X POST http://127.0.0.1:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "model",
    "target": "image.sdxl-inpaint",
    "payload": {
      "input_path": "C:/images/source.png",
      "mask_path": "C:/images/mask.png",
      "prompt": "replace the masked area with a clean studio desk",
      "project": "thumbnail-test"
    }
  }'
```

## Inspect and control jobs

```bash
curl http://127.0.0.1:8000/models
curl http://127.0.0.1:8000/models/active
curl http://127.0.0.1:8000/jobs
curl http://127.0.0.1:8000/jobs/JOB_ID
curl -X DELETE http://127.0.0.1:8000/jobs/JOB_ID
curl -X POST http://127.0.0.1:8000/models/unload
```

Cancellation is cooperative. An active model call or FFmpeg process completes its current operation before the next cancellation checkpoint.

## Output organization

```text
outputs/
  project-name/
    audio/
    image/
    video/
    workflow/
```

Thumbnail workflow runs save all candidates, exact seeds and generation settings, analysis scores, the selected source, optional intermediate assets, the final image, and a JSON manifest.

## RTX 4060 Ti rules

- Keep image and video batch size at one.
- Variations are generated sequentially.
- Stay near 1024×576 or 1024×1024 for image generation.
- Upscale only selected images.
- Leave at least 0.5–1GB VRAM headroom.
- Do not manually load multiple heavyweight models.
