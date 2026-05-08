"""Normalize .env file contents for consistent comparison."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class NormalizeResult:
    """Result of normalizing an env mapping."""

    normalized: Dict[str, str]
    changes: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, before, after)

    @property
    def change_count(self) -> int:
        return len(self.changes)

    @property
    def was_modified(self) -> bool:
        return bool(self.changes)

    def summary(self) -> str:
        if not self.was_modified:
            return "No normalization changes."
        lines = [f"{self.change_count} key(s) normalized:"]
        for key, before, after in self.changes:
            lines.append(f"  {key}: {before!r} -> {after!r}")
        return "\n".join(lines)


def _strip_inline_comment(value: str) -> str:
    """Remove trailing inline comments (unquoted # ...) from a value."""
    if value.startswith(("'", '"')):
        return value
    idx = value.find(" #")
    if idx != -1:
        return value[:idx].rstrip()
    return value


def _normalize_value(value: str) -> str:
    """Strip surrounding whitespace and inline comments."""
    value = value.strip()
    value = _strip_inline_comment(value)
    return value


def normalize_env(
    env: Dict[str, str],
    *,
    strip_values: bool = True,
    uppercase_keys: bool = False,
    remove_inline_comments: bool = True,
) -> NormalizeResult:
    """Return a normalized copy of *env* and record what changed."""
    normalized: Dict[str, str] = {}
    changes: List[Tuple[str, str, str]] = []

    for raw_key, raw_value in env.items():
        key = raw_key.upper() if uppercase_keys else raw_key
        value = raw_value

        if strip_values:
            value = value.strip()

        if remove_inline_comments:
            cleaned = _strip_inline_comment(value)
            if cleaned != value:
                changes.append((key, value, cleaned))
                value = cleaned

        if key != raw_key:
            changes.append((raw_key, raw_key, key))

        normalized[key] = value

    return NormalizeResult(normalized=normalized, changes=changes)
