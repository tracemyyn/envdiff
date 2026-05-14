"""Integration tests for envdiff.cli_patch."""
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def _run(*args):
    return subprocess.run(
        [sys.executable, "-m", "envdiff.cli_patch", *args],
        capture_output=True,
        text=True,
    )


def test_build_patch_parser_returns_parser():
    from envdiff.cli_patch import build_patch_parser
    p = build_patch_parser()
    assert p is not None


def test_patch_applies_set(tmp_env):
    env_f = _write(tmp_env / ".env", "FOO=old\nBAR=bar\n")
    patch_f = _write(tmp_env / "patch.txt", "SET FOO=new\n")
    proc = _run(str(env_f), str(patch_f))
    assert proc.returncode == 0
    assert "FOO=new" in proc.stdout
    assert "BAR=bar" in proc.stdout


def test_patch_applies_delete(tmp_env):
    env_f = _write(tmp_env / ".env", "FOO=foo\nBAR=bar\n")
    patch_f = _write(tmp_env / "patch.txt", "DELETE FOO\n")
    proc = _run(str(env_f), str(patch_f))
    assert proc.returncode == 0
    assert "FOO" not in proc.stdout
    assert "BAR=bar" in proc.stdout


def test_patch_missing_env_file_exits_two(tmp_env):
    patch_f = _write(tmp_env / "patch.txt", "SET X=1\n")
    proc = _run(str(tmp_env / "missing.env"), str(patch_f))
    assert proc.returncode == 2


def test_patch_missing_patch_file_exits_two(tmp_env):
    env_f = _write(tmp_env / ".env", "FOO=foo\n")
    proc = _run(str(env_f), str(tmp_env / "missing_patch.txt"))
    assert proc.returncode == 2


def test_patch_exit_code_flag_when_modified(tmp_env):
    env_f = _write(tmp_env / ".env", "FOO=foo\n")
    patch_f = _write(tmp_env / "patch.txt", "SET FOO=bar\n")
    proc = _run(str(env_f), str(patch_f), "--exit-code")
    assert proc.returncode == 1


def test_patch_exit_code_flag_when_unmodified(tmp_env):
    env_f = _write(tmp_env / ".env", "FOO=foo\n")
    patch_f = _write(tmp_env / "patch.txt", "# just a comment\n")
    proc = _run(str(env_f), str(patch_f), "--exit-code")
    assert proc.returncode == 0


def test_patch_writes_to_output_file(tmp_env):
    env_f = _write(tmp_env / ".env", "A=1\nB=2\n")
    patch_f = _write(tmp_env / "patch.txt", "SET A=99\n")
    out_f = tmp_env / "out.env"
    proc = _run(str(env_f), str(patch_f), "-o", str(out_f))
    assert proc.returncode == 0
    content = out_f.read_text()
    assert "A=99" in content
