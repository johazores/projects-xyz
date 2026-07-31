# Usage

## Start the API

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app
```

Open `http://127.0.0.1:8000/docs`.

## Optional local tools

```bash
python -m pip install -r requirements-local.txt
```

This enables faster-whisper transcription and rembg background removal. Bark is separate because it needs a compatible PyTorch install:

```bash
python -m pip install -r requirements-bark.txt
```

## Main endpoints

- `POST /audio/generate`
- `POST /audio/convert`
- `POST /audio/normalize`
- `POST /audio/enhance`
- `POST /audio/trim`
- `POST /audio/transcribe`
- `POST /image/generate`
- `POST /image/generate-batch`
- `POST /image/remove-background`
- `GET /image/presets`
- `POST /video/generate`
- `POST /video/resize`
- `POST /video/frames`

File-processing endpoints accept a local `input_path`. Use the optional `project` field to group outputs by project.

## Output layout

```text
outputs/
  project-name/
    audio/
    image/
    video/
```

Without a project value, files are written directly under `outputs/audio`, `outputs/image`, or `outputs/video`.

See `examples/requests.http` for copy-paste requests.
