# Practical Workflows

## YouTube production

### 1. Clean narration

```bash
cd audio-process
python cli.py enhance path/to/narration.wav --output-dir ../media/youtube-video/audio
```

The enhancement chain is intended for spoken voice. Keep the original recording and compare results before publishing.

### 2. Generate subtitles

```bash
python cli.py transcribe path/to/final-video.mp4 \
  --format srt \
  --model small \
  --output-dir ../media/youtube-video/subtitles
```

Use `--format txt` for a plain transcript that can be turned into descriptions, chapters, or captions.

### 3. Prepare thumbnail concepts

```bash
cd ../image-process
python cli.py batch examples/thumbnail-ideas.txt \
  --preset youtube-thumbnail \
  --output-dir ../media/youtube-video/thumbnails
```

### 4. Prepare platform versions

```bash
cd ../video-process
python cli.py resize path/to/final-video.mp4 --preset youtube
python cli.py resize path/to/highlight.mp4 --preset shorts
```

## Indie game asset prototyping

### Character portraits

```bash
cd image-process
python cli.py batch examples/characters.txt --preset game-character
```

### Pixel art placeholders

```bash
python cli.py batch examples/game-assets.txt --preset pixel-art
```

### Item icons

```bash
python cli.py batch examples/items.txt --preset item-icon
```

### Transparent assets

```bash
python -m pip install -r requirements-background.txt
python cli.py remove-background outputs/character.png
```

### Reference frames from gameplay or concept videos

```bash
cd ../video-process
python cli.py frames path/to/reference.mp4 --fps 0.5
```

The command writes PNG files plus a JSON manifest listing the frame folder and count.

## Project-organized API requests

Include the same `project` name in related API requests:

```json
{
  "input_path": "C:/media/video.mp4",
  "output_format": "srt",
  "project": "episode-12"
}
```

Outputs are stored under `media-process-api/outputs/episode-12/` and separated by media type.
