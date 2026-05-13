"""Tests for envdiff.truncator."""
import pytest

from envdiff.truncator import TruncateResult, truncate_env, DEFAULT_MAX_LENGTH


@pytest.fixture()
def sample_env():
    return {
        "SHORT": "hi",
        "EXACT": "x" * DEFAULT_MAX_LENGTH,
        "LONG": "a" * (DEFAULT_MAX_LENGTH + 20),
        "EMPTY": "",
    }


def test_truncate_returns_truncate_result(sample_env):
    result = truncate_env(sample_env)
    assert isinstance(result, TruncateResult)


def test_short_values_unchanged(sample_env):
    result = truncate_env(sample_env)
    assert result.truncated["SHORT"] == "hi"


def test_empty_value_unchanged(sample_env):
    result = truncate_env(sample_env)
    assert result.truncated["EMPTY"] == ""


def test_exact_length_value_unchanged(sample_env):
    result = truncate_env(sample_env)
    assert result.truncated["EXACT"] == "x" * DEFAULT_MAX_LENGTH


def test_long_value_is_truncated(sample_env):
    result = truncate_env(sample_env)
    assert len(result.truncated["LONG"]) == DEFAULT_MAX_LENGTH
    assert result.truncated["LONG"].endswith("...")


def test_changed_keys_lists_only_truncated_keys(sample_env):
    result = truncate_env(sample_env)
    assert result.changed_keys == ["LONG"]


def test_was_modified_true_when_changes(sample_env):
    result = truncate_env(sample_env)
    assert result.was_modified is True


def test_was_modified_false_when_no_changes():
    result = truncate_env({"A": "short"})
    assert result.was_modified is False


def test_change_count_correct(sample_env):
    result = truncate_env(sample_env)
    assert result.change_count == 1


def test_summary_no_changes():
    result = truncate_env({"K": "v"})
    assert result.summary() == "No values truncated."


def test_summary_with_changes(sample_env):
    result = truncate_env(sample_env)
    assert "LONG" in result.summary()
    assert "1" in result.summary()


def test_original_is_preserved(sample_env):
    result = truncate_env(sample_env)
    assert result.original == sample_env


def test_custom_max_length():
    env = {"KEY": "hello world"}
    result = truncate_env(env, max_length=8)
    assert result.truncated["KEY"] == "hello..."
    assert len(result.truncated["KEY"]) == 8


def test_custom_suffix():
    env = {"KEY": "abcdefghij"}
    result = truncate_env(env, max_length=6, suffix="--")
    assert result.truncated["KEY"] == "abcd--"


def test_invalid_max_length_raises():
    with pytest.raises(ValueError):
        truncate_env({"K": "v"}, max_length=2, suffix="...")


def test_all_short_env_no_changes():
    env = {"A": "1", "B": "2", "C": "three"}
    result = truncate_env(env)
    assert result.change_count == 0
    assert result.truncated == env
