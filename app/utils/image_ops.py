"""Deterministic image scoring and exact thumbnail composition."""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageStat

from app.utils.files import MediaError, existing_file

_TOKEN_RE = re.compile(r"[a-z0-9]{3,}")


def fit_image(source: Path, destination: Path, width: int, height: int) -> Path:
    image = Image.open(source).convert("RGB")
    fitted = ImageOps.fit(image, (width, height), method=Image.Resampling.LANCZOS)
    fitted.save(destination, quality=95)
    return destination


def score_thumbnail(
    path: Path, title: str, prompt: str, caption: str | None = None
) -> dict[str, Any]:
    image = Image.open(path).convert("RGB")
    preview = ImageOps.fit(image, (512, 288), method=Image.Resampling.LANCZOS)
    gray = preview.convert("L")
    stat = ImageStat.Stat(gray)
    contrast = min(1.0, (stat.stddev[0] if stat.stddev else 0.0) / 64.0)
    entropy = min(1.0, gray.entropy() / 8.0)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_mean = ImageStat.Stat(edges).mean[0] / 255.0
    edge_score = min(1.0, edge_mean * 5.0)
    center = gray.crop((128, 48, 384, 240))
    center_contrast = min(1.0, ImageStat.Stat(center).stddev[0] / 64.0)
    target_tokens = set(_TOKEN_RE.findall(f"{title} {prompt}".lower()))
    caption_tokens = set(_TOKEN_RE.findall((caption or "").lower()))
    semantic = len(target_tokens & caption_tokens) / max(
        1, min(len(target_tokens), 12)
    )
    total = 100 * (
        0.28 * contrast
        + 0.18 * entropy
        + 0.18 * edge_score
        + 0.16 * center_contrast
        + 0.20 * min(1.0, semantic)
    )
    return {
        "score": round(total, 2),
        "contrast": round(contrast, 3),
        "entropy": round(entropy, 3),
        "edge_density": round(edge_score, 3),
        "center_contrast": round(center_contrast, 3),
        "semantic_overlap": round(min(1.0, semantic), 3),
        "caption": caption,
    }


def compose_thumbnail(
    background_path: Path,
    destination: Path,
    *,
    title: str,
    width: int,
    height: int,
    subject_path: Path | None = None,
    text_position: str = "auto",
    font_path: str | None = None,
    text_color: str = "#FFFFFF",
    accent_color: str = "#FFD400",
) -> Path:
    background = Image.open(background_path).convert("RGB")
    canvas = ImageOps.fit(background, (width, height), method=Image.Resampling.LANCZOS)
    canvas = ImageEnhance.Contrast(canvas).enhance(1.08)

    if subject_path:
        subject = Image.open(subject_path).convert("RGBA")
        max_w, max_h = int(width * 0.52), int(height * 0.9)
        subject.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
        subject_x = width - subject.width - int(width * 0.035)
        subject_y = height - subject.height
        canvas.paste(subject, (subject_x, subject_y), subject)
        if text_position == "auto":
            text_position = "left"
    elif text_position == "auto":
        text_position = "left"

    draw = ImageDraw.Draw(canvas, "RGBA")
    font = _load_font(font_path, max(42, int(height * 0.095)))
    lines = _wrap_text(draw, title.upper(), font, int(width * 0.48), max_lines=4)
    line_height = int(font.size * 1.05) if hasattr(font, "size") else 60
    text_height = line_height * len(lines)

    if text_position == "right":
        x = int(width * 0.51)
    else:
        x = int(width * 0.055)
    if text_position == "top":
        y = int(height * 0.07)
    elif text_position == "bottom":
        y = max(int(height * 0.5), height - text_height - int(height * 0.09))
    else:
        y = max(int(height * 0.12), (height - text_height) // 2)

    box_width = min(int(width * 0.48), width - x - int(width * 0.07))
    padding = int(height * 0.035)
    draw.rounded_rectangle(
        (x - padding, y - padding, x + box_width + padding, y + text_height + padding),
        radius=24,
        fill=(0, 0, 0, 145),
    )
    draw.rectangle(
        (x - padding, y - padding, x - padding + 12, y + text_height + padding),
        fill=accent_color,
    )

    for line in lines:
        draw.text(
            (x, y),
            line,
            font=font,
            fill=text_color,
            stroke_width=max(2, int(height * 0.006)),
            stroke_fill="#000000",
        )
        y += line_height

    canvas.save(destination, quality=95)
    return destination


def _load_font(
    font_path: str | None, size: int
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates: list[Path] = []
    if font_path:
        candidates.append(existing_file(font_path))
    candidates.extend(
        Path(value)
        for value in (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/impact.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        )
    )
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def _wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
    max_lines: int,
) -> list[str]:
    words = text.split()
    if not words:
        raise MediaError("Thumbnail title cannot be empty.")
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        bbox = draw.textbbox((0, 0), candidate, font=font, stroke_width=2)
        if current and bbox[2] - bbox[0] > max_width:
            lines.append(" ".join(current))
            current = [word]
            if len(lines) == max_lines - 1:
                break
        else:
            current.append(word)
    remaining = " ".join(current)
    if remaining and len(lines) < max_lines:
        lines.append(remaining)
    consumed = sum(len(line.split()) for line in lines)
    if consumed < len(words):
        lines[-1] = lines[-1].rstrip(" .") + "…"
    return lines
