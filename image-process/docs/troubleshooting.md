# Image Troubleshooting

## Background removal dependencies are missing

Use Python 3.11 to 3.13, then install:

```bash
python -m pip install -r requirements-background.txt
```

## The first background removal is slow

rembg downloads the selected model on first use. Later runs reuse the cached model file.

## A preset is unknown

```bash
python cli.py presets
```

Preset names and templates are stored in `presets.json`.

## A batch creates no files

Confirm the prompt file contains non-empty lines. Lines beginning with `#` are treated as comments.

## Negative prompts appear to do nothing

Support depends on the selected generation provider. The demo provider only displays the prepared prompt information.

## A provider is unknown

Register it in `providers/__init__.py` and test the provider directly through the CLI.
