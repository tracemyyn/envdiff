"""Integration tests for envdiff.cli_clone."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.fixture()
def tmp_env(tmp_path: Path):
    return tmp_path


def _write(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(content)
    return p


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "envdiff.cli_clone", *args],
        capture_output=True,
        text=True,
    )


def test_build_clone_parser_returns_parser():
    from envdiff.cli_clone import build_clone_parser
    import argparse
    parser = build_clone_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_clone_clean_file_exits_zero(tmp_env):
    src = _write(tmp_env, ".env", "APP=hello\nDEBUG=true\n")
    result = _run(str(src))
    assert result.returncode == 0


def test_clone_missing_file_exits_two(tmp_env):
    result = _run(str(tmp_env / "missing.env"))
    assert result.returncode == 2


def test_clone_stdout_contains_keys(tmp_env):
    src = _write(tmp_env, ".env", "APP=hello\nPORT=8080\n")
    result = _run(str(src))
    assert "APP=hello" in result.stdout
    assert "PORT=8080" in result.stdout


def test_clone_blank_empties_values(tmp_env):
    src = _write(tmp_env, ".env", "APP=hello\nPORT=8080\n")
    result = _run(str(src), "--blank")
    assert result.returncode == 0
    assert "APP=" in result.stdout
    assert "hello" not in result.stdout


def test_clone_redact_replaces_secrets(tmp_env):
    src = _write(tmp_env, ".env", "APP=hello\nDB_PASSWORD=s3cr3t\n")
    result = _run(str(src), "--redact")
    assert result.returncode == 0
    assert "REDACTED" in result.stdout
    assert "s3cr3t" not in result.stdout


def test_clone_output_to_file(tmp_env):
    src = _write(tmp_env, ".env", "APP=hello\n")
    out = tmp_env / "cloned.env"
    result = _run(str(src), "-o", str(out))
    assert result.returncode == 0
    assert out.exists()
    assert "APP=hello" in out.read_text()


def test_clone_custom_placeholder(tmp_env):
    src = _write(tmp_env, ".env", "API_KEY=supersecret\n")
    result = _run(str(src), "--redact", "--placeholder", "***")
    assert "***" in result.stdout
    assert "supersecret" not in result.stdout
