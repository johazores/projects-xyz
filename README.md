# AI Media Toolkit

A local FastAPI studio for creating YouTube images, videos, narration, music, sound effects, podcasts, and Shorts with open-source models.

The runtime targets one RTX 4060 Ti 8GB workstation. GPU-heavy jobs are serialized, only one in-process model stays loaded, and each model run records local timing and VRAM information when available.

## Working capabilities

Runtime:

- persistent SQLite job queue
- one serialized GPU worker
- automatic model swapping and unloading
- progress, cancellation, restart recovery, and readable failures
- GPU diagnostics and append-only benchmark history
- reproducible workflow manifests
- consent records for every cloned reference voice

Local models and backends:

- Kokoro, Bark, and faster-whisper
- Chatterbox Turbo and Multilingual V3
- ACE-Step 1.5 through its official localhost API
- Stable Audio 3 Small-SFX through its official local CLI
- Sana 1.6B INT4, SDXL inpainting, Florence-2, BiRefNet Lite, and Real-ESRGAN
- LTX-Video through an external Q8 backend or the official Diffusers low-VRAM path

Creator workflows:

- `youtube.narration`
- `youtube.social-clip-prep`
- `youtube.thumbnail`
- `youtube.ai-short`
- `youtube.podcast`

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

## Optional capability groups

Install only what you need after installing a compatible CUDA-enabled PyTorch build:

```bash
python -m pip install -r requirements-speech.txt
python -m pip install -r requirements-image.txt
python -m pip install -r requirements-vision.txt
python -m pip install -r requirements-video.txt
python -m pip install -r requirements-voices.txt
```

ACE-Step and Stable Audio 3 stay in their own official environments to avoid dependency conflicts. Configure their local endpoints or executables in `.env`:

```env
ACESTEP_API_URL=http://127.0.0.1:8001
ACESTEP_API_KEY=
STABLE_AUDIO_CLI=C:/models/stable-audio-3/.venv/Scripts/stable-audio.exe
```

## Create a mixed AI Short

```bash
curl -X POST http://127.0.0.1:8000/workflows/youtube.ai-short \
  -H "Content-Type: application/json" \
  -d '{
    "script": "This Short was created with local open-source AI.",
    "project": "local-ai-short",
    "music_prompt": "subtle futuristic electronic background music, instrumental",
    "scenes": [
      {
        "prompt": "a cinematic local AI workstation",
        "sfx_prompt": "short digital interface whoosh"
      },
      {
        "prompt": "a vertical video timeline filled with generated media"
      }
    ],
    "use_motion": true,
    "fallback_to_stills": true
  }'
```

The workflow creates narration, scene images, optional LTX motion, optional ACE-Step music, optional Stable Audio sound effects, subtitles, a mixed vertical MP4, audio validation, and a manifest.

## Main API groups

```text
/jobs          queued work and status
/models        model availability and unloading
/workflows     complete creator pipelines
/system        GPU details and benchmark history
/voices        cloned-voice consent records
/audio-ai      queued speech, music, and sound effects
/audio         direct audio utilities
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

Application source: MIT. Model weights, custom kernels, and third-party executables retain their own licenses. Review the license of every downloaded model before publishing or monetizing generated work.
