"""Annotate .env keys with inline comments describing their type, sensitivity, and status."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

_SENSITIVE_FRAGMENTS = ("password", "secret", "token", "key", "api", "auth", "private")
_PLACEHOLDER_VALUES = ("", "changeme", "todo", "fixme", "your_value", "placeholder", "xxx")


@dataclass
class AnnotateResult:
    annotated: Dict[str, Tuple[str, str]]  # key -> (value, comment)
    annotation_count: int = 0

    def was_annotated(self) -> bool:
        return self.annotation_count > 0

    def summary(self) -> str:
        return (
            f"{self.annotation_count} annotation(s) added across {len(self.annotated)} key(s)"
        )

    def render(self) -> str:
        lines: List[str] = []
        for key, (value, comment) in self.annotated.items():
            line = f"{key}={value}"
            if comment:
                line += f"  # {comment}"
            lines.append(line)
        return "\n".join(lines)


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(frag in lower for frag in _SENSITIVE_FRAGMENTS)


def _is_placeholder(value: str) -> bool:
    return value.strip().lower() in _PLACEHOLDER_VALUES


def _build_comment(key: str, value: str) -> str:
    parts: List[str] = []
    if _is_sensitive(key):
        parts.append("sensitive")
    if _is_placeholder(value):
        parts.append("placeholder")
    if not value.strip():
        parts.append("empty")
    return ", ".join(parts)


def annotate_env(env: Dict[str, str]) -> AnnotateResult:
    """Annotate each key in *env* with a descriptive inline comment."""
    annotated: Dict[str, Tuple[str, str]] = {}
    count = 0
    for key, value in env.items():
        comment = _build_comment(key, value)
        annotated[key] = (value, comment)
        if comment:
            count += 1
    return AnnotateResult(annotated=annotated, annotation_count=count)
