"""Filter utilities for envdiff — allow/deny key patterns when comparing envs."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class KeyFilter:
    """Holds include/exclude glob patterns and applies them to key sets."""

    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)

    def matches(self, key: str) -> bool:
        """Return True if *key* should be kept after applying include/exclude rules.

        Rules:
        - If *include* patterns are given, the key must match at least one.
        - If *exclude* patterns are given, the key must not match any.
        """
        if self.include:
            included = any(fnmatch.fnmatch(key, pat) for pat in self.include)
            if not included:
                return False
        if self.exclude:
            excluded = any(fnmatch.fnmatch(key, pat) for pat in self.exclude)
            if excluded:
                return False
        return True

    def apply(self, keys: Iterable[str]) -> list[str]:
        """Return the subset of *keys* that pass the filter, preserving order."""
        return [k for k in keys if self.matches(k)]

    def filter_env(self, env: dict[str, str]) -> dict[str, str]:
        """Return a new dict containing only the entries whose keys pass the filter."""
        return {k: v for k, v in env.items() if self.matches(k)}


def build_filter(
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> KeyFilter:
    """Convenience constructor that accepts *None* for empty lists."""
    return KeyFilter(
        include=include or [],
        exclude=exclude or [],
    )
