"""Tests for envdiff.splitter."""
from __future__ import annotations

import pytest

from envdiff.splitter import SplitResult, render_split, split_env


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET_KEY": "secret",
        "APP_NAME": "envdiff",
        "APP_ENV": "production",
        "STANDALONE": "solo",
    }


def test_split_returns_split_result(sample_env):
    result = split_env(sample_env)
    assert isinstance(result, SplitResult)


def test_split_auto_detects_db_prefix(sample_env):
    result = split_env(sample_env)
    assert "DB" in result.groups


def test_split_auto_detects_aws_prefix(sample_env):
    result = split_env(sample_env)
    assert "AWS" in result.groups


def test_split_auto_detects_app_prefix(sample_env):
    result = split_env(sample_env)
    assert "APP" in result.groups


def test_split_ungrouped_contains_standalone(sample_env):
    result = split_env(sample_env)
    assert "STANDALONE" in result.ungrouped


def test_split_group_count(sample_env):
    result = split_env(sample_env)
    assert result.group_count == 3


def test_split_total_keys(sample_env):
    result = split_env(sample_env)
    assert result.total_keys == len(sample_env)


def test_split_explicit_prefix(sample_env):
    result = split_env(sample_env, prefixes=["DB"])
    assert "DB" in result.groups
    assert "AWS" not in result.groups


def test_split_strip_prefix_removes_leading_prefix(sample_env):
    result = split_env(sample_env, prefixes=["DB"], strip_prefix=True)
    assert "HOST" in result.groups["DB"]
    assert "DB_HOST" not in result.groups["DB"]


def test_split_without_strip_prefix_keeps_full_key(sample_env):
    result = split_env(sample_env, prefixes=["DB"], strip_prefix=False)
    assert "DB_HOST" in result.groups["DB"]


def test_split_was_split_true(sample_env):
    result = split_env(sample_env)
    assert result.was_split is True


def test_split_was_split_false_on_empty():
    result = split_env({})
    assert result.was_split is False


def test_split_summary_contains_group_count(sample_env):
    result = split_env(sample_env)
    assert "3 group(s)" in result.summary()


def test_render_split_produces_key_value_lines(sample_env):
    result = split_env(sample_env, prefixes=["DB"])
    text = render_split(result, "DB")
    assert "DB_HOST=localhost" in text
    assert "DB_PORT=5432" in text


def test_render_split_unknown_group_returns_empty(sample_env):
    result = split_env(sample_env)
    text = render_split(result, "NONEXISTENT")
    assert text == ""


def test_split_custom_separator():
    env = {"APP.NAME": "foo", "APP.ENV": "bar", "OTHER": "x"}
    result = split_env(env, separator=".")
    assert "APP" in result.groups
    assert "OTHER" in result.ungrouped
