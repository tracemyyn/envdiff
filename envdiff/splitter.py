"""Split a single .env file into multiple files grouped by key prefix."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SplitResult:
    """Result of splitting an env dict by prefix."""

    groups: Dict[str, Dict[str, str]] = field(default_factory=dict)
    ungrouped: Dict[str, str] = field(default_factory=dict)

    @property
    def group_count(self) -> int:
        return len(self.groups)

    @property
    def total_keys(self) -> int:
        return sum(len(v) for v in self.groups.values()) + len(self.ungrouped)

    @property
    def was_split(self) -> bool:
        return self.group_count > 0

    def summary(self) -> str:
        parts = [f"{self.group_count} group(s), {self.total_keys} total key(s)"]
        if self.ungrouped:
            parts.append(f"{len(self.ungrouped)} ungrouped key(s)")
        return "; ".join(parts)


def split_env(
    env: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    separator: str = "_",
    strip_prefix: bool = False,
) -> SplitResult:
    """Split *env* into groups by *prefixes*.

    If *prefixes* is None the function auto-detects prefixes from the keys
    (the part before the first *separator*).

    When *strip_prefix* is True the leading ``PREFIX_`` is removed from keys
    in each group's output dict.
    """
    if prefixes is None:
        seen: Dict[str, int] = {}
        for key in env:
            if separator in key:
                p = key.split(separator, 1)[0]
                seen[p] = seen.get(p, 0) + 1
        prefixes = [p for p, count in seen.items() if count > 1]

    groups: Dict[str, Dict[str, str]] = {p: {} for p in prefixes}
    ungrouped: Dict[str, str] = {}

    prefix_set = set(prefixes)

    for key, value in env.items():
        matched = False
        if separator in key:
            p = key.split(separator, 1)[0]
            if p in prefix_set:
                out_key = key[len(p) + len(separator):] if strip_prefix else key
                groups[p][out_key] = value
                matched = True
        if not matched:
            ungrouped[key] = value

    # Remove empty groups that were explicitly requested but had no keys
    groups = {p: d for p, d in groups.items() if d}

    return SplitResult(groups=groups, ungrouped=ungrouped)


def render_split(result: SplitResult, group_name: str) -> str:
    """Render a single group from a SplitResult as .env text."""
    lines = []
    group = result.groups.get(group_name, {})
    for key, value in group.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")
