"""Edge-case tests for envdiff.differ_summary."""
from __future__ import annotations

from envdiff.differ import diff_envs
from envdiff.differ_summary import summarize_diff


def test_empty_envs_are_clean():
    result = summarize_diff(diff_envs({}, {}))
    assert result.is_clean()
    assert result.lines == []


def test_empty_to_populated_all_added():
    target = {"A": "1", "B": "2", "C": "3"}
    result = summarize_diff(diff_envs({}, target))
    assert result.added == 3
    assert result.removed == 0
    assert result.changed == 0
    assert len(result.lines) == 3


def test_populated_to_empty_all_removed():
    base = {"X": "foo", "Y": "bar"}
    result = summarize_diff(diff_envs(base, {}))
    assert result.removed == 2
    assert result.added == 0


def test_total_changes_is_correct_for_mixed_diff():
    base = {"A": "1", "B": "2", "C": "3"}
    target = {"A": "changed", "C": "3", "D": "new"}
    result = summarize_diff(diff_envs(base, target))
    # A changed, B removed, D added
    assert result.changed == 1
    assert result.removed == 1
    assert result.added == 1
    assert result.total_changes == 3


def test_summary_contains_all_change_types():
    base = {"A": "1", "B": "2"}
    target = {"A": "X", "C": "3"}
    result = summarize_diff(diff_envs(base, target))
    s = result.summary()
    assert "added" in s
    assert "removed" in s
    assert "changed" in s


def test_default_names_used_in_lines():
    result = summarize_diff(diff_envs({}, {"K": "v"}))
    assert any("target" in line for line in result.lines)


def test_custom_names_used_in_lines():
    result = summarize_diff(diff_envs({"K": "v"}, {}), base_name="local", target_name="ci")
    assert any("local" in line for line in result.lines)


def test_single_changed_value_arrow_format():
    result = summarize_diff(diff_envs({"PORT": "3000"}, {"PORT": "8080"}))
    assert len(result.lines) == 1
    assert "->" in result.lines[0]
    assert "3000" in result.lines[0]
    assert "8080" in result.lines[0]
