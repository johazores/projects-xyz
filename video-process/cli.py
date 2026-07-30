"""Command-line interface for video generation."""

from __future__ import annotations

import argparse
import logging

from config import load_config
from main import generate_video
from utils.logging import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create video generation requests.")
    parser.add_argument("--config", help="Path to a JSON configuration file.")

    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="Generate a video or request artifact.")
    generate.add_argument("--prompt", required=True, help="Video prompt.")
    generate.add_argument("--provider", help="Provider override.")
    generate.add_argument("--output-dir", help="Output directory override.")
    return parser


def run() -> int:
    args = build_parser().parse_args()

    try:
        config = load_config(args.config)
        configure_logging(config.log_level)
        generate_video(
            prompt=args.prompt,
            config=config,
            provider_name=args.provider,
            output_dir=args.output_dir,
        )
        return 0
    except Exception as exc:
        logging.getLogger(__name__).error("%s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
