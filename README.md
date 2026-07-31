# AI Media Toolkit

One lightweight FastAPI application for local audio, image, and video work.

The repository was intentionally consolidated into a single app. There are no separate media projects, duplicate CLIs, job queues, databases, or cloud requirements.

## What works

### Audio

- Demo tone generation
- Optional Bark text-to-audio
- MP3 conversion
- Loudness normalization
- Spoken-audio enhancement
- Trimming
- Optional faster-whisper transcription and SRT subtitles

### Image

- Prompt presets
- Batch prompt processing
- Local background removal with optional rembg
- A dependency-free SVG prompt-card provider for testing the workflow

### Video

- Request manifest generation
- Resize presets for YouTube, Shorts, square, and 720p
- Frame extraction with a JSON manifest

## Structure

```text
app/
  main.py
  config.py
  models.py
  routes/
  services/
  utils/
outputs/
examples/
docs/
requirements.txt
requirements-local.txt
requirements-bark.txt
presets.json
```

## Quick start

```bash
git clone https://github.com/johazores/projects-xyz.git
cd projects-xyz
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app
```

Open `http://127.0.0.1:8000/docs`.

Optional local processing dependencies:

```bash
python -m pip install -r requirements-local.txt
```

## Example

```bash
curl -X POST http://127.0.0.1:8000/audio/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"menu confirmation sound","provider":"demo","project":"game-prototype"}'
```

Generated files are available through `/outputs/...` and stored locally in the `outputs` directory.

- [Usage guide](docs/usage.md)
- [Roadmap](docs/roadmap.md)
- [Request examples](examples/requests.http)

## Requirements

- Python 3.11 recommended
- FFmpeg for audio and video processing commands
- No cloud account required

## License

MIT. See [LICENSE](LICENSE).
