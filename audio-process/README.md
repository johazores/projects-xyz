# Audio Process

Local audio generation, cleanup, conversion, transcription, and subtitle tools.

## Capabilities

- dependency-free demo tone generation
- optional Bark text-to-audio generation
- MP3 conversion
- loudness normalization
- spoken-audio enhancement
- trimming
- local faster-whisper transcription
- TXT transcripts and SRT subtitles

## Requirements

- Python 3.10 or newer; Python 3.11 is recommended for the full toolkit
- FFmpeg for conversion, normalization, enhancement, and trimming
- optional dependencies only for Bark or transcription

## Installation

```bash
cd audio-process
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Install only the optional feature you need:

```bash
python -m pip install -r requirements-ai.txt
python -m pip install -r requirements-transcription.txt
```

## Configuration

```bash
cp config.json.example config.json
```

Important transcription settings:

| Setting | Default | Purpose |
| --- | --- | --- |
| `transcription_model` | `small` | faster-whisper model name |
| `transcription_device` | `auto` | `auto`, `cpu`, or `cuda` |
| `transcription_compute_type` | `default` | CTranslate2 compute type |
| `transcription_language` | `null` | Optional language code |

Environment variables remain limited to `AUDIO_PROCESS_CONFIG` and secrets.

## CLI examples

Generate audio:

```bash
python cli.py generate --prompt "A calm notification tone"
python cli.py generate --provider bark --prompt "Welcome to the channel"
```

Clean spoken audio:

```bash
python cli.py enhance narration.wav
```

The enhancement chain applies a voice-focused high-pass, low-pass, noise reduction, and loudness normalization. Keep the original recording and compare results.

Create subtitles:

```bash
python cli.py transcribe video.mp4 --format srt --model small
```

Create a transcript:

```bash
python cli.py transcribe podcast.wav --format txt --language en
```

Other utilities:

```bash
python cli.py convert input.wav
python cli.py normalize input.wav
python cli.py trim input.wav --start 2 --duration 5
```

Every successful command prints the final absolute output path.

## Output

Files are stored in `outputs/` by default. Use `--output-dir` to organize files by video or game project.

## Troubleshooting

- Confirm `ffmpeg -version` works before using processing commands.
- Install `requirements-transcription.txt` in the same environment used to run the CLI or API.
- Start with the `small` model. Use a smaller model when CPU speed or memory is limited.
- For CUDA errors, try `--device cpu` first to confirm the workflow.

See [docs/troubleshooting.md](docs/troubleshooting.md).
