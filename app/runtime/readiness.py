"""Disk, executable, model, and cache readiness checks."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
from typing import Any


def readiness_snapshot(settings: Any, registry: Any) -> dict[str, Any]:
    storage = storage_snapshot(settings)
    checks = {
        "output_directory": _directory_check(settings.output_dir),
        "data_directory": _directory_check(settings.data_dir),
        "ffmpeg": _executable_check("ffmpeg"),
        "ffprobe": _executable_check("ffprobe"),
        "disk_headroom": {
            "ok": storage["disk_free_gb"] >= settings.min_disk_free_gb,
            "free_gb": storage["disk_free_gb"],
            "minimum_gb": settings.min_disk_free_gb,
        },
    }
    specs = registry.list()
    implemented = [spec for spec in specs if spec.implemented]
    available = [spec.id for spec in implemented if registry.is_available(spec)]
    checks["models"] = {"ok": bool(available), "implemented": len(implemented), "available": len(available), "available_ids": available}
    cache = settings.model_cache_dir
    checks["model_cache"] = {"configured": cache is not None, "path": str(cache) if cache else None, "exists": bool(cache and cache.exists())}
    required = ("output_directory", "data_directory", "ffmpeg", "ffprobe", "disk_headroom")
    return {"ready": all(bool(checks[name]["ok"]) for name in required), "checks": checks, "storage": storage}


def storage_snapshot(settings: Any) -> dict[str, Any]:
    usage = shutil.disk_usage(settings.output_dir)
    cache = settings.model_cache_dir
    return {
        "disk_total_gb": round(usage.total / 1024**3, 2),
        "disk_free_gb": round(usage.free / 1024**3, 2),
        "output_bytes": _tree_size(settings.output_dir),
        "data_bytes": _tree_size(settings.data_dir),
        "model_cache_bytes": _tree_size(cache) if cache else None,
        "model_cache_path": str(cache) if cache else None,
    }


def _directory_check(path: Path) -> dict[str, Any]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        writable = os.access(path, os.W_OK)
    except OSError:
        writable = False
    return {"ok": writable, "path": str(path), "writable": writable}


def _executable_check(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    return {"ok": bool(path), "path": path}


def _tree_size(root: Path | None) -> int:
    if root is None or not root.exists():
        return 0
    total = 0
    for path in root.rglob("*"):
        try:
            if path.is_file() and not path.is_symlink():
                total += path.stat().st_size
        except OSError:
            continue
    return total
