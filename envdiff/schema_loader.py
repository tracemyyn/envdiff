"""Load a validation schema from a YAML or JSON file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from envdiff.validator import KeySchema


class SchemaLoadError(Exception):
    """Raised when a schema file cannot be loaded or parsed."""


def _parse_schema_dict(raw: dict) -> Dict[str, KeySchema]:
    schema: Dict[str, KeySchema] = {}
    for key, cfg in raw.items():
        if not isinstance(cfg, dict):
            raise SchemaLoadError(f"Schema entry for {key!r} must be a mapping, got {type(cfg).__name__}")
        schema[key] = KeySchema(
            required=bool(cfg.get("required", False)),
            pattern=cfg.get("pattern"),
            allowed_values=cfg.get("allowed_values"),
            description=cfg.get("description", ""),
        )
    return schema


def load_schema(path: str | Path) -> Dict[str, KeySchema]:
    """Load a schema from a JSON or YAML file."""
    p = Path(path)
    if not p.exists():
        raise SchemaLoadError(f"Schema file not found: {p}")

    suffix = p.suffix.lower()
    text = p.read_text(encoding="utf-8")

    if suffix == ".json":
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SchemaLoadError(f"Invalid JSON in schema file: {exc}") from exc
    elif suffix in (".yaml", ".yml"):
        try:
            import yaml  # optional dependency
            raw = yaml.safe_load(text)
        except Exception as exc:
            raise SchemaLoadError(f"Invalid YAML in schema file: {exc}") from exc
    else:
        raise SchemaLoadError(f"Unsupported schema file format: {suffix!r}")

    if not isinstance(raw, dict):
        raise SchemaLoadError("Schema root must be a mapping of key names to rules")

    return _parse_schema_dict(raw)
