# Video Architecture

```text
CLI -> config -> main
                  ├── generation provider
                  └── FFmpeg utilities
                       ├── resize and pad
                       └── frame extraction
```

Resize presets are a small dictionary in `main.py`. A configuration framework is unnecessary for four stable local formats.

Frame extraction writes PNG files plus one JSON manifest. Returning the manifest keeps CLI and API output handling consistent without creating a special directory response type.

A real video generation provider should own submission, polling, timeout handling, download, and provider-specific errors.
