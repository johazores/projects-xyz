# Video Troubleshooting

## FFmpeg is not found

```bash
ffmpeg -version
```

## Resize is slow

Use `--preset 720p` for prototypes. Encoding time increases with resolution and source duration.

## The resized video has borders

This is expected when source and target aspect ratios differ. Padding preserves the full image instead of stretching or cropping it.

## Too many frames are created

Use a smaller rate:

```bash
python cli.py frames input.mp4 --fps 0.5
```

## No AI video is created

The current generation provider writes an honest request manifest. Add a tested provider before expecting a rendered video.
