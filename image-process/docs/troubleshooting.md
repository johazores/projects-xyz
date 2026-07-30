# Image Troubleshooting

## The SVG does not open

Use a modern browser or image editor with SVG support.

## The config file fails to load

Confirm the file is valid JSON and uses only keys from `config.json.example`.

## A negative prompt appears to do nothing

The demo provider only displays the negative prompt. Real providers may ignore it when their API does not support the feature.

## A provider is unknown

Only `demo` is included initially. Register additional providers in `providers/__init__.py` after implementing them.
