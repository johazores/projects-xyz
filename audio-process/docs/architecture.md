# Audio Architecture

`cli.py` exposes generation and practical processing commands:

- `generate`
- `convert`
- `normalize`
- `enhance`
- `transcribe`
- `trim`

`main.py` validates local files, chooses output paths, and calls focused utilities. Generation providers remain separate because they may require large optional model dependencies.

```text
CLI -> config -> main
                  ├── provider generation
                  ├── FFmpeg processing
                  └── faster-whisper transcription
```

FFmpeg and transcription are functions rather than provider classes because they are concrete operations, not interchangeable generation backends.

The transcription model is loaded per command. This is simple and reliable for local use. A persistent model process should be added only if repeated startup time becomes a real bottleneck.
