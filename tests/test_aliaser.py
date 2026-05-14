"""Tests for envdiff.aliaser."""
import pytest
from envdiff.aliaser import AliasResult, alias_keys


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "s3cr3t",
        "DEBUG": "true",
    }


def test_alias_keys_returns_alias_result(sample_env):
    result = alias_keys(sample_env, {})
    assert isinstance(result, AliasResult)


def test_no_aliases_returns_unchanged(sample_env):
    result = alias_keys(sample_env, {})
    assert result.aliased == sample_env
    assert result.change_count == 0
    assert not result.was_modified


def test_single_key_renamed(sample_env):
    result = alias_keys(sample_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.aliased
    assert "DB_HOST" not in result.aliased
    assert result.aliased["DATABASE_HOST"] == "localhost"


def test_multiple_keys_renamed(sample_env):
    alias_map = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
    result = alias_keys(sample_env, alias_map)
    assert "DATABASE_HOST" in result.aliased
    assert "DATABASE_PORT" in result.aliased
    assert "DB_HOST" not in result.aliased
    assert "DB_PORT" not in result.aliased
    assert result.change_count == 2


def test_missing_alias_key_is_skipped(sample_env):
    result = alias_keys(sample_env, {"NONEXISTENT": "NEW_NAME"})
    assert "NONEXISTENT" not in result.aliased
    assert "NEW_NAME" not in result.aliased
    assert "NONEXISTENT" in result.skipped
    assert result.change_count == 0


def test_applied_list_contains_renamed_keys(sample_env):
    result = alias_keys(sample_env, {"DEBUG": "APP_DEBUG"})
    assert "DEBUG" in result.applied


def test_keep_original_preserves_old_key(sample_env):
    result = alias_keys(sample_env, {"DB_HOST": "DATABASE_HOST"}, keep_original=True)
    assert "DB_HOST" in result.aliased
    assert "DATABASE_HOST" in result.aliased
    assert result.aliased["DB_HOST"] == result.aliased["DATABASE_HOST"] == "localhost"


def test_original_env_not_mutated(sample_env):
    original_copy = dict(sample_env)
    alias_keys(sample_env, {"DB_HOST": "DATABASE_HOST"})
    assert sample_env == original_copy


def test_was_modified_true_when_keys_renamed(sample_env):
    result = alias_keys(sample_env, {"DEBUG": "APP_DEBUG"})
    assert result.was_modified


def test_summary_no_changes(sample_env):
    result = alias_keys(sample_env, {})
    assert result.summary() == "No keys aliased."


def test_summary_with_changes(sample_env):
    result = alias_keys(sample_env, {"DB_HOST": "DATABASE_HOST"})
    assert "1 key(s) aliased" in result.summary()


def test_summary_includes_skipped_count(sample_env):
    result = alias_keys(sample_env, {"DB_HOST": "DATABASE_HOST", "MISSING": "X"})
    assert "1 alias(es) not found" in result.summary()


def test_empty_env_with_alias_map():
    result = alias_keys({}, {"SOME_KEY": "OTHER_KEY"})
    assert result.aliased == {}
    assert result.skipped == ["SOME_KEY"]
    assert result.change_count == 0
