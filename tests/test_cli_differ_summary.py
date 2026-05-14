"""Integration tests for cli_differ_summary."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.fixture()
def tmp_env(tmp_path: Path):
    return tmp_path


def _write(directory: Path, name: str, content: str) -> str:
    path = directory / name
    path.write_text(content)
    return str(path)


def _run(*args: str):
    return subprocess.run(
        [sys.executable, "-m", "envdiff.cli_differ_summary", *args],
        capture_output=True,
        text=True,
    )


def test_build_differ_summary_parser_returns_parser():
    from envdiff.cli_differ_summary import build_differ_summary_parser
    parser = build_differ_summary_parser()
    assert parser is not None


def test_identical_files_exits_zero(tmp_env):
    f = _write(tmp_env, "a.env", "KEY=value\n")
    result = _run(f, f)
    assert result.returncode == 0


def test_identical_files_reports_no_differences(tmp_env):
    f = _write(tmp_env, "a.env", "KEY=value\n")
    result = _run(f, f)
    assert "No differences found" in result.stdout


def test_different_files_exits_zero_without_flag(tmp_env):
    a = _write(tmp_env, "a.env", "KEY=one\n")
    b = _write(tmp_env, "b.env", "KEY=two\n")
    result = _run(a, b)
    assert result.returncode == 0


def test_different_files_exits_one_with_exit_code_flag(tmp_env):
    a = _write(tmp_env, "a.env", "KEY=one\n")
    b = _write(tmp_env, "b.env", "KEY=two\n")
    result = _run(a, b, "--exit-code")
    assert result.returncode == 1


def test_missing_file_exits_two(tmp_env):
    a = _write(tmp_env, "a.env", "KEY=value\n")
    result = _run(a, str(tmp_env / "missing.env"))
    assert result.returncode == 2


def test_custom_labels_appear_in_output(tmp_env):
    a = _write(tmp_env, "a.env", "KEY=one\n")
    b = _write(tmp_env, "b.env", "KEY=one\nEXTRA=yes\n")
    result = _run(a, b, "--base-name", "staging", "--target-name", "prod")
    assert "staging" in result.stdout or "prod" in result.stdout


def test_added_key_shown_in_output(tmp_env):
    a = _write(tmp_env, "a.env", "A=1\n")
    b = _write(tmp_env, "b.env", "A=1\nB=2\n")
    result = _run(a, b)
    assert "[+]" in result.stdout
    assert "B" in result.stdout
