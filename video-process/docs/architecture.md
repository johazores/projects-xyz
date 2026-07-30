# Video Architecture

`cli.py` accepts a prompt and optional provider or output overrides.

`config.py` stores duration, aspect ratio, model, retry behavior, and output settings.

`main.py` owns output naming and retries. A provider owns the provider-specific generation lifecycle.

The demo provider writes a request manifest. A real provider will normally:

1. submit a generation request
2. receive a job identifier
3. poll until the job succeeds or fails
4. download the generated media
5. return the local file path

Those steps should remain inside the provider so the CLI stays consistent.
