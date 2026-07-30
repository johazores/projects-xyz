# Local Media Toolkit

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](docs/development-guide.md)
[![API](https://img.shields.io/badge/api-FastAPI-009688.svg)](media-process-api/README.md)

A local-first Python toolkit for practical audio, image, and video processing.

The repository supports daily content production, indie game asset preparation, rapid prototyping, and experimentation with local models. Each media project remains independently usable, with an optional FastAPI entry point for shared workflows.

> **Status:** Active toolkit development. Core local processing workflows are usable today, while generation providers remain intentionally small and optional.

## Capabilities

| Project | Practical capabilities |
| --- | --- |
| [`audio-process`](audio-process/) | Audio generation, conversion, normalization, spoken-audio cleanup, transcription, and SRT subtitles |
| [`image-process`](image-process/) | Image generation, prompt presets, batch prompts, and local background removal |
| [`video-process`](video-process/) | Generation request preparation, social-format resizing, and frame extraction |
| [`media-process-api`](media-process-api/) | Shared local HTTP API for the same audio, image, and video workflows |

Useful local processing is implemented through FFmpeg, faster-whisper, and rembg. Optional model dependencies are installed only when needed.

## Requirements

- Python 3.11 recommended
- FFmpeg for audio and video processing
- Optional dependencies for transcription, background removal, or generation providers

Confirm FFmpeg is available:

```bash
ffmpeg -version
```

## Installation

```bash
git clone https://github.com/johazores/projects-xyz.git
cd projects-xyz
```

Each project contains its own requirements and setup instructions.

## Usage examples

### Create subtitles

```bash
cd audio-process
python -m pip install -r requirements-transcription.txt
python cli.py transcribe ../recording.mp4 --format srt --model small
```

### Clean recorded voice audio

```bash
python cli.py enhance ../voice-recording.wav
```

### Generate game asset concepts

```bash
cd ../image-process
python cli.py batch examples/game-assets.txt --preset pixel-art
```

### Remove an image background

```bash
python -m pip install -r requirements-background.txt
python cli.py remove-background ../character.png
```

### Resize a vertical video

```bash
cd ../video-process
python cli.py resize ../clip.mp4 --preset shorts
```

### Extract reference frames

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

Open `http://127.0.0.1:8000/docs` for the interactive API.

Optional processing dependencies must be installed in the same environment used by the API:

```bash
python -m pip install -r ../audio-process/requirements-transcription.txt
python -m pip install -r ../image-process/requirements-background.txt
```

## Output organization

CLI commands write to each media project's `outputs/` folder unless `--output-dir` is supplied.

API requests may include a project name:

```text
media-process-api/outputs/my-youtube-video/audio/
media-process-api/outputs/my-youtube-video/image/
media-process-api/outputs/my-youtube-video/video/
```

Generated media, local configuration, virtual environments, model caches, and personal files must not be committed.

## Architecture

The toolkit keeps each media type independent while sharing a small set of design principles:

- CLI commands handle user input and readable errors.
- Processing functions own practical media operations.
- Provider interfaces isolate optional generation backends.
- Configuration files manage normal runtime settings.
- Environment variables are limited to secrets and bootstrap paths.
- The FastAPI application calls the same underlying workflows rather than duplicating processing logic.

Read the [architecture guide](docs/architecture.md) and [design decisions](docs/design-decisions.md).

## Project structure

```text
audio-process/       audio generation and processing
image-process/       image generation and processing
video-process/       video generation preparation and processing
media-process-api/   local FastAPI interface
docs/                architecture, workflows, development, roadmap, and community docs
```

## Development

Start with the [development guide](docs/development-guide.md) and [coding standards](docs/coding-standards.md).

Changes should preserve the local-first design, optional dependency boundaries, clear command behavior, and independent project usability.

## Documentation

- [Documentation index](docs/index.md)
- [Practical workflows](docs/practical-workflows.md)
- [Architecture](docs/architecture.md)
- [Development guide](docs/development-guide.md)
- [Coding standards](docs/coding-standards.md)
- [Roadmap](docs/roadmap.md)
- [Changelog](docs/changelog.md)
- [Contributing](docs/contributing.md)
- [Security policy](docs/security.md)
- [Code of conduct](docs/code-of-conduct.md)

## License

MIT. See [LICENSE](LICENSE).

## Author

Created and maintained by [Johanssen Azores](https://github.com/johazores).
