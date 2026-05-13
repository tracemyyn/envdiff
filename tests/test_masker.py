"""Tests for envdiff.masker."""
from __future__ import annotations

import pytest

from envdiff.masker import MaskResult, mask_env, _is_sensitive, _mask_value


@pytest.fixture
def sample_env() -> dict:
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "supersecret",
        "AWS_SECRET_KEY": "abc123xyz",
        "API_KEY": "key-value-here",
        "PORT": "8080",
        "AUTH_TOKEN": "tok_live_abcdef",
        "EMPTY_SECRET": "",
    }


def test_mask_returns_mask_result(sample_env):
    result = mask_env(sample_env)
    assert isinstance(result, MaskResult)


def test_non_sensitive_keys_unchanged(sample_env):
    result = mask_env(sample_env)
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["PORT"] == "8080"


def test_sensitive_keys_are_masked(sample_env):
    result = mask_env(sample_env)
    assert result.masked["DB_PASSWORD"] != "supersecret"
    assert result.masked["API_KEY"] != "key-value-here"
    assert result.masked["AUTH_TOKEN"] != "tok_live_abcdef"


def test_visible_chars_preserved(sample_env):
    result = mask_env(sample_env, visible_chars=4)
    assert result.masked["DB_PASSWORD"].startswith("supe")
    assert result.masked["API_KEY"].startswith("key-")


def test_empty_sensitive_value_stays_empty(sample_env):
    result = mask_env(sample_env)
    assert result.masked["EMPTY_SECRET"] == ""


def test_mask_count_matches_sensitive_keys(sample_env):
    result = mask_env(sample_env)
    assert result.mask_count == 5  # PASSWORD, SECRET_KEY, API_KEY, AUTH_TOKEN, EMPTY_SECRET


def test_was_modified_true_when_sensitive_present(sample_env):
    result = mask_env(sample_env)
    assert result.was_modified is True


def test_was_modified_false_for_clean_env():
    result = mask_env({"HOST": "localhost", "PORT": "5432"})
    assert result.was_modified is False
    assert result.mask_count == 0


def test_original_env_not_mutated(sample_env):
    original_copy = dict(sample_env)
    mask_env(sample_env)
    assert sample_env == original_copy


def test_summary_no_masked():
    result = mask_env({"HOST": "localhost"})
    assert "No sensitive" in result.summary()


def test_summary_with_masked(sample_env):
    result = mask_env(sample_env)
    assert str(result.mask_count) in result.summary()


def test_extra_patterns_extend_masking():
    env = {"MY_CUSTOM_CRED": "should-be-masked", "OTHER": "visible"}
    result = mask_env(env, extra_patterns=["CRED"])
    assert result.masked["MY_CUSTOM_CRED"] != "should-be-masked"
    assert result.masked["OTHER"] == "visible"


def test_mask_value_short_string():
    assert _mask_value("ab", visible=4) == "**"


def test_mask_value_exact_visible():
    masked = _mask_value("abcd", visible=4)
    assert masked == "abcd"


def test_is_sensitive_detects_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_case_insensitive():
    assert _is_sensitive("db_password") is True


def test_is_sensitive_clean_key():
    assert _is_sensitive("APP_NAME") is False
