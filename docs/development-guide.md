# Development Guide

## Requirements

- Python 3.10 or newer
- FFmpeg only for audio conversion, normalization, and trimming
- Optional provider-specific dependencies when using a real model

## Local setup

Each media project is independent:

```bash
cd audio-process
python -m venv .venv
```

Activate the environment, then install the project requirements:

```bash
python -m pip install -r requirements.txt
```

The base demo providers use only the standard library, so installation is normally immediate.

For the unified local API:

```bash
cd media-process-api
python -m venv .venv
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Configuration workflow

1. Copy `config.json.example` to `config.json`.
2. Change normal settings in `config.json`.
3. Store provider secrets in environment variables.
4. Run the CLI with `--config config.json`, or set the documented config-path environment variable.

## Adding a provider

1. Create one file in the project's `providers/` directory.
2. Implement the method described by `providers/base.py`.
3. Register the provider in `providers/__init__.py`.
4. Add only the dependency required by that provider.
5. Document its settings, environment variables, and limitations.
6. Test failure cases as well as a successful generation.

## Validation

Before committing:

```bash
python -m compileall audio-process image-process video-process media-process-api/app
python audio-process/cli.py --help
python image-process/cli.py --help
python video-process/cli.py --help
cd media-process-api && python -m app
```

Run each demo provider once, then call the three API generation endpoints and confirm outputs are created in the expected folders.

## Git workflow

- Use `feat/<feature-name>` branches.
- Use Conventional Commit messages.
- Keep commits focused.
- Do not add GitHub Actions during the active foundation phase.
- Do not add generated attribution, co-author trailers, or tool signatures.
