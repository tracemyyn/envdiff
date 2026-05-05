"""Tests for envdiff.comparator module."""

import pytest

from envdiff.comparator import EnvDiffResult, compare_envs


BASE_ENV = {
    "APP_NAME": "myapp",
    "DEBUG": "true",
    "DATABASE_URL": "postgres://localhost/dev",
    "SECRET_KEY": "dev-secret",
}

TARGET_ENV = {
    "APP_NAME": "myapp",
    "DEBUG": "false",
    "DATABASE_URL": "postgres://prod-host/prod",
    "SECRET_KEY": "prod-secret",
    "NEW_FEATURE_FLAG": "enabled",
}


def test_compare_identical_envs():
    result = compare_envs(BASE_ENV, BASE_ENV)
    assert not result.has_differences
    assert result.missing_in_target == []
    assert result.missing_in_base == []
    assert result.mismatched_keys == {}


def test_compare_detects_missing_in_target():
    target = {k: v for k, v in BASE_ENV.items() if k != "SECRET_KEY"}
    result = compare_envs(BASE_ENV, target)
    assert "SECRET_KEY" in result.missing_in_target
    assert result.has_differences


def test_compare_detects_missing_in_base():
    result = compare_envs(BASE_ENV, TARGET_ENV)
    assert "NEW_FEATURE_FLAG" in result.missing_in_base


def test_compare_detects_value_mismatches():
    result = compare_envs(BASE_ENV, TARGET_ENV)
    assert "DEBUG" in result.mismatched_keys
    assert result.mismatched_keys["DEBUG"]["base"] == "true"
    assert result.mismatched_keys["DEBUG"]["target"] == "false"


def test_compare_ignore_values_skips_mismatches():
    result = compare_envs(BASE_ENV, TARGET_ENV, ignore_values=True)
    assert result.mismatched_keys == {}
    assert "NEW_FEATURE_FLAG" in result.missing_in_base


def test_compare_custom_names():
    result = compare_envs(BASE_ENV, TARGET_ENV, base_name="dev", target_name="prod")
    assert result.base_name == "dev"
    assert result.target_name == "prod"


def test_summary_no_differences():
    result = compare_envs(BASE_ENV, BASE_ENV, base_name="a", target_name="b")
    summary = result.summary()
    assert "No differences found" in summary


def test_summary_with_differences():
    result = compare_envs(BASE_ENV, TARGET_ENV, base_name="dev", target_name="prod")
    summary = result.summary()
    assert "Missing in 'prod'" not in summary or "NEW_FEATURE_FLAG" in summary
    assert "Missing in 'dev'" in summary or "NEW_FEATURE_FLAG" in summary
    assert "DEBUG" in summary


def test_compare_empty_envs():
    result = compare_envs({}, {})
    assert not result.has_differences


def test_compare_one_empty_base():
    result = compare_envs({}, {"KEY": "value"})
    assert "KEY" in result.missing_in_base
    assert not result.missing_in_target


def test_compare_none_values():
    base = {"KEY": None}
    target = {"KEY": ""}
    result = compare_envs(base, target)
    assert "KEY" in result.mismatched_keys
