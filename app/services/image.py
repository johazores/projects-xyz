"""Simple image generation helpers, presets, batching, and background removal."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path

from app.config import settings
from app.models import (
    BatchOutput,
    ImageBackgroundRequest,
    ImageBatchRequest,
    ImageGenerateRequest,
    MediaOutput,
)
from app.utils.background import remove_background
from app.utils.files import (
    MediaError,
    existing_file,
    media_output_dir,
    output_response,
    unique_path,
)


def list_presets() -> dict[str, dict[str, str]]:
    try:
        value = json.loads(settings.presets_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MediaError(f"Unable to load presets: {exc}") from exc
    return value


def generate(request: ImageGenerateRequest) -> MediaOutput:
    provider = request.provider.strip().lower()
    if provider != "demo":
        raise MediaError("Unknown image provider. Available providers: demo.")

    prompt, negative = _apply_preset(request.prompt, request.negative_prompt, request.preset)
    destination = unique_path(
        media_output_dir("image", request.project), prompt, ".svg"
    )
    _write_prompt_card(destination, prompt, negative)
    return output_response("image", "generate", destination, provider)


def generate_batch(request: ImageBatchRequest) -> BatchOutput:
    items = [
        generate(
            ImageGenerateRequest(
                prompt=prompt,
                provider=request.provider,
                negative_prompt=request.negative_prompt,
                preset=request.preset,
                project=request.project,
            )
        )
        for prompt in request.prompts
        if prompt.strip()
    ]
    if not items:
        raise MediaError("At least one non-empty prompt is required.")
    return BatchOutput(items=items)


def remove_background_file(request: ImageBackgroundRequest) -> MediaOutput:
    source = existing_file(request.input_path)
    destination = unique_path(
        media_output_dir("image", request.project), f"{source.stem}-transparent", ".png"
    )
    remove_background(source, destination, request.model)
    return output_response("image", "remove-background", destination)


def _apply_preset(
    prompt: str,
    negative_prompt: str | None,
    preset_name: str | None,
) -> tuple[str, str | None]:
    if not preset_name:
        return prompt.strip(), negative_prompt

    presets = list_presets()
    preset = presets.get(preset_name)
    if not preset:
        raise MediaError(
            f"Unknown preset: {preset_name}. Available: {', '.join(sorted(presets))}"
        )

    combined_prompt = f"{preset.get('prefix', '').strip()} {prompt.strip()}".strip()
    preset_negative = preset.get("negative", "").strip()
    combined_negative = ", ".join(
        value for value in (negative_prompt, preset_negative) if value
    ) or None
    return combined_prompt, combined_negative


def _write_prompt_card(
    destination: Path,
    prompt: str,
    negative_prompt: str | None,
) -> None:
    prompt_text = escape(prompt[:500])
    negative_text = escape((negative_prompt or "None")[:300])
    destination.write_text(
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
<rect width="1024" height="1024" fill="#10131a"/>
<rect x="72" y="72" width="880" height="880" rx="36" fill="#181d27" stroke="#333b4d"/>
<text x="120" y="160" fill="#ffffff" font-family="Arial" font-size="42" font-weight="bold">Image prompt</text>
<foreignObject x="120" y="210" width="784" height="470"><div xmlns="http://www.w3.org/1999/xhtml" style="color:#e8ecf4;font:30px Arial;line-height:1.45;word-wrap:break-word">{prompt_text}</div></foreignObject>
<text x="120" y="750" fill="#aeb7c8" font-family="Arial" font-size="26">Negative prompt</text>
<foreignObject x="120" y="790" width="784" height="120"><div xmlns="http://www.w3.org/1999/xhtml" style="color:#858fa2;font:22px Arial;line-height:1.35;word-wrap:break-word">{negative_text}</div></foreignObject>
</svg>''',
        encoding="utf-8",
    )
