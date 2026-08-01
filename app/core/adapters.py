"""Small contracts shared by local model adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

ProgressCallback = Callable[[int, str], None]


class ModelAdapter(Protocol):
    model_id: str

    def load(self) -> None: ...
    def run(self, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]: ...
    def unload(self) -> None: ...


@dataclass(frozen=True, slots=True)
class ModelSpec:
    id: str
    capability: str
    adapter: str
    description: str
    implemented: bool = False
    recommended: bool = False
    vram_gb: float | None = None
    dependency_group: str | None = None
    packages: tuple[str, ...] = ()
    executable: str | None = None
    notes: str | None = None
    options: dict[str, Any] = field(default_factory=dict)
