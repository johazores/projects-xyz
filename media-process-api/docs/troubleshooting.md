# Troubleshooting

## `ModuleNotFoundError: No module named app`

Run the server from `media-process-api`:

```bash
cd media-process-api
uvicorn app.main:app --reload
```

## The API says a media CLI is missing

Keep these folders beside each other at the repository root:

```text
audio-process/
image-process/
video-process/
media-process-api/
```

## Unknown provider

Check:

```bash
curl http://127.0.0.1:8000/providers
```

Then test the provider directly through the corresponding CLI. The provider must be registered in that media project's `providers/__init__.py`.

## Bark dependencies are missing

Install the optional audio dependencies from `audio-process/requirements-ai.txt` and install a compatible PyTorch build for the machine.

The API base requirements intentionally do not install large model libraries.

## A request times out

Increase the local timeout in `.env`:

```text
MEDIA_API_PROCESS_TIMEOUT=1800
```

Restart the server after changing `.env`.

## Output path is unexpected

By default, outputs are stored in:

```text
media-process-api/outputs/audio/
media-process-api/outputs/image/
media-process-api/outputs/video/
```

Set an absolute `MEDIA_API_OUTPUT_DIR` when starting the server from an unusual working directory.

## The output URL does not open

Use the same host and port as the API, followed by the returned `output_url`:

```text
http://127.0.0.1:8000/outputs/image/example.svg
```

## GPU is not used

The API does not choose CPU or GPU. Device selection belongs to the provider configuration in the relevant media project. The demo providers are CPU-only and intentionally lightweight.
