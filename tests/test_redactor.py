"""Tests for envdiff.redactor."""

from __future__ import annotations

import pytest

from envdiff.redactor import (
    REDACTED_PLACEHOLDER,
    Redactor,
    redact_env,
)


@pytest.fixture()
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DATABASE_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "AUTH_TOKEN": "tok_xyz",
        "LOG_LEVEL": "info",
    }


def test_non_sensitive_keys_unchanged(sample_env):
    result = redact_env(sample_env)
    assert result["APP_NAME"] == "myapp"
    assert result["DEBUG"] == "true"
    assert result["LOG_LEVEL"] == "info"


def test_sensitive_keys_are_redacted(sample_env):
    result = redact_env(sample_env)
    assert result["DATABASE_PASSWORD"] == REDACTED_PLACEHOLDER
    assert result["API_KEY"] == REDACTED_PLACEHOLDER
    assert result["AUTH_TOKEN"] == REDACTED_PLACEHOLDER


def test_redact_returns_copy_not_mutating_original(sample_env):
    original_password = sample_env["DATABASE_PASSWORD"]
    redact_env(sample_env)
    assert sample_env["DATABASE_PASSWORD"] == original_password


def test_custom_placeholder(sample_env):
    result = redact_env(sample_env, placeholder="<hidden>")
    assert result["API_KEY"] == "<hidden>"


def test_custom_patterns():
    env = {"MY_CUSTOM_SECRET": "val", "NORMAL_KEY": "val2"}
    result = redact_env(env, patterns=[r"MY_CUSTOM_SECRET"])
    assert result["MY_CUSTOM_SECRET"] == REDACTED_PLACEHOLDER
    assert result["NORMAL_KEY"] == "val2"


def test_empty_env_returns_empty():
    assert redact_env({}) == {}


def test_is_sensitive_true_for_known_key():
    r = Redactor()
    assert r.is_sensitive("DB_PASSWORD") is True
    assert r.is_sensitive("SECRET_KEY") is True


def test_is_sensitive_false_for_normal_key():
    r = Redactor()
    assert r.is_sensitive("APP_ENV") is False
    assert r.is_sensitive("PORT") is False


def test_sensitive_keys_returns_sorted_list(sample_env):
    r = Redactor()
    keys = r.sensitive_keys(sample_env)
    assert "API_KEY" in keys
    assert "DATABASE_PASSWORD" in keys
    assert "AUTH_TOKEN" in keys
    assert "APP_NAME" not in keys
    assert keys == sorted(keys)


def test_case_insensitive_matching_by_default():
    r = Redactor()
    assert r.is_sensitive("db_password") is True
    assert r.is_sensitive("Api_Key") is True


def test_case_sensitive_mode_does_not_match_lowercase():
    r = Redactor(case_sensitive=True)
    assert r.is_sensitive("db_password") is False
    assert r.is_sensitive("DATABASE_PASSWORD") is True
