"""Linter for .env files — checks for style and quality issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LintIssue:
    line: int
    key: Optional[str]
    message: str
    severity: str  # 'error' | 'warning' | 'info'

    def __str__(self) -> str:
        loc = f"line {self.line}" + (f" ({self.key})" if self.key else "")
        return f"[{self.severity.upper()}] {loc}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    def summary(self) -> str:
        if not self.has_issues:
            return "No lint issues found."
        return (
            f"{len(self.issues)} issue(s): "
            f"{self.error_count} error(s), {self.warning_count} warning(s)"
        )


_PLACEHOLDER_VALUES = {"", "TODO", "CHANGEME", "YOUR_VALUE_HERE", "xxx", "<value>"}


def lint_env(env: Dict[str, str], raw_lines: Optional[List[str]] = None) -> LintResult:
    """Run all lint checks on a parsed env dict.

    Args:
        env: Mapping of key -> value from parse_env_file.
        raw_lines: Optional original file lines for positional checks.
    """
    result = LintResult()
    seen_keys: Dict[str, int] = {}

    lines = raw_lines or []
    # Build a line-number index: key -> first line number (1-based)
    key_lines: Dict[str, int] = {}
    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            k = stripped.split("=", 1)[0].strip()
            if k not in key_lines:
                key_lines[k] = lineno

    for key, value in env.items():
        lineno = key_lines.get(key, 0)

        # Duplicate key detection (raw_lines pass)
        if key in seen_keys:
            result.issues.append(
                LintIssue(lineno, key, f"Duplicate key '{key}' (first seen at line {seen_keys[key]})", "error")
            )
        else:
            seen_keys[key] = lineno

        # Key naming convention: should be UPPER_SNAKE_CASE
        if not key.isupper() and key == key.upper().replace("-", "_"):
            pass  # acceptable
        elif key != key.upper():
            result.issues.append(
                LintIssue(lineno, key, f"Key '{key}' is not uppercase", "warning")
            )

        # Placeholder value check
        if value.strip().upper() in {p.upper() for p in _PLACEHOLDER_VALUES}:
            result.issues.append(
                LintIssue(lineno, key, f"Key '{key}' has a placeholder value", "warning")
            )

        # Whitespace in value (unquoted leading/trailing)
        if value != value.strip():
            result.issues.append(
                LintIssue(lineno, key, f"Key '{key}' value has leading/trailing whitespace", "info")
            )

    return result
