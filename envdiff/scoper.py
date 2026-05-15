"""Scope filtering: restrict an env dict to keys matching a given prefix scope."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeResult:
    """Result of scoping an env dict to a prefix."""

    scope: str
    matched: Dict[str, str] = field(default_factory=dict)
    excluded: List[str] = field(default_factory=list)
    strip_prefix: bool = False

    @property
    def match_count(self) -> int:
        return len(self.matched)

    @property
    def excluded_count(self) -> int:
        return len(self.excluded)

    @property
    def was_filtered(self) -> bool:
        return len(self.excluded) > 0

    def summary(self) -> str:
        stripped = " (prefix stripped)" if self.strip_prefix else ""
        return (
            f"Scope '{self.scope}'{stripped}: "
            f"{self.match_count} matched, {self.excluded_count} excluded."
        )


def scope_env(
    env: Dict[str, str],
    scope: str,
    strip_prefix: bool = False,
    separator: str = "_",
) -> ScopeResult:
    """Return only the keys whose names start with *scope* + *separator*.

    Parameters
    ----------
    env:          The source environment dictionary.
    scope:        Prefix to filter by (case-insensitive, e.g. ``"DB"``).
    strip_prefix: When *True* the leading ``<scope><separator>`` is removed
                  from the keys in the result.
    separator:    Character that separates the scope from the rest of the key
                  (default ``"_"``).
    """
    prefix = (scope.upper() + separator).upper()
    matched: Dict[str, str] = {}
    excluded: List[str] = []

    for key, value in env.items():
        if key.upper().startswith(prefix):
            out_key = key[len(prefix):] if strip_prefix else key
            matched[out_key] = value
        else:
            excluded.append(key)

    return ScopeResult(
        scope=scope,
        matched=matched,
        excluded=excluded,
        strip_prefix=strip_prefix,
    )
