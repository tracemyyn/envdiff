"""Summarizes an env file into human-readable statistics and highlights."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SummaryResult:
    total: int
    empty_keys: List[str] = field(default_factory=list)
    placeholder_keys: List[str] = field(default_factory=list)
    sensitive_keys: List[str] = field(default_factory=list)
    long_value_keys: List[str] = field(default_factory=list)

    # configurable thresholds
    long_value_threshold: int = 128

    @property
    def empty_count(self) -> int:
        return len(self.empty_keys)

    @property
    def placeholder_count(self) -> int:
        return len(self.placeholder_keys)

    @property
    def sensitive_count(self) -> int:
        return len(self.sensitive_keys)

    @property
    def long_value_count(self) -> int:
        return len(self.long_value_keys)

    def summary(self) -> str:
        lines = [
            f"Total keys    : {self.total}",
            f"Empty values  : {self.empty_count}",
            f"Placeholders  : {self.placeholder_count}",
            f"Sensitive keys: {self.sensitive_count}",
            f"Long values   : {self.long_value_count} (>{self.long_value_threshold} chars)",
        ]
        return "\n".join(lines)


_PLACEHOLDER_MARKERS = ("changeme", "todo", "fixme", "your_", "<", "example")
_SENSITIVE_FRAGMENTS = ("secret", "password", "passwd", "token", "api_key", "private_key", "auth")


def summarize_env(
    env: Dict[str, str],
    long_value_threshold: int = 128,
) -> SummaryResult:
    """Analyse *env* and return a :class:`SummaryResult`."""
    result = SummaryResult(
        total=len(env),
        long_value_threshold=long_value_threshold,
    )

    for key, value in env.items():
        key_lower = key.lower()
        value_lower = value.lower()

        if value == "":
            result.empty_keys.append(key)
        elif any(m in value_lower for m in _PLACEHOLDER_MARKERS):
            result.placeholder_keys.append(key)

        if any(f in key_lower for f in _SENSITIVE_FRAGMENTS):
            result.sensitive_keys.append(key)

        if len(value) > long_value_threshold:
            result.long_value_keys.append(key)

    return result
