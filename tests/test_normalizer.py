"""Tests for envdiff.normalizer."""

import pytest

from envdiff.normalizer import NormalizeResult, normalize_env, _strip_inline_comment


# ---------------------------------------------------------------------------
# _strip_inline_comment
# ---------------------------------------------------------------------------

def test_strip_inline_comment_removes_trailing_comment():
    assert _strip_inline_comment("value # comment") == "value"


def test_strip_inline_comment_no_comment_unchanged():
    assert _strip_inline_comment("value") == "value"


def test_strip_inline_comment_preserves_quoted_hash():
    assert _strip_inline_comment("'value # not a comment'") == "'value # not a comment'"


def test_strip_inline_comment_hash_without_space_is_kept():
    """A '#' not preceded by a space is part of the value."""
    assert _strip_inline_comment("val#ue") == "val#ue"


# ---------------------------------------------------------------------------
# normalize_env — default options
# ---------------------------------------------------------------------------

def test_normalize_clean_env_no_changes():
    env = {"KEY": "value", "OTHER": "123"}
    result = normalize_env(env)
    assert result.normalized == env
    assert not result.was_modified
    assert result.change_count == 0


def test_normalize_strips_whitespace_from_values():
    env = {"KEY": "  hello  "}
    result = normalize_env(env)
    assert result.normalized["KEY"] == "hello"


def test_normalize_removes_inline_comment():
    env = {"KEY": "myvalue # this is a comment"}
    result = normalize_env(env)
    assert result.normalized["KEY"] == "myvalue"
    assert result.was_modified


def test_normalize_records_change_tuple():
    env = {"KEY": "val # comment"}
    result = normalize_env(env)
    assert len(result.changes) == 1
    key, before, after = result.changes[0]
    assert key == "KEY"
    assert "comment" in before
    assert "comment" not in after


# ---------------------------------------------------------------------------
# normalize_env — uppercase_keys option
# ---------------------------------------------------------------------------

def test_normalize_uppercase_keys():
    env = {"my_key": "value"}
    result = normalize_env(env, uppercase_keys=True)
    assert "MY_KEY" in result.normalized
    assert "my_key" not in result.normalized


def test_normalize_uppercase_already_upper_no_duplicate_change():
    env = {"MY_KEY": "value"}
    result = normalize_env(env, uppercase_keys=True)
    assert result.normalized == {"MY_KEY": "value"}


# ---------------------------------------------------------------------------
# normalize_env — flags disabled
# ---------------------------------------------------------------------------

def test_normalize_strip_values_false_preserves_whitespace():
    env = {"KEY": "  spaced  "}
    result = normalize_env(env, strip_values=False, remove_inline_comments=False)
    assert result.normalized["KEY"] == "  spaced  "


def test_normalize_remove_inline_comments_false_keeps_comment():
    env = {"KEY": "value # keep"}
    result = normalize_env(env, remove_inline_comments=False)
    assert "#" in result.normalized["KEY"]


# ---------------------------------------------------------------------------
# NormalizeResult.summary
# ---------------------------------------------------------------------------

def test_summary_no_changes():
    result = NormalizeResult(normalized={"A": "1"})
    assert result.summary() == "No normalization changes."


def test_summary_lists_changes():
    result = NormalizeResult(
        normalized={"A": "clean"},
        changes=[("A", "clean # old", "clean")],
    )
    summary = result.summary()
    assert "1 key(s) normalized" in summary
    assert "A" in summary
