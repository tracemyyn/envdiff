"""Mask sensitive values in an env dict, replacing them with partial redactions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_PATTERNS = ("SECRET", "PASSWORD", "PASSWD", "TOKEN", "API_KEY", "PRIVATE", "AUTH")
_DEFAULT_VISIBLE = 4
_MASK_CHAR = "*"


@dataclass
class MaskResult:
    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str] = field(default_factory=list)

    @property
    def mask_count(self) -> int:
        return len(self.masked_keys)

    @property
    def was_modified(self) -> bool:
        return self.mask_count > 0

    def summary(self) -> str:
        if not self.was_modified:
            return "No sensitive values masked."
        keys = ", ".join(self.masked_keys)
        return f"{self.mask_count} value(s) masked: {keys}"


def _is_sensitive(key: str) -> bool:
    upper = key.upper()
    return any(pat in upper for pat in _SENSITIVE_PATTERNS)


def _mask_value(value: str, visible: int = _DEFAULT_VISIBLE) -> str:
    if not value:
        return value
    if len(value) <= visible:
        return _MASK_CHAR * len(value)
    return value[:visible] + _MASK_CHAR * (len(value) - visible)


def mask_env(
    env: Dict[str, str],
    visible_chars: int = _DEFAULT_VISIBLE,
    extra_patterns: List[str] | None = None,
) -> MaskResult:
    """Return a MaskResult with sensitive values partially masked."""
    patterns = list(_SENSITIVE_PATTERNS)
    if extra_patterns:
        patterns.extend(p.upper() for p in extra_patterns)

    masked: Dict[str, str] = {}
    masked_keys: List[str] = []

    for key, value in env.items():
        upper = key.upper()
        if any(pat in upper for pat in patterns):
            masked[key] = _mask_value(value, visible_chars)
            masked_keys.append(key)
        else:
            masked[key] = value

    return MaskResult(original=dict(env), masked=masked, masked_keys=sorted(masked_keys))
