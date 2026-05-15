"""Cascade multiple .env files, later files overriding earlier ones."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class CascadeResult:
    """Result of cascading multiple env files."""

    resolved: Dict[str, str]
    sources: Dict[str, str]          # key -> filename that provided final value
    overrides: List[Tuple[str, str, str, str]]  # (key, old_val, new_val, filename)
    file_names: List[str]

    @property
    def override_count(self) -> int:
        return len(self.overrides)

    @property
    def total_keys(self) -> int:
        return len(self.resolved)

    @property
    def was_overridden(self) -> bool:
        return len(self.overrides) > 0

    def summary(self) -> str:
        parts = [
            f"{self.total_keys} key(s) resolved across {len(self.file_names)} file(s)",
        ]
        if self.override_count:
            parts.append(f"{self.override_count} override(s) applied")
        return "; ".join(parts)


def cascade_envs(
    envs: List[Dict[str, str]],
    file_names: List[str] | None = None,
) -> CascadeResult:
    """Merge a sequence of env dicts, later entries win.

    Args:
        envs: Ordered list of parsed env dicts (first = lowest priority).
        file_names: Optional human-readable labels for each dict.

    Returns:
        CascadeResult with the fully resolved env and provenance info.
    """
    if file_names is None:
        file_names = [f"file{i + 1}" for i in range(len(envs))]

    if len(file_names) != len(envs):
        raise ValueError("file_names length must match envs length")

    resolved: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    overrides: List[Tuple[str, str, str, str]] = []

    for env, name in zip(envs, file_names):
        for key, value in env.items():
            if key in resolved and resolved[key] != value:
                overrides.append((key, resolved[key], value, name))
            resolved[key] = value
            sources[key] = name

    return CascadeResult(
        resolved=resolved,
        sources=sources,
        overrides=overrides,
        file_names=list(file_names),
    )
