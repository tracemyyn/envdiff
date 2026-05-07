"""Redact sensitive values in an env dict before display or export."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

# Keys whose values should be redacted by default
_DEFAULT_SENSITIVE_PATTERNS: List[str] = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*PASSWD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE_KEY.*",
    r".*CREDENTIALS.*",
    r".*AUTH.*",
]

REDACTED_PLACEHOLDER = "***REDACTED***"


class Redactor:
    """Redacts sensitive values from an env mapping."""

    def __init__(
        self,
        patterns: Optional[List[str]] = None,
        placeholder: str = REDACTED_PLACEHOLDER,
        case_sensitive: bool = False,
    ) -> None:
        raw = patterns if patterns is not None else _DEFAULT_SENSITIVE_PATTERNS
        flags = 0 if case_sensitive else re.IGNORECASE
        self._patterns = [re.compile(p, flags) for p in raw]
        self.placeholder = placeholder

    def is_sensitive(self, key: str) -> bool:
        """Return True if *key* matches any sensitive pattern."""
        return any(p.fullmatch(key) for p in self._patterns)

    def redact(self, env: Dict[str, str]) -> Dict[str, str]:
        """Return a copy of *env* with sensitive values replaced."""
        return {
            k: (self.placeholder if self.is_sensitive(k) else v)
            for k, v in env.items()
        }

    def sensitive_keys(self, env: Dict[str, str]) -> List[str]:
        """Return a sorted list of keys that would be redacted."""
        return sorted(k for k in env if self.is_sensitive(k))


def redact_env(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
    placeholder: str = REDACTED_PLACEHOLDER,
) -> Dict[str, str]:
    """Convenience wrapper: redact *env* and return the sanitised copy."""
    return Redactor(patterns=patterns, placeholder=placeholder).redact(env)
