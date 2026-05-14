"""Tests for envdiff.cli_annotate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from envdiff.cli_annotate import build_annotate_parser, run_annotate


@pytest.fixture()
def tmp_env(tmp_path: Path):
    return tmp_path


def _write(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(content, encoding="utf-8")
    return p


def _run(*args: str):
    return subprocess.run(
        [sys.executable, "-m", "envdiff.cli_annotate", *args],
        capture_output=True,
        text=True,
    )


def test_build_annotate_parser_returns_parser():
    parser = build_annotate_parser()
    assert parser is not None


def test_annotate_clean_file_exits_zero(tmp_env):
    f = _write(tmp_env, ".env", "DEBUG=true\nPORT=8080\n")
    proc = _run(str(f))
    assert proc.returncode == 0


def test_annotate_sensitive_key_in_output(tmp_env):
    f = _write(tmp_env, ".env", "DB_PASSWORD=changeme\n")
    proc = _run(str(f))
    assert proc.returncode == 0
    assert "sensitive" in proc.stdout or "sensitive" in proc.stderr


def test_annotate_missing_file_exits_two(tmp_env):
    proc = _run(str(tmp_env / "nonexistent.env"))
    assert proc.returncode == 2


def test_annotate_only_annotated_flag(tmp_env):
    f = _write(tmp_env, ".env", "DEBUG=true\nDB_PASSWORD=changeme\n")
    proc = _run(str(f), "--only-annotated")
    assert proc.returncode == 0
    assert "DEBUG" not in proc.stdout
    assert "DB_PASSWORD" in proc.stdout


def test_annotate_output_to_file(tmp_env):
    f = _write(tmp_env, ".env", "DB_PASSWORD=secret\nAPP=myapp\n")
    out = tmp_env / "annotated.env"
    proc = _run(str(f), "--output", str(out))
    assert proc.returncode == 0
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "DB_PASSWORD" in content


def test_run_annotate_via_namespace(tmp_env):
    import argparse

    f = _write(tmp_env, ".env", "API_KEY=\nAPP=myapp\n")
    parser = build_annotate_parser()
    args = parser.parse_args([str(f)])
    code = run_annotate(args)
    assert code == 0
