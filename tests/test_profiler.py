"""Tests for envdiff.profiler."""
import pytest
from envdiff.profiler import profile_env, ProfileResult


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "secret123",
        "API_KEY": "changeme",
        "DEBUG": "",
        "PORT": "8080",
        "HOST": "8080",  # duplicate value with PORT
        "VERY_LONG_KEY_NAME_FOR_TESTING": "short",
        "X": "a" * 120,
    }


def test_profile_total_keys(sample_env):
    result = profile_env(sample_env)
    assert result.total_keys == len(sample_env)


def test_profile_detects_empty_values(sample_env):
    result = profile_env(sample_env)
    assert "DEBUG" in result.empty_values
    assert result.empty_count == 1


def test_profile_detects_placeholder_values(sample_env):
    result = profile_env(sample_env)
    assert "API_KEY" in result.placeholder_values
    assert result.placeholder_count >= 1


def test_profile_detects_sensitive_keys(sample_env):
    result = profile_env(sample_env)
    assert "DB_PASSWORD" in result.sensitive_keys
    assert "API_KEY" in result.sensitive_keys
    assert result.sensitive_count >= 2


def test_profile_detects_duplicate_values(sample_env):
    result = profile_env(sample_env)
    assert "8080" in result.duplicate_values
    dup_keys = result.duplicate_values["8080"]
    assert "PORT" in dup_keys
    assert "HOST" in dup_keys


def test_profile_no_duplicates_when_all_unique():
    env = {"A": "1", "B": "2", "C": "3"}
    result = profile_env(env)
    assert result.duplicate_values == {}


def test_profile_longest_key(sample_env):
    result = profile_env(sample_env)
    assert result.longest_key == "VERY_LONG_KEY_NAME_FOR_TESTING"


def test_profile_longest_value_key(sample_env):
    result = profile_env(sample_env)
    assert result.longest_value_key == "X"


def test_profile_empty_env():
    result = profile_env({})
    assert result.total_keys == 0
    assert result.empty_count == 0
    assert result.placeholder_count == 0
    assert result.sensitive_count == 0
    assert result.duplicate_values == {}


def test_summary_contains_expected_labels(sample_env):
    result = profile_env(sample_env)
    summary = result.summary()
    assert "Total keys" in summary
    assert "Empty values" in summary
    assert "Sensitive keys" in summary
    assert "Duplicate values" in summary
