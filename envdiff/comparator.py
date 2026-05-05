"""Compare two parsed .env dicts and report differences."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from envdiff.filter import KeyFilter, build_filter


@dataclass
class EnvDiffResult:
    """Holds the diff between a *base* and *target* environment."""

    missing_in_target: list[str] = field(default_factory=list)
    missing_in_base: list[str] = field(default_factory=list)
    value_mismatches: dict[str, tuple[str, str]] = field(default_factory=dict)
    base_name: str = "base"
    target_name: str = "target"

    def has_differences(self) -> bool:
        """Return True when any difference exists."""
        return bool(
            self.missing_in_target or self.missing_in_base or self.value_mismatches
        )

    def summary(self) -> str:
        """Return a one-line human-readable summary."""
        parts = []
        if self.missing_in_target:
            parts.append(
                f"{len(self.missing_in_target)} key(s) missing in {self.target_name}"
            )
        if self.missing_in_base:
            parts.append(
                f"{len(self.missing_in_base)} key(s) missing in {self.base_name}"
            )
        if self.value_mismatches:
            parts.append(f"{len(self.value_mismatches)} value mismatch(es)")
        return ", ".join(parts) if parts else "No differences found."


def compare_envs(
    base: dict[str, str],
    target: dict[str, str],
    base_name: str = "base",
    target_name: str = "target",
    ignore_values: bool = False,
    key_filter: Optional[KeyFilter] = None,
) -> EnvDiffResult:
    """Compare *base* and *target* env dicts and return an :class:`EnvDiffResult`.

    Parameters
    ----------
    base:
        The reference environment (e.g. ``.env.example``).
    target:
        The environment being validated (e.g. ``.env``).
    base_name:
        Human-readable label for *base* used in reports.
    target_name:
        Human-readable label for *target* used in reports.
    ignore_values:
        When *True*, only check for key presence; skip value comparison.
    key_filter:
        Optional :class:`~envdiff.filter.KeyFilter` to restrict which keys are
        considered.  Pass ``None`` to include all keys.
    """
    if key_filter is not None:
        base = key_filter.filter_env(base)
        target = key_filter.filter_env(target)

    base_keys = set(base)
    target_keys = set(target)

    missing_in_target = sorted(base_keys - target_keys)
    missing_in_base = sorted(target_keys - base_keys)

    value_mismatches: dict[str, tuple[str, str]] = {}
    if not ignore_values:
        for key in sorted(base_keys & target_keys):
            if base[key] != target[key]:
                value_mismatches[key] = (base[key], target[key])

    return EnvDiffResult(
        missing_in_target=missing_in_target,
        missing_in_base=missing_in_base,
        value_mismatches=value_mismatches,
        base_name=base_name,
        target_name=target_name,
    )
