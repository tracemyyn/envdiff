"""Flatten nested-style env keys by expanding delimiter-separated segments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FlattenResult:
    """Result of flattening an env mapping."""

    original: Dict[str, str]
    flattened: Dict[str, str]
    renamed: Dict[str, str] = field(default_factory=dict)  # old_key -> new_key

    @property
    def change_count(self) -> int:
        """Number of keys that were renamed during flattening."""
        return len(self.renamed)

    @property
    def was_modified(self) -> bool:
        return self.change_count > 0

    def summary(self) -> str:
        if not self.was_modified:
            return "No keys required flattening."
        return (
            f"{self.change_count} key(s) flattened: "
            + ", ".join(f"{o} -> {n}" for o, n in self.renamed.items())
        )


def _flatten_key(key: str, delimiter: str, separator: str) -> str:
    """Replace all occurrences of *delimiter* in *key* with *separator*."""
    return key.replace(delimiter, separator)


def flatten_env(
    env: Dict[str, str],
    delimiter: str = ".",
    separator: str = "_",
    uppercase: bool = True,
) -> FlattenResult:
    """Return a FlattenResult where keys containing *delimiter* are rewritten.

    Parameters
    ----------
    env:        Parsed env mapping.
    delimiter:  The character (or string) to replace, default ``'.'``.
    separator:  Replacement character, default ``'_'``.
    uppercase:  When *True* (default) the resulting key is upper-cased.
    """
    flattened: Dict[str, str] = {}
    renamed: Dict[str, str] = {}

    for key, value in env.items():
        new_key = _flatten_key(key, delimiter, separator)
        if uppercase:
            new_key = new_key.upper()
        if new_key != key:
            renamed[key] = new_key
        flattened[new_key] = value

    return FlattenResult(original=dict(env), flattened=flattened, renamed=renamed)


def render_flattened(result: FlattenResult) -> List[str]:
    """Return the flattened env as a list of ``KEY=VALUE`` lines."""
    return [f"{k}={v}" for k, v in sorted(result.flattened.items())]
