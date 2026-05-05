"""Tests for envdiff.comparator, including key-filter integration."""

import pytest

from envdiff.comparator import EnvDiffResult, compare_envs
from envdiff.filter import build_filter


BASE = {"APP_NAME": "myapp", "DEBUG": "true", "DB_HOST": "localhost", "DB_PORT": "5432"}
TARGET = {"APP_NAME": "myapp", "DEBUG": "false", "DB_HOST": "localhost", "EXTRA": "1"}


def test_compare_identical_envs():
    result = compare_envs({"A": "1"}, {"A": "1"})
    assert not result.has_differences()


def test_compare_detects_missing_in_target():
    result = compare_envs(BASE, TARGET)
    assert "DB_PORT" in result.missing_in_target


def test_compare_detects_missing_in_base():
    result = compare_envs(BASE, TARGET)
    assert "EXTRA" in result.missing_in_base


def test_compare_detects_value_mismatches():
    result = compare_envs(BASE, TARGET)
    assert "DEBUG" in result.value_mismatches
    assert result.value_mismatches["DEBUG"] == ("true", "false")


def test_compare_ignore_values_skips_mismatches():
    result = compare_envs(BASE, TARGET, ignore_values=True)
    assert result.value_mismatches == {}


def test_summary_no_differences():
    result = compare_envs({"X": "1"}, {"X": "1"})
    assert result.summary() == "No differences found."


def test_summary_contains_counts():
    result = compare_envs(BASE, TARGET)
    s = result.summary()
    assert "missing" in s or "mismatch" in s


def test_custom_names_appear_in_summary():
    result = compare_envs(
        {"A": "1"},
        {},
        base_name="prod",
        target_name="staging",
    )
    assert "staging" in result.summary()


# ---------------------------------------------------------------------------
# key_filter integration
# ---------------------------------------------------------------------------

def test_compare_with_include_filter_limits_scope():
    kf = build_filter(include=["DB_*"])
    result = compare_envs(BASE, TARGET, key_filter=kf)
    # DB_PORT missing in target
    assert "DB_PORT" in result.missing_in_target
    # DEBUG mismatch should be invisible because it's filtered out
    assert "DEBUG" not in result.value_mismatches
    # EXTRA is not a DB_ key, so it should be invisible too
    assert "EXTRA" not in result.missing_in_base


def test_compare_with_exclude_filter_hides_keys():
    kf = build_filter(exclude=["DEBUG", "EXTRA"])
    result = compare_envs(BASE, TARGET, key_filter=kf)
    assert "DEBUG" not in result.value_mismatches
    assert "EXTRA" not in result.missing_in_base
    assert "DB_PORT" in result.missing_in_target


def test_compare_filter_all_keys_out_yields_no_diff():
    kf = build_filter(include=["NONEXISTENT_*"])
    result = compare_envs(BASE, TARGET, key_filter=kf)
    assert not result.has_differences()


def test_compare_filter_none_behaves_as_no_filter():
    result_no_filter = compare_envs(BASE, TARGET, key_filter=None)
    result_none = compare_envs(BASE, TARGET)
    assert result_no_filter.missing_in_target == result_none.missing_in_target
    assert result_no_filter.missing_in_base == result_none.missing_in_base
    assert result_no_filter.value_mismatches == result_none.value_mismatches
