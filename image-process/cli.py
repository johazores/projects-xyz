"""Command-line interface for image generation."""

from __future__ import annotations

import argparse
import logging

from config import load_config
from main import generate_image
from utils.logging import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate images from text prompts.")
    parser.add_argument("--config", help="Path to a JSON configuration file.")

    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="Generate an image.")
    generate.add_argument("--prompt", required=True, help="Image prompt.")
    generate.add_argument("--negative-prompt", help="Elements to avoid when supported.")
    generate.add_argument("--provider", help="Provider override.")
    generate.add_argument("--output-dir", help="Output directory override.")
    return parser


def run() -> int:
    args = build_parser().parse_args()

    try:
        config = load_config(args.config)
        configure_logging(config.log_level)
        generate_image(
            prompt=args.prompt,
            negative_prompt=args.negative_prompt,
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
