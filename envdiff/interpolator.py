"""Variable interpolation for .env files.

Expands ${VAR} and $VAR references within env values using the
same env dict or a provided context.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolationResult:
    original: Dict[str, str]
    resolved: Dict[str, str]
    unresolved_keys: List[str] = field(default_factory=list)

    @property
    def has_unresolved(self) -> bool:
        return bool(self.unresolved_keys)

    @property
    def change_count(self) -> int:
        return sum(
            1 for k in self.resolved if self.resolved[k] != self.original.get(k)
        )

    def summary(self) -> str:
        parts = [f"{len(self.resolved)} keys"]
        if self.change_count:
            parts.append(f"{self.change_count} interpolated")
        if self.unresolved_keys:
            parts.append(f"{len(self.unresolved_keys)} unresolved")
        return ", ".join(parts)


def _resolve_value(
    value: str,
    env: Dict[str, str],
    context: Optional[Dict[str, str]],
    missing: List[str],
) -> str:
    lookup = dict(env)
    if context:
        lookup.update(context)

    def replace(m: re.Match) -> str:
        name = m.group(1) or m.group(2)
        if name in lookup:
            return lookup[name]
        if name not in missing:
            missing.append(name)
        return m.group(0)

    return _REF_RE.sub(replace, value)


def interpolate_env(
    env: Dict[str, str],
    context: Optional[Dict[str, str]] = None,
) -> InterpolationResult:
    """Resolve variable references in *env* values.

    References of the form ``${VAR}`` or ``$VAR`` are replaced with the
    corresponding value from *env* itself (self-referential) or *context*.
    Keys whose references cannot be resolved are recorded in
    ``InterpolationResult.unresolved_keys``.
    """
    unresolved: List[str] = []
    resolved: Dict[str, str] = {}
    for key, value in env.items():
        resolved[key] = _resolve_value(value, env, context, unresolved)
    return InterpolationResult(
        original=dict(env),
        resolved=resolved,
        unresolved_keys=list(dict.fromkeys(unresolved)),
    )
