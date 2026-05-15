"""Tests for envdiff.cloner."""

from __future__ import annotations

import pytest

from envdiff.cloner import clone_env, CloneResult, _is_sensitive


@pytest.fixture()
def sample_env() -> dict:
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "PORT": "8080",
    }


def test_clone_returns_clone_result(sample_env):
    result = clone_env(sample_env)
    assert isinstance(result, CloneResult)


def test_clone_no_transforms_is_identical(sample_env):
    result = clone_env(sample_env)
    assert result.cloned == sample_env
    assert not result.was_modified


def test_clone_does_not_mutate_original(sample_env):
    original_copy = dict(sample_env)
    clone_env(sample_env, blank_all=True)
    assert sample_env == original_copy


def test_blank_all_empties_every_value(sample_env):
    result = clone_env(sample_env, blank_all=True)
    assert all(v == "" for v in result.cloned.values())


def test_blank_all_tracks_blanked_keys(sample_env):
    result = clone_env(sample_env, blank_all=True)
    assert set(result.blanked_keys) == set(sample_env.keys())


def test_blank_already_empty_value_not_counted():
    env = {"EMPTY": "", "NAME": "foo"}
    result = clone_env(env, blank_all=True)
    assert "EMPTY" not in result.blanked_keys
    assert "NAME" in result.blanked_keys


def test_redact_sensitive_replaces_secret_values(sample_env):
    result = clone_env(sample_env, redact_sensitive=True)
    assert result.cloned["DB_PASSWORD"] == "REDACTED"
    assert result.cloned["API_KEY"] == "REDACTED"


def test_redact_sensitive_leaves_normal_values(sample_env):
    result = clone_env(sample_env, redact_sensitive=True)
    assert result.cloned["APP_NAME"] == "myapp"
    assert result.cloned["DEBUG"] == "true"


def test_redact_tracks_redacted_keys(sample_env):
    result = clone_env(sample_env, redact_sensitive=True)
    assert "DB_PASSWORD" in result.redacted_keys
    assert "API_KEY" in result.redacted_keys


def test_custom_placeholder(sample_env):
    result = clone_env(sample_env, redact_sensitive=True, placeholder="***")
    assert result.cloned["DB_PASSWORD"] == "***"


def test_extra_sensitive_keys_are_redacted():
    env = {"MY_CERT": "cert_data", "APP_NAME": "app"}
    result = clone_env(env, redact_sensitive=True, extra_sensitive=["MY_CERT"])
    assert result.cloned["MY_CERT"] == "REDACTED"
    assert result.cloned["APP_NAME"] == "app"


def test_change_count_reflects_modifications(sample_env):
    result = clone_env(sample_env, redact_sensitive=True)
    assert result.change_count == len(result.redacted_keys)


def test_summary_includes_key_count(sample_env):
    result = clone_env(sample_env, redact_sensitive=True)
    assert "5 key(s) cloned" in result.summary()
    assert "redacted" in result.summary()


def test_is_sensitive_detects_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_ignores_normal_key():
    assert _is_sensitive("APP_NAME") is False


def test_blank_and_redact_blank_wins(sample_env):
    # blank_all takes precedence over redact_sensitive
    result = clone_env(sample_env, blank_all=True, redact_sensitive=True)
    assert all(v == "" for v in result.cloned.values())
    assert not result.redacted_keys
