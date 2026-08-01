# AI Media Toolkit

One local FastAPI application for building YouTube media workflows with open-source models.

The application is designed for a single workstation with an RTX 4060 Ti 8GB. Heavy GPU jobs run one at a time, and only one model adapter remains loaded in memory.

## Current phase

The toolkit now has the runtime foundation required for real local models:

- SQLite job persistence
- one serialized local GPU worker
- progress, cancellation, failure, and restart recovery
- configuration-backed model registry
- automatic model swapping and unloading
- reproducible workflow manifests
- practical YouTube workflow endpoints
- existing direct audio, image-processing, and video-processing endpoints remain available

Implemented queued models:

- `speech.kokoro`
- `speech.faster-whisper`
- `audio.bark`

Configured next models:

- `image.sana-1.5-int4`
- `image.sdxl-inpaint`
- `video.ltx-q8`
- `music.ace-step-1.5`
- `vision.florence-2-large`

Planned models are visible through the API but cannot be queued until their adapters are implemented.

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

## Install local speech models

Install a CUDA-enabled PyTorch build suitable for your system, then:

```bash
python -m pip install -r requirements-speech.txt
```

Kokoro also requires `espeak-ng` on the machine.

Bark remains optional:

```bash
python -m pip install -r requirements-bark.txt
```

## Submit a narration workflow

```bash
curl -X POST http://127.0.0.1:8000/workflows/youtube.narration \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome to my local AI media studio.",
    "project": "channel-intro",
    "model": "speech.kokoro",
    "voice": "af_heart",
    "normalize": true
  }'
```

The endpoint returns a queued job. Check it with:

```bash
curl http://127.0.0.1:8000/jobs/JOB_ID
```

## Prepare a social clip

```bash
curl -X POST http://127.0.0.1:8000/workflows/youtube.social-clip-prep \
  -H "Content-Type: application/json" \
  -d '{
    "input_path": "C:/videos/source.mp4",
    "project": "episode-12",
    "preset": "shorts",
    "transcribe": true,
    "extract_fps": 0.2
  }'
```

This workflow creates a vertical video, optional SRT subtitles, optional reference frames, and a run manifest.

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
  services/     existing direct media operations
  utils/        FFmpeg, files, transcription, and background removal
models.json     model profiles and hardware defaults
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

MIT. See [LICENSE](LICENSE).
