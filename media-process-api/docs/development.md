# Development Guide

## Start with the media CLI

The API is a thin transport layer. Debug generation in the relevant media project first:

```bash
cd image-process
python cli.py generate --prompt "A clean test image"
```

After that succeeds, test the API endpoint.

## Run with reload

```bash
cd media-process-api
uvicorn app.main:app --reload
```

## Manual validation

```bash
python -m compileall app ../audio-process ../image-process ../video-process
```

Check discovery endpoints:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/providers
curl http://127.0.0.1:8000/models
```

Generate one artifact for every media type using [../examples/requests.http](../examples/requests.http).

## Boundaries

Keep in the API:

- HTTP request and response models
- route definitions
- local server settings
- CLI invocation
- consistent output metadata

Keep in the media projects:

- provider selection
- model or API integration
- generation logic
- provider retries
- output naming
- media-specific processing

## Adding dependencies

Add a dependency to `media-process-api/requirements.txt` only when the API itself imports it. Provider dependencies should remain in the relevant media project.

## Coding style

- Prefer synchronous route functions while work is performed by blocking subprocesses.
- Use explicit lists for subprocess arguments.
- Never build shell command strings from request values.
- Keep service functions small.
- Avoid a repository-wide shared package until repeated code creates a real maintenance issue.
