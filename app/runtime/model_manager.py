"""Keeps at most one heavyweight local model active and records benchmarks."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from time import perf_counter
from typing import Any

from app.core.adapters import ModelAdapter, ProgressCallback
from app.core.registry import ModelRegistry
from app.runtime.benchmark_store import BenchmarkStore
from app.runtime.hardware import hardware_snapshot, peak_gpu_memory_gb, reset_peak_gpu_memory


class ModelManager:
    def __init__(self, registry: ModelRegistry, benchmarks: BenchmarkStore | None = None):
        self.registry = registry
        self.benchmarks = benchmarks
        self._active_id: str | None = None
        self._adapter: ModelAdapter | None = None
        self._lock = RLock()

    @property
    def active_id(self) -> str | None:
        return self._active_id

    def run(
        self,
        model_id: str,
        payload: dict[str, Any],
        progress: ProgressCallback,
    ) -> dict[str, Any]:
        with self._lock:
            started = perf_counter()
            loading_started = perf_counter()
            reused = self._active_id == model_id and self._adapter is not None
            reset_peak_gpu_memory()
            try:
                adapter = self._get(model_id)
                load_seconds = perf_counter() - loading_started
                run_started = perf_counter()
                result = adapter.run(payload, progress)
                run_seconds = perf_counter() - run_started
                record = self._record(
                    model_id=model_id,
                    payload=payload,
                    success=True,
                    reused=reused,
                    load_seconds=load_seconds,
                    run_seconds=run_seconds,
                    total_seconds=perf_counter() - started,
                    result=result,
                )
                if isinstance(result, dict):
                    result.setdefault("benchmark", record)
                return result
            except Exception as exc:
                self._record(
                    model_id=model_id,
                    payload=payload,
                    success=False,
                    reused=reused,
                    load_seconds=perf_counter() - loading_started,
                    run_seconds=None,
                    total_seconds=perf_counter() - started,
                    error=str(exc),
                )
                raise

    def unload(self) -> None:
        with self._lock:
            if self._adapter is not None:
                self._adapter.unload()
            self._adapter = None
            self._active_id = None

    def _get(self, model_id: str) -> ModelAdapter:
        if self._active_id == model_id and self._adapter is not None:
            return self._adapter
        self.unload()
        adapter = self.registry.create(model_id)
        adapter.load()
        self._adapter = adapter
        self._active_id = model_id
        return adapter

    def _record(
        self,
        *,
        model_id: str,
        payload: dict[str, Any],
        success: bool,
        reused: bool,
        load_seconds: float,
        run_seconds: float | None,
        total_seconds: float,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> dict[str, Any]:
        spec = self.registry.get(model_id)
        hardware = hardware_snapshot()
        devices = hardware.get("devices") or []
        record: dict[str, Any] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "model": model_id,
            "capability": spec.capability,
            "success": success,
            "model_reused": reused,
            "load_seconds": round(load_seconds, 3),
            "run_seconds": round(run_seconds, 3) if run_seconds is not None else None,
            "total_seconds": round(total_seconds, 3),
            "peak_allocated_vram_gb": peak_gpu_memory_gb(),
            "gpu": devices[0] if devices else None,
            "request": _payload_summary(payload),
        }
        if result:
            for key in ("backend", "actual", "retry_used", "reported_peak_vram_mb"):
                if key in result:
                    record[key] = result[key]
        if error:
            record["error"] = error
        if self.benchmarks is not None:
            self.benchmarks.append(record)
        return record


def _payload_summary(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "width", "height", "num_frames", "frames", "steps", "guidance",
        "seed", "fps", "count", "scale", "tile", "output_format",
    }
    summary: dict[str, Any] = {"keys": sorted(payload)}
    for key in allowed:
        if key not in payload:
            continue
        value = payload.get(key)
        if isinstance(value, (str, int, float, bool)) or value is None:
            summary[key] = value
    for key in ("input_path", "image_path", "subject_path"):
        value = payload.get(key)
        if value:
            summary[key] = Path(str(value)).name
    return summary
