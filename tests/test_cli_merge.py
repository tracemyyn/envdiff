"""Tests for the CLI merge subcommand (envdiff/cli_merge.py)."""

import sys
import pytest
from pathlib import Path
from unittest.mock import patch

from envdiff.cli_merge import build_merge_parser, run_merge


@pytest.fixture()
def tmp_env(tmp_path):
    """Return a helper that writes a .env file and returns its path."""

    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p

    return _write


def _run(args: list[str]) -> int:
    """Parse *args* and call run_merge; return the exit code."""
    parser = build_merge_parser()
    ns = parser.parse_args(args)
    return run_merge(ns)


# ---------------------------------------------------------------------------
# Parser smoke-tests
# ---------------------------------------------------------------------------


def test_build_merge_parser_returns_parser():
    import argparse

    parser = build_merge_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_merge_parser_requires_at_least_one_file():
    parser = build_merge_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


# ---------------------------------------------------------------------------
# Merging identical files
# ---------------------------------------------------------------------------


def test_merge_identical_files_exits_zero(tmp_env):
    a = tmp_env("a.env", "KEY=value\nFOO=bar\n")
    b = tmp_env("b.env", "KEY=value\nFOO=bar\n")
    assert _run([str(a), str(b)]) == 0


def test_merge_single_file_exits_zero(tmp_env):
    a = tmp_env("a.env", "KEY=value\n")
    assert _run([str(a)]) == 0


# ---------------------------------------------------------------------------
# Conflict behaviour
# ---------------------------------------------------------------------------


def test_merge_conflict_exits_one_by_default(tmp_env):
    a = tmp_env("a.env", "KEY=alpha\n")
    b = tmp_env("b.env", "KEY=beta\n")
    assert _run([str(a), str(b)]) == 1


def test_merge_conflict_first_strategy_exits_zero(tmp_env):
    """With --strategy first conflicts are resolved, so exit code should be 0."""
    a = tmp_env("a.env", "KEY=alpha\n")
    b = tmp_env("b.env", "KEY=beta\n")
    assert _run([str(a), str(b), "--strategy", "first"]) == 0


def test_merge_conflict_last_strategy_exits_zero(tmp_env):
    a = tmp_env("a.env", "KEY=alpha\n")
    b = tmp_env("b.env", "KEY=beta\n")
    assert _run([str(a), str(b), "--strategy", "last"]) == 0


# ---------------------------------------------------------------------------
# Output flag
# ---------------------------------------------------------------------------


def test_merge_output_writes_file(tmp_env, tmp_path):
    a = tmp_env("a.env", "KEY=alpha\nFOO=bar\n")
    b = tmp_env("b.env", "OTHER=value\n")
    out = tmp_path / "merged.env"
    code = _run([str(a), str(b), "--strategy", "first", "--output", str(out)])
    assert code == 0
    assert out.exists()
    content = out.read_text()
    assert "KEY" in content
    assert "OTHER" in content


def test_merge_output_contains_all_keys(tmp_env, tmp_path):
    a = tmp_env("a.env", "ALPHA=1\nBETA=2\n")
    b = tmp_env("b.env", "GAMMA=3\n")
    out = tmp_path / "merged.env"
    _run([str(a), str(b), "--strategy", "first", "--output", str(out)])
    content = out.read_text()
    for key in ("ALPHA", "BETA", "GAMMA"):
        assert key in content


# ---------------------------------------------------------------------------
# Missing / unreadable files
# ---------------------------------------------------------------------------


def test_merge_missing_file_exits_two(tmp_env):
    a = tmp_env("a.env", "KEY=value\n")
    code = _run([str(a), "/nonexistent/path.env"])
    assert code == 2
