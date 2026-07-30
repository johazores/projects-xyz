# Audio Troubleshooting

## FFmpeg is not found

Install FFmpeg and confirm this works:

```bash
ffmpeg -version
```

Restart the terminal after changing the system path.

## Bark dependencies are missing

Install `requirements-ai.txt`, then install a compatible PyTorch build.

## CUDA was requested but unavailable

Set `"device": "auto"` or `"device": "cpu"` in `config.json`, or install a CUDA-enabled PyTorch build that matches the machine.

## The config file fails to load

Confirm the file contains valid JSON and only keys listed in `config.json.example`.

## Output is not created

Check the final CLI error, confirm the output directory is writable, and run with `"log_level": "DEBUG"` for more detail.
