# AI Media Processing Toolkit

A simple, beginner-friendly collection of Python projects for experimenting with audio, image, and video generation workflows.

The repository is designed as a reusable personal toolkit and portfolio project. Each media project uses the same small set of concepts:

- a configuration file for normal settings
- environment variables only for secrets or bootstrap paths
- a command-line interface
- a provider layer that can be extended later
- output folder management
- logging, progress messages, graceful errors, and retry support
- project-specific examples and documentation

## Project index

| Project | Status | Purpose |
| --- | --- | --- |
| [`media-process-api`](media-process-api/) | Local API | Expose audio, image, and video generation through one lightweight FastAPI server |
| [`audio-process`](audio-process/) | Reference implementation | Generate demo audio, use optional Bark generation, and process audio with FFmpeg |
| [`image-process`](image-process/) | Foundation | Generate prompt-based demo images and prepare provider adapters |
| [`video-process`](video-process/) | Foundation | Create structured video generation requests and prepare provider adapters |

The built-in `demo` providers require only Python. They make the complete workflow easy to test without API keys or large model downloads. Real providers can be added without changing the CLI or orchestration flow.

## Quick start

```bash
git clone https://github.com/johazores/projects-xyz.git
cd projects-xyz

cd audio-process
python cli.py generate --prompt "A calm welcome tone"
```

Try the other projects:

```bash
cd ../image-process
python cli.py generate --prompt "A floating island above soft clouds"

cd ../video-process
python cli.py generate --prompt "A slow camera move through a neon city"
```

Generated files are saved inside each project's `outputs/` directory by default.

Run all three projects through the local API:

```bash
cd ../media-process-api
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation. See the [API README](media-process-api/README.md) for Windows setup, requests, responses, providers, and troubleshooting.

## Repository documentation

- [Architecture overview](docs/architecture.md)
- [Folder structure](docs/folder-structure.md)
- [Development guide](docs/development-guide.md)
- [Contribution guide](docs/contributing.md)
- [Coding standards](docs/coding-standards.md)
- [Roadmap](docs/roadmap.md)
- [FAQ](docs/faq.md)
- [Design decisions](docs/design-decisions.md)
- [Initial repository review](docs/review-report.md)

## Principles

- Prefer readable code over clever code.
- Add an abstraction only when it removes real duplication or supports a clear extension point.
- Keep dependencies small and optional.
- Keep each project independently understandable.
- Preserve a consistent structure across media types.
- Use configuration files for normal runtime settings.
- Use environment variables only for secrets and minimal bootstrapping.

## License

This repository is available under the [MIT License](LICENSE).
