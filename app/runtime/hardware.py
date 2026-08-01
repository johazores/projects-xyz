"""Local hardware inspection and lightweight CUDA memory helpers."""

from __future__ import annotations

import csv
import io
import platform
import shutil
import subprocess
import sys
from typing import Any

_GIB = 1024**3


def hardware_snapshot() -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "torch_installed": False,
        "cuda_available": False,
        "cuda_version": None,
        "devices": [],
    }
    try:
        import torch
    except ImportError:
        snapshot["devices"] = _nvidia_smi_devices()
        snapshot["cuda_available"] = bool(snapshot["devices"])
        return snapshot

    snapshot["torch_installed"] = True
    snapshot["torch_version"] = torch.__version__
    snapshot["cuda_version"] = torch.version.cuda
    snapshot["cuda_available"] = torch.cuda.is_available()
    if not torch.cuda.is_available():
        snapshot["devices"] = _nvidia_smi_devices()
        return snapshot

    devices: list[dict[str, Any]] = []
    for index in range(torch.cuda.device_count()):
        properties = torch.cuda.get_device_properties(index)
        free_bytes = total_bytes = None
        try:
            with torch.cuda.device(index):
                free_bytes, total_bytes = torch.cuda.mem_get_info()
        except (RuntimeError, AttributeError):
            total_bytes = properties.total_memory
        devices.append(
            {
                "index": index,
                "name": properties.name,
                "compute_capability": f"{properties.major}.{properties.minor}",
                "total_vram_gb": round((total_bytes or properties.total_memory) / _GIB, 2),
                "free_vram_gb": round(free_bytes / _GIB, 2) if free_bytes is not None else None,
                "allocated_vram_gb": round(torch.cuda.memory_allocated(index) / _GIB, 3),
                "reserved_vram_gb": round(torch.cuda.memory_reserved(index) / _GIB, 3),
            }
        )
    snapshot["devices"] = devices
    return snapshot


def reset_peak_gpu_memory() -> None:
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
    except (ImportError, RuntimeError):
        pass


def peak_gpu_memory_gb() -> float | None:
    try:
        import torch
        if torch.cuda.is_available():
            return round(torch.cuda.max_memory_allocated() / _GIB, 3)
    except (ImportError, RuntimeError):
        pass
    return None


def release_gpu_cache() -> None:
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except (ImportError, RuntimeError):
        pass


def _nvidia_smi_devices() -> list[dict[str, Any]]:
    executable = shutil.which("nvidia-smi")
    if not executable:
        return []
    result = subprocess.run(
        [
            executable,
            "--query-gpu=index,name,memory.total,memory.free,compute_cap",
            "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    if result.returncode != 0:
        return []
    devices: list[dict[str, Any]] = []
    for row in csv.reader(io.StringIO(result.stdout)):
        if len(row) < 5:
            continue
        try:
            devices.append(
                {
                    "index": int(row[0].strip()),
                    "name": row[1].strip(),
                    "total_vram_gb": round(float(row[2]) / 1024, 2),
                    "free_vram_gb": round(float(row[3]) / 1024, 2),
                    "compute_capability": row[4].strip(),
                }
            )
        except ValueError:
            continue
    return devices
