# Design Decisions

## Practical operations before more providers

The toolkit now prioritizes transcription, subtitles, cleanup, background removal, resizing, frames, presets, and batching. These solve current workflow problems even before more generation models are integrated.

## CLI projects with an optional API

Each media project stays CLI-first. The API is a thin local entry point and does not replace the CLIs.

## Subprocess API integration

Subprocesses preserve independent projects, isolate optional dependencies, and avoid module-name collisions. Selected local models can move in-process later when repeated loading is proven to be a problem.

## Local paths instead of uploads

The API accepts paths to files already on the developer machine. This avoids multipart dependencies and extra copies of large video files. It also means the API should remain bound to localhost.

## Simple sequential batches

Image batches run sequentially. Parallel execution is deferred until a specific provider and machine have measured memory and rate-limit behavior.

## Presets as JSON

Prompt presets are editable data, not Python classes. They can be versioned, shared, and changed without touching orchestration code.

## FFmpeg for media transformations

FFmpeg already handles the required audio and video operations reliably. Adding separate Python media frameworks would increase dependencies without improving the current workflow.

## Optional heavy dependencies

faster-whisper, rembg, Bark, and future model SDKs remain separate requirement files.

## No automation infrastructure

No queues, databases, authentication, cloud setup, or GitHub Actions are added during active toolkit development.
