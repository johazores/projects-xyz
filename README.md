# AI Media Toolkit

A local FastAPI studio for creating YouTube images, videos, narration, music, sound effects, podcasts, and Shorts with open-source models.

The runtime targets one RTX 4060 Ti 8GB workstation. GPU-heavy jobs are serialized, only one in-process model stays loaded, and each model run records local timing and VRAM information when available.

## Working capabilities

Runtime:

- persistent SQLite job queue
- resumable project runs with durable model checkpoints
- one serialized GPU worker
- automatic model swapping and unloading
- progress, cancellation, restart recovery, and readable failures
- GPU, disk, executable, and model readiness checks
- dry-run-first project and cache cleanup
- append-only benchmark history
- reproducible workflow manifests
- consent records for every cloned reference voice

Local models and backends:

- Kokoro, Bark, faster-whisper, and Chatterbox
- ACE-Step music and Stable Audio Small-SFX
- Sana, SDXL inpainting, Florence-2, BiRefNet, and Real-ESRGAN
- LTX-Video through an external Q8 backend or the Diffusers low-VRAM path

Creator workflows:

- `youtube.narration`
- `youtube.social-clip-prep`
- `youtube.thumbnail`
- `youtube.ai-short`
- `youtube.podcast`

## Quick start

```bash
git clone https://github.com/johazores/projects-xyz.git
cd projects-xyz

python -m venv .venv
source .venv/bin/activate
# Windows: .\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
python -m app
```

Open `http://127.0.0.1:8000/docs`.

## Resume a failed workflow

Every workflow job receives a `project_run_id`. Inspect and resume it with:

```bash
curl http://127.0.0.1:8000/projects/runs/PROJECT_RUN_ID
curl -X POST http://127.0.0.1:8000/projects/runs/PROJECT_RUN_ID/resume
```

Completed model steps are reused only while their output artifacts still exist. Missing files cause that step to run again.

## Readiness and cleanup

```bash
curl http://127.0.0.1:8000/system/readiness
curl http://127.0.0.1:8000/system/storage
```

Cleanup previews are non-destructive by default:

```bash
curl -X POST http://127.0.0.1:8000/system/cleanup \
  -H "Content-Type: application/json" \
  -d '{"project":"local-ai-short","include_project_runs":true}'
```

Run the same request with `"dry_run": false, "confirm": true` only after reviewing the returned paths. Active projects are always rejected.

## Audio presets

```bash
curl http://127.0.0.1:8000/audio-ai/presets
```

Music and sound-effect requests accept preset names such as `technology-bed`, `documentary-bed`, `interface-whoosh`, and `soft-transition`.

## Main API groups

```text
/jobs          queued work and status
/projects      durable workflow runs and resume controls
/models        model availability and unloading
/workflows     complete creator pipelines
/system        readiness, storage, cleanup, GPU, and benchmarks
/voices        cloned-voice consent records
/audio-ai      queued speech, music, sound effects, and presets
/audio         direct audio utilities
/image         queued image jobs and presets
/video         queued LTX generation and FFmpeg utilities
/outputs       generated local artifacts
```

## Validation

```bash
python -m unittest -v tests.test_project_reliability
```

## Documentation

- [Usage guide](docs/usage.md)
- [Implementation checklist](docs/implementation-checklist.md)
- [Roadmap](docs/roadmap.md)
- [Request examples](examples/requests.http)

## License

Application source: MIT. Model weights, custom kernels, and third-party executables retain their own licenses. Review each model license before publishing or monetizing generated work.
