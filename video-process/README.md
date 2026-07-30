# Video Process

A minimal foundation for AI video generation workflows.

The built-in `demo` provider writes a structured generation request manifest instead of pretending to create an AI video. Real video services commonly require asynchronous submission, polling, and download steps; those details will be added with the first tested provider.

## Architecture

```text
cli.py -> config.py -> main.py -> providers/
                         |
                         -> utils/
```

See [docs/architecture.md](docs/architecture.md).

## Requirements

- Python 3.10 or newer
- No dependencies for the demo provider
- Provider-specific SDKs only when a real provider is added

## Installation

```bash
cd video-process
python -m venv .venv
python -m pip install -r requirements.txt
```

## Configuration

Copy `config.json.example` to `config.json` and manage normal settings there.

### Environment variables

| Variable | Purpose |
| --- | --- |
| `VIDEO_PROCESS_CONFIG` | Optional path to the JSON configuration file |
| `VIDEO_API_KEY` | Secret used by a future provider |

## CLI usage

```bash
python cli.py generate --prompt "A slow camera move through a neon city"
```

Use a different output folder:

```bash
python cli.py generate \
  --prompt "Ocean waves at sunrise, cinematic wide shot" \
  --output-dir generated
```

The demo provider creates a JSON request artifact in `outputs/`.

## Examples

- [Sample prompts](examples/prompts.txt)
- [Example request artifact](examples/example-video-request.json)

## Logging, errors, and retries

The CLI reports submission progress and the saved artifact. Retry behavior is controlled through JSON configuration. Provider and configuration errors return a non-zero exit code.

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md).

## Future providers

The provider layer can later support OpenAI video generation, Runway, Pika, Luma, Kling, Veo, and future providers. Each integration should own its submission, polling, status mapping, and download logic.

## Future improvements

- Add the first tested video provider
- Add asynchronous job polling
- Add timeout and cancellation handling
- Save provider job IDs and generation metadata
- Add image-to-video inputs where supported
- Add webhook support only if the toolkit becomes a hosted service
