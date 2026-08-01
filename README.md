# AI Media Toolkit

One local FastAPI application for creating YouTube media with open-source models.

The runtime targets a single RTX 4060 Ti 8GB workstation. GPU-heavy jobs run one at a time, only one model stays loaded, and every model run records local timing and VRAM information when available.

## What works

Runtime:

- persistent SQLite job queue
- one serialized GPU worker
- automatic model swapping and unloading
- progress, cancellation, restart recovery, and readable failures
- GPU and VRAM diagnostics
- append-only local benchmark history
- reproducible workflow manifests

Queued local models:

- Kokoro, faster-whisper, and Bark
- Sana 1.6B INT4 and SDXL inpainting
- Florence-2 and BiRefNet Lite
- Real-ESRGAN NCNN
- LTX-Video with an external Q8 backend or an official Diffusers low-VRAM fallback

Creator workflows:

- `youtube.narration`
- `youtube.social-clip-prep`
- `youtube.thumbnail`
- `youtube.ai-short`

## Quick start

```bash
git clone https://github.com/johazores/projects-xyz.git
cd projects-xyz

python -m venv .venv
source .venv/bin/activate
# Windows: .\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
python -m app
```

Open `http://127.0.0.1:8000/docs`.

## Optional model groups

Install only the capabilities you need after installing a compatible CUDA-enabled PyTorch build:

```bash
python -m pip install -r requirements-speech.txt
python -m pip install -r requirements-image.txt
python -m pip install -r requirements-vision.txt
python -m pip install -r requirements-video.txt
```

Sana INT4 requires the official Nunchaku wheel matching Python, PyTorch, CUDA, and the operating system. Real-ESRGAN uses its official NCNN Vulkan executable.

LTX has two local backends:

1. Configure `LTX_Q8_REPO_PATH` and `LTX_Q8_PYTHON` for the patched Ada-optimized Q8 environment.
2. Leave them empty to use the official Diffusers backend with FP8 layerwise casting, VAE tiling, and CPU or group offloading.

## Create an AI Short

```bash
curl -X POST http://127.0.0.1:8000/workflows/youtube.ai-short \
  -H "Content-Type: application/json" \
  -d '{
    "script": "Local AI tools can now create a complete short on one computer.",
    "project": "local-ai-short",
    "scenes": [
      {"prompt": "a cinematic workstation running local AI models"},
      {"prompt": "a vertical video timeline with generated media"}
    ],
    "use_motion": true,
    "fallback_to_stills": true
  }'
```

The workflow creates narration, scene images, optional LTX motion clips, a still-image fallback, subtitles when faster-whisper is available, a final vertical MP4, and a manifest.

Check the returned job:

```bash
curl http://127.0.0.1:8000/jobs/JOB_ID
```

## Main API groups

```text
/jobs          queued work and status
/models        local model availability and unloading
/workflows     complete creator pipelines
/system        GPU details and benchmark history
/audio         audio utilities
/image         queued image jobs and presets
/video         queued LTX generation and FFmpeg utilities
/outputs       generated local artifacts
```

## Documentation

- [Usage guide](docs/usage.md)
- [Implementation checklist](docs/implementation-checklist.md)
- [Roadmap](docs/roadmap.md)
- [Request examples](examples/requests.http)

## License

Application source: MIT. Model weights, custom kernels, and third-party executables retain their own licenses.
