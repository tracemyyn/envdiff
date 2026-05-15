"""Tests for envdiff.scoper."""
from __future__ import annotations

import pytest

from envdiff.scoper import ScopeResult, scope_env


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_PASSWORD": "secret",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET": "abc",
        "APP_NAME": "envdiff",
        "DEBUG": "true",
    }


def test_scope_returns_scope_result(sample_env):
    result = scope_env(sample_env, "DB")
    assert isinstance(result, ScopeResult)


def test_scope_matches_db_prefix(sample_env):
    result = scope_env(sample_env, "DB")
    assert set(result.matched.keys()) == {"DB_HOST", "DB_PORT", "DB_PASSWORD"}


def test_scope_excludes_non_matching_keys(sample_env):
    result = scope_env(sample_env, "DB")
    assert "AWS_ACCESS_KEY" in result.excluded
    assert "APP_NAME" in result.excluded
    assert "DEBUG" in result.excluded


def test_scope_match_count(sample_env):
    result = scope_env(sample_env, "AWS")
    assert result.match_count == 2


def test_scope_excluded_count(sample_env):
    result = scope_env(sample_env, "AWS")
    assert result.excluded_count == len(sample_env) - 2


def test_scope_was_filtered_true_when_keys_excluded(sample_env):
    result = scope_env(sample_env, "DB")
    assert result.was_filtered is True


def test_scope_was_filtered_false_when_all_match():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = scope_env(env, "DB")
    assert result.was_filtered is False


def test_scope_strip_prefix_removes_leading_scope(sample_env):
    result = scope_env(sample_env, "DB", strip_prefix=True)
    assert "HOST" in result.matched
    assert "PORT" in result.matched
    assert "PASSWORD" in result.matched
    assert "DB_HOST" not in result.matched


def test_scope_strip_prefix_false_keeps_full_key(sample_env):
    result = scope_env(sample_env, "DB", strip_prefix=False)
    assert "DB_HOST" in result.matched


def test_scope_is_case_insensitive_for_scope_arg(sample_env):
    result_lower = scope_env(sample_env, "db")
    result_upper = scope_env(sample_env, "DB")
    assert result_lower.match_count == result_upper.match_count


def test_scope_empty_env_returns_empty_result():
    result = scope_env({}, "DB")
    assert result.match_count == 0
    assert result.excluded_count == 0
    assert result.was_filtered is False


def test_scope_no_matches_returns_all_excluded(sample_env):
    result = scope_env(sample_env, "NONEXISTENT")
    assert result.match_count == 0
    assert result.excluded_count == len(sample_env)


def test_scope_summary_contains_scope_name(sample_env):
    result = scope_env(sample_env, "DB")
    assert "DB" in result.summary()


def test_scope_summary_mentions_stripped_when_strip_prefix(sample_env):
    result = scope_env(sample_env, "DB", strip_prefix=True)
    assert "stripped" in result.summary()


def test_scope_custom_separator():
    env = {"DB.HOST": "localhost", "DB.PORT": "5432", "APP_NAME": "x"}
    result = scope_env(env, "DB", separator=".")
    assert result.match_count == 2
    assert "APP_NAME" in result.excluded
