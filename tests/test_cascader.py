"""Tests for envdiff.cascader."""
from __future__ import annotations

import pytest

from envdiff.cascader import cascade_envs, CascadeResult


@pytest.fixture
def base_env() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "development"}


def test_cascade_returns_cascade_result(base_env):
    result = cascade_envs([base_env])
    assert isinstance(result, CascadeResult)


def test_cascade_single_env_unchanged(base_env):
    result = cascade_envs([base_env])
    assert result.resolved == base_env


def test_cascade_later_file_overrides_earlier():
    first = {"KEY": "first", "ONLY_FIRST": "yes"}
    second = {"KEY": "second", "ONLY_SECOND": "yes"}
    result = cascade_envs([first, second])
    assert result.resolved["KEY"] == "second"
    assert result.resolved["ONLY_FIRST"] == "yes"
    assert result.resolved["ONLY_SECOND"] == "yes"


def test_cascade_collects_all_keys():
    a = {"A": "1"}
    b = {"B": "2"}
    c = {"C": "3"}
    result = cascade_envs([a, b, c])
    assert set(result.resolved.keys()) == {"A", "B", "C"}


def test_cascade_override_recorded():
    first = {"KEY": "old"}
    second = {"KEY": "new"}
    result = cascade_envs([first, second], ["base.env", "prod.env"])
    assert result.override_count == 1
    key, old, new, fname = result.overrides[0]
    assert key == "KEY"
    assert old == "old"
    assert new == "new"
    assert fname == "prod.env"


def test_cascade_no_override_when_same_value():
    first = {"KEY": "same"}
    second = {"KEY": "same"}
    result = cascade_envs([first, second])
    assert result.override_count == 0


def test_cascade_sources_track_winning_file():
    first = {"A": "1"}
    second = {"A": "2", "B": "3"}
    result = cascade_envs([first, second], ["f1", "f2"])
    assert result.sources["A"] == "f2"
    assert result.sources["B"] == "f2"


def test_cascade_was_overridden_false_for_identical():
    result = cascade_envs([{"X": "1"}, {"X": "1"}])
    assert result.was_overridden is False


def test_cascade_was_overridden_true_for_diff():
    result = cascade_envs([{"X": "1"}, {"X": "2"}])
    assert result.was_overridden is True


def test_cascade_total_keys():
    result = cascade_envs([{"A": "1", "B": "2"}, {"C": "3"}])
    assert result.total_keys == 3


def test_cascade_summary_contains_key_count():
    result = cascade_envs([{"A": "1"}, {"B": "2"}])
    assert "2 key(s)" in result.summary()


def test_cascade_summary_contains_override_count():
    result = cascade_envs([{"A": "1"}, {"A": "2"}])
    assert "1 override" in result.summary()


def test_cascade_mismatched_names_raises():
    with pytest.raises(ValueError, match="file_names length"):
        cascade_envs([{"A": "1"}, {"B": "2"}], ["only_one"])


def test_cascade_empty_envs_returns_empty():
    result = cascade_envs([])
    assert result.resolved == {}
    assert result.total_keys == 0


def test_cascade_file_names_default_generated():
    result = cascade_envs([{"A": "1"}, {"A": "2"}])
    assert result.file_names == ["file1", "file2"]
