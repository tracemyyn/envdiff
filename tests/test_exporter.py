"""Tests for envdiff.exporter."""

import csv
import io
import json

import pytest

from envdiff.comparator import compare_envs
from envdiff.exporter import export, export_csv, export_json, export_yaml


@pytest.fixture()
def diff_result():
    base = {"HOST": "localhost", "PORT": "5432", "SECRET": "abc"}
    target = {"HOST": "prod.example.com", "PORT": "5432", "DB": "mydb"}
    return compare_envs(base, target)


@pytest.fixture()
def empty_result():
    env = {"A": "1", "B": "2"}
    return compare_envs(env, env)


# --- JSON ---

def test_export_json_is_valid_json(diff_result):
    out = export_json(diff_result)
    data = json.loads(out)  # must not raise
    assert isinstance(data, dict)


def test_export_json_contains_expected_keys(diff_result):
    data = json.loads(export_json(diff_result))
    assert "missing_in_target" in data
    assert "missing_in_base" in data
    assert "mismatched" in data


def test_export_json_custom_names(diff_result):
    data = json.loads(export_json(diff_result, base_name="dev", target_name="prod"))
    assert data["base_name"] == "dev"
    assert data["target_name"] == "prod"


def test_export_json_empty_result(empty_result):
    data = json.loads(export_json(empty_result))
    assert data["missing_in_target"] == []
    assert data["missing_in_base"] == []
    assert data["mismatched"] == []


# --- YAML ---

def test_export_yaml_is_string(diff_result):
    out = export_yaml(diff_result)
    assert isinstance(out, str)
    assert len(out) > 0


def test_export_yaml_contains_section_headers(diff_result):
    out = export_yaml(diff_result)
    assert "missing_in_target" in out or "missing" in out


# --- CSV ---

def test_export_csv_has_header_row(diff_result):
    out = export_csv(diff_result)
    reader = csv.reader(io.StringIO(out))
    header = next(reader)
    assert header[0] == "key"
    assert header[1] == "status"


def test_export_csv_missing_in_target_row(diff_result):
    out = export_csv(diff_result)
    rows = list(csv.reader(io.StringIO(out)))
    statuses = {row[1] for row in rows[1:]}
    assert "missing_in_target" in statuses


def test_export_csv_mismatch_row(diff_result):
    out = export_csv(diff_result)
    rows = list(csv.reader(io.StringIO(out)))
    statuses = {row[1] for row in rows[1:]}
    assert "mismatch" in statuses


def test_export_csv_custom_column_names(diff_result):
    out = export_csv(diff_result, base_name="dev", target_name="prod")
    header = next(csv.reader(io.StringIO(out)))
    assert "dev_value" in header
    assert "prod_value" in header


# --- dispatch ---

def test_export_dispatch_json(diff_result):
    out = export(diff_result, "json")
    json.loads(out)  # valid JSON


def test_export_dispatch_csv(diff_result):
    out = export(diff_result, "csv")
    assert "key" in out


def test_export_dispatch_unknown_raises(diff_result):
    with pytest.raises(ValueError, match="Unknown export format"):
        export(diff_result, "xml")
