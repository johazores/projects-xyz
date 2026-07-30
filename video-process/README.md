# Video Process

A minimal video generation foundation plus practical FFmpeg utilities.

## Capabilities

- provider-based video generation requests
- aspect-safe resizing and padding
- common output presets
- frame extraction
- JSON frame manifests

## Requirements

- Python 3.10 or newer
- FFmpeg for resizing and frame extraction
- provider-specific dependencies only when a real generation provider is added

## Installation

```bash
cd video-process
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
ffmpeg -version
```

## Resize presets

| Preset | Resolution | Typical use |
| --- | --- | --- |
| `youtube` | 1920×1080 | landscape video |
| `shorts` | 1080×1920 | vertical short-form video |
| `square` | 1080×1080 | square social asset |
| `720p` | 1280×720 | smaller preview or prototype |

The input is scaled to fit and padded instead of stretched.

## CLI examples

```bash
python cli.py resize clip.mp4 --preset youtube
python cli.py resize highlight.mp4 --preset shorts
python cli.py frames gameplay.mp4 --fps 1
```

Frame extraction creates:

```text
outputs/gameplay-frames/frame-000001.png
outputs/gameplay-frames/frame-000002.png
outputs/gameplay-frames.json
```

The manifest records the source, frame rate, folder, frame count, and filenames.

The generation command remains available for provider development:

```bash
python cli.py generate --prompt "A slow camera move through a forest village"
```

## Future provider direction

Add a real provider only when its submission, polling, download, and error behavior can be tested. Keep asynchronous logic inside that provider rather than adding a repository-wide job system prematurely.

## Troubleshooting

- Confirm `ffmpeg -version` works.
- Use the `720p` preset for faster prototypes.
- Frame extraction can create many files; start with `--fps 0.5` or `--fps 1`.

See [docs/troubleshooting.md](docs/troubleshooting.md).
