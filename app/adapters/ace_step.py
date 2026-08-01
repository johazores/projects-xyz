"""ACE-Step 1.5 adapter for its official localhost asynchronous REST API."""

from __future__ import annotations

import json
import os
from pathlib import Path
from time import sleep, monotonic
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from app.core.adapters import ModelSpec, ProgressCallback
from app.utils.files import MediaError, media_output_dir, output_response, unique_path


class AceStepAdapter:
    def __init__(self, spec: ModelSpec):
        self.spec = spec
        self.model_id = spec.id
        self.base_url = ""
        self.api_key: str | None = None

    def load(self) -> None:
        env_name = str(self.spec.options.get("url_env", "ACESTEP_API_URL"))
        self.base_url = os.getenv(env_name, "").strip().rstrip("/")
        if not self.base_url:
            raise MediaError(
                "ACE-Step is not configured. Start `acestep-api` locally and set ACESTEP_API_URL."
            )
        host = (urlparse(self.base_url).hostname or "").lower()
        if host not in {"127.0.0.1", "localhost", "::1"}:
            raise MediaError("ACESTEP_API_URL must point to a localhost ACE-Step server.")
        self.api_key = os.getenv(str(self.spec.options.get("key_env", "ACESTEP_API_KEY")))
        try:
            self._request("GET", "/health")
        except MediaError:
            self._request("GET", "/v1/stats")

    def run(self, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
        prompt = str(payload.get("prompt", "")).strip()
        if not prompt:
            raise MediaError("ACE-Step requires a music prompt.")
        duration = max(10.0, min(600.0, float(payload.get("duration", 30))))
        audio_format = str(payload.get("audio_format", "mp3")).lower()
        if audio_format not in {"mp3", "wav", "flac", "opus", "aac"}:
            raise MediaError("ACE-Step audio_format must be mp3, wav, flac, opus, or aac.")

        request_payload: dict[str, Any] = {
            "prompt": prompt,
            "lyrics": str(payload.get("lyrics", "")),
            "instrumental": bool(payload.get("instrumental", not bool(payload.get("lyrics")))),
            "thinking": bool(payload.get("thinking", True)),
            "vocal_language": str(payload.get("language", "en")),
            "audio_format": audio_format,
            "audio_duration": duration,
            "inference_steps": max(1, min(20, int(payload.get("steps", 8)))),
            "batch_size": 1,
            "model": str(payload.get("model_name", self.spec.options.get("model", "acestep-v15-turbo"))),
            "lm_model_path": str(payload.get("lm_model", self.spec.options.get("lm_model", "acestep-5Hz-lm-0.6B"))),
            "lm_backend": str(payload.get("lm_backend", self.spec.options.get("lm_backend", "pt"))),
            "use_random_seed": payload.get("seed") is None,
            "seed": int(payload.get("seed", -1)),
        }
        for key in ("bpm", "key_scale", "time_signature"):
            if payload.get(key) not in (None, ""):
                request_payload[key] = payload[key]

        progress(10, "Submitting music generation")
        submitted = self._request("POST", "/release_task", request_payload)
        task_id = ((submitted.get("data") or {}).get("task_id"))
        if not task_id:
            raise MediaError("ACE-Step did not return a task_id.")

        timeout = max(30, min(3600, int(payload.get("timeout_seconds", 900))))
        poll_seconds = max(0.5, min(10.0, float(payload.get("poll_seconds", 2))))
        started = monotonic()
        item: dict[str, Any] | None = None
        while monotonic() - started < timeout:
            queried = self._request("POST", "/query_result", {"task_id_list": [task_id]})
            rows = queried.get("data") or []
            row = rows[0] if rows else {}
            status = int(row.get("status", 0))
            elapsed = monotonic() - started
            progress(min(88, 15 + int((elapsed / timeout) * 70)), "Generating music locally")
            if status == 2:
                raise MediaError(str(row.get("error") or "ACE-Step music generation failed."))
            if status == 1:
                result_value = row.get("result") or "[]"
                try:
                    parsed = json.loads(result_value) if isinstance(result_value, str) else result_value
                except json.JSONDecodeError as exc:
                    raise MediaError("ACE-Step returned invalid result metadata.") from exc
                item = parsed[0] if parsed else None
                break
            sleep(poll_seconds)
        if not item:
            raise MediaError("ACE-Step music generation timed out.")

        file_url = str(item.get("file", ""))
        if not file_url:
            raise MediaError("ACE-Step completed without an audio file URL.")
        destination = unique_path(
            media_output_dir("audio", payload.get("project")),
            payload.get("name", "generated-music"),
            f".{audio_format}",
        )
        destination.write_bytes(self._request_bytes(file_url))
        progress(96, "Saving generated music")
        result = output_response("audio", "music", destination, self.model_id).model_dump()
        result.update(
            {
                "task_id": task_id,
                "seed": item.get("seed_value"),
                "metadata": item.get("metas"),
                "dit_model": item.get("dit_model"),
                "lm_model": item.get("lm_model"),
            }
        )
        return result

    def unload(self) -> None:
        self.base_url = ""
        self.api_key = None

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        url = self._local_url(path)
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=30) as response:
                value = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise MediaError(f"Unable to communicate with local ACE-Step: {exc}") from exc
        if int(value.get("code", 200)) != 200 or value.get("error"):
            raise MediaError(str(value.get("error") or "ACE-Step request failed."))
        return value

    def _request_bytes(self, path: str) -> bytes:
        url = self._local_url(path)
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        try:
            with urlopen(Request(url, headers=headers), timeout=120) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            raise MediaError(f"Unable to download ACE-Step audio: {exc}") from exc

    def _local_url(self, path: str) -> str:
        url = path if path.startswith(("http://", "https://")) else urljoin(
            self.base_url + "/", path.lstrip("/")
        )
        parsed = urlparse(url)
        base = urlparse(self.base_url)
        host = (parsed.hostname or "").lower()
        if host not in {"127.0.0.1", "localhost", "::1"}:
            raise MediaError("ACE-Step returned a non-local URL, which was blocked.")
        if parsed.port != base.port:
            raise MediaError("ACE-Step returned a URL on an unexpected local port.")
        return url
