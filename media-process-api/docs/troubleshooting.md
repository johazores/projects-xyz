# Troubleshooting

## `ModuleNotFoundError: No module named app`

Run from `media-process-api`:

```bash
uvicorn app.main:app --reload
```

## Optional operation dependencies are missing

Install them in the API virtual environment because media CLIs are launched with the same Python interpreter:

```bash
python -m pip install -r ../audio-process/requirements-transcription.txt
python -m pip install -r ../image-process/requirements-background.txt
```

## FFmpeg operations fail

Confirm `ffmpeg -version` works in the terminal that starts the API.

## A local input file is not found

Use an absolute path. On Windows, JSON accepts forward slashes:

```json
{"input_path":"C:/media/video.mp4"}
```

## A request times out

Increase:

```text
MEDIA_API_PROCESS_TIMEOUT=7200
```

Restart the API after changing `.env`.

## Output folders are unexpected

Requests with `project` are stored under `outputs/<project>/<media-type>/`. Project names are converted to lowercase safe folder names.

## The output URL does not open

Prefix the returned `output_url` with the server host:

```text
http://127.0.0.1:8000/outputs/episode-12/audio/video-transcript.srt
```
