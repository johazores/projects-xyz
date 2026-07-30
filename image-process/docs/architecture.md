# Image Architecture

`cli.py` collects the prompt, optional negative prompt, provider override, and output directory.

`config.py` loads dimensions, retry settings, model name, and output defaults.

`main.py` creates the output path and handles retries. Providers receive a complete request and write one image file.

The demo provider writes SVG because SVG is a real image format, works without dependencies, and can be stored as readable source code. A real provider should keep the same method signature and return the downloaded or generated file path.
