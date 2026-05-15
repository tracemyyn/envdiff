"""Tests for envdiff.trimmer and envdiff.cli_trim."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from envdiff.trimmer import TrimResult, trim_env


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "  5432  ",
        "API_KEY": "abc123   ",
        "APP_NAME": "   myapp",
        "CLEAN": "no-whitespace",
    }


# ---------------------------------------------------------------------------
# Unit tests for trim_env
# ---------------------------------------------------------------------------

def test_trim_returns_trim_result(sample_env):
    result = trim_env(sample_env)
    assert isinstance(result, TrimResult)


def test_clean_value_unchanged(sample_env):
    result = trim_env(sample_env)
    assert result.trimmed["DB_HOST"] == "localhost"
    assert result.trimmed["CLEAN"] == "no-whitespace"


def test_leading_whitespace_removed(sample_env):
    result = trim_env(sample_env)
    assert result.trimmed["APP_NAME"] == "myapp"


def test_trailing_whitespace_removed(sample_env):
    result = trim_env(sample_env)
    assert result.trimmed["API_KEY"] == "abc123"


def test_both_sides_trimmed(sample_env):
    result = trim_env(sample_env)
    assert result.trimmed["DB_PORT"] == "5432"


def test_change_count_matches_dirty_keys(sample_env):
    result = trim_env(sample_env)
    # DB_PORT, API_KEY, APP_NAME have whitespace
    assert result.change_count == 3


def test_was_modified_true_when_changes(sample_env):
    result = trim_env(sample_env)
    assert result.was_modified is True


def test_was_modified_false_when_clean():
    env = {"KEY": "value", "OTHER": "fine"}
    result = trim_env(env)
    assert result.was_modified is False
    assert result.change_count == 0


def test_changed_keys_are_sorted(sample_env):
    result = trim_env(sample_env)
    assert result.changed_keys == sorted(result.changed_keys)


def test_original_is_not_mutated(sample_env):
    original_copy = dict(sample_env)
    trim_env(sample_env)
    assert sample_env == original_copy


def test_empty_env_returns_empty_trimmed():
    result = trim_env({})
    assert result.trimmed == {}
    assert result.change_count == 0


def test_empty_value_unchanged():
    result = trim_env({"EMPTY": ""})
    assert result.trimmed["EMPTY"] == ""
    assert result.change_count == 0


def test_summary_no_changes():
    result = trim_env({"A": "clean"})
    assert "No values" in result.summary()


def test_summary_with_changes(sample_env):
    result = trim_env(sample_env)
    assert str(result.change_count) in result.summary()


# ---------------------------------------------------------------------------
# CLI smoke tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(textwrap.dedent(content))
    return path


def _run(args):
    from envdiff.cli_trim import build_trim_parser, run_trim
    parser = build_trim_parser()
    parsed = parser.parse_args(args)
    return run_trim(parsed)


def test_trim_clean_file_exits_zero(tmp_env):
    f = _write(tmp_env / ".env", "KEY=value\nOTHER=fine\n")
    assert _run([str(f), "--quiet"]) == 0


def test_trim_missing_file_exits_two(tmp_env):
    assert _run([str(tmp_env / "missing.env"), "--quiet"]) == 2


def test_trim_output_written_to_file(tmp_env):
    src = _write(tmp_env / ".env", "KEY=  hello  \n")
    out = tmp_env / "out.env"
    _run([str(src), "--output", str(out), "--quiet"])
    assert "KEY=hello" in out.read_text()


def test_trim_in_place_modifies_file(tmp_env):
    src = _write(tmp_env / ".env", "KEY=  hello  \n")
    _run([str(src), "--in-place", "--quiet"])
    assert "KEY=hello" in src.read_text()
