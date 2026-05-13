"""Tests for envdiff.grouper."""
from __future__ import annotations
import pytest
from envdiff.grouper import GroupResult, group_env, top_prefixes


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET_KEY": "secret",
        "APP_DEBUG": "true",
        "APP_ENV": "production",
        "APP_VERSION": "1.0.0",
        "PORT": "8080",
        "DEBUG": "false",
    }


def test_group_returns_group_result(sample_env):
    result = group_env(sample_env)
    assert isinstance(result, GroupResult)


def test_group_detects_db_prefix(sample_env):
    result = group_env(sample_env)
    assert "DB" in result.groups
    assert len(result.groups["DB"]) == 3


def test_group_detects_aws_prefix(sample_env):
    result = group_env(sample_env)
    assert "AWS" in result.groups
    assert len(result.groups["AWS"]) == 2


def test_group_detects_app_prefix(sample_env):
    result = group_env(sample_env)
    assert "APP" in result.groups
    assert len(result.groups["APP"]) == 3


def test_ungrouped_keys_have_no_separator(sample_env):
    result = group_env(sample_env)
    assert "PORT" in result.ungrouped
    assert "DEBUG" in result.ungrouped


def test_total_keys_matches_input(sample_env):
    result = group_env(sample_env)
    assert result.total_keys == len(sample_env)


def test_group_count(sample_env):
    result = group_env(sample_env)
    assert result.group_count == 3


def test_summary_contains_prefix_names(sample_env):
    result = group_env(sample_env)
    summary = result.summary()
    assert "DB" in summary
    assert "AWS" in summary
    assert "APP" in summary


def test_summary_mentions_ungrouped(sample_env):
    result = group_env(sample_env)
    summary = result.summary()
    assert "ungrouped" in summary


def test_empty_env_returns_empty_result():
    result = group_env({})
    assert result.group_count == 0
    assert result.total_keys == 0
    assert result.ungrouped == []


def test_min_prefix_length_filters_short_prefixes():
    env = {"A_KEY": "val", "DB_HOST": "localhost"}
    result = group_env(env, min_prefix_length=2)
    assert "A" not in result.groups
    assert "A_KEY" in result.ungrouped
    assert "DB" in result.groups


def test_top_prefixes_returns_sorted_by_count(sample_env):
    result = group_env(sample_env)
    tops = top_prefixes(result, n=2)
    assert len(tops) == 2
    # APP and DB both have 3; AWS has 2 — top 2 should not include AWS
    assert "AWS" not in tops


def test_top_prefixes_respects_n(sample_env):
    result = group_env(sample_env)
    tops = top_prefixes(result, n=1)
    assert len(tops) == 1


def test_custom_separator():
    env = {"APP.DEBUG": "true", "APP.HOST": "localhost", "PLAIN": "value"}
    result = group_env(env, separator=".")
    assert "APP" in result.groups
    assert len(result.groups["APP"]) == 2
    assert "PLAIN" in result.ungrouped
