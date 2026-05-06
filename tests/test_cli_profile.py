"""Tests for envdiff.cli_profile."""
import pytest
from pathlib import Path
from envdiff.cli_profile import build_profile_parser, run_profile


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p
    return _write


def _run(args_list):
    parser = build_profile_parser()
    args = parser.parse_args(args_list)
    return run_profile(args)


def test_profile_clean_file_exits_zero(tmp_env):
    f = tmp_env(".env", "APP=myapp\nPORT=8080\n")
    assert _run([str(f)]) == 0


def test_profile_missing_file_exits_two(tmp_path):
    missing = str(tmp_path / "nonexistent.env")
    assert _run([missing]) == 2


def test_profile_exit_code_flag_triggers_on_empty_value(tmp_env):
    f = tmp_env(".env", "APP=myapp\nSECRET=\n")
    assert _run([str(f), "--exit-code"]) == 1


def test_profile_exit_code_flag_triggers_on_placeholder(tmp_env):
    f = tmp_env(".env", "API_KEY=changeme\n")
    assert _run([str(f), "--exit-code"]) == 1


def test_profile_exit_code_clean_stays_zero(tmp_env):
    f = tmp_env(".env", "APP=myapp\nPORT=8080\n")
    assert _run([str(f), "--exit-code"]) == 0


def test_profile_show_sensitive_flag_accepted(tmp_env):
    f = tmp_env(".env", "DB_PASSWORD=hunter2\nAPP=x\n")
    assert _run([str(f), "--show-sensitive"]) == 0


def test_profile_show_duplicates_flag_accepted(tmp_env):
    f = tmp_env(".env", "A=same\nB=same\n")
    assert _run([str(f), "--show-duplicates", "--exit-code"]) == 1


def test_build_profile_parser_returns_parser():
    parser = build_profile_parser()
    assert parser is not None
    args = parser.parse_args(["/some/file"])
    assert args.file == "/some/file"
    assert args.exit_code is False
    assert args.show_sensitive is False
    assert args.show_duplicates is False
