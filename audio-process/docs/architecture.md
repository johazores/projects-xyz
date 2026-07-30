# Audio Architecture

`cli.py` parses four commands: `generate`, `convert`, `normalize`, and `trim`.

`config.py` loads defaults and optional JSON settings. `main.py` owns orchestration so the same functions can later be called from a web API, desktop app, or batch script without reusing CLI code.

Generation providers implement one small method and declare their output extension. The demo provider writes a deterministic WAV file with only the standard library. The Bark provider imports heavy dependencies only when selected.

FFmpeg operations remain plain utility functions because they do not need provider classes or application state.
