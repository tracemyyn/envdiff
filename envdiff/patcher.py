"""Apply a set of key patches (add, update, delete) to an env dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PatchOp:
    """A single patch operation."""

    action: str  # 'set' | 'delete'
    key: str
    value: Optional[str] = None

    def __str__(self) -> str:
        if self.action == "delete":
            return f"DELETE {self.key}"
        return f"SET {self.key}={self.value}"


@dataclass
class PatchResult:
    """Result of applying patches to an env dict."""

    patched: Dict[str, str]
    applied: List[PatchOp] = field(default_factory=list)
    skipped: List[PatchOp] = field(default_factory=list)

    @property
    def change_count(self) -> int:
        return len(self.applied)

    @property
    def was_modified(self) -> bool:
        return self.change_count > 0

    def summary(self) -> str:
        return (
            f"{self.change_count} patch(es) applied, "
            f"{len(self.skipped)} skipped."
        )


def parse_patch_line(line: str) -> Optional[PatchOp]:
    """Parse a single patch-file line into a PatchOp.

    Syntax:
        SET KEY=value
        DELETE KEY
    Lines starting with '#' or blank lines are ignored.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if line.upper().startswith("DELETE "):
        key = line[7:].strip()
        return PatchOp(action="delete", key=key)
    if line.upper().startswith("SET "):
        rest = line[4:]
        key, _, value = rest.partition("=")
        return PatchOp(action="set", key=key.strip(), value=value)
    raise ValueError(f"Unknown patch directive: {line!r}")


def apply_patches(
    env: Dict[str, str],
    ops: List[PatchOp],
    *,
    skip_missing_deletes: bool = True,
) -> PatchResult:
    """Apply a list of PatchOp objects to *env* and return a PatchResult."""
    patched = dict(env)
    applied: List[PatchOp] = []
    skipped: List[PatchOp] = []

    for op in ops:
        if op.action == "set":
            patched[op.key] = op.value or ""
            applied.append(op)
        elif op.action == "delete":
            if op.key in patched:
                del patched[op.key]
                applied.append(op)
            elif skip_missing_deletes:
                skipped.append(op)
            else:
                skipped.append(op)

    return PatchResult(patched=patched, applied=applied, skipped=skipped)
