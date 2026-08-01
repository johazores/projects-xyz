"""Practical local YouTube workflows."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from app.models import WorkflowView
from app.services.video import VIDEO_PRESETS
from app.utils import ffmpeg
from app.utils.files import MediaError, existing_file, media_output_dir, output_response, unique_directory, unique_path
from app.utils.image_ops import compose_thumbnail, score_thumbnail

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
        description="Generate, analyze, compose, and export a reproducible 1280x720 YouTube thumbnail.",
        implemented=True,
        steps=[
            "sequential Sana variations",
            "optional Florence captions",
            "deterministic candidate scoring",
            "optional BiRefNet subject cutout",
            "optional Real-ESRGAN upscale",
            "exact Pillow text composition",
            "run manifest",
        ],
    ),
    "youtube.ai-short": WorkflowView(
        id="youtube.ai-short",
        description="Create a complete vertical Short from a script and scene prompts with optional LTX motion.",
        implemented=True,
        steps=[
            "local narration",
            "sequential scene images",
            "optional LTX image-to-video",
            "still-image fallback",
            "vertical FFmpeg assembly",
            "optional subtitles",
            "run manifest",
        ],
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
    if workflow_id == "youtube.thumbnail":
        return _thumbnail(payload, model_manager, progress)
    if workflow_id == "youtube.ai-short":
        return _ai_short(payload, model_manager, progress)
    raise MediaError(f"Workflow runner missing for: {workflow_id}")


def _narration(payload: dict[str, Any], model_manager: Any, progress: Any) -> dict[str, Any]:
    text = str(payload.get("text", "")).strip()
    if not text:
        raise MediaError("youtube.narration requires text.")
    model_id = str(payload.get("model", "speech.kokoro"))
    project = payload.get("project")
    progress(5, "Starting narration workflow")
    generated = model_manager.run(
        model_id,
        {**payload, "text": text},
        lambda value, message: progress(5 + int(value * 0.65), message),
    )
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
    manifest_path = _manifest(
        workflow_dir,
        "youtube-narration",
        payload,
        outputs + [{"output_path": str(script_path)}],
    )
    progress(100, "Narration workflow completed")
    return {
        "workflow": "youtube.narration",
        "outputs": outputs,
        "script_path": str(script_path),
        "manifest_path": str(manifest_path),
    }


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
            {
                "input_path": str(source),
                "output_format": "srt",
                "language": payload.get("language"),
                "project": project,
            },
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
    manifest_path = _manifest(
        media_output_dir("workflow", project),
        "youtube-social-clip-prep",
        payload,
        outputs,
    )
    progress(100, "Social clip preparation completed")
    return {
        "workflow": "youtube.social-clip-prep",
        "outputs": outputs,
        "frames_directory": str(frames_directory) if frames_directory else None,
        "manifest_path": str(manifest_path),
    }


def _thumbnail(payload: dict[str, Any], model_manager: Any, progress: Any) -> dict[str, Any]:
    title = str(payload.get("title", "")).strip()
    prompt = str(payload.get("prompt", "")).strip()
    if not title or not prompt:
        raise MediaError("youtube.thumbnail requires title and prompt.")
    project = payload.get("project")
    workflow_dir = unique_directory(media_output_dir("workflow", project), "youtube-thumbnail")
    outputs: list[dict[str, Any]] = []

    progress(3, "Generating thumbnail candidates")
    generated = model_manager.run(
        str(payload.get("model", "image.sana-1.6b-int4")),
        {
            "prompt": prompt,
            "negative_prompt": payload.get("negative_prompt", "blurry, low quality, watermark, text, logo"),
            "project": project,
            "name": "thumbnail-candidate",
            "count": int(payload.get("count", 4)),
            "width": int(payload.get("width", 1024)),
            "height": int(payload.get("height", 576)),
            "steps": int(payload.get("steps", 20)),
            "guidance": float(payload.get("guidance", 4.5)),
            "seed": payload.get("seed"),
        },
        lambda value, message: progress(3 + int(value * 0.40), message),
    )
    candidates = list(generated.get("outputs", []))
    if not candidates:
        raise MediaError("The image model did not return thumbnail candidates.")
    outputs.extend(candidates)

    vision_model = payload.get("vision_model", "vision.florence-2-large")
    scored: list[dict[str, Any]] = []
    for index, item in enumerate(candidates):
        caption = None
        if vision_model and _model_available(model_manager, str(vision_model)):
            analysis = model_manager.run(
                str(vision_model),
                {"input_path": item["output_path"], "task": "<DETAILED_CAPTION>"},
                lambda value, message, i=index: progress(
                    45 + int(((i + value / 100) / len(candidates)) * 20), message
                ),
            )
            caption = analysis.get("caption")
        score = score_thumbnail(Path(item["output_path"]), title, prompt, caption)
        scored.append({**item, "analysis": score})

    selected = max(scored, key=lambda value: value["analysis"]["score"])
    selected_path = Path(selected["output_path"])
    progress(68, "Preparing selected thumbnail background")

    upscale_model = payload.get("upscale_model", "image.realesrgan-ncnn")
    upscaled = None
    if upscale_model and _model_available(model_manager, str(upscale_model)):
        upscaled = model_manager.run(
            str(upscale_model),
            {
                "input_path": str(selected_path),
                "project": project,
                "name": "thumbnail-background",
                "scale": 2,
                "tile": 256,
            },
            lambda value, message: progress(68 + int(value * 0.10), message),
        )
        selected_path = Path(upscaled["output_path"])
        outputs.append(upscaled)

    subject_output = None
    subject_path = payload.get("subject_path")
    if subject_path:
        background_model = str(payload.get("background_model", "image.birefnet-lite"))
        if not _model_available(model_manager, background_model):
            raise MediaError(f"Subject image was provided, but {background_model} is not available.")
        subject_output = model_manager.run(
            background_model,
            {
                "input_path": str(existing_file(str(subject_path))),
                "project": project,
                "name": "thumbnail-subject",
            },
            lambda value, message: progress(78 + int(value * 0.08), message),
        )
        outputs.append(subject_output)

    progress(88, "Composing exact thumbnail text")
    final_path = unique_path(media_output_dir("image", project), title, ".png")
    compose_thumbnail(
        selected_path,
        final_path,
        title=title,
        width=int(payload.get("final_width", 1280)),
        height=int(payload.get("final_height", 720)),
        subject_path=Path(subject_output["output_path"]) if subject_output else None,
        text_position=str(payload.get("text_position", "auto")),
        font_path=payload.get("font_path"),
        text_color=str(payload.get("text_color", "#FFFFFF")),
        accent_color=str(payload.get("accent_color", "#FFD400")),
    )
    final_output = output_response("image", "thumbnail", final_path, "youtube.thumbnail").model_dump()
    outputs.append(final_output)

    scores_path = workflow_dir / "candidate-scores.json"
    scores_path.write_text(json.dumps(scored, indent=2), encoding="utf-8")
    manifest_path = _manifest(
        workflow_dir,
        "youtube-thumbnail",
        payload,
        outputs,
        extra={
            "selected_candidate": selected,
            "candidate_scores_path": str(scores_path),
            "upscale_used": bool(upscaled),
            "subject_cutout_used": bool(subject_output),
        },
    )
    progress(100, "Thumbnail workflow completed")
    return {
        "workflow": "youtube.thumbnail",
        "output": final_output,
        "selected_candidate": selected,
        "candidates": scored,
        "candidate_scores_path": str(scores_path),
        "manifest_path": str(manifest_path),
    }


def _ai_short(payload: dict[str, Any], model_manager: Any, progress: Any) -> dict[str, Any]:
    script = str(payload.get("script", "")).strip()
    scenes = list(payload.get("scenes") or [])
    if not script or not scenes:
        raise MediaError("youtube.ai-short requires a script and at least one scene.")

    project = payload.get("project")
    workflow_dir = unique_directory(media_output_dir("workflow", project), "youtube-ai-short")
    outputs: list[dict[str, Any]] = []

    progress(3, "Generating local narration")
    narration = model_manager.run(
        str(payload.get("narration_model", "speech.kokoro")),
        {
            "text": script,
            "voice": payload.get("voice", "af_heart"),
            "project": project,
            "name": "short-narration",
        },
        lambda value, message: progress(3 + int(value * 0.14), message),
    )
    outputs.append(narration)
    narration_path = Path(narration["output_path"])
    normalized_audio = unique_path(media_output_dir("audio", project), "short-narration-normalized", ".mp3")
    ffmpeg.normalize_audio(narration_path, normalized_audio)
    normalized_output = output_response("audio", "normalize", normalized_audio).model_dump()
    outputs.append(normalized_output)
    total_duration = ffmpeg.probe_duration(normalized_audio)
    durations = _scene_durations(scenes, total_duration)

    image_width = int(payload.get("image_width", 576))
    image_height = int(payload.get("image_height", 1024))
    image_model = str(payload.get("image_model", "image.sana-1.6b-int4"))
    scene_images: list[Path] = []
    progress(20, "Preparing scene images")
    for index, scene in enumerate(scenes):
        image_path = scene.get("image_path")
        if image_path:
            scene_images.append(existing_file(str(image_path)))
            continue
        generated = model_manager.run(
            image_model,
            {
                "prompt": str(scene.get("prompt", "")),
                "negative_prompt": "blurry, low quality, watermark, text, logo",
                "project": project,
                "name": f"short-scene-{index + 1}",
                "count": 1,
                "width": image_width,
                "height": image_height,
                "steps": 20,
                "guidance": 4.5,
                "seed": None,
            },
            lambda value, message, i=index: progress(
                20 + int(((i + value / 100) / len(scenes)) * 25), message
            ),
        )
        candidates = list(generated.get("outputs") or [])
        if not candidates:
            raise MediaError(f"No image was generated for scene {index + 1}.")
        outputs.extend(candidates)
        scene_images.append(Path(candidates[0]["output_path"]))

    final_width = int(payload.get("final_width", 1080))
    final_height = int(payload.get("final_height", 1920))
    fps = int(payload.get("fps", 30))
    video_width = int(payload.get("video_width", 320))
    video_height = int(payload.get("video_height", 576))
    video_model = str(payload.get("video_model", "video.ltx-q8"))
    use_motion = bool(payload.get("use_motion", True))
    fallback_to_stills = bool(payload.get("fallback_to_stills", True))
    motion_available = use_motion and _model_available(model_manager, video_model)
    motion_disabled_reason = None
    clips: list[Path] = []
    scene_records: list[dict[str, Any]] = []

    for index, (scene, image_path, duration) in enumerate(zip(scenes, scene_images, durations, strict=True)):
        normalized_clip = unique_path(media_output_dir("video", project), f"short-scene-{index + 1}", ".mp4")
        animated = False
        generated_video: dict[str, Any] | None = None
        if motion_available and bool(scene.get("animate", True)):
            try:
                generated_video = model_manager.run(
                    video_model,
                    {
                        "prompt": str(scene.get("prompt", "")),
                        "negative_prompt": "blurry, jittery, distorted, watermark, text",
                        "input_path": str(image_path),
                        "project": project,
                        "name": f"short-motion-{index + 1}",
                        "width": video_width,
                        "height": video_height,
                        "num_frames": int(payload.get("video_frames", 65)),
                        "steps": int(payload.get("video_steps", 20)),
                        "fps": 24,
                        "seed": 42 + index,
                        "allow_low_vram_retry": True,
                    },
                    lambda value, message, i=index: progress(
                        48 + int(((i + value / 100) / len(scenes)) * 25), message
                    ),
                )
                outputs.append(generated_video)
                ffmpeg.normalize_video_clip(
                    Path(generated_video["output_path"]),
                    normalized_clip,
                    duration=duration,
                    width=final_width,
                    height=final_height,
                    fps=fps,
                )
                animated = True
            except Exception as exc:
                if exc.__class__.__name__ == "JobCancelled" or not fallback_to_stills:
                    raise
                motion_available = False
                motion_disabled_reason = str(exc)

        if not animated:
            ffmpeg.create_image_clip(
                image_path,
                normalized_clip,
                duration=duration,
                width=final_width,
                height=final_height,
                fps=fps,
            )

        clip_output = output_response(
            "video", "scene-clip", normalized_clip, video_model if animated else "still-image"
        ).model_dump()
        outputs.append(clip_output)
        clips.append(normalized_clip)
        scene_records.append(
            {
                "index": index + 1,
                "prompt": scene.get("prompt"),
                "duration": round(duration, 3),
                "image_path": str(image_path),
                "clip_path": str(normalized_clip),
                "animated": animated,
                "video_generation": generated_video,
            }
        )

    progress(76, "Concatenating vertical scene clips")
    silent_video = unique_path(media_output_dir("video", project), "short-visuals", ".mp4")
    ffmpeg.concatenate_videos(clips, silent_video)
    outputs.append(output_response("video", "concatenate", silent_video).model_dump())

    subtitles = None
    transcription_model = payload.get("transcription_model", "speech.faster-whisper")
    if transcription_model and _model_available(model_manager, str(transcription_model)):
        progress(82, "Creating local subtitles")
        subtitles = model_manager.run(
            str(transcription_model),
            {
                "input_path": str(normalized_audio),
                "output_format": "srt",
                "project": project,
            },
            lambda value, message: progress(82 + int(value * 0.08), message),
        )
        outputs.append(subtitles)

    progress(91, "Mixing narration with the final Short")
    muxed = unique_path(media_output_dir("video", project), "youtube-short", ".mp4")
    ffmpeg.mux_audio(silent_video, normalized_audio, muxed)
    final_path = muxed
    if bool(payload.get("burn_subtitles", False)) and subtitles:
        burned = unique_path(media_output_dir("video", project), "youtube-short-subtitled", ".mp4")
        ffmpeg.burn_subtitles(muxed, Path(subtitles["output_path"]), burned)
        final_path = burned

    final_output = output_response("video", "ai-short", final_path, "youtube.ai-short").model_dump()
    outputs.append(final_output)
    manifest_path = _manifest(
        workflow_dir,
        "youtube-ai-short",
        payload,
        outputs,
        extra={
            "duration_seconds": round(total_duration, 3),
            "scenes": scene_records,
            "motion_requested": use_motion,
            "motion_disabled_reason": motion_disabled_reason,
            "subtitles_path": subtitles.get("output_path") if subtitles else None,
        },
    )
    progress(100, "AI Short workflow completed")
    return {
        "workflow": "youtube.ai-short",
        "output": final_output,
        "duration_seconds": round(total_duration, 3),
        "scenes": scene_records,
        "subtitles": subtitles,
        "manifest_path": str(manifest_path),
        "motion_disabled_reason": motion_disabled_reason,
    }


def _scene_durations(scenes: list[dict[str, Any]], total_duration: float) -> list[float]:
    explicit = [float(scene["duration"]) if scene.get("duration") is not None else None for scene in scenes]
    explicit_total = sum(value for value in explicit if value is not None)
    missing = [index for index, value in enumerate(explicit) if value is None]
    if missing and explicit_total < total_duration:
        remaining = total_duration - explicit_total
        weights = []
        for index in missing:
            text = str(scenes[index].get("text") or scenes[index].get("prompt") or "")
            weights.append(max(1.0, len(text.split()) / 8))
        weight_total = sum(weights) or float(len(missing))
        result = [value or 0.0 for value in explicit]
        for index, weight in zip(missing, weights, strict=True):
            result[index] = remaining * weight / weight_total
        return result

    weights = [
        value if value is not None else max(
            1.0,
            len(str(scene.get("text") or scene.get("prompt") or "").split()) / 8,
        )
        for value, scene in zip(explicit, scenes, strict=True)
    ]
    weight_total = sum(weights) or float(len(scenes))
    return [total_duration * weight / weight_total for weight in weights]


def _model_available(model_manager: Any, model_id: str) -> bool:
    try:
        spec = model_manager.registry.get(model_id)
    except Exception:
        return False
    return model_manager.registry.is_available(spec)


def _manifest(
    directory: Path,
    name: str,
    payload: dict[str, Any],
    outputs: list[dict[str, Any]],
    *,
    extra: dict[str, Any] | None = None,
) -> Path:
    path = unique_path(directory, name, ".json")
    content = {
        "workflow": name.replace("-", "."),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "request": payload,
        "outputs": outputs,
    }
    if extra:
        content.update(extra)
    path.write_text(json.dumps(content, indent=2), encoding="utf-8")
    return path
