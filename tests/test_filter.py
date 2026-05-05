"""Tests for envdiff.filter."""

import pytest

from envdiff.filter import KeyFilter, build_filter


# ---------------------------------------------------------------------------
# KeyFilter.matches
# ---------------------------------------------------------------------------

def test_matches_no_patterns_accepts_everything():
    kf = KeyFilter()
    assert kf.matches("APP_SECRET") is True
    assert kf.matches("DEBUG") is True


def test_matches_include_pattern():
    kf = KeyFilter(include=["AWS_*"])
    assert kf.matches("AWS_ACCESS_KEY") is True
    assert kf.matches("AWS_SECRET") is True
    assert kf.matches("DATABASE_URL") is False


def test_matches_exclude_pattern():
    kf = KeyFilter(exclude=["*_SECRET", "*_PASSWORD"])
    assert kf.matches("DB_PASSWORD") is False
    assert kf.matches("APP_SECRET") is False
    assert kf.matches("DEBUG") is True


def test_matches_include_and_exclude_combined():
    kf = KeyFilter(include=["AWS_*"], exclude=["AWS_SECRET"])
    assert kf.matches("AWS_ACCESS_KEY") is True
    assert kf.matches("AWS_SECRET") is False
    assert kf.matches("DATABASE_URL") is False


def test_matches_glob_wildcard_question_mark():
    kf = KeyFilter(include=["DB_HOS?"])
    assert kf.matches("DB_HOST") is True
    assert kf.matches("DB_HOSTNAME") is False


# ---------------------------------------------------------------------------
# KeyFilter.apply
# ---------------------------------------------------------------------------

def test_apply_returns_filtered_list():
    kf = KeyFilter(include=["APP_*"])
    result = kf.apply(["APP_NAME", "APP_ENV", "DATABASE_URL", "DEBUG"])
    assert result == ["APP_NAME", "APP_ENV"]


def test_apply_preserves_order():
    kf = KeyFilter(exclude=["SECRET"])
    keys = ["ALPHA", "SECRET", "BETA", "GAMMA"]
    assert kf.apply(keys) == ["ALPHA", "BETA", "GAMMA"]


# ---------------------------------------------------------------------------
# KeyFilter.filter_env
# ---------------------------------------------------------------------------

def test_filter_env_returns_subset_dict():
    kf = KeyFilter(include=["DB_*"])
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp"}
    assert kf.filter_env(env) == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_filter_env_empty_result():
    kf = KeyFilter(include=["AWS_*"])
    env = {"DATABASE_URL": "postgres://", "DEBUG": "true"}
    assert kf.filter_env(env) == {}


# ---------------------------------------------------------------------------
# build_filter
# ---------------------------------------------------------------------------

def test_build_filter_none_args():
    kf = build_filter()
    assert kf.include == []
    assert kf.exclude == []


def test_build_filter_with_patterns():
    kf = build_filter(include=["APP_*"], exclude=["APP_SECRET"])
    assert kf.include == ["APP_*"]
    assert kf.exclude == ["APP_SECRET"]
    assert kf.matches("APP_NAME") is True
    assert kf.matches("APP_SECRET") is False
