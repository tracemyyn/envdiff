"""Rename keys in an .env mapping, optionally applying a prefix or suffix."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameResult:
    """Result of a rename operation."""

    renamed: Dict[str, str] = field(default_factory=dict)  # old_key -> new_key
    env: Dict[str, str] = field(default_factory=dict)      # final env dict
    skipped: List[str] = field(default_factory=list)       # keys not renamed

    @property
    def change_count(self) -> int:
        return len(self.renamed)

    @property
    def was_modified(self) -> bool:
        return self.change_count > 0

    def summary(self) -> str:
        if not self.was_modified:
            return "No keys renamed."
        parts = [f"{old} -> {new}" for old, new in self.renamed.items()]
        return f"Renamed {self.change_count} key(s): " + ", ".join(parts)


def rename_keys(
    env: Dict[str, str],
    mapping: Optional[Dict[str, str]] = None,
    prefix: str = "",
    suffix: str = "",
    uppercase: bool = False,
    lowercase: bool = False,
) -> RenameResult:
    """Return a RenameResult applying explicit mapping and/or prefix/suffix transforms.

    Explicit *mapping* takes precedence over prefix/suffix transforms.
    If both *uppercase* and *lowercase* are True, uppercase wins.
    """
    mapping = mapping or {}
    renamed: Dict[str, str] = {}
    new_env: Dict[str, str] = {}
    skipped: List[str] = []

    for key, value in env.items():
        if key in mapping:
            new_key = mapping[key]
        else:
            new_key = f"{prefix}{key}{suffix}"
            if uppercase:
                new_key = new_key.upper()
            elif lowercase:
                new_key = new_key.lower()

        if new_key != key:
            renamed[key] = new_key
        else:
            skipped.append(key)

        new_env[new_key] = value

    return RenameResult(renamed=renamed, env=new_env, skipped=skipped)
