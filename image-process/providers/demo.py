"""Dependency-free demo image provider."""

from __future__ import annotations

from html import escape
from pathlib import Path
import textwrap

from config import ImageConfig


class DemoImageProvider:
    """Create an SVG prompt card so the workflow can be tested locally."""

    file_extension = ".svg"

    def generate(
        self,
        prompt: str,
        negative_prompt: str | None,
        output_path: Path,
        config: ImageConfig,
    ) -> Path:
        if not prompt.strip():
            raise ValueError("A prompt is required.")

        prompt_lines = textwrap.wrap(prompt.strip(), width=44)[:6]
        negative_lines = textwrap.wrap(negative_prompt.strip(), width=48)[:3] if negative_prompt else []

        prompt_text = self._text_lines(prompt_lines, start_y=config.height * 0.42, size=34)
        negative_text = self._text_lines(
            [f"Avoid: {line}" for line in negative_lines],
            start_y=config.height * 0.70,
            size=20,
        )

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{config.width}" height="{config.height}" viewBox="0 0 {config.width} {config.height}">
  <defs>
    <linearGradient id="background" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#111827"/>
      <stop offset="100%" stop-color="#334155"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#background)"/>
  <circle cx="{config.width * 0.82}" cy="{config.height * 0.18}" r="{min(config.width, config.height) * 0.12}" fill="#ffffff" opacity="0.08"/>
  <text x="8%" y="14%" fill="#cbd5e1" font-family="Arial, sans-serif" font-size="22">DEMO TEXT-TO-IMAGE OUTPUT</text>
  {prompt_text}
  {negative_text}
  <text x="8%" y="91%" fill="#94a3b8" font-family="Arial, sans-serif" font-size="18">Replace the demo provider with a tested AI provider when ready.</text>
</svg>
"""
        output_path.write_text(svg, encoding="utf-8")
        return output_path

    @staticmethod
    def _text_lines(lines: list[str], start_y: float, size: int) -> str:
        parts = []
        for index, line in enumerate(lines):
            y = start_y + index * (size * 1.35)
            parts.append(
                f'<text x="8%" y="{y:.0f}" fill="#f8fafc" '
                f'font-family="Arial, sans-serif" font-size="{size}">{escape(line)}</text>'
            )
        return "\n  ".join(parts)
