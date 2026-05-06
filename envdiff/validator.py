"""Validate .env files against a schema of required keys and expected patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ValidationError:
    key: str
    message: str

    def __str__(self) -> str:
        return f"{self.key}: {self.message}"


@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    @property
    def error_count(self) -> int:
        return len(self.errors)

    def summary(self) -> str:
        if self.is_valid:
            return "All keys are valid."
        lines = [f"{self.error_count} validation error(s):"]
        for err in self.errors:
            lines.append(f"  - {err}")
        return "\n".join(lines)


@dataclass
class KeySchema:
    required: bool = False
    pattern: Optional[str] = None
    allowed_values: Optional[List[str]] = None
    description: str = ""


def validate_env(
    env: Dict[str, str],
    schema: Dict[str, KeySchema],
) -> ValidationResult:
    """Validate an env dict against a schema."""
    result = ValidationResult()

    for key, rule in schema.items():
        if key not in env:
            if rule.required:
                result.errors.append(ValidationError(key, "required key is missing"))
            continue

        value = env[key]

        if rule.pattern is not None:
            if not re.fullmatch(rule.pattern, value):
                result.errors.append(
                    ValidationError(key, f"value {value!r} does not match pattern {rule.pattern!r}")
                )

        if rule.allowed_values is not None:
            if value not in rule.allowed_values:
                result.errors.append(
                    ValidationError(
                        key,
                        f"value {value!r} not in allowed values {rule.allowed_values}",
                    )
                )

    return result
