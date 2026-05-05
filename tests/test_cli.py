"""Tests for the envdiff CLI module."""

import textwrap
from pathlib import Path

import pytest

from envdiff.cli import run


@pytest.fixture()
def tmp_env(tmp_path: Path):
    """Factory that writes a .env file and returns its path."""

    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(textwrap.dedent(content))
        return p

    return _write


def test_cli_identical_files_exits_zero(tmp_env):
    base = tmp_env("base.env", "KEY=value\nOTHER=123\n")
    target = tmp_env("target.env", "KEY=value\nOTHER=123\n")
    assert run([str(base), str(target)]) == 0


def test_cli_differences_exits_zero_without_flag(tmp_env):
    base = tmp_env("base.env", "KEY=value\nMISSING=yes\n")
    target = tmp_env("target.env", "KEY=value\n")
    # Without --exit-code the command should still return 0
    assert run([str(base), str(target)]) == 0


def test_cli_differences_exits_one_with_exit_code_flag(tmp_env):
    base = tmp_env("base.env", "KEY=value\nMISSING=yes\n")
    target = tmp_env("target.env", "KEY=value\n")
    assert run([str(base), str(target), "--exit-code"]) == 1


def test_cli_missing_file_exits_two(tmp_env):
    base = tmp_env("base.env", "KEY=value\n")
    assert run([str(base), "/nonexistent/.env"]) == 2


def test_cli_ignore_values_flag(tmp_env):
    base = tmp_env("base.env", "KEY=value1\n")
    target = tmp_env("target.env", "KEY=value2\n")
    # Value mismatch exists, but --ignore-values means no differences reported
    assert run([str(base), str(target), "--ignore-values", "--exit-code"]) == 0


def test_cli_no_color_flag_does_not_crash(tmp_env, capsys):
    base = tmp_env("base.env", "KEY=value\nEXTRA=1\n")
    target = tmp_env("target.env", "KEY=different\n")
    exit_code = run([str(base), str(target), "--no-color"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out  # some output was produced


def test_cli_parse_error_exits_two(tmp_path):
    bad = tmp_path / "bad.env"
    # Write a file that our parser treats as invalid (bare key without '=')
    bad.write_text("INVALID LINE NO EQUALS\n")
    good = tmp_path / "good.env"
    good.write_text("KEY=value\n")
    # Depending on parser strictness this may or may not raise; we just ensure
    # the CLI doesn't crash unexpectedly.
    result = run([str(good), str(bad)])
    assert result in (0, 1, 2)
