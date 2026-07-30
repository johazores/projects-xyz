# Audio Troubleshooting

## FFmpeg is not found

```bash
ffmpeg -version
```

Restart the terminal after installing or changing the system path.

## Transcription dependencies are missing

```bash
python -m pip install -r requirements-transcription.txt
```

Install them in the same environment used to run the CLI or API.

## Transcription is slow

Start with a smaller model such as `tiny`, `base`, or `small`. Use `--device cpu` to verify the workflow before troubleshooting CUDA.

## CUDA transcription fails

Try:

```bash
python cli.py transcribe input.mp4 --device cpu --format srt
```

If CPU works, review the installed CUDA, cuDNN, and CTranslate2 compatibility before switching back to `cuda`.

## Enhanced audio sounds too filtered

The enhancement preset is tuned for spoken voice. Use `normalize` instead for music or ambience, and always keep the original recording.

## Bark dependencies are missing

Install `requirements-ai.txt`, then install a compatible PyTorch build.

## Configuration fails

Confirm `config.json` is valid JSON and uses only keys from `config.json.example`.
