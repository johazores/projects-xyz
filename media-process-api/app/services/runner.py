"""Run an existing media CLI and return the generated file path."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


class ProcessExecutionError(RuntimeError):
    """Raised when a media CLI fails or returns an invalid output."""


def run_cli(project_dir: Path, arguments: list[str], timeout_seconds: int) -> Path:
    """Execute one media CLI with the current Python interpreter."""

    command = [sys.executable, "cli.py", *arguments]

    try:
        result = subprocess.run(
            command,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ProcessExecutionError(
            f"Media processing exceeded the {timeout_seconds}-second timeout."
        ) from exc

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Media processing failed."
        raise ProcessExecutionError(message.splitlines()[-1])

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        raise ProcessExecutionError("The media process did not return an output path.")

    output_path = Path(lines[-1]).resolve()
    if not output_path.is_file():
        raise ProcessExecutionError(f"Generated output was not found: {output_path}")

    return output_path
