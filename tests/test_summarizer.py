"""Tests for envdiff.summarizer and envdiff.cli_summarize."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from envdiff.summarizer import summarize_env, SummaryResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "",
        "API_KEY": "changeme",
        "SECRET_TOKEN": "abc123",
        "DESCRIPTION": "x" * 200,
        "DEBUG": "true",
    }


# ---------------------------------------------------------------------------
# summarize_env unit tests
# ---------------------------------------------------------------------------

def test_total_count(sample_env):
    result = summarize_env(sample_env)
    assert result.total == len(sample_env)


def test_empty_key_detected(sample_env):
    result = summarize_env(sample_env)
    assert "DB_PASSWORD" in result.empty_keys


def test_placeholder_key_detected(sample_env):
    result = summarize_env(sample_env)
    assert "API_KEY" in result.placeholder_keys


def test_empty_key_not_in_placeholder(sample_env):
    result = summarize_env(sample_env)
    assert "DB_PASSWORD" not in result.placeholder_keys


def test_sensitive_key_detected(sample_env):
    result = summarize_env(sample_env)
    assert "SECRET_TOKEN" in result.sensitive_keys
    assert "DB_PASSWORD" in result.sensitive_keys
    assert "API_KEY" in result.sensitive_keys


def test_long_value_detected(sample_env):
    result = summarize_env(sample_env)
    assert "DESCRIPTION" in result.long_value_keys


def test_long_value_threshold_respected():
    env = {"KEY": "x" * 50}
    result = summarize_env(env, long_value_threshold=40)
    assert "KEY" in result.long_value_keys

    result2 = summarize_env(env, long_value_threshold=100)
    assert "KEY" not in result2.long_value_keys


def test_clean_env_has_no_issues():
    env = {"APP": "production", "PORT": "8080"}
    result = summarize_env(env)
    assert result.empty_count == 0
    assert result.placeholder_count == 0
    assert result.sensitive_count == 0
    assert result.long_value_count == 0


def test_summary_string_contains_totals(sample_env):
    result = summarize_env(sample_env)
    text = result.summary()
    assert str(result.total) in text
    assert "Empty" in text
    assert "Sensitive" in text


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_env(tmp_path):
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(textwrap.dedent(content))
        return p
    return _write


def _run(path: Path, extra: list[str] | None = None):
    from envdiff.cli_summarize import build_summarize_parser, run_summarize
    parser = build_summarize_parser()
    args = parser.parse_args([str(path)] + (extra or []))
    return run_summarize(args)


def test_cli_exits_zero_for_valid_file(tmp_env):
    p = tmp_env("APP=hello\nPORT=8080\n")
    assert _run(p) == 0


def test_cli_missing_file_exits_two(tmp_path):
    from envdiff.cli_summarize import build_summarize_parser, run_summarize
    parser = build_summarize_parser()
    args = parser.parse_args([str(tmp_path / "missing.env")])
    assert run_summarize(args) == 2


def test_cli_json_output_is_valid(tmp_env, capsys):
    p = tmp_env("SECRET_KEY=abc\nEMPTY=\n")
    code = _run(p, ["--json"])
    assert code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "total" in data
    assert "sensitive_keys" in data
    assert "SECRET_KEY" in data["sensitive_keys"]
