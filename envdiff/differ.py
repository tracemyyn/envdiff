"""Line-level diff utilities for .env file contents."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class LineDiff:
    """Represents a single line-level difference between two env files."""

    line_number_base: int | None
    line_number_target: int | None
    kind: str  # 'added', 'removed', 'changed', 'unchanged'
    key: str
    base_value: str | None = None
    target_value: str | None = None

    def __str__(self) -> str:
        if self.kind == "added":
            return f"+ [{self.line_number_target}] {self.key}={self.target_value}"
        if self.kind == "removed":
            return f"- [{self.line_number_base}] {self.key}={self.base_value}"
        if self.kind == "changed":
            return (
                f"~ [{self.line_number_base}->{self.line_number_target}] "
                f"{self.key}: {self.base_value!r} -> {self.target_value!r}"
            )
        return f"  [{self.line_number_base}] {self.key}={self.base_value}"


@dataclass
class FileDiff:
    """Collection of line diffs between a base and target env mapping."""

    diffs: List[LineDiff] = field(default_factory=list)

    @property
    def added(self) -> List[LineDiff]:
        return [d for d in self.diffs if d.kind == "added"]

    @property
    def removed(self) -> List[LineDiff]:
        return [d for d in self.diffs if d.kind == "removed"]

    @property
    def changed(self) -> List[LineDiff]:
        return [d for d in self.diffs if d.kind == "changed"]

    @property
    def unchanged(self) -> List[LineDiff]:
        return [d for d in self.diffs if d.kind == "unchanged"]

    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def diff_envs(
    base: dict[str, str],
    target: dict[str, str],
    *,
    ignore_values: bool = False,
) -> FileDiff:
    """Compute a line-level diff between two parsed env mappings.

    Args:
        base: Mapping from the base environment file.
        target: Mapping from the target environment file.
        ignore_values: When True, only flag missing keys, not value changes.

    Returns:
        A :class:`FileDiff` describing all differences.
    """
    diffs: List[LineDiff] = []
    all_keys = sorted(set(base) | set(target))

    base_keys = list(base.keys())
    target_keys = list(target.keys())

    for key in all_keys:
        b_val = base.get(key)
        t_val = target.get(key)
        b_line = (base_keys.index(key) + 1) if key in base else None
        t_line = (target_keys.index(key) + 1) if key in target else None

        if b_val is None:
            diffs.append(LineDiff(None, t_line, "added", key, None, t_val))
        elif t_val is None:
            diffs.append(LineDiff(b_line, None, "removed", key, b_val, None))
        elif not ignore_values and b_val != t_val:
            diffs.append(LineDiff(b_line, t_line, "changed", key, b_val, t_val))
        else:
            diffs.append(LineDiff(b_line, t_line, "unchanged", key, b_val, t_val))

    return FileDiff(diffs=diffs)
