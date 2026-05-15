"""Trims leading/trailing whitespace from .env values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TrimResult:
    """Result of trimming whitespace from env values."""

    original: Dict[str, str]
    trimmed: Dict[str, str]
    changed_keys: List[str] = field(default_factory=list)

    @property
    def change_count(self) -> int:
        """Number of keys whose values were trimmed."""
        return len(self.changed_keys)

    @property
    def was_modified(self) -> bool:
        """True if any value was trimmed."""
        return self.change_count > 0

    def summary(self) -> str:
        """Human-readable summary of the trim operation."""
        if not self.was_modified:
            return "No values required trimming."
        keys = ", ".join(self.changed_keys)
        return f"Trimmed {self.change_count} value(s): {keys}"


def trim_env(env: Dict[str, str]) -> TrimResult:
    """Trim leading and trailing whitespace from all values in *env*.

    Keys are never modified; only values are trimmed.

    Args:
        env: Mapping of environment variable names to their raw values.

    Returns:
        A :class:`TrimResult` describing what changed.
    """
    trimmed: Dict[str, str] = {}
    changed_keys: List[str] = []

    for key, value in env.items():
        new_value = value.strip()
        trimmed[key] = new_value
        if new_value != value:
            changed_keys.append(key)

    return TrimResult(
        original=dict(env),
        trimmed=trimmed,
        changed_keys=sorted(changed_keys),
    )
