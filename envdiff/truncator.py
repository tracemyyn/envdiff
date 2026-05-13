"""Truncate long values in an env dictionary to a maximum length."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

DEFAULT_MAX_LENGTH = 64
DEFAULT_SUFFIX = "..."


@dataclass
class TruncateResult:
    original: Dict[str, str]
    truncated: Dict[str, str]
    changed_keys: List[str] = field(default_factory=list)

    @property
    def change_count(self) -> int:
        return len(self.changed_keys)

    @property
    def was_modified(self) -> bool:
        return bool(self.changed_keys)

    def summary(self) -> str:
        if not self.was_modified:
            return "No values truncated."
        keys = ", ".join(self.changed_keys)
        return f"{self.change_count} value(s) truncated: {keys}"


def truncate_env(
    env: Dict[str, str],
    max_length: int = DEFAULT_MAX_LENGTH,
    suffix: str = DEFAULT_SUFFIX,
) -> TruncateResult:
    """Return a TruncateResult with values longer than *max_length* shortened.

    The suffix is appended to indicate truncation.  Keys are never modified.
    """
    if max_length < len(suffix):
        raise ValueError(
            f"max_length ({max_length}) must be >= suffix length ({len(suffix)})"
        )

    truncated: Dict[str, str] = {}
    changed_keys: List[str] = []

    for key, value in env.items():
        if len(value) > max_length:
            keep = max_length - len(suffix)
            truncated[key] = value[:keep] + suffix
            changed_keys.append(key)
        else:
            truncated[key] = value

    return TruncateResult(
        original=dict(env),
        truncated=truncated,
        changed_keys=changed_keys,
    )
