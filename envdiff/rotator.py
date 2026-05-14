"""Key rotation helper: flags stale keys based on age metadata in a pin file."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from envdiff.pinner import PinEntry

_SENSITIVE_FRAGMENTS = ("password", "secret", "token", "key", "api", "auth", "pass")


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(f in lower for f in _SENSITIVE_FRAGMENTS)


@dataclass
class RotationIssue:
    key: str
    reason: str
    days_old: Optional[int] = None

    def __str__(self) -> str:
        age = f" ({self.days_old}d old)" if self.days_old is not None else ""
        return f"{self.key}: {self.reason}{age}"


@dataclass
class RotateResult:
    issues: List[RotationIssue] = field(default_factory=list)
    checked: int = 0

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    def summary(self) -> str:
        if not self.has_issues:
            return f"All {self.checked} keys are fresh."
        return (
            f"{self.issue_count} rotation issue(s) found across {self.checked} keys."
        )


def check_rotation(
    env: Dict[str, str],
    pins: List[PinEntry],
    max_age_days: int = 90,
) -> RotateResult:
    """Compare current env against pinned entries and flag stale sensitive keys."""
    pinned: Dict[str, PinEntry] = {p.key: p for p in pins}
    issues: List[RotationIssue] = []
    now = datetime.now(tz=timezone.utc)

    for key, value in env.items():
        if not _is_sensitive(key):
            continue

        if key not in pinned:
            issues.append(RotationIssue(key=key, reason="no pin record found"))
            continue

        entry = pinned[key]
        current_hash = hashlib.sha256(value.encode()).hexdigest()
        if current_hash == entry.value_hash:
            # Value unchanged since pin — check age
            try:
                pinned_at = datetime.fromisoformat(entry.pinned_at).replace(
                    tzinfo=timezone.utc
                )
                age_days = (now - pinned_at).days
                if age_days > max_age_days:
                    issues.append(
                        RotationIssue(
                            key=key,
                            reason=f"value unchanged for over {max_age_days} days",
                            days_old=age_days,
                        )
                    )
            except (ValueError, AttributeError):
                issues.append(
                    RotationIssue(key=key, reason="invalid pinned_at timestamp")
                )

    return RotateResult(issues=issues, checked=sum(1 for k in env if _is_sensitive(k)))
