class AppError(Exception):
    """Base application error."""


class FFmpegNotFoundError(AppError):
    """Raised when FFmpeg is not installed or not found in PATH."""


class AudioProcessingError(AppError):
    """Raised when FFmpeg fails to process audio."""


class AudioGenerationError(AppError):
    """Raised when AI audio generation fails."""
