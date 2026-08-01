"""Local consent records required before cloning a reference voice."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4

from app.utils.files import MediaError, existing_file


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class VoiceConsentStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def create(
        self,
        *,
        voice_name: str,
        owner_name: str,
        reference_path: str,
        usage_scope: str,
        confirmed: bool,
        notes: str | None = None,
    ) -> dict[str, Any]:
        if not confirmed:
            raise MediaError("Voice consent must be explicitly confirmed.")
        source = existing_file(reference_path)
        record = {
            "id": uuid4().hex,
            "voice_name": voice_name.strip(),
            "owner_name": owner_name.strip(),
            "reference_path": str(source),
            "reference_sha256": _file_hash(source),
            "usage_scope": usage_scope.strip(),
            "notes": notes.strip() if notes else None,
            "created_at": _now(),
            "revoked_at": None,
        }
        if not record["voice_name"] or not record["owner_name"] or not record["usage_scope"]:
            raise MediaError("Voice name, owner name, and usage scope are required.")
        with self._lock:
            records = self._read()
            records.append(record)
            self._write(records)
        return record

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(reversed(self._read()))

    def revoke(self, consent_id: str) -> dict[str, Any]:
        with self._lock:
            records = self._read()
            for record in records:
                if record["id"] == consent_id:
                    if not record.get("revoked_at"):
                        record["revoked_at"] = _now()
                        self._write(records)
                    return record
        raise MediaError(f"Voice consent not found: {consent_id}")

    def require(self, consent_id: str | None, reference_path: str | Path) -> dict[str, Any]:
        if not consent_id:
            raise MediaError("A valid consent_id is required when using a reference voice.")
        source = existing_file(reference_path)
        current_hash = _file_hash(source)
        with self._lock:
            for record in self._read():
                if record["id"] != consent_id:
                    continue
                if record.get("revoked_at"):
                    raise MediaError("The selected voice consent has been revoked.")
                if record["reference_sha256"] != current_hash:
                    raise MediaError("The reference voice file does not match the consent record.")
                return record
        raise MediaError(f"Voice consent not found: {consent_id}")

    def _read(self) -> list[dict[str, Any]]:
        if not self.path.is_file():
            return []
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MediaError(f"Unable to read voice consent records: {exc}") from exc
        return value if isinstance(value, list) else []

    def _write(self, records: list[dict[str, Any]]) -> None:
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.path)
