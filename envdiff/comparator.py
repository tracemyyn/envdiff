"""Compares parsed .env dictionaries and reports differences."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class EnvDiffResult:
    """Holds the result of comparing two .env files."""

    base_name: str
    target_name: str
    missing_in_target: List[str] = field(default_factory=list)
    missing_in_base: List[str] = field(default_factory=list)
    mismatched_keys: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(
            self.missing_in_target or self.missing_in_base or self.mismatched_keys
        )

    def summary(self) -> str:
        lines = [f"Comparing '{self.base_name}' vs '{self.target_name}':"]
        if not self.has_differences:
            lines.append("  No differences found.")
            return "\n".join(lines)

        if self.missing_in_target:
            lines.append(f"  Missing in '{self.target_name}':")
            for key in sorted(self.missing_in_target):
                lines.append(f"    - {key}")

        if self.missing_in_base:
            lines.append(f"  Missing in '{self.base_name}':")
            for key in sorted(self.missing_in_base):
                lines.append(f"    - {key}")

        if self.mismatched_keys:
            lines.append("  Value mismatches:")
            for key in sorted(self.mismatched_keys):
                base_val = self.mismatched_keys[key]["base"]
                target_val = self.mismatched_keys[key]["target"]
                lines.append(f"    ~ {key}: '{base_val}' != '{target_val}'")

        return "\n".join(lines)


def compare_envs(
    base: Dict[str, Optional[str]],
    target: Dict[str, Optional[str]],
    base_name: str = "base",
    target_name: str = "target",
    ignore_values: bool = False,
) -> EnvDiffResult:
    """Compare two parsed env dicts and return an EnvDiffResult.

    Args:
        base: The reference environment mapping.
        target: The environment mapping to compare against base.
        base_name: Label for the base environment.
        target_name: Label for the target environment.
        ignore_values: If True, only check for missing keys, not value differences.

    Returns:
        An EnvDiffResult describing all differences.
    """
    base_keys: Set[str] = set(base.keys())
    target_keys: Set[str] = set(target.keys())

    result = EnvDiffResult(base_name=base_name, target_name=target_name)
    result.missing_in_target = list(base_keys - target_keys)
    result.missing_in_base = list(target_keys - base_keys)

    if not ignore_values:
        common_keys = base_keys & target_keys
        for key in common_keys:
            if base[key] != target[key]:
                result.mismatched_keys[key] = {
                    "base": base[key],
                    "target": target[key],
                }

    return result
