"""Tests for envdiff.schema_loader."""

import json
import pytest
from pathlib import Path

from envdiff.schema_loader import SchemaLoadError, load_schema
from envdiff.validator import KeySchema


@pytest.fixture()
def tmp_dir(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_load_json_schema(tmp_dir):
    schema_file = tmp_dir / "schema.json"
    data = {
        "API_KEY": {"required": True, "description": "API key"},
        "LOG_LEVEL": {"allowed_values": ["DEBUG", "INFO"]},
    }
    _write(schema_file, json.dumps(data))
    schema = load_schema(schema_file)
    assert "API_KEY" in schema
    assert schema["API_KEY"].required is True
    assert schema["LOG_LEVEL"].allowed_values == ["DEBUG", "INFO"]


def test_load_schema_missing_file(tmp_dir):
    with pytest.raises(SchemaLoadError, match="not found"):
        load_schema(tmp_dir / "nonexistent.json")


def test_load_schema_invalid_json(tmp_dir):
    bad = tmp_dir / "bad.json"
    _write(bad, "{not valid json")
    with pytest.raises(SchemaLoadError, match="Invalid JSON"):
        load_schema(bad)


def test_load_schema_unsupported_format(tmp_dir):
    f = tmp_dir / "schema.toml"
    _write(f, "[section]\nkey = 'value'")
    with pytest.raises(SchemaLoadError, match="Unsupported"):
        load_schema(f)


def test_load_schema_non_mapping_root(tmp_dir):
    f = tmp_dir / "schema.json"
    _write(f, json.dumps(["list", "not", "mapping"]))
    with pytest.raises(SchemaLoadError, match="mapping"):
        load_schema(f)


def test_load_schema_invalid_entry_type(tmp_dir):
    f = tmp_dir / "schema.json"
    _write(f, json.dumps({"KEY": "should_be_dict"}))
    with pytest.raises(SchemaLoadError, match="mapping"):
        load_schema(f)


def test_load_schema_pattern_field(tmp_dir):
    f = tmp_dir / "schema.json"
    data = {"PORT": {"required": True, "pattern": r"\d+"}}
    _write(f, json.dumps(data))
    schema = load_schema(f)
    assert schema["PORT"].pattern == r"\d+"
