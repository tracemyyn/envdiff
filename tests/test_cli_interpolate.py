"""Tests for envdiff.cli_interpolate."""
import subprocess
import sys
from pathlib import Path

import pytest

from envdiff.cli_interpolate import build_interpolate_parser, run_interpolate


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _run(args, tmp_path):
    """Run cli_interpolate.run_interpolate with given arg list."""
    parser = build_interpolate_parser()
    parsed = parser.parse_args(args)
    return run_interpolate(parsed)


def test_build_interpolate_parser_returns_parser():
    parser = build_interpolate_parser()
    assert parser is not None


def test_interpolate_simple_file_exits_zero(tmp_env):
    f = _write(tmp_env / ".env", "HOST=localhost\nPORT=5432\n")
    assert _run([str(f)], tmp_env) == 0


def test_interpolate_resolves_references(tmp_env, capsys):
    f = _write(
        tmp_env / ".env",
        "HOST=localhost\nURL=http://${HOST}:8080\n",
    )
    _run([str(f)], tmp_env)
    out = capsys.readouterr().out
    assert "URL=http://localhost:8080" in out


def test_interpolate_unresolved_no_flag_still_exits_zero(tmp_env):
    f = _write(tmp_env / ".env", "URL=http://${MISSING}/path\n")
    assert _run([str(f)], tmp_env) == 0


def test_interpolate_unresolved_with_flag_exits_one(tmp_env):
    f = _write(tmp_env / ".env", "URL=http://${MISSING}/path\n")
    assert _run([str(f), "--show-unresolved"], tmp_env) == 1


def test_interpolate_missing_file_exits_two(tmp_env):
    assert _run([str(tmp_env / "nonexistent.env")], tmp_env) == 2


def test_interpolate_with_context_file(tmp_env, capsys):
    base = _write(tmp_env / "base.env", "GREETING=Hello, ${NAME}!\n")
    ctx = _write(tmp_env / "ctx.env", "NAME=World\n")
    code = _run([str(base), "--context", str(ctx)], tmp_env)
    assert code == 0
    out = capsys.readouterr().out
    assert "GREETING=Hello, World!" in out


def test_interpolate_quiet_suppresses_stdout(tmp_env, capsys):
    f = _write(tmp_env / ".env", "HOST=localhost\nURL=http://${HOST}\n")
    _run([str(f), "--quiet"], tmp_env)
    out = capsys.readouterr().out
    assert out == ""


def test_interpolate_invalid_context_file_exits_two(tmp_env):
    f = _write(tmp_env / ".env", "KEY=value\n")
    code = _run(
        [str(f), "--context", str(tmp_env / "missing_ctx.env")], tmp_env
    )
    assert code == 2
