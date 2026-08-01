"""Initial practical YouTube workflows."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from app.models import WorkflowView
from app.services.video import VIDEO_PRESETS
from app.utils import ffmpeg
from app.utils.files import MediaError, existing_file, media_output_dir, output_response, unique_directory, unique_path

WORKFLOWS = {
    "youtube.narration": WorkflowView(
        id="youtube.narration",
        description="Generate local narration, normalize it, save the script, and write a run manifest.",
        implemented=True,
        steps=["local TTS", "loudness normalization", "script copy", "run manifest"],
    ),
    "youtube.social-clip-prep": WorkflowView(
        id="youtube.social-clip-prep",
        description="Prepare a source video for Shorts with optional subtitles and frame extraction.",
        implemented=True,
        steps=["vertical resize", "optional transcription", "optional frame extraction", "run manifest"],
    ),
    "youtube.thumbnail": WorkflowView(
        id="youtube.thumbnail",
        description="Planned Sana generation, vision scoring, inpainting, background removal, and upscaling.",
        implemented=False,
        steps=["Sana image generation", "vision scoring", "inpainting", "upscaling", "text composition"],
    ),
    "youtube.ai-short": WorkflowView(
        id="youtube.ai-short",
        description="Planned script, narration, generated images, short LTX motion clips, subtitles, and assembly.",
        implemented=False,
        steps=["script", "narration", "images", "motion clips", "subtitles", "FFmpeg assembly"],
    ),
}


def list_workflows() -> list[WorkflowView]:
    return list(WORKFLOWS.values())


def validate_workflow(workflow_id: str) -> WorkflowView:
    workflow = WORKFLOWS.get(workflow_id)
    if not workflow:
        raise MediaError(f"Unknown workflow: {workflow_id}")
    if not workflow.implemented:
        raise MediaError(f"Workflow {workflow_id} is planned but not implemented yet.")
    return workflow


def run(workflow_id: str, payload: dict[str, Any], model_manager: Any, progress: Any) -> dict[str, Any]:
    validate_workflow(workflow_id)
    if workflow_id == "youtube.narration":
        return _narration(payload, model_manager, progress)
    if workflow_id == "youtube.social-clip-prep":
        return _social_clip(payload, model_manager, progress)
    raise MediaError(f"Workflow runner missing for: {workflow_id}")


def _narration(payload: dict[str, Any], model_manager: Any, progress: Any) -> dict[str, Any]:
    text = str(payload.get("text", "")).strip()
    if not text:
        raise MediaError("youtube.narration requires text.")
    model_id = str(payload.get("model", "speech.kokoro"))
    project = payload.get("project")
    progress(5, "Starting narration workflow")
    generated = model_manager.run(model_id, {**payload, "text": text}, lambda value, message: progress(5 + int(value * 0.65), message))
    source = Path(generated["output_path"])
    outputs = [generated]
    if payload.get("normalize", True):
        progress(75, "Normalizing narration")
        normalized = unique_path(media_output_dir("audio", project), f"{source.stem}-normalized", ".mp3")
        ffmpeg.normalize_audio(source, normalized)
        outputs.append(output_response("audio", "normalize", normalized).model_dump())
    progress(85, "Saving script and manifest")
    workflow_dir = media_output_dir("workflow", project)
    script_path = unique_path(workflow_dir, payload.get("name", "narration-script"), ".txt")
    script_path.write_text(text.rstrip() + "\n", encoding="utf-8")
    manifest_path = _manifest(workflow_dir, "youtube-narration", payload, outputs + [{"output_path": str(script_path)}])
    progress(100, "Narration workflow completed")
    return {"workflow": "youtube.narration", "outputs": outputs, "script_path": str(script_path), "manifest_path": str(manifest_path)}


def _social_clip(payload: dict[str, Any], model_manager: Any, progress: Any) -> dict[str, Any]:
    source = existing_file(str(payload.get("input_path", "")))
    project = payload.get("project")
    preset = str(payload.get("preset", "shorts"))
    if preset not in VIDEO_PRESETS:
        raise MediaError(f"Unknown video preset: {preset}")
    width, height = VIDEO_PRESETS[preset]
    outputs: list[dict[str, Any]] = []
    progress(10, "Resizing source video")
    resized = unique_path(media_output_dir("video", project), f"{source.stem}-{preset}", ".mp4")
    ffmpeg.resize_video(source, resized, width, height)
    outputs.append(output_response("video", "resize", resized).model_dump())
    if payload.get("transcribe", True):
        progress(45, "Creating subtitles")
        transcript = model_manager.run(
            str(payload.get("transcription_model", "speech.faster-whisper")),
            {"input_path": str(source), "output_format": "srt", "language": payload.get("language"), "project": project},
            lambda value, message: progress(45 + int(value * 0.35), message),
        )
        outputs.append(transcript)
    fps = float(payload.get("extract_fps", 0))
    frames_directory = None
    if fps > 0:
        progress(82, "Extracting reference frames")
        frames_directory = unique_directory(media_output_dir("video", project), f"{source.stem}-frames")
        ffmpeg.extract_frames(source, frames_directory / "frame-%06d.png", fps)
    progress(92, "Saving workflow manifest")
    manifest_path = _manifest(media_output_dir("workflow", project), "youtube-social-clip-prep", payload, outputs)
    progress(100, "Social clip preparation completed")
    return {"workflow": "youtube.social-clip-prep", "outputs": outputs, "frames_directory": str(frames_directory) if frames_directory else None, "manifest_path": str(manifest_path)}


def _manifest(directory: Path, name: str, payload: dict[str, Any], outputs: list[dict[str, Any]]) -> Path:
    path = unique_path(directory, name, ".json")
    path.write_text(json.dumps({"workflow": name.replace("-", "."), "created_at": datetime.now(timezone.utc).isoformat(), "request": payload, "outputs": outputs}, indent=2), encoding="utf-8")
    return path
