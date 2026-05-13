"""Detect and remove duplicate keys within a single .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DeduplicateResult:
    """Result of a deduplication pass over an env mapping."""

    original: Dict[str, List[str]]  # key -> all values seen (in order)
    deduped: Dict[str, str]         # key -> winning (last) value
    duplicates: Dict[str, List[str]]  # only keys that appeared more than once

    @property
    def duplicate_count(self) -> int:
        """Number of keys that had duplicate definitions."""
        return len(self.duplicates)

    @property
    def has_duplicates(self) -> bool:
        return self.duplicate_count > 0

    def summary(self) -> str:
        if not self.has_duplicates:
            return "No duplicate keys found."
        lines = [f"{self.duplicate_count} duplicate key(s) detected:"]
        for key, values in self.duplicates.items():
            rendered = ", ".join(f"'{v}'" for v in values)
            lines.append(f"  {key}: [{rendered}] -> kept '{self.deduped[key]}'")
        return "\n".join(lines)


def deduplicate_lines(lines: List[str]) -> DeduplicateResult:
    """Parse *raw* lines from an .env file and detect duplicate keys.

    Blank lines and comments are ignored.  The *last* definition of a key
    wins (consistent with shell semantics).
    """
    seen: Dict[str, List[str]] = {}

    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        seen.setdefault(key, []).append(value)

    deduped = {k: vals[-1] for k, vals in seen.items()}
    duplicates = {k: vals for k, vals in seen.items() if len(vals) > 1}
    return DeduplicateResult(original=seen, deduped=deduped, duplicates=duplicates)


def deduplicate_env(env: Dict[str, str]) -> DeduplicateResult:
    """Wrap an already-parsed env dict (no duplicates possible, convenience)."""
    original = {k: [v] for k, v in env.items()}
    return DeduplicateResult(original=original, deduped=dict(env), duplicates={})
