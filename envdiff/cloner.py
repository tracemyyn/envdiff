"""Clone an env file with optional transformations: strip values, redact secrets, or reset to blanks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

_SENSITIVE_FRAGMENTS = ("password", "secret", "token", "key", "api", "auth", "private")


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(frag in lower for frag in _SENSITIVE_FRAGMENTS)


@dataclass
class CloneResult:
    original: Dict[str, str]
    cloned: Dict[str, str]
    redacted_keys: list = field(default_factory=list)
    blanked_keys: list = field(default_factory=list)

    @property
    def change_count(self) -> int:
        return len(self.redacted_keys) + len(self.blanked_keys)

    @property
    def was_modified(self) -> bool:
        return self.change_count > 0

    def summary(self) -> str:
        parts = [f"{len(self.cloned)} key(s) cloned"]
        if self.redacted_keys:
            parts.append(f"{len(self.redacted_keys)} redacted")
        if self.blanked_keys:
            parts.append(f"{len(self.blanked_keys)} blanked")
        return ", ".join(parts) + "."


def clone_env(
    env: Dict[str, str],
    *,
    redact_sensitive: bool = False,
    blank_all: bool = False,
    placeholder: str = "REDACTED",
    extra_sensitive: Optional[list] = None,
) -> CloneResult:
    """Return a cloned copy of *env* with optional value transformations."""
    sensitive_extra = set(k.lower() for k in (extra_sensitive or []))
    cloned: Dict[str, str] = {}
    redacted: list = []
    blanked: list = []

    for key, value in env.items():
        if blank_all:
            cloned[key] = ""
            if value != "":
                blanked.append(key)
        elif redact_sensitive and (_is_sensitive(key) or key.lower() in sensitive_extra):
            cloned[key] = placeholder
            if value != placeholder:
                redacted.append(key)
        else:
            cloned[key] = value

    return CloneResult(
        original=dict(env),
        cloned=cloned,
        redacted_keys=redacted,
        blanked_keys=blanked,
    )
