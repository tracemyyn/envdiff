"""Tests for envdiff.differ module."""
import pytest
from envdiff.differ import diff_envs, FileDiff, LineDiff


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
TARGET = {"HOST": "prod.example.com", "PORT": "5432", "LOG_LEVEL": "warn"}


def test_diff_identical_envs_has_no_differences():
    env = {"A": "1", "B": "2"}
    result = diff_envs(env, env)
    assert not result.has_differences()
    assert len(result.unchanged) == 2


def test_diff_detects_added_key():
    result = diff_envs({}, {"NEW_KEY": "value"})
    assert len(result.added) == 1
    assert result.added[0].key == "NEW_KEY"
    assert result.added[0].target_value == "value"
    assert result.added[0].base_value is None


def test_diff_detects_removed_key():
    result = diff_envs({"OLD_KEY": "val"}, {})
    assert len(result.removed) == 1
    assert result.removed[0].key == "OLD_KEY"
    assert result.removed[0].base_value == "val"
    assert result.removed[0].target_value is None


def test_diff_detects_changed_value():
    result = diff_envs({"HOST": "localhost"}, {"HOST": "prod.example.com"})
    assert len(result.changed) == 1
    diff = result.changed[0]
    assert diff.key == "HOST"
    assert diff.base_value == "localhost"
    assert diff.target_value == "prod.example.com"


def test_diff_full_scenario():
    result = diff_envs(BASE, TARGET)
    assert result.has_differences()
    assert len(result.changed) == 1   # HOST
    assert len(result.removed) == 1   # DEBUG
    assert len(result.added) == 1     # LOG_LEVEL
    assert len(result.unchanged) == 1  # PORT


def test_diff_ignore_values_skips_changed():
    result = diff_envs(BASE, TARGET, ignore_values=True)
    changed_keys = {d.key for d in result.changed}
    assert "HOST" not in changed_keys
    # HOST should appear as unchanged when ignoring values
    unchanged_keys = {d.key for d in result.unchanged}
    assert "HOST" in unchanged_keys


def test_diff_keys_sorted_alphabetically():
    base = {"Z": "1", "A": "2", "M": "3"}
    target = {"Z": "1", "A": "2", "M": "3"}
    result = diff_envs(base, target)
    keys = [d.key for d in result.diffs]
    assert keys == sorted(keys)


def test_line_diff_str_added():
    d = LineDiff(None, 3, "added", "FOO", None, "bar")
    assert str(d).startswith("+")
    assert "FOO" in str(d)


def test_line_diff_str_removed():
    d = LineDiff(2, None, "removed", "BAR", "old", None)
    assert str(d).startswith("-")
    assert "BAR" in str(d)


def test_line_diff_str_changed():
    d = LineDiff(1, 1, "changed", "KEY", "old", "new")
    assert str(d).startswith("~")
    assert "old" in str(d)
    assert "new" in str(d)


def test_line_diff_str_unchanged():
    d = LineDiff(4, 4, "unchanged", "SAME", "val", "val")
    assert str(d).startswith(" ")


def test_file_diff_empty():
    fd = FileDiff()
    assert not fd.has_differences()
    assert fd.added == []
    assert fd.removed == []
    assert fd.changed == []
