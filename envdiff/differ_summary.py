"""Produces a human-readable summary from a FileDiff."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from envdiff.differ import FileDiff


@dataclass
class DiffSummaryResult:
    added: int
    removed: int
    changed: int
    total_changes: int
    lines: List[str]

    def is_clean(self) -> bool:
        return self.total_changes == 0

    def summary(self) -> str:
        if self.is_clean():
            return "No differences found."
        parts = []
        if self.added:
            parts.append(f"{self.added} added")
        if self.removed:
            parts.append(f"{self.removed} removed")
        if self.changed:
            parts.append(f"{self.changed} changed")
        return ", ".join(parts) + "."


def summarize_diff(diff: FileDiff, base_name: str = "base", target_name: str = "target") -> DiffSummaryResult:
    """Build a DiffSummaryResult from a FileDiff object."""
    lines: List[str] = []

    for key in sorted(diff.added):
        lines.append(f"  [+] {key} (only in {target_name})")

    for key in sorted(diff.removed):
        lines.append(f"  [-] {key} (only in {base_name})")

    for key, (old_val, new_val) in sorted(diff.changed.items()):
        lines.append(f"  [~] {key}: {old_val!r} -> {new_val!r}")

    return DiffSummaryResult(
        added=len(diff.added),
        removed=len(diff.removed),
        changed=len(diff.changed),
        total_changes=len(diff.added) + len(diff.removed) + len(diff.changed),
        lines=lines,
    )
