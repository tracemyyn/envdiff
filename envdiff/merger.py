"""Merge multiple .env files into a unified output, with conflict resolution."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class MergeResult:
    """Outcome of merging two or more .env mappings."""

    merged: Dict[str, str] = field(default_factory=dict)
    conflicts: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)
    """key -> list of (source_name, value) tuples that disagreed."""

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def conflict_count(self) -> int:
        return len(self.conflicts)


def merge_envs(
    envs: List[Tuple[str, Dict[str, str]]],
    strategy: str = "first",
) -> MergeResult:
    """Merge a list of (name, env_dict) pairs.

    Parameters
    ----------
    envs:
        Ordered list of ``(source_name, mapping)`` pairs.  Earlier entries
        are considered higher-priority when *strategy* is ``"first"``;
        later entries win when *strategy* is ``"last"``.
    strategy:
        ``"first"`` – keep the value from the first source that defines a key.
        ``"last"``  – keep the value from the last source that defines a key.

    Returns
    -------
    MergeResult
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown merge strategy {strategy!r}; use 'first' or 'last'.")

    merged: Dict[str, str] = {}
    seen: Dict[str, List[Tuple[str, str]]] = {}  # key -> [(name, value), ...]

    ordered = envs if strategy == "last" else list(reversed(envs))

    for name, mapping in ordered:
        for key, value in mapping.items():
            seen.setdefault(key, []).append((name, value))
            merged[key] = value  # last write wins after ordering

    conflicts: Dict[str, List[Tuple[str, str]]] = {
        key: sources
        for key, sources in seen.items()
        if len({v for _, v in sources}) > 1
    }

    return MergeResult(merged=merged, conflicts=conflicts)


def render_merged(result: MergeResult, comment_conflicts: bool = True) -> str:
    """Render a MergeResult back to .env file text."""
    lines: List[str] = []
    for key, value in sorted(result.merged.items()):
        if comment_conflicts and key in result.conflicts:
            sources = ", ".join(f"{n}={v!r}" for n, v in result.conflicts[key])
            lines.append(f"# CONFLICT: {sources}")
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")
