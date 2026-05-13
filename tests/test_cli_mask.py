"""Integration tests for envdiff.cli_mask."""
from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

from envdiff.cli_mask import build_mask_parser, run_mask


@pytest.fixture
def tmp_env(tmp_path: Path):
    return tmp_path


def _write(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(textwrap.dedent(content))
    return p


def _run(args: list[str]):
    parser = build_mask_parser()
    namespace = parser.parse_args(args)
    return run_mask(namespace)


def test_build_mask_parser_returns_parser():
    parser = build_mask_parser()
    assert parser is not None


def test_mask_clean_file_exits_zero(tmp_env):
    f = _write(tmp_env, ".env", """
        APP_NAME=myapp
        PORT=8080
    """)
    assert _run([str(f)]) == 0


def test_mask_sensitive_file_exits_zero(tmp_env):
    f = _write(tmp_env, ".env", """
        APP_NAME=myapp
        DB_PASSWORD=supersecret
    """)
    assert _run([str(f)]) == 0


def test_mask_missing_file_exits_two(tmp_env):
    assert _run([str(tmp_env / "nonexistent.env")]) == 2


def test_mask_visible_option_accepted(tmp_env):
    f = _write(tmp_env, ".env", "API_KEY=abcdefgh")
    assert _run([str(f), "--visible", "2"]) == 0


def test_mask_extra_patterns_accepted(tmp_env):
    f = _write(tmp_env, ".env", """
        MY_CRED=hidden
        OTHER=visible
    """)
    assert _run([str(f), "--extra-patterns", "CRED"]) == 0


def test_mask_show_keys_flag_accepted(tmp_env):
    f = _write(tmp_env, ".env", "DB_PASSWORD=secret")
    assert _run([str(f), "--show-keys"]) == 0
