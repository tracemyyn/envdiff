"""Audit .env files for common security and quality issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

# Keys that should never have empty values
_SENSITIVE_PATTERNS = ("SECRET", "PASSWORD", "TOKEN", "KEY", "PASS", "PRIVATE")

# Keys commonly left as placeholder values
_PLACEHOLDER_VALUES = {"changeme", "todo", "fixme", "placeholder", "example", "your_", "<", ">", "xxx"}


@dataclass
class AuditIssue:
    key: str
    message: str
    severity: str  # "warn" | "error"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


@dataclass
class AuditResult:
    issues: List[AuditIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warn_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warn")

    def summary(self) -> str:
        if not self.has_issues:
            return "No audit issues found."
        return f"{self.error_count} error(s), {self.warn_count} warning(s) found."


def _is_sensitive_key(key: str) -> bool:
    upper = key.upper()
    return any(pat in upper for pat in _SENSITIVE_PATTERNS)


def _looks_like_placeholder(value: str) -> bool:
    lower = value.lower()
    return any(p in lower for p in _PLACEHOLDER_VALUES)


def audit_env(env: Dict[str, str]) -> AuditResult:
    """Audit a parsed env dict and return an AuditResult with any issues."""
    result = AuditResult()

    for key, value in env.items():
        # Error: sensitive key with empty value
        if _is_sensitive_key(key) and value.strip() == "":
            result.issues.append(
                AuditIssue(key=key, message="Sensitive key has an empty value.", severity="error")
            )
            continue

        # Warning: sensitive key with placeholder value
        if _is_sensitive_key(key) and _looks_like_placeholder(value):
            result.issues.append(
                AuditIssue(key=key, message=f"Sensitive key appears to have a placeholder value: {value!r}", severity="warn")
            )

        # Warning: any key with empty value
        elif value.strip() == "":
            result.issues.append(
                AuditIssue(key=key, message="Key has an empty value.", severity="warn")
            )

    return result
