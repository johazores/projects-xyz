# Image Process

A small text-to-image foundation with a consistent CLI, configuration, provider boundary, logging, retry support, and output management.

The built-in `demo` provider creates an SVG prompt card. It is not an AI model; it exists so the complete workflow runs immediately without credentials. Tested AI providers can be added behind the same interface.

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
cd image-process
python -m venv .venv
python -m pip install -r requirements.txt
```

## Configuration

Copy `config.json.example` to `config.json` and change normal settings there.

### Environment variables

| Variable | Purpose |
| --- | --- |
| `IMAGE_PROCESS_CONFIG` | Optional path to the JSON configuration file |
| `IMAGE_API_KEY` | Secret used by a future provider |

## CLI usage

```bash
python cli.py generate --prompt "A floating island above soft clouds"
```

With a negative prompt:

```bash
python cli.py generate \
  --prompt "A clean futuristic workspace" \
  --negative-prompt "clutter, unreadable text"
```

Use a custom output folder:

```bash
python cli.py generate --prompt "Minimal mountain poster" --output-dir generated
```

## Examples

- [Sample prompts](examples/prompts.txt)
- [Example SVG image](examples/example-image.svg)
- [Example output metadata](examples/example-output.json)

## Logging, errors, and retries

The CLI reports progress and the saved output path. Provider failures use the retry settings in the JSON configuration. Invalid settings and unknown providers return a readable error.

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md).

## Future providers

The provider boundary can support services such as OpenAI, Stability AI, Replicate, Hugging Face, local Stable Diffusion, ComfyUI, and future providers. Add integrations only when they can be tested and documented clearly.

## Future improvements

- Add the first tested AI image provider
- Add provider-specific size and quality options
- Save prompt metadata beside each image
- Add batch prompt files
- Add seed support where available
