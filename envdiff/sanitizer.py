"""Sanitize .env values by removing control characters and null bytes."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


@dataclass
class SanitizeResult:
    original: Dict[str, str]
    sanitized: Dict[str, str]
    changes: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, before, after)

    @property
    def change_count(self) -> int:
        return len(self.changes)

    @property
    def was_modified(self) -> bool:
        return bool(self.changes)

    def summary(self) -> str:
        if not self.was_modified:
            return "No sanitization needed."
        return (
            f"Sanitized {self.change_count} value(s) out of {len(self.original)} key(s)."
        )


def _sanitize_value(value: str) -> str:
    """Strip control characters and normalize unicode to NFC form."""
    cleaned = _CONTROL_RE.sub("", value)
    cleaned = unicodedata.normalize("NFC", cleaned)
    return cleaned


def sanitize_env(
    env: Dict[str, str],
    *,
    strip_null_bytes: bool = True,
    normalize_unicode: bool = True,
) -> SanitizeResult:
    """Return a SanitizeResult with cleaned values."""
    sanitized: Dict[str, str] = {}
    changes: List[Tuple[str, str, str]] = []

    for key, value in env.items():
        new_value = value

        if strip_null_bytes:
            new_value = new_value.replace("\x00", "")

        new_value = _sanitize_value(new_value) if normalize_unicode else new_value

        if not normalize_unicode:
            # Still strip control chars even if unicode normalization is off
            new_value = _CONTROL_RE.sub("", new_value)

        if new_value != value:
            changes.append((key, value, new_value))

        sanitized[key] = new_value

    return SanitizeResult(original=dict(env), sanitized=sanitized, changes=changes)
