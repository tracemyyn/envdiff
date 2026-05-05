"""Tests for envdiff.formatter (JSON / YAML structured output)."""

from __future__ import annotations

import json
import pytest

from envdiff.comparator import EnvDiffResult
from envdiff.formatter import _diff_to_dict, format_json, format_yaml


@pytest.fixture()
def empty_result() -> EnvDiffResult:
    return EnvDiffResult(
        missing_in_target=set(),
        missing_in_base=set(),
        mismatched_values={},
    )


@pytest.fixture()
def rich_result() -> EnvDiffResult:
    return EnvDiffResult(
        missing_in_target={"SECRET_KEY"},
        missing_in_base={"NEW_FLAG"},
        mismatched_values={"DB_URL": ("postgres://old", "postgres://new")},
    )


# --- _diff_to_dict -----------------------------------------------------------

def test_diff_to_dict_empty(empty_result):
    data = _diff_to_dict(empty_result)
    assert data["summary"]["has_differences"] is False
    assert data["missing_in_target"] == []
    assert data["missing_in_base"] == []
    assert data["mismatched_values"] == {}


def test_diff_to_dict_counts(rich_result):
    data = _diff_to_dict(rich_result)
    assert data["summary"]["missing_in_target_count"] == 1
    assert data["summary"]["missing_in_base_count"] == 1
    assert data["summary"]["mismatched_values_count"] == 1
    assert data["summary"]["has_differences"] is True


def test_diff_to_dict_custom_names(rich_result):
    data = _diff_to_dict(rich_result, base_name="prod", target_name="staging")
    mismatch = data["mismatched_values"]["DB_URL"]
    assert "prod" in mismatch
    assert "staging" in mismatch
    assert mismatch["prod"] == "postgres://old"
    assert mismatch["staging"] == "postgres://new"


# --- format_json -------------------------------------------------------------

def test_format_json_is_valid_json(rich_result):
    output = format_json(rich_result)
    parsed = json.loads(output)  # must not raise
    assert isinstance(parsed, dict)


def test_format_json_contains_expected_keys(rich_result):
    parsed = json.loads(format_json(rich_result))
    assert "summary" in parsed
    assert "missing_in_target" in parsed
    assert "missing_in_base" in parsed
    assert "mismatched_values" in parsed


def test_format_json_missing_keys_sorted(rich_result):
    result = EnvDiffResult(
        missing_in_target={"Z_KEY", "A_KEY"},
        missing_in_base=set(),
        mismatched_values={},
    )
    parsed = json.loads(format_json(result))
    assert parsed["missing_in_target"] == ["A_KEY", "Z_KEY"]


# --- format_yaml -------------------------------------------------------------

def test_format_yaml_requires_pyyaml(rich_result, monkeypatch):
    import envdiff.formatter as fmt_module
    monkeypatch.setattr(fmt_module, "_YAML_AVAILABLE", False)
    with pytest.raises(ImportError, match="PyYAML"):
        format_yaml(rich_result)


def test_format_yaml_output(rich_result):
    yaml = pytest.importorskip("yaml")
    output = format_yaml(rich_result)
    parsed = yaml.safe_load(output)
    assert parsed["summary"]["has_differences"] is True
    assert "SECRET_KEY" in parsed["missing_in_target"]
