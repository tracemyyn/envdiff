"""Tests for envdiff.cli_group."""
from __future__ import annotations
import os
import pytest
from pathlib import Path
from envdiff.cli_group import build_group_parser, run_group


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(directory: Path, name: str, content: str) -> str:
    p = directory / name
    p.write_text(content)
    return str(p)


def _run(args: list[str]):
    parser = build_group_parser()
    parsed = parser.parse_args(args)
    return run_group(parsed)


def test_build_group_parser_returns_parser():
    parser = build_group_parser()
    assert parser is not None


def test_group_clean_file_exits_zero(tmp_env):
    path = _write(tmp_env, ".env", "DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=prod\n")
    assert _run([path]) == 0


def test_group_missing_file_exits_two(tmp_env):
    assert _run([str(tmp_env / "missing.env")]) == 2


def test_group_with_top_flag(tmp_env):
    path = _write(
        tmp_env,
        ".env",
        "DB_HOST=localhost\nDB_PORT=5432\nAWS_KEY=abc\nAPP_ENV=prod\n",
    )
    assert _run([path, "--top", "2"]) == 0


def test_group_custom_separator(tmp_env):
    path = _write(tmp_env, ".env", "APP.HOST=localhost\nAPP.PORT=8080\nDEBUG=true\n")
    assert _run([path, "--separator", "."]) == 0


def test_group_min_prefix_option(tmp_env):
    path = _write(tmp_env, ".env", "A_KEY=val\nDB_HOST=localhost\n")
    assert _run([path, "--min-prefix", "2"]) == 0


def test_group_empty_file_exits_zero(tmp_env):
    path = _write(tmp_env, ".env", "")
    assert _run([path]) == 0
