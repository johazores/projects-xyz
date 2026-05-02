from pathlib import Path
import shutil
import subprocess
from app.core.errors import FFmpegNotFoundError, AudioProcessingError


class FFmpegService:
    def __init__(self) -> None:
        self.ffmpeg_path = shutil.which("ffmpeg")

    def ensure_available(self) -> None:
        if not self.ffmpeg_path:
            raise FFmpegNotFoundError(
                "FFmpeg is not installed or not added to PATH. Run: ffmpeg -version"
            )

    def convert_to_mp3(self, input_path: Path, output_path: Path) -> None:
        self.ensure_available()

        command = [
            self.ffmpeg_path,
            "-y",
            "-i",
            str(input_path),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(output_path),
        ]

        self._run(command)

    def normalize_audio(self, input_path: Path, output_path: Path) -> None:
        self.ensure_available()

        command = [
            self.ffmpeg_path,
            "-y",
            "-i",
            str(input_path),
            "-af",
            "loudnorm",
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(output_path),
        ]

        self._run(command)

    def trim_audio(self, input_path: Path, output_path: Path, start: float, duration: float) -> None:
        self.ensure_available()

        command = [
            self.ffmpeg_path,
            "-y",
            "-ss",
            str(start),
            "-i",
            str(input_path),
            "-t",
            str(duration),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(output_path),
        ]

        self._run(command)

    def _run(self, command: list[str]) -> None:
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise AudioProcessingError(result.stderr or "FFmpeg failed to process audio.")
