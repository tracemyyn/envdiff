"""aliaser.py – rename keys using an alias map (old_name -> new_name).

Differs from renamer.py which applies bulk transforms (prefix/suffix/case);
aliaser.py applies an explicit one-to-one mapping from a provided dict.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AliasResult:
    original: Dict[str, str]
    aliased: Dict[str, str]
    applied: List[str] = field(default_factory=list)   # keys that were renamed
    skipped: List[str] = field(default_factory=list)   # alias keys not found in env

    @property
    def change_count(self) -> int:
        return len(self.applied)

    @property
    def was_modified(self) -> bool:
        return self.change_count > 0

    def summary(self) -> str:
        if not self.was_modified:
            return "No keys aliased."
        parts = [f"{self.change_count} key(s) aliased."]
        if self.skipped:
            parts.append(f"{len(self.skipped)} alias(es) not found in env.")
        return " ".join(parts)


def alias_keys(
    env: Dict[str, str],
    alias_map: Dict[str, str],
    *,
    keep_original: bool = False,
) -> AliasResult:
    """Return a new env with keys renamed according to *alias_map*.

    Parameters
    ----------
    env:
        The source environment dictionary.
    alias_map:
        Mapping of ``{old_key: new_key}``.
    keep_original:
        When *True* the original key is kept alongside the new alias.
        Defaults to *False* (original key is removed).
    """
    result: Dict[str, str] = dict(env)
    applied: List[str] = []
    skipped: List[str] = []

    for old_key, new_key in alias_map.items():
        if old_key not in result:
            skipped.append(old_key)
            continue
        value = result[old_key]
        if not keep_original:
            del result[old_key]
        result[new_key] = value
        applied.append(old_key)

    return AliasResult(
        original=dict(env),
        aliased=result,
        applied=applied,
        skipped=skipped,
    )
