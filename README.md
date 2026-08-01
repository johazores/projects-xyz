# AI Media Toolkit

One local FastAPI application for building YouTube media workflows with open-source models.

The application is designed for a single workstation with an RTX 4060 Ti 8GB. Heavy GPU jobs run one at a time, and only one model adapter remains loaded in memory.

## What works

Runtime:

- persistent SQLite jobs
- one serialized GPU worker
- progress, cancellation, restart recovery, and readable errors
- configuration-backed model registry
- automatic model swapping and unloading
- reproducible workflow manifests

Queued local models:

- `speech.kokoro`
- `speech.faster-whisper`
- `audio.bark`
- `image.sana-1.6b-int4`
- `image.sdxl-inpaint`
- `image.birefnet-lite`
- `image.realesrgan-ncnn`
- `vision.florence-2-large`

Creator workflows:

- `youtube.narration`
- `youtube.social-clip-prep`
- `youtube.thumbnail`

LTX-VideoQ8 and ACE-Step remain planned and cannot be queued yet.

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

## Install local image models

Install the CUDA-enabled PyTorch build appropriate for your machine, then:

```bash
python -m pip install -r requirements-image.txt
python -m pip install -r requirements-vision.txt
```

Sana INT4 requires an official Nunchaku wheel matching your Python, PyTorch, CUDA, and operating system. Do not install the unrelated PyPI package named `nunchaku`.

For optional Real-ESRGAN upscaling, download the official `realesrgan-ncnn-vulkan` executable and either add it to `PATH` or set:

```text
REALESRGAN_NCNN_PATH=C:/tools/realesrgan/realesrgan-ncnn-vulkan.exe
```

Review each downloaded model's license before publishing or monetizing generated work.

## Create a thumbnail

```bash
curl -X POST http://127.0.0.1:8000/workflows/youtube.thumbnail \
  -H "Content-Type: application/json" \
  -d '{
    "title": "BUILD AI VIDEOS LOCALLY",
    "prompt": "a creator editing a futuristic video studio, cinematic lighting, strong subject, empty space on the left",
    "project": "local-ai-video",
    "count": 4,
    "seed": 42,
    "subject_path": "C:/photos/creator.png"
  }'
```

The workflow generates candidates sequentially, analyzes and scores them, optionally removes a subject background, optionally upscales the chosen image, and renders exact 1280×720 text with Pillow.

Check the returned job:

```bash
curl http://127.0.0.1:8000/jobs/JOB_ID
```

## Main API groups

```text
/jobs          submit, list, inspect, and cancel queued work
/models        inspect configured models and unload the active model
/workflows     inspect and run complete YouTube workflows
/audio         direct audio utilities
/image         direct image utilities
/video         direct video utilities
/outputs       generated local artifacts
```

## Structure

```text
app/
  adapters/     replaceable local model implementations
  core/         model contracts and registry
  runtime/      SQLite jobs, model manager, and one worker
  workflows/    complete content-creation pipelines
  routes/       FastAPI endpoints
  services/     direct media operations
  utils/        FFmpeg, files, transcription, and image composition
models.json     model profiles and 8GB defaults
data/           local SQLite runtime state
outputs/        generated artifacts and manifests
docs/           usage, checklist, and roadmap
```

## Documentation

- [Usage guide](docs/usage.md)
- [Implementation checklist](docs/implementation-checklist.md)
- [Roadmap](docs/roadmap.md)
- [Request examples](examples/requests.http)

## License

Application source: MIT. Model weights and third-party executables retain their own licenses.
