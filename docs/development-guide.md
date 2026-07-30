# Development Guide

## Recommended environment

Use Python 3.11 for the full practical toolkit and install FFmpeg.

Base projects keep optional dependencies separate:

```bash
python -m pip install -r audio-process/requirements-transcription.txt
python -m pip install -r image-process/requirements-background.txt
```

Install only the features being used.

## Adding a generation provider

1. Add one file under the relevant `providers/` folder.
2. Implement the existing protocol.
3. Register it in `providers/__init__.py`.
4. Add only its required dependency.
5. Test through the media CLI.
6. Add model metadata to the API catalog.

## Adding a practical operation

1. Prefer a focused utility function.
2. Add orchestration in the media project's `main.py`.
3. Add one CLI command.
4. Add an API service and route only when HTTP access is useful.
5. Update examples and troubleshooting.

Do not create a provider class for a fixed operation such as resizing or transcription unless multiple interchangeable implementations actually exist.

## Validation

```bash
python -m compileall audio-process image-process video-process media-process-api/app
python audio-process/cli.py --help
python image-process/cli.py --help
python video-process/cli.py --help
```

Also test:

- one audio enhancement
- one TXT or SRT transcription
- one image preset batch
- one background removal
- one video resize
- one frame extraction
- the corresponding API routes

## Git workflow

- branch: `feat/<feature-name>`
- focused Conventional Commits
- create a pull request
- merge directly into `master`
- no GitHub Actions during rapid development
- no co-author or generated attribution
