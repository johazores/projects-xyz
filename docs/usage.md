# Usage

## Start the studio

```bash
python -m pip install -r requirements.txt
python -m app
```

The API documentation is available at `http://127.0.0.1:8000/docs`.

## Job lifecycle

Every model or workflow job follows this process:

```text
submit
→ queued in SQLite
→ picked by the single worker
→ current heavy model is unloaded when necessary
→ required model is loaded
→ progress is saved
→ artifacts and a manifest are written
→ job completes or fails with a readable error
```

Jobs survive an application restart. A job that was marked as running is moved back to queued when the worker starts again.

## Inspect models

```bash
curl http://127.0.0.1:8000/models
curl http://127.0.0.1:8000/models/active
```

Unload the current model:

```bash
curl -X POST http://127.0.0.1:8000/models/unload
```

Only unload manually while no job is running.

## Generic model job

```bash
curl -X POST http://127.0.0.1:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "model",
    "target": "speech.kokoro",
    "payload": {
      "text": "This narration is generated locally.",
      "voice": "af_heart",
      "project": "demo"
    }
  }'
```

## Generic workflow job

```bash
curl -X POST http://127.0.0.1:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "workflow",
    "target": "youtube.social-clip-prep",
    "payload": {
      "input_path": "C:/videos/source.mp4",
      "project": "episode-01",
      "preset": "shorts",
      "transcribe": true
    }
  }'
```

## Check or cancel a job

```bash
curl http://127.0.0.1:8000/jobs/JOB_ID
curl -X DELETE http://127.0.0.1:8000/jobs/JOB_ID
```

Cancellation is cooperative. A model operation stops when it reaches the next progress checkpoint; FFmpeg subprocesses currently finish their active operation before cancellation is applied.

## Output organization

```text
outputs/
  project-name/
    audio/
    image/
    video/
    workflow/
```

Workflow manifests include the request, generated artifact paths, and creation time. Model-specific seeds and revisions will be added when the Sana and LTX adapters are implemented.

## RTX 4060 Ti operating rules

- Run one GPU job at a time.
- Keep diffusion and video batch size at one.
- Use 480p generation for video and upscale only selected clips.
- Use quantized model profiles where available.
- Keep at least 0.5–1GB of VRAM free.
- Do not manually load multiple heavyweight models.
