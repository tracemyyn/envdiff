"""Tests for envdiff.deduplicator."""
import pytest
from envdiff.deduplicator import (
    DeduplicateResult,
    deduplicate_lines,
    deduplicate_env,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _lines(*entries: str) -> list:
    return list(entries)


# ---------------------------------------------------------------------------
# deduplicate_lines
# ---------------------------------------------------------------------------

def test_no_duplicates_returns_empty_duplicates_dict():
    lines = _lines("FOO=bar", "BAZ=qux")
    result = deduplicate_lines(lines)
    assert not result.has_duplicates
    assert result.duplicate_count == 0


def test_duplicate_key_detected():
    lines = _lines("FOO=first", "FOO=second")
    result = deduplicate_lines(lines)
    assert result.has_duplicates
    assert "FOO" in result.duplicates


def test_last_value_wins():
    lines = _lines("KEY=alpha", "KEY=beta", "KEY=gamma")
    result = deduplicate_lines(lines)
    assert result.deduped["KEY"] == "gamma"


def test_duplicate_stores_all_seen_values():
    lines = _lines("KEY=one", "KEY=two", "KEY=three")
    result = deduplicate_lines(lines)
    assert result.duplicates["KEY"] == ["one", "two", "three"]


def test_comments_and_blanks_are_ignored():
    lines = _lines("# comment", "", "A=1", "  ", "# another")
    result = deduplicate_lines(lines)
    assert not result.has_duplicates
    assert result.deduped == {"A": "1"}


def test_quoted_values_stripped():
    lines = _lines('SECRET="hello"', 'SECRET="world"')
    result = deduplicate_lines(lines)
    assert result.deduped["SECRET"] == "world"


def test_single_quoted_values_stripped():
    lines = _lines("TOKEN='abc'", "TOKEN='xyz'")
    result = deduplicate_lines(lines)
    assert result.deduped["TOKEN"] == "xyz"


def test_lines_without_equals_are_skipped():
    lines = _lines("NOEQUALS", "KEY=val")
    result = deduplicate_lines(lines)
    assert "NOEQUALS" not in result.deduped
    assert result.deduped["KEY"] == "val"


def test_summary_no_duplicates():
    result = deduplicate_lines(_lines("A=1"))
    assert result.summary() == "No duplicate keys found."


def test_summary_with_duplicates_mentions_key():
    result = deduplicate_lines(_lines("X=1", "X=2"))
    summary = result.summary()
    assert "X" in summary
    assert "kept" in summary


# ---------------------------------------------------------------------------
# deduplicate_env
# ---------------------------------------------------------------------------

def test_deduplicate_env_never_has_duplicates():
    env = {"A": "1", "B": "2"}
    result = deduplicate_env(env)
    assert not result.has_duplicates
    assert result.deduped == env


def test_deduplicate_env_returns_deduplicate_result():
    result = deduplicate_env({"K": "v"})
    assert isinstance(result, DeduplicateResult)
