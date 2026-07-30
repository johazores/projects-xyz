# AI Media Processing Toolkit

A local-first Python toolkit for practical audio, image, and video work.

The repository is designed for daily YouTube production, indie game asset creation, rapid prototyping, and experimentation with local models. It keeps each media project independently usable while providing one optional FastAPI entry point.

## What is useful today

| Project | Practical capabilities |
| --- | --- |
| [`audio-process`](audio-process/) | Generate audio, convert, normalize, clean spoken audio, transcribe, and create SRT subtitles |
| [`image-process`](image-process/) | Generate images, apply prompt presets, batch prompts, and remove backgrounds locally |
| [`video-process`](video-process/) | Prepare generation requests, resize videos for common formats, and extract frames |
| [`media-process-api`](media-process-api/) | Use the same workflows through one local HTTP API |

The generation providers are still intentionally small. The useful local processing commands do real work through FFmpeg, faster-whisper, and rembg.

## Recommended setup

Use Python 3.11 for the simplest installation across all optional tools.

```bash
git clone https://github.com/johazores/projects-xyz.git
cd projects-xyz
```

Install FFmpeg and confirm it is available:

```bash
ffmpeg -version
```

Each project has its own installation instructions. Optional model dependencies are installed only when needed.

## Daily workflow examples

Create subtitles for a YouTube video:

```bash
cd audio-process
python -m pip install -r requirements-transcription.txt
python cli.py transcribe ../recording.mp4 --format srt --model small
```

Clean recorded voice audio:

```bash
python cli.py enhance ../voice-recording.wav
```

Generate a batch of game asset concepts with a preset:

```bash
cd ../image-process
python cli.py batch examples/game-assets.txt --preset pixel-art
```

Remove an image background:

```bash
python -m pip install -r requirements-background.txt
python cli.py remove-background ../character.png
```

Resize a video for a vertical short:

```bash
cd ../video-process
python cli.py resize ../clip.mp4 --preset shorts
```

Extract reference frames:

```bash
python cli.py frames ../clip.mp4 --fps 1
```

## Local API

```bash
cd media-process-api
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

Optional tools used by API operations must be installed in the same virtual environment:

```bash
python -m pip install -r ../audio-process/requirements-transcription.txt
python -m pip install -r ../image-process/requirements-background.txt
```

## Output organization

CLI commands write to the current media project's `outputs/` folder unless `--output-dir` is supplied.

API requests may include a `project` value. Outputs are then grouped automatically:

```text
media-process-api/outputs/my-youtube-video/audio/
media-process-api/outputs/my-youtube-video/image/
media-process-api/outputs/my-youtube-video/video/
```

## Documentation

- [Practical toolkit review](docs/practical-toolkit-review.md)
- [Daily workflows](docs/practical-workflows.md)
- [Architecture](docs/architecture.md)
- [Development guide](docs/development-guide.md)
- [Coding standards](docs/coding-standards.md)
- [Roadmap](docs/roadmap.md)
- [Design decisions](docs/design-decisions.md)
- [Initial repository review](docs/review-report.md)

## Principles

- Prefer useful workflows over feature count.
- Keep local processing available without cloud infrastructure.
- Keep optional model dependencies isolated.
- Add provider integrations only when they can be tested.
- Prefer clear subprocess or function calls over framework-heavy orchestration.
- Add queues, databases, and user interfaces only when a real workflow requires them.

## License

MIT. See [LICENSE](LICENSE).
