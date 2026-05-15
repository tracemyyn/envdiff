"""Tests for envdiff.extractor."""
import pytest
from envdiff.extractor import ExtractResult, extract_env


@pytest.fixture()
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_PASSWORD": "secret",
        "AWS_ACCESS_KEY": "AKIA123",
        "AWS_SECRET": "abc",
        "APP_DEBUG": "true",
        "APP_NAME": "envdiff",
    }


def test_extract_returns_extract_result(sample_env):
    result = extract_env(sample_env, prefix="DB_")
    assert isinstance(result, ExtractResult)


def test_extract_by_prefix(sample_env):
    result = extract_env(sample_env, prefix="DB_")
    assert set(result.extracted.keys()) == {"DB_HOST", "DB_PORT", "DB_PASSWORD"}


def test_extract_by_suffix(sample_env):
    result = extract_env(sample_env, suffix="_KEY")
    assert set(result.extracted.keys()) == {"AWS_ACCESS_KEY"}


def test_extract_by_explicit_keys(sample_env):
    result = extract_env(sample_env, keys=["APP_DEBUG", "APP_NAME"])
    assert set(result.extracted.keys()) == {"APP_DEBUG", "APP_NAME"}


def test_extract_by_pattern(sample_env):
    result = extract_env(sample_env, pattern="AWS_*")
    assert set(result.extracted.keys()) == {"AWS_ACCESS_KEY", "AWS_SECRET"}


def test_extract_prefix_and_suffix_combined(sample_env):
    result = extract_env(sample_env, prefix="DB_", suffix="_PASSWORD")
    assert set(result.extracted.keys()) == {"DB_PASSWORD"}


def test_skipped_keys_are_remainder(sample_env):
    result = extract_env(sample_env, prefix="DB_")
    assert set(result.skipped.keys()) == {
        "AWS_ACCESS_KEY", "AWS_SECRET", "APP_DEBUG", "APP_NAME"
    }


def test_extract_count(sample_env):
    result = extract_env(sample_env, prefix="APP_")
    assert result.extract_count == 2


def test_skip_count(sample_env):
    result = extract_env(sample_env, prefix="APP_")
    assert result.skip_count == 5


def test_was_filtered_true_when_keys_skipped(sample_env):
    result = extract_env(sample_env, prefix="DB_")
    assert result.was_filtered is True


def test_was_filtered_false_when_all_match(sample_env):
    all_keys = list(sample_env.keys())
    result = extract_env(sample_env, keys=all_keys)
    assert result.was_filtered is False


def test_matched_keys_populated(sample_env):
    result = extract_env(sample_env, prefix="AWS_")
    assert set(result.matched_keys) == {"AWS_ACCESS_KEY", "AWS_SECRET"}


def test_no_criteria_returns_all(sample_env):
    result = extract_env(sample_env)
    assert result.extracted == sample_env
    assert result.skipped == {}


def test_summary_string(sample_env):
    result = extract_env(sample_env, prefix="DB_")
    s = result.summary()
    assert "3" in s
    assert "4" in s


def test_explicit_keys_beats_prefix(sample_env):
    # keys= overrides prefix= entirely
    result = extract_env(sample_env, keys=["APP_DEBUG"], prefix="DB_")
    assert set(result.extracted.keys()) == {"APP_DEBUG"}
