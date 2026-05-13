"""Sort .env file keys alphabetically or by custom order."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortResult:
    original: Dict[str, str]
    sorted_env: Dict[str, str]
    original_order: List[str]
    sorted_order: List[str]

    @property
    def change_count(self) -> int:
        """Number of keys whose position changed."""
        return sum(
            1
            for i, (a, b) in enumerate(zip(self.original_order, self.sorted_order))
            if a != b
        )

    @property
    def was_reordered(self) -> bool:
        return self.original_order != self.sorted_order

    def summary(self) -> str:
        if not self.was_reordered:
            return "Already sorted — no changes needed."
        return (
            f"{self.change_count} key(s) moved out of "
            f"{len(self.original_order)} total."
        )

    def render(self) -> str:
        """Render sorted env as .env file content."""
        lines = []
        for key in self.sorted_order:
            value = self.sorted_env[key]
            if " " in value or "#" in value or value == "":
                lines.append(f'{key}="{value}"')
            else:
                lines.append(f"{key}={value}")
        return "\n".join(lines) + ("\n" if lines else "")


def sort_env(
    env: Dict[str, str],
    reverse: bool = False,
    key_order: Optional[List[str]] = None,
) -> SortResult:
    """Sort env dict keys.

    Args:
        env: Parsed environment dictionary.
        reverse: If True, sort in descending order.
        key_order: Optional explicit ordering; unspecified keys follow alphabetically.

    Returns:
        SortResult with original and sorted state.
    """
    original_order = list(env.keys())

    if key_order is not None:
        pinned = [k for k in key_order if k in env]
        rest = sorted(
            [k for k in env if k not in key_order], reverse=reverse
        )
        new_order = pinned + rest
    else:
        new_order = sorted(original_order, reverse=reverse)

    sorted_env = {k: env[k] for k in new_order}

    return SortResult(
        original=dict(env),
        sorted_env=sorted_env,
        original_order=original_order,
        sorted_order=new_order,
    )
