"""Command-line interface for audio generation and processing."""

from __future__ import annotations

import argparse
import logging

from config import load_config
from main import (
    convert_audio_file,
    enhance_audio_file,
    generate_audio,
    normalize_audio_file,
    transcribe_audio_file,
    trim_audio_file,
)
from utils.logging import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate, clean, and transcribe audio files.")
    parser.add_argument("--config", help="Path to a JSON configuration file.")

    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate", help="Generate audio from a text prompt.")
    generate.add_argument("--prompt", required=True, help="Text describing the audio.")
    generate.add_argument("--provider", help="Provider override, such as demo or bark.")
    generate.add_argument("--output-dir", help="Output directory override.")

    convert = commands.add_parser("convert", help="Convert an audio file to MP3.")
    convert.add_argument("input", help="Input audio file.")
    convert.add_argument("--output-dir", help="Output directory override.")

    normalize = commands.add_parser("normalize", help="Normalize audio volume.")
    normalize.add_argument("input", help="Input audio file.")
    normalize.add_argument("--output-dir", help="Output directory override.")

    enhance = commands.add_parser("enhance", help="Reduce noise and normalize spoken audio.")
    enhance.add_argument("input", help="Input audio or video file.")
    enhance.add_argument("--output-dir", help="Output directory override.")

    transcribe = commands.add_parser("transcribe", help="Create TXT transcripts or SRT subtitles.")
    transcribe.add_argument("input", help="Input audio or video file.")
    transcribe.add_argument("--format", choices=("txt", "srt"), default="srt")
    transcribe.add_argument("--language", help="Optional language code such as en or fil.")
    transcribe.add_argument("--model", help="faster-whisper model override.")
    transcribe.add_argument("--device", choices=("auto", "cpu", "cuda"))
    transcribe.add_argument("--compute-type", help="CTranslate2 compute type override.")
    transcribe.add_argument("--output-dir", help="Output directory override.")

    trim = commands.add_parser("trim", help="Trim an audio file.")
    trim.add_argument("input", help="Input audio file.")
    trim.add_argument("--start", type=float, default=0, help="Start time in seconds.")
    trim.add_argument("--duration", type=float, required=True, help="Duration in seconds.")
    trim.add_argument("--output-dir", help="Output directory override.")

    return parser


def run() -> int:
    args = build_parser().parse_args()

    try:
        config = load_config(args.config)
        configure_logging(config.log_level)

        if args.command == "generate":
            output_path = generate_audio(args.prompt, config, args.provider, args.output_dir)
        elif args.command == "convert":
            output_path = convert_audio_file(args.input, config, args.output_dir)
        elif args.command == "normalize":
            output_path = normalize_audio_file(args.input, config, args.output_dir)
        elif args.command == "enhance":
            output_path = enhance_audio_file(args.input, config, args.output_dir)
        elif args.command == "transcribe":
            output_path = transcribe_audio_file(
                args.input,
                config,
                output_format=args.format,
                language=args.language,
                model_name=args.model,
                device=args.device,
                compute_type=args.compute_type,
                output_dir=args.output_dir,
            )
        else:
            output_path = trim_audio_file(
                args.input,
                args.start,
                args.duration,
                config,
                args.output_dir,
            )

        print(output_path.resolve())
        return 0
    except Exception as exc:
        logging.getLogger(__name__).error("%s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
