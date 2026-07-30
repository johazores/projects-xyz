# Image Process

A simple image generation and asset-preparation toolkit.

## Capabilities

- provider-based text-to-image generation
- negative prompts
- reusable prompt presets
- prompt-file batch generation
- local background removal with rembg
- organized output folders

The built-in demo provider still exists for testing the pipeline. Practical image generation should be added through a tested local provider such as ComfyUI or Diffusers.

## Installation

```bash
cd image-process
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

For background removal, use Python 3.11 to 3.13 and install:

```bash
python -m pip install -r requirements-background.txt
```

## Prompt presets

List presets:

```bash
python cli.py presets
python cli.py presets --json
```

Included presets:

- `youtube-thumbnail`
- `game-character`
- `pixel-art`
- `item-icon`
- `environment-concept`

Presets are stored in `presets.json` and use `{prompt}` as the insertion point.

## CLI examples

Generate one image with a preset:

```bash
python cli.py generate \
  --prompt "a forest guardian with an ancient wooden mask" \
  --preset game-character
```

Generate a batch from a text file:

```bash
python cli.py batch examples/game-assets.txt --preset pixel-art
```

Blank lines and lines beginning with `#` are ignored.

Remove a background:

```bash
python cli.py remove-background character.png
python cli.py remove-background character.png --model isnet-general-use
```

Every generated path is printed to standard output.

## Adding a real image provider

1. Add one provider module under `providers/`.
2. Implement the existing `generate` contract.
3. Register the provider in `providers/__init__.py`.
4. Test it through the CLI before exposing it through the API.

For local workflows, prefer a thin ComfyUI API adapter or a focused Diffusers provider rather than rebuilding a model manager.

## Troubleshooting

- rembg downloads its selected model on first use.
- CPU background removal can be slow on large images.
- Keep prompt batches small until the selected generation provider is tested for memory use.

See [docs/troubleshooting.md](docs/troubleshooting.md).
