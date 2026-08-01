# Usage

## Start the studio

```bash
python -m pip install -r requirements.txt
python -m app
```

Open `http://127.0.0.1:8000/docs`.

## Project runs and resume

Workflow submissions automatically create a durable project run under `data/projects/`. The completed job result includes `project_run_id`.

List project runs:

```bash
curl http://127.0.0.1:8000/projects/runs
curl "http://127.0.0.1:8000/projects/runs?project=local-ai-short"
```

Inspect one run:

```bash
curl http://127.0.0.1:8000/projects/runs/PROJECT_RUN_ID
```

Resume a failed or cancelled run:

```bash
curl -X POST http://127.0.0.1:8000/projects/runs/PROJECT_RUN_ID/resume
```

Each model call has a deterministic checkpoint based on the model ID and payload. A checkpoint is reused only when all recorded output paths still exist. FFmpeg assembly is intentionally rerun so final media is rebuilt from verified inputs.

## Readiness

```bash
curl http://127.0.0.1:8000/system/readiness
curl http://127.0.0.1:8000/system/storage
```

Readiness reports:

- output and data directory write access
- FFmpeg and FFprobe availability
- free disk space against `MEDIA_MIN_DISK_FREE_GB`
- implemented and currently available model counts
- configured model cache location and size

Optional configuration:

```env
MEDIA_PROJECT_RUNS_DIR=data/projects
MEDIA_AUDIO_PRESETS_FILE=audio-presets.json
MEDIA_MODEL_CACHE_DIR=C:/Users/name/.cache/huggingface
MEDIA_MIN_DISK_FREE_GB=10
```

## Safe cleanup

Preview project cleanup:

```bash
curl -X POST http://127.0.0.1:8000/system/cleanup \
  -H "Content-Type: application/json" \
  -d '{
    "project": "local-ai-short",
    "include_project_runs": true
  }'
```

Delete only after reviewing the preview:

```bash
curl -X POST http://127.0.0.1:8000/system/cleanup \
  -H "Content-Type: application/json" \
  -d '{
    "project": "local-ai-short",
    "include_project_runs": true,
    "dry_run": false,
    "confirm": true
  }'
```

Cleanup rules:

- active queued or running projects are rejected
- configured root directories are never deleted
- paths outside configured output or cache directories are rejected
- model-cache cleanup requires `MEDIA_MODEL_CACHE_DIR`, `include_model_cache=true`, and confirmation
- cache cleanup removes its contents while preserving the configured cache root

## Audio presets

List presets:

```bash
curl http://127.0.0.1:8000/audio-ai/presets
```

Generate music with a preset:

```bash
curl -X POST http://127.0.0.1:8000/audio-ai/music \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "local AI creator episode",
    "preset": "technology-bed",
    "duration": 30,
    "project": "episode-01"
  }'
```

Generate a transition effect:

```bash
curl -X POST http://127.0.0.1:8000/audio-ai/sound-effect \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "between two scenes",
    "preset": "soft-transition",
    "project": "episode-01"
  }'
```

AI Shorts accept `music_preset` and per-scene `sfx_preset`. Podcasts accept `music_preset`.

## Tests

```bash
python -m unittest -v tests.test_project_reliability
```

The tests cover checkpoint reuse, missing-artifact reruns, resume identity, active-project cleanup protection, model-cache root preservation, readiness output, and preset capability validation.
