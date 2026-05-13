"""Tests for envdiff.sorter."""

import pytest

from envdiff.sorter import SortResult, sort_env


@pytest.fixture()
def sample_env() -> dict:
    return {"ZEBRA": "1", "APPLE": "2", "MANGO": "3", "BANANA": "4"}


def test_sort_returns_sort_result(sample_env):
    result = sort_env(sample_env)
    assert isinstance(result, SortResult)


def test_sort_alphabetical_order(sample_env):
    result = sort_env(sample_env)
    assert result.sorted_order == ["APPLE", "BANANA", "MANGO", "ZEBRA"]


def test_sort_reverse_order(sample_env):
    result = sort_env(sample_env, reverse=True)
    assert result.sorted_order == ["ZEBRA", "MANGO", "BANANA", "APPLE"]


def test_sort_preserves_values(sample_env):
    result = sort_env(sample_env)
    assert result.sorted_env["APPLE"] == "2"
    assert result.sorted_env["ZEBRA"] == "1"


def test_sort_original_order_unchanged(sample_env):
    original_keys = list(sample_env.keys())
    result = sort_env(sample_env)
    assert result.original_order == original_keys


def test_was_reordered_true_when_unsorted(sample_env):
    result = sort_env(sample_env)
    assert result.was_reordered is True


def test_was_reordered_false_when_already_sorted():
    env = {"A": "1", "B": "2", "C": "3"}
    result = sort_env(env)
    assert result.was_reordered is False


def test_change_count_reflects_moved_keys(sample_env):
    result = sort_env(sample_env)
    assert result.change_count > 0


def test_change_count_zero_when_already_sorted():
    env = {"A": "1", "B": "2", "C": "3"}
    result = sort_env(env)
    assert result.change_count == 0


def test_summary_no_changes():
    env = {"A": "1", "B": "2"}
    result = sort_env(env)
    assert "no changes" in result.summary().lower()


def test_summary_with_changes(sample_env):
    result = sort_env(sample_env)
    assert "moved" in result.summary().lower()


def test_custom_key_order_pins_specified_keys(sample_env):
    result = sort_env(sample_env, key_order=["ZEBRA", "MANGO"])
    assert result.sorted_order[0] == "ZEBRA"
    assert result.sorted_order[1] == "MANGO"


def test_custom_key_order_remaining_keys_sorted(sample_env):
    result = sort_env(sample_env, key_order=["ZEBRA"])
    remaining = result.sorted_order[1:]
    assert remaining == sorted(remaining)


def test_render_produces_valid_lines(sample_env):
    result = sort_env(sample_env)
    rendered = result.render()
    assert "APPLE=2" in rendered
    assert "ZEBRA=1" in rendered


def test_render_quotes_values_with_spaces():
    env = {"KEY": "hello world"}
    result = sort_env(env)
    assert 'KEY="hello world"' in result.render()


def test_render_quotes_empty_values():
    env = {"EMPTY": ""}
    result = sort_env(env)
    assert 'EMPTY=""' in result.render()


def test_sort_empty_env():
    result = sort_env({})
    assert result.sorted_order == []
    assert result.was_reordered is False
    assert result.render() == ""
