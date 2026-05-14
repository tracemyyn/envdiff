"""Tests for envdiff.sanitizer."""

import pytest
from envdiff.sanitizer import SanitizeResult, sanitize_env


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASS": "s3cr\x00et",
        "MSG": "hello\x01world",
        "CLEAN": "no_issues_here",
        "UNICODE": "caf\u0065\u0301",  # 'cafe' + combining accent (not NFC)
    }


def test_sanitize_returns_sanitize_result(sample_env):
    result = sanitize_env(sample_env)
    assert isinstance(result, SanitizeResult)


def test_clean_value_unchanged(sample_env):
    result = sanitize_env(sample_env)
    assert result.sanitized["APP_NAME"] == "myapp"
    assert result.sanitized["CLEAN"] == "no_issues_here"


def test_null_byte_removed(sample_env):
    result = sanitize_env(sample_env)
    assert "\x00" not in result.sanitized["DB_PASS"]
    assert result.sanitized["DB_PASS"] == "s3cret"


def test_control_character_removed(sample_env):
    result = sanitize_env(sample_env)
    assert "\x01" not in result.sanitized["MSG"]
    assert result.sanitized["MSG"] == "helloworld"


def test_unicode_normalized_to_nfc(sample_env):
    result = sanitize_env(sample_env)
    import unicodedata
    assert unicodedata.is_normalized("NFC", result.sanitized["UNICODE"])


def test_change_count_reflects_modified_keys(sample_env):
    result = sanitize_env(sample_env)
    changed_keys = {c[0] for c in result.changes}
    assert "DB_PASS" in changed_keys
    assert "MSG" in changed_keys
    assert "APP_NAME" not in changed_keys
    assert "CLEAN" not in changed_keys


def test_was_modified_true_when_changes(sample_env):
    result = sanitize_env(sample_env)
    assert result.was_modified is True


def test_was_modified_false_for_clean_env():
    env = {"KEY": "value", "OTHER": "clean"}
    result = sanitize_env(env)
    assert result.was_modified is False
    assert result.change_count == 0


def test_summary_clean():
    env = {"A": "1", "B": "2"}
    result = sanitize_env(env)
    assert result.summary() == "No sanitization needed."


def test_summary_with_changes(sample_env):
    result = sanitize_env(sample_env)
    assert "Sanitized" in result.summary()
    assert str(result.change_count) in result.summary()


def test_original_env_not_mutated(sample_env):
    original_copy = dict(sample_env)
    sanitize_env(sample_env)
    assert sample_env == original_copy


def test_strip_null_bytes_disabled():
    env = {"KEY": "val\x00ue"}
    result = sanitize_env(env, strip_null_bytes=False)
    # null byte should remain (only control chars 0x01-0x08 etc. stripped)
    assert "\x00" in result.sanitized["KEY"]


def test_empty_env_returns_empty_sanitized():
    result = sanitize_env({})
    assert result.sanitized == {}
    assert result.change_count == 0
    assert not result.was_modified
