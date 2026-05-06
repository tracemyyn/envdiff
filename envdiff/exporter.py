"""Export env diff results to various file formats (JSON, YAML, CSV)."""

from __future__ import annotations

import csv
import io
import json
from typing import Optional

from envdiff.comparator import EnvDiffResult
from envdiff.formatter import _diff_to_dict


EXPORT_FORMATS = ("json", "yaml", "csv")


def export_json(
    result: EnvDiffResult,
    base_name: str = "base",
    target_name: str = "target",
    indent: int = 2,
) -> str:
    """Serialize *result* to a JSON string."""
    data = _diff_to_dict(result, base_name=base_name, target_name=target_name)
    return json.dumps(data, indent=indent)


def export_yaml(
    result: EnvDiffResult,
    base_name: str = "base",
    target_name: str = "target",
) -> str:
    """Serialize *result* to a YAML string.

    Falls back to a simple hand-rolled YAML if PyYAML is not installed.
    """
    from envdiff.formatter import format_yaml

    return format_yaml(result, base_name=base_name, target_name=target_name)


def export_csv(
    result: EnvDiffResult,
    base_name: str = "base",
    target_name: str = "target",
) -> str:
    """Serialize *result* to CSV with columns: key, status, base_value, target_value."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "status", base_name + "_value", target_name + "_value"])

    for key in sorted(result.missing_in_target):
        writer.writerow([key, "missing_in_target", result.base.get(key, ""), ""])

    for key in sorted(result.missing_in_base):
        writer.writerow([key, "missing_in_base", "", result.target.get(key, "")])

    for key in sorted(result.mismatched):
        writer.writerow(
            [
                key,
                "mismatch",
                result.base.get(key, ""),
                result.target.get(key, ""),
            ]
        )

    return buf.getvalue()


def export(
    result: EnvDiffResult,
    fmt: str,
    base_name: str = "base",
    target_name: str = "target",
) -> str:
    """Dispatch to the correct exporter for *fmt*.

    Raises ValueError for unknown formats.
    """
    fmt = fmt.lower()
    if fmt == "json":
        return export_json(result, base_name=base_name, target_name=target_name)
    if fmt == "yaml":
        return export_yaml(result, base_name=base_name, target_name=target_name)
    if fmt == "csv":
        return export_csv(result, base_name=base_name, target_name=target_name)
    raise ValueError(f"Unknown export format {fmt!r}. Choose from: {EXPORT_FORMATS}")
