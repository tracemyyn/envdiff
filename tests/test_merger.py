"""Tests for envdiff.merger."""

import pytest

from envdiff.merger import MergeResult, merge_envs, render_merged


# ---------------------------------------------------------------------------
# merge_envs
# ---------------------------------------------------------------------------

def test_merge_identical_sources_no_conflicts():
    a = {"KEY": "val", "OTHER": "x"}
    b = {"KEY": "val", "OTHER": "x"}
    result = merge_envs([("a", a), ("b", b)])
    assert result.merged == {"KEY": "val", "OTHER": "x"}
    assert not result.has_conflicts


def test_merge_first_strategy_keeps_first_value():
    a = {"KEY": "from_a"}
    b = {"KEY": "from_b"}
    result = merge_envs([("a", a), ("b", b)], strategy="first")
    assert result.merged["KEY"] == "from_a"


def test_merge_last_strategy_keeps_last_value():
    a = {"KEY": "from_a"}
    b = {"KEY": "from_b"}
    result = merge_envs([("a", a), ("b", b)], strategy="last")
    assert result.merged["KEY"] == "from_b"


def test_merge_collects_all_keys_from_all_sources():
    a = {"ONLY_A": "1"}
    b = {"ONLY_B": "2"}
    result = merge_envs([("a", a), ("b", b)])
    assert "ONLY_A" in result.merged
    assert "ONLY_B" in result.merged


def test_merge_conflict_detected_when_values_differ():
    a = {"KEY": "v1"}
    b = {"KEY": "v2"}
    result = merge_envs([("a", a), ("b", b)])
    assert result.has_conflicts
    assert "KEY" in result.conflicts
    assert result.conflict_count() == 1


def test_merge_no_conflict_when_values_same_across_sources():
    envs = [(str(i), {"SHARED": "same"}) for i in range(4)]
    result = merge_envs(envs)
    assert not result.has_conflicts


def test_merge_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_envs([("a", {})], strategy="unknown")


def test_merge_empty_sources_returns_empty():
    result = merge_envs([])
    assert result.merged == {}
    assert not result.has_conflicts


def test_merge_three_sources_conflict_resolution_first():
    envs = [("a", {"K": "1"}), ("b", {"K": "2"}), ("c", {"K": "3"})]
    result = merge_envs(envs, strategy="first")
    assert result.merged["K"] == "1"
    assert result.has_conflicts


# ---------------------------------------------------------------------------
# render_merged
# ---------------------------------------------------------------------------

def test_render_merged_basic():
    result = MergeResult(merged={"A": "1", "B": "2"})
    output = render_merged(result)
    assert "A=1" in output
    assert "B=2" in output


def test_render_merged_annotates_conflicts():
    result = MergeResult(
        merged={"KEY": "v1"},
        conflicts={"KEY": [("a", "v1"), ("b", "v2")]},
    )
    output = render_merged(result, comment_conflicts=True)
    assert "# CONFLICT" in output
    assert "KEY=v1" in output


def test_render_merged_no_conflict_annotation_when_disabled():
    result = MergeResult(
        merged={"KEY": "v1"},
        conflicts={"KEY": [("a", "v1"), ("b", "v2")]},
    )
    output = render_merged(result, comment_conflicts=False)
    assert "# CONFLICT" not in output


def test_render_merged_empty_result_is_empty_string():
    result = MergeResult()
    assert render_merged(result) == ""
