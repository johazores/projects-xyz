# Audio Process

The reference implementation for the AI Media Processing Toolkit.

It provides a dependency-free demo generator, an optional Bark provider, and FFmpeg commands for conversion, normalization, and trimming.

## Architecture

```text
cli.py -> config.py -> main.py -> providers/
                         |
                         -> utils/ffmpeg.py
                         -> utils/files.py
                         -> utils/retry.py
```

See [docs/architecture.md](docs/architecture.md) for details.

## Requirements

- Python 3.10 or newer
- FFmpeg for `convert`, `normalize`, and `trim`
- Optional Bark dependencies for real text-to-audio generation

## Installation

```bash
cd audio-process
python -m venv .venv
```

Activate the environment, then install the base requirements:

```bash
python -m pip install -r requirements.txt
```

For Bark:

```bash
python -m pip install -r requirements-ai.txt
```

Install a compatible PyTorch build separately for your operating system and GPU.

## Configuration

Copy the example:

```bash
cp config.json.example config.json
```

Windows PowerShell:

```powershell
Copy-Item config.json.example config.json
```

Normal settings are stored in `config.json`. The built-in defaults work without a file.

### Environment variables

| Variable | Purpose |
| --- | --- |
| `AUDIO_PROCESS_CONFIG` | Optional path to the JSON configuration file |
| `AUDIO_API_KEY` | Reserved for provider secrets |

Non-secret runtime settings should remain in the JSON configuration.

## CLI usage

Generate a local demo WAV:

```bash
python cli.py generate --prompt "A calm notification tone"
```

Use Bark:

```bash
python cli.py generate --provider bark --prompt "Welcome to the media toolkit"
```

Convert to MP3:

```bash
python cli.py convert path/to/input.wav
```

Normalize audio:

```bash
python cli.py normalize path/to/input.wav
```

Trim audio:

```bash
python cli.py trim path/to/input.wav --start 2 --duration 5
```

Use a custom configuration file:

```bash
python cli.py --config config.json generate --prompt "Soft rain ambience"
```

## Examples

- [Sample prompts](examples/prompts.txt)
- [Example output metadata](examples/example-output.json)

Generated files are written to `outputs/` and ignored by Git.

## Logging, progress, and retries

The CLI logs the selected operation and final path. Provider generation is retried according to `max_retries` and `retry_delay_seconds`. Validation and FFmpeg failures return a readable error and a non-zero exit code.

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md).

## Future improvements

- Add tested cloud audio providers
- Add prompt-file batch generation
- Save generation metadata beside each output
- Add optional seed and voice controls
- Reuse loaded local models during batch sessions
