"""Small SQLite job store for one local workstation."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any
from uuid import uuid4

from app.models import JobView
from app.utils.files import MediaError


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def create(self, kind: str, target: str, payload: dict[str, Any]) -> JobView:
        job_id = uuid4().hex
        timestamp = now()
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO jobs
                (id, kind, target, status, progress, message, payload_json, created_at, updated_at)
                VALUES (?, ?, ?, 'queued', 0, 'Queued', ?, ?, ?)""",
                (job_id, kind, target, json.dumps(payload), timestamp, timestamp),
            )
        return self.get(job_id)

    def get(self, job_id: str) -> JobView:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            raise MediaError(f"Job not found: {job_id}")
        return self._view(row)

    def list(self, limit: int = 50) -> list[JobView]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [self._view(row) for row in rows]

    def update(self, job_id: str, *, status: str | None = None, progress: int | None = None, message: str | None = None, result: dict[str, Any] | None = None, error: str | None = None, started: bool = False, finished: bool = False) -> JobView:
        fields = ["updated_at = ?"]
        values: list[Any] = [now()]
        for name, value in (("status", status), ("progress", progress), ("message", message), ("error", error)):
            if value is not None:
                fields.append(f"{name} = ?")
                values.append(value)
        if result is not None:
            fields.append("result_json = ?")
            values.append(json.dumps(result))
        if started:
            fields.append("started_at = ?")
            values.append(now())
        if finished:
            fields.append("finished_at = ?")
            values.append(now())
        values.append(job_id)
        with self._connect() as connection:
            connection.execute(f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?", values)
        return self.get(job_id)

    def request_cancel(self, job_id: str) -> JobView:
        job = self.get(job_id)
        if job.status in {"completed", "failed", "cancelled"}:
            return job
        with self._connect() as connection:
            connection.execute("UPDATE jobs SET cancel_requested = 1, updated_at = ? WHERE id = ?", (now(), job_id))
        return self.get(job_id)

    def cancel_requested(self, job_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute("SELECT cancel_requested FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return bool(row and row[0])

    def recover_pending(self) -> list[str]:
        with self._connect() as connection:
            connection.execute("UPDATE jobs SET status = 'queued', message = 'Recovered after restart', updated_at = ? WHERE status = 'running'", (now(),))
            rows = connection.execute("SELECT id FROM jobs WHERE status = 'queued' AND cancel_requested = 0 ORDER BY created_at").fetchall()
        return [row[0] for row in rows]

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                target TEXT NOT NULL,
                status TEXT NOT NULL,
                progress INTEGER NOT NULL DEFAULT 0,
                message TEXT,
                payload_json TEXT NOT NULL,
                result_json TEXT,
                error TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                cancel_requested INTEGER NOT NULL DEFAULT 0
                )"""
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _view(row: sqlite3.Row) -> JobView:
        return JobView(
            id=row["id"], kind=row["kind"], target=row["target"], status=row["status"],
            progress=row["progress"], message=row["message"], payload=json.loads(row["payload_json"]),
            result=json.loads(row["result_json"]) if row["result_json"] else None,
            error=row["error"], created_at=row["created_at"], updated_at=row["updated_at"],
            started_at=row["started_at"], finished_at=row["finished_at"],
            cancel_requested=bool(row["cancel_requested"]),
        )
