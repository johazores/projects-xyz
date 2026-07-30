# Coding Standards

## Python

- Use Python 3.11 for the full toolkit.
- Add type hints to public functions and meaningful boundaries.
- Keep functions focused and explicit.
- Prefer standard-library modules and dataclasses when sufficient.
- Raise actionable errors.
- Comment decisions, not obvious syntax.

## Simplicity

- Prefer functions over classes when state is unnecessary.
- Use provider classes only for interchangeable generation backends.
- Keep concrete transformations as focused utilities.
- Avoid dependency injection containers, dynamic plugin loaders, queues, and databases without a current need.
- Keep optional dependencies in separate requirement files.

## Subprocesses

- Pass arguments as lists.
- Do not use `shell=True` with user-controlled values.
- Capture output and return concise errors.
- Print the final absolute artifact path from successful CLI commands.

## Naming

- `snake_case` for files, functions, and variables.
- `PascalCase` for classes and protocols.
- Use operation-specific names such as `resize_video_file` and `transcribe_audio_file`.

## Logging

Use `logging` for progress and diagnostics. Keep CLI errors readable. Do not print stack traces by default.
