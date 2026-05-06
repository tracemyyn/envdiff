"""Scores an .env file for overall health based on lint, audit, and profile results."""

from dataclasses import dataclass, field
from typing import List

from envdiff.linter import LintResult
from envdiff.auditor import AuditResult
from envdiff.profiler import ProfileResult

# Penalty weights
_LINT_ERROR_PENALTY = 10
_LINT_WARNING_PENALTY = 3
_AUDIT_ERROR_PENALTY = 15
_AUDIT_WARNING_PENALTY = 5
_EMPTY_KEY_PENALTY = 4
_PLACEHOLDER_PENALTY = 2
_MAX_SCORE = 100


@dataclass
class ScoreResult:
    score: int
    max_score: int = _MAX_SCORE
    penalties: List[str] = field(default_factory=list)

    @property
    def grade(self) -> str:
        pct = self.score / self.max_score
        if pct >= 0.90:
            return "A"
        if pct >= 0.75:
            return "B"
        if pct >= 0.60:
            return "C"
        if pct >= 0.40:
            return "D"
        return "F"

    def summary(self) -> str:
        return (
            f"Score: {self.score}/{self.max_score} (Grade: {self.grade})\n"
            + ("\n".join(f"  - {p}" for p in self.penalties) if self.penalties else "  No penalties.")
        )


def score_env(
    lint: LintResult,
    audit: AuditResult,
    profile: ProfileResult,
) -> ScoreResult:
    """Compute a health score for an env file from analysis results."""
    deductions = 0
    penalties: List[str] = []

    if lint.error_count():
        pts = lint.error_count() * _LINT_ERROR_PENALTY
        deductions += pts
        penalties.append(f"{lint.error_count()} lint error(s) (-{pts} pts)")

    lint_warnings = len(lint.issues) - lint.error_count()
    if lint_warnings:
        pts = lint_warnings * _LINT_WARNING_PENALTY
        deductions += pts
        penalties.append(f"{lint_warnings} lint warning(s) (-{pts} pts)")

    if audit.error_count():
        pts = audit.error_count() * _AUDIT_ERROR_PENALTY
        deductions += pts
        penalties.append(f"{audit.error_count()} audit error(s) (-{pts} pts)")

    audit_warnings = len(audit.issues) - audit.error_count()
    if audit_warnings:
        pts = audit_warnings * _AUDIT_WARNING_PENALTY
        deductions += pts
        penalties.append(f"{audit_warnings} audit warning(s) (-{pts} pts)")

    if profile.empty_count():
        pts = profile.empty_count() * _EMPTY_KEY_PENALTY
        deductions += pts
        penalties.append(f"{profile.empty_count()} empty key(s) (-{pts} pts)")

    if profile.placeholder_count():
        pts = profile.placeholder_count() * _PLACEHOLDER_PENALTY
        deductions += pts
        penalties.append(f"{profile.placeholder_count()} placeholder value(s) (-{pts} pts)")

    score = max(0, _MAX_SCORE - deductions)
    return ScoreResult(score=score, penalties=penalties)
