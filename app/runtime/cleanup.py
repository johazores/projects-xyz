"""Safe dry-run-first cleanup for project artifacts and optional model caches."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
from typing import Any

from app.runtime.project_store import ProjectStore
from app.utils.files import MediaError, slugify


def cleanup(*, settings: Any, projects: ProjectStore, project: str | None, older_than_days: int | None, include_project_runs: bool, include_model_cache: bool, dry_run: bool, confirm: bool) -> dict[str, Any]:
    if not project and older_than_days is None and not include_model_cache:
        raise MediaError("Specify a project, older_than_days, or include_model_cache.")
    if not dry_run and not confirm:
        raise MediaError("Set confirm=true before deleting files.")

    project_slug = slugify(project, "default") if project else None
    if project_slug and project_slug in projects.active_projects():
        raise MediaError("Active project artifacts cannot be cleaned up.")

    candidates: list[Path] = []
    if project_slug:
        output_root = (settings.output_dir / project_slug).resolve()
        if output_root.exists():
            candidates.append(output_root)
    elif older_than_days is not None:
        threshold = datetime.now(timezone.utc) - timedelta(days=max(0, older_than_days))
        for path in settings.output_dir.iterdir():
            if path.name in {"audio", "image", "video", "workflow"}:
                continue
            try:
                modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
            except OSError:
                continue
            if modified <= threshold:
                candidates.append(path.resolve())

    run_ids: list[str] = []
    if include_project_runs:
        for record in projects.list(project=project, limit=500):
            if record.get("status") in {"queued", "running"}:
                continue
            if older_than_days is not None:
                created = datetime.fromisoformat(str(record["created_at"]))
                threshold = datetime.now(timezone.utc) - timedelta(days=max(0, older_than_days))
                if created > threshold:
                    continue
            run_ids.append(str(record["id"]))

    if include_model_cache:
        if settings.model_cache_dir is None:
            raise MediaError("MEDIA_MODEL_CACHE_DIR must be configured before cache cleanup.")
        cache = settings.model_cache_dir.resolve()
        if cache.exists():
            candidates.extend(path.resolve() for path in cache.iterdir())

    roots = [settings.output_dir.resolve()]
    if settings.model_cache_dir is not None:
        roots.append(settings.model_cache_dir.resolve())
    safe_candidates = [_safe_path(path, roots) for path in candidates]
    estimated_bytes = sum(_tree_size(path) for path in safe_candidates)

    deleted: list[str] = []
    if not dry_run:
        for path in safe_candidates:
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
            deleted.append(str(path))
        for run_id in run_ids:
            projects.delete_record(run_id)

    return {
        "dry_run": dry_run,
        "project": project_slug,
        "paths": [str(path) for path in safe_candidates],
        "project_run_ids": run_ids,
        "estimated_bytes": estimated_bytes,
        "deleted_paths": deleted,
        "deleted_project_runs": [] if dry_run else run_ids,
    }


def _safe_path(path: Path, roots: list[Path]) -> Path:
    resolved = path.resolve()
    for root in roots:
        try:
            relative = resolved.relative_to(root)
        except ValueError:
            continue
        if not relative.parts:
            raise MediaError(f"Cleanup cannot delete a configured root directory: {resolved}")
        return resolved
    raise MediaError(f"Cleanup path is outside configured directories: {resolved}")


def _tree_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    total = 0
    for child in path.rglob("*"):
        try:
            if child.is_file() and not child.is_symlink():
                total += child.stat().st_size
        except OSError:
            continue
    return total
