"""Type-casting inference for .env values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

_BOOL_TRUE = {"true", "yes", "1", "on"}
_BOOL_FALSE = {"false", "no", "0", "off"}


def _infer_type(value: str) -> str:
    """Return a string label for the inferred type of *value*."""
    if value == "":
        return "empty"
    if value.lower() in _BOOL_TRUE | _BOOL_FALSE:
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    return "str"


@dataclass
class CastResult:
    """Result of casting inference over an env mapping."""

    types: Dict[str, str] = field(default_factory=dict)
    # key -> inferred Python-like type label

    @property
    def type_count(self) -> int:
        return len(self.types)

    def keys_of_type(self, type_label: str) -> list:
        return [k for k, t in self.types.items() if t == type_label]

    def summary(self) -> str:
        counts: Dict[str, int] = {}
        for t in self.types.values():
            counts[t] = counts.get(t, 0) + 1
        parts = ", ".join(f"{t}={n}" for t, n in sorted(counts.items()))
        return f"CastResult({self.type_count} keys: {parts})"


def cast_env(env: Dict[str, str]) -> CastResult:
    """Infer the type of every value in *env* and return a :class:`CastResult`."""
    types = {key: _infer_type(value) for key, value in env.items()}
    return CastResult(types=types)
