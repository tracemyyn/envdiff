"""Groups .env keys by prefix (e.g. DB_, AWS_, APP_) for organized reporting."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_DEFAULT_SEPARATOR = "_"


@dataclass
class GroupResult:
    groups: Dict[str, List[str]] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)

    @property
    def group_count(self) -> int:
        return len(self.groups)

    @property
    def total_keys(self) -> int:
        return sum(len(v) for v in self.groups.values()) + len(self.ungrouped)

    def summary(self) -> str:
        lines = [f"Groups: {self.group_count}, Total keys: {self.total_keys}"]
        for prefix, keys in sorted(self.groups.items()):
            lines.append(f"  [{prefix}] {len(keys)} key(s)")
        if self.ungrouped:
            lines.append(f"  [ungrouped] {len(self.ungrouped)} key(s)")
        return "\n".join(lines)


def group_env(
    env: Dict[str, str],
    separator: str = _DEFAULT_SEPARATOR,
    min_prefix_length: int = 2,
) -> GroupResult:
    """Group environment keys by their prefix (part before the first separator)."""
    groups: Dict[str, List[str]] = {}
    ungrouped: List[str] = []

    for key in env:
        if separator in key:
            prefix = key.split(separator, 1)[0]
            if len(prefix) >= min_prefix_length:
                groups.setdefault(prefix, []).append(key)
                continue
        ungrouped.append(key)

    return GroupResult(groups=groups, ungrouped=ungrouped)


def top_prefixes(result: GroupResult, n: int = 5) -> List[str]:
    """Return the top-n prefixes by key count."""
    sorted_groups = sorted(result.groups.items(), key=lambda x: len(x[1]), reverse=True)
    return [prefix for prefix, _ in sorted_groups[:n]]
