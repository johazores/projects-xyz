"""Command-line interface for video generation and processing."""

from __future__ import annotations

import argparse
import logging

from config import load_config
from main import VIDEO_PRESETS, extract_video_frames, generate_video, resize_video_file
from utils.logging import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate and prepare video assets.")
    parser.add_argument("--config", help="Path to a JSON configuration file.")

    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate", help="Generate a video or request artifact.")
    generate.add_argument("--prompt", required=True, help="Video prompt.")
    generate.add_argument("--provider", help="Provider override.")
    generate.add_argument("--output-dir", help="Output directory override.")

    resize = commands.add_parser("resize", help="Resize and pad a video for a common format.")
    resize.add_argument("input", help="Input video file.")
    resize.add_argument("--preset", choices=tuple(VIDEO_PRESETS), required=True)
    resize.add_argument("--output-dir", help="Output directory override.")

    frames = commands.add_parser("frames", help="Extract PNG frames from a video.")
    frames.add_argument("input", help="Input video file.")
    frames.add_argument("--fps", type=float, default=1.0, help="Frames per second to extract.")
    frames.add_argument("--output-dir", help="Output directory override.")
    return parser


def run() -> int:
    args = build_parser().parse_args()

    try:
        config = load_config(args.config)
        configure_logging(config.log_level)

        if args.command == "generate":
            output_path = generate_video(
                prompt=args.prompt,
                config=config,
                provider_name=args.provider,
                output_dir=args.output_dir,
            )
        elif args.command == "resize":
            output_path = resize_video_file(
                args.input,
                config,
                preset_name=args.preset,
                output_dir=args.output_dir,
            )
        else:
            output_path = extract_video_frames(
                args.input,
                config,
                fps=args.fps,
                output_dir=args.output_dir,
            )

        print(output_path.resolve())
        return 0
    except Exception as exc:
        logging.getLogger(__name__).error("%s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
