"""Generate .env.example files from existing .env files by redacting values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.redactor import Redactor

# Keys whose values should be replaced with a descriptive placeholder
_SENSITIVE_PLACEHOLDER = "your_{key}_here"
_DEFAULT_PLACEHOLDER = ""


@dataclass
class TemplateResult:
    """Result of templating an env dictionary."""

    lines: List[str] = field(default_factory=list)
    redacted_keys: List[str] = field(default_factory=list)
    blanked_keys: List[str] = field(default_factory=list)

    @property
    def total_keys(self) -> int:
        return len(self.lines)

    def render(self) -> str:
        """Return the template as a newline-joined string."""
        return "\n".join(self.lines) + "\n"


def build_template(
    env: Dict[str, str],
    keep_values: Optional[List[str]] = None,
    sensitive_placeholder: bool = True,
) -> TemplateResult:
    """Convert an env dict into a template by stripping or replacing values.

    Args:
        env: Parsed environment dictionary.
        keep_values: List of keys whose values should be preserved as-is.
        sensitive_placeholder: If True, sensitive keys get a descriptive
            placeholder instead of an empty string.
    """
    keep_values = set(keep_values or [])
    redactor = Redactor()
    result = TemplateResult()

    for key, value in env.items():
        if key in keep_values:
            result.lines.append(f"{key}={value}")
            continue

        if redactor.is_sensitive(key) and sensitive_placeholder:
            placeholder = _SENSITIVE_PLACEHOLDER.format(key=key.lower())
            result.lines.append(f"{key}={placeholder}")
            result.redacted_keys.append(key)
        else:
            result.lines.append(f"{key}={_DEFAULT_PLACEHOLDER}")
            result.blanked_keys.append(key)

    return result


def write_template(result: TemplateResult, path: str) -> None:
    """Write a TemplateResult to a file."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(result.render())
