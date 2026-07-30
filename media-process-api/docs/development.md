# Development Guide

## Start with the media CLI

The API is transport and orchestration only. Debug the operation directly first:

```bash
cd audio-process
python cli.py transcribe path/to/video.mp4 --format srt
```

Then test the matching API route.

## Run locally

```bash
cd media-process-api
uvicorn app.main:app --reload
```

## Manual validation

```bash
python -m compileall app ../audio-process ../image-process ../video-process
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/capabilities
curl http://127.0.0.1:8000/providers
curl http://127.0.0.1:8000/image/presets
```

Use `examples/requests.http` to test practical operations.

## Boundaries

Keep in the API:

- request and response models
- routes
- project output grouping
- CLI invocation
- consistent error responses

Keep in the media projects:

- generation providers
- FFmpeg operations
- transcription
- prompt presets
- background removal
- output naming

## Dependencies

Add a dependency to `media-process-api/requirements.txt` only when the API imports it directly. Optional media dependencies must remain in the relevant media project requirement file, even though they are installed into the API environment when the API uses that operation.

## Style

- use synchronous routes while subprocesses are blocking
- pass subprocess arguments as lists
- never use `shell=True` with request values
- keep one service function per operation
- reuse request models only when their fields genuinely match
