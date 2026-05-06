"""Tests for envdiff.validator."""

import pytest
from envdiff.validator import KeySchema, ValidationError, ValidationResult, validate_env


@pytest.fixture()
def basic_schema():
    return {
        "DATABASE_URL": KeySchema(required=True, pattern=r"postgres://.+"),
        "LOG_LEVEL": KeySchema(required=False, allowed_values=["DEBUG", "INFO", "WARNING", "ERROR"]),
        "PORT": KeySchema(required=True, pattern=r"\d+"),
    }


def test_valid_env_passes(basic_schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "LOG_LEVEL": "INFO", "PORT": "8080"}
    result = validate_env(env, basic_schema)
    assert result.is_valid
    assert result.error_count == 0


def test_missing_required_key_is_error(basic_schema):
    env = {"LOG_LEVEL": "INFO", "PORT": "8080"}
    result = validate_env(env, basic_schema)
    assert not result.is_valid
    keys_with_errors = [e.key for e in result.errors]
    assert "DATABASE_URL" in keys_with_errors


def test_missing_optional_key_is_not_error(basic_schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "PORT": "5000"}
    result = validate_env(env, basic_schema)
    assert result.is_valid


def test_pattern_mismatch_is_error(basic_schema):
    env = {"DATABASE_URL": "mysql://localhost/db", "PORT": "8080"}
    result = validate_env(env, basic_schema)
    assert not result.is_valid
    assert any("pattern" in e.message for e in result.errors)


def test_allowed_values_violation_is_error(basic_schema):
    env = {"DATABASE_URL": "postgres://localhost/db", "LOG_LEVEL": "TRACE", "PORT": "8080"}
    result = validate_env(env, basic_schema)
    assert not result.is_valid
    assert any(e.key == "LOG_LEVEL" for e in result.errors)


def test_multiple_errors_collected(basic_schema):
    env = {"LOG_LEVEL": "NOPE"}  # missing DATABASE_URL, PORT; bad LOG_LEVEL
    result = validate_env(env, basic_schema)
    assert result.error_count == 3


def test_summary_valid():
    result = ValidationResult()
    assert "valid" in result.summary().lower()


def test_summary_invalid():
    result = ValidationResult(errors=[ValidationError("FOO", "required key is missing")])
    assert "1 validation error" in result.summary()
    assert "FOO" in result.summary()


def test_empty_schema_always_passes():
    env = {"ANYTHING": "goes"}
    result = validate_env(env, {})
    assert result.is_valid
