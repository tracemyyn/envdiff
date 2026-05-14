"""Tests for envdiff.differ_summary."""
from __future__ import annotations

import pytest

from envdiff.differ import diff_envs
from envdiff.differ_summary import DiffSummaryResult, summarize_diff


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _diff(base: dict, target: dict):
    return diff_envs(base, target)


# ---------------------------------------------------------------------------
# DiffSummaryResult.is_clean
# ---------------------------------------------------------------------------

def test_is_clean_when_no_changes():
    env = {"A": "1", "B": "2"}
    result = summarize_diff(_diff(env, env))
    assert result.is_clean()


def test_not_clean_when_key_added():
    result = summarize_diff(_diff({"A": "1"}, {"A": "1", "B": "2"}))
    assert not result.is_clean()


def test_not_clean_when_key_removed():
    result = summarize_diff(_diff({"A": "1", "B": "2"}, {"A": "1"}))
    assert not result.is_clean()


def test_not_clean_when_value_changed():
    result = summarize_diff(_diff({"A": "1"}, {"A": "2"}))
    assert not result.is_clean()


# ---------------------------------------------------------------------------
# Counts
# ---------------------------------------------------------------------------

def test_added_count():
    result = summarize_diff(_diff({}, {"X": "1", "Y": "2"}))
    assert result.added == 2
    assert result.removed == 0
    assert result.changed == 0


def test_removed_count():
    result = summarize_diff(_diff({"X": "1", "Y": "2"}, {}))
    assert result.removed == 2


def test_changed_count():
    result = summarize_diff(_diff({"A": "old"}, {"A": "new"}))
    assert result.changed == 1


def test_total_changes_sums_all():
    result = summarize_diff(_diff({"A": "1", "B": "2"}, {"A": "X", "C": "3"}))
    # B removed, C added, A changed
    assert result.total_changes == 3


# ---------------------------------------------------------------------------
# Summary string
# ---------------------------------------------------------------------------

def test_summary_clean():
    env = {"A": "1"}
    result = summarize_diff(_diff(env, env))
    assert result.summary() == "No differences found."


def test_summary_lists_added():
    result = summarize_diff(_diff({}, {"X": "1"}))
    assert "1 added" in result.summary()


def test_summary_lists_removed():
    result = summarize_diff(_diff({"X": "1"}, {}))
    assert "1 removed" in result.summary()


def test_summary_lists_changed():
    result = summarize_diff(_diff({"A": "1"}, {"A": "2"}))
    assert "1 changed" in result.summary()


# ---------------------------------------------------------------------------
# Lines output
# ---------------------------------------------------------------------------

def test_lines_added_marker():
    result = summarize_diff(_diff({}, {"NEW": "val"}), target_name="prod")
    assert any("[+]" in l and "prod" in l for l in result.lines)


def test_lines_removed_marker():
    result = summarize_diff(_diff({"OLD": "val"}, {}), base_name="dev")
    assert any("[-]" in l and "dev" in l for l in result.lines)


def test_lines_changed_marker():
    result = summarize_diff(_diff({"K": "old"}, {"K": "new"}))
    assert any("[~]" in l and "old" in l and "new" in l for l in result.lines)


def test_lines_are_sorted():
    result = summarize_diff(_diff({}, {"Z": "1", "A": "2", "M": "3"}))
    keys = [l.split()[1] for l in result.lines]
    assert keys == sorted(keys)
