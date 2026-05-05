"""Utilities for formatting EnvDiffResult as structured data (JSON/YAML)."""

from __future__ import annotations

import json
from typing import Any, Dict

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

from envdiff.comparator import EnvDiffResult


def _diff_to_dict(result: EnvDiffResult, base_name: str = "base", target_name: str = "target") -> Dict[str, Any]:
    """Convert an EnvDiffResult into a plain dictionary."""
    return {
        "summary": {
            "has_differences": result.has_differences,
            "missing_in_target_count": len(result.missing_in_target),
            "missing_in_base_count": len(result.missing_in_base),
            "mismatched_values_count": len(result.mismatched_values),
        },
        "missing_in_target": sorted(result.missing_in_target),
        "missing_in_base": sorted(result.missing_in_base),
        "mismatched_values": {
            key: {
                base_name: base_val,
                target_name: target_val,
            }
            for key, (base_val, target_val) in sorted(result.mismatched_values.items())
        },
    }


def format_json(
    result: EnvDiffResult,
    base_name: str = "base",
    target_name: str = "target",
    indent: int = 2,
) -> str:
    """Serialize an EnvDiffResult to a JSON string."""
    data = _diff_to_dict(result, base_name=base_name, target_name=target_name)
    return json.dumps(data, indent=indent)


def format_yaml(
    result: EnvDiffResult,
    base_name: str = "base",
    target_name: str = "target",
) -> str:
    """Serialize an EnvDiffResult to a YAML string.

    Raises ImportError if PyYAML is not installed.
    """
    if not _YAML_AVAILABLE:
        raise ImportError(
            "PyYAML is required for YAML output. Install it with: pip install pyyaml"
        )
    data = _diff_to_dict(result, base_name=base_name, target_name=target_name)
    return yaml.dump(data, default_flow_style=False, sort_keys=True)
