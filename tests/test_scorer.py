"""Tests for envdiff.scorer and envdiff.cli_score."""

import json
import os
import textwrap
from pathlib import Path

import pytest

from envdiff.linter import LintResult, LintIssue
from envdiff.auditor import AuditResult, AuditIssue
from envdiff.profiler import ProfileResult
from envdiff.scorer import score_env, ScoreResult, _MAX_SCORE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lint(errors=0, warnings=0) -> LintResult:
    issues = [LintIssue("K", "msg", "error") for _ in range(errors)]
    issues += [LintIssue("K", "msg", "warning") for _ in range(warnings)]
    return LintResult(issues=issues)


def _audit(errors=0, warnings=0) -> AuditResult:
    issues = [AuditIssue("K", "msg", "error") for _ in range(errors)]
    issues += [AuditIssue("K", "msg", "warning") for _ in range(warnings)]
    return AuditResult(issues=issues)


def _profile(empty=0, placeholders=0) -> ProfileResult:
    env = {}
    for i in range(empty):
        env[f"EMPTY_{i}"] = ""
    for i in range(placeholders):
        env[f"PH_{i}"] = "changeme"
    return ProfileResult(env=env)


# ---------------------------------------------------------------------------
# scorer unit tests
# ---------------------------------------------------------------------------

def test_perfect_score_for_clean_env():
    result = score_env(_lint(), _audit(), _profile())
    assert result.score == _MAX_SCORE
    assert result.grade == "A"
    assert result.penalties == []


def test_lint_errors_reduce_score():
    result = score_env(_lint(errors=2), _audit(), _profile())
    assert result.score == _MAX_SCORE - 2 * 10


def test_lint_warnings_reduce_score():
    result = score_env(_lint(warnings=3), _audit(), _profile())
    assert result.score == _MAX_SCORE - 3 * 3


def test_audit_errors_reduce_score():
    result = score_env(_lint(), _audit(errors=1), _profile())
    assert result.score == _MAX_SCORE - 15


def test_empty_keys_reduce_score():
    result = score_env(_lint(), _audit(), _profile(empty=2))
    assert result.score == _MAX_SCORE - 2 * 4


def test_score_never_goes_below_zero():
    result = score_env(_lint(errors=20), _audit(errors=10), _profile(empty=10))
    assert result.score == 0


def test_grade_boundaries():
    assert ScoreResult(score=100).grade == "A"
    assert ScoreResult(score=75).grade == "B"
    assert ScoreResult(score=60).grade == "C"
    assert ScoreResult(score=40).grade == "D"
    assert ScoreResult(score=39).grade == "F"


def test_summary_contains_score_and_grade():
    result = ScoreResult(score=85, penalties=["1 lint error(s) (-10 pts)"])
    summary = result.summary()
    assert "85/100" in summary
    assert "Grade: B" in summary
    assert "lint error" in summary


# ---------------------------------------------------------------------------
# cli_score integration tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_env(tmp_path: Path):
    def _write(content: str) -> str:
        p = tmp_path / ".env"
        p.write_text(textwrap.dedent(content))
        return str(p)
    return _write


def test_cli_score_clean_file_exits_zero(tmp_env, capsys):
    from envdiff.cli_score import build_score_parser, run_score
    path = tmp_env("API_KEY=secret123\nDEBUG=false\n")
    args = build_score_parser().parse_args([path])
    rc = run_score(args)
    assert rc == 0


def test_cli_score_missing_file_exits_two(tmp_path, capsys):
    from envdiff.cli_score import build_score_parser, run_score
    args = build_score_parser().parse_args([str(tmp_path / "nope.env")])
    rc = run_score(args)
    assert rc == 2


def test_cli_score_min_score_flag_triggers_exit_one(tmp_env):
    from envdiff.cli_score import build_score_parser, run_score
    # empty value will incur penalty
    path = tmp_env("EMPTY_KEY=\n" * 20)
    args = build_score_parser().parse_args([path, "--min-score", "99"])
    rc = run_score(args)
    assert rc == 1


def test_cli_score_json_output(tmp_env, capsys):
    from envdiff.cli_score import build_score_parser, run_score
    path = tmp_env("FOO=bar\n")
    args = build_score_parser().parse_args([path, "--json"])
    run_score(args)
    captured = capsys.readouterr().out
    data = json.loads(captured)
    assert "score" in data
    assert "grade" in data
    assert "penalties" in data
