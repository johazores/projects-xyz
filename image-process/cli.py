"""Command-line interface for image generation and processing."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from config import load_config
from main import generate_image, generate_image_batch, remove_image_background
from utils.logging import configure_logging
from utils.presets import load_presets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate and prepare images for content and games."
    )
    parser.add_argument("--config", help="Path to a JSON configuration file.")

    commands = parser.add_subparsers(dest="command", required=True)

    generate = commands.add_parser("generate", help="Generate one image.")
    generate.add_argument("--prompt", required=True, help="Image prompt.")
    generate.add_argument("--negative-prompt", help="Elements to avoid when supported.")
    generate.add_argument("--preset", help="Prompt preset such as pixel-art or item-icon.")
    generate.add_argument("--provider", help="Provider override.")
    generate.add_argument("--output-dir", help="Output directory override.")

    batch = commands.add_parser("batch", help="Generate one image per line in a prompt file.")
    batch.add_argument("prompt_file", help="Text file containing one prompt per line.")
    batch.add_argument("--negative-prompt", help="Elements to avoid when supported.")
    batch.add_argument("--preset", help="Prompt preset applied to every line.")
    batch.add_argument("--provider", help="Provider override.")
    batch.add_argument("--output-dir", help="Output directory override.")

    background = commands.add_parser("remove-background", help="Create a transparent PNG.")
    background.add_argument("input", help="Input image file.")
    background.add_argument("--model", default="u2net", help="rembg model name.")
    background.add_argument("--output-dir", help="Output directory override.")

    presets = commands.add_parser("presets", help="List available prompt presets.")
    presets.add_argument("--json", action="store_true", help="Print the full preset JSON.")
    return parser


def run() -> int:
    args = build_parser().parse_args()

    try:
        config = load_config(args.config)
        configure_logging(config.log_level)

        if args.command == "generate":
            outputs = [
                generate_image(
                    prompt=args.prompt,
                    negative_prompt=args.negative_prompt,
                    config=config,
                    provider_name=args.provider,
                    output_dir=args.output_dir,
                    preset_name=args.preset,
                )
            ]
        elif args.command == "batch":
            prompt_file = Path(args.prompt_file).expanduser().resolve()
            if not prompt_file.is_file():
                raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
            prompts = [
                line.strip()
                for line in prompt_file.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.lstrip().startswith("#")
            ]
            outputs = generate_image_batch(
                prompts=prompts,
                negative_prompt=args.negative_prompt,
                config=config,
                provider_name=args.provider,
                output_dir=args.output_dir,
                preset_name=args.preset,
            )
        elif args.command == "remove-background":
            outputs = [
                remove_image_background(
                    args.input,
                    config,
                    model_name=args.model,
                    output_dir=args.output_dir,
                )
            ]
        else:
            presets = load_presets()
            print(json.dumps(presets, indent=2) if args.json else "\n".join(sorted(presets)))
            return 0

        for output_path in outputs:
            print(output_path.resolve())
        return 0
    except Exception as exc:
        logging.getLogger(__name__).error("%s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
