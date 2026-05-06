"""Profile an env file: collect statistics and surface insights."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

_PLACEHOLDER_VALUES = {"", "changeme", "todo", "fixme", "placeholder", "your_value_here", "xxx"}
_SENSITIVE_PATTERNS = ("secret", "password", "passwd", "token", "api_key", "private", "auth")


@dataclass
class ProfileResult:
    total_keys: int = 0
    empty_values: List[str] = field(default_factory=list)
    placeholder_values: List[str] = field(default_factory=list)
    sensitive_keys: List[str] = field(default_factory=list)
    duplicate_values: Dict[str, List[str]] = field(default_factory=dict)
    longest_key: str = ""
    longest_value_key: str = ""

    @property
    def empty_count(self) -> int:
        return len(self.empty_values)

    @property
    def placeholder_count(self) -> int:
        return len(self.placeholder_values)

    @property
    def sensitive_count(self) -> int:
        return len(self.sensitive_keys)

    def summary(self) -> str:
        lines = [
            f"Total keys        : {self.total_keys}",
            f"Empty values      : {self.empty_count}",
            f"Placeholder values: {self.placeholder_count}",
            f"Sensitive keys    : {self.sensitive_count}",
            f"Duplicate values  : {len(self.duplicate_values)}",
        ]
        if self.longest_key:
            lines.append(f"Longest key       : {self.longest_key}")
        if self.longest_value_key:
            lines.append(f"Longest value key : {self.longest_value_key}")
        return "\n".join(lines)


def profile_env(env: Dict[str, str]) -> ProfileResult:
    """Analyse *env* and return a :class:`ProfileResult`."""
    result = ProfileResult(total_keys=len(env))

    value_index: Dict[str, List[str]] = {}

    longest_key = ""
    longest_value_key = ""

    for key, value in env.items():
        # empty
        if value == "":
            result.empty_values.append(key)

        # placeholder
        if value.lower() in _PLACEHOLDER_VALUES and value != "":
            result.placeholder_values.append(key)

        # sensitive
        key_lower = key.lower()
        if any(pat in key_lower for pat in _SENSITIVE_PATTERNS):
            result.sensitive_keys.append(key)

        # duplicate values
        value_index.setdefault(value, []).append(key)

        # longest key
        if len(key) > len(longest_key):
            longest_key = key

        # longest value
        if len(value) > len(env.get(longest_value_key, "")):
            longest_value_key = key

    result.longest_key = longest_key
    result.longest_value_key = longest_value_key

    result.duplicate_values = {
        val: keys for val, keys in value_index.items() if len(keys) > 1
    }

    return result
