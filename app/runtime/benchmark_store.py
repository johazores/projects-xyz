"""Append-only local benchmark records for real workstation measurements."""

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any


class BenchmarkStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def append(self, record: dict[str, Any]) -> None:
        with self._lock:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self.path.is_file():
            return []
        with self._lock:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        records: list[dict[str, Any]] = []
        for line in reversed(lines[-limit:]):
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return records
