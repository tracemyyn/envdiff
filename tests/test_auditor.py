"""Tests for envdiff.auditor."""

import pytest
from envdiff.auditor import audit_env, AuditIssue, AuditResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _severities(result: AuditResult):
    return [i.severity for i in result.issues]


def _messages(result: AuditResult):
    return [i.message for i in result.issues]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_clean_env_has_no_issues():
    env = {"APP_NAME": "myapp", "PORT": "8080", "DEBUG": "false"}
    result = audit_env(env)
    assert not result.has_issues
    assert result.summary() == "No audit issues found."


def test_empty_sensitive_key_is_error():
    result = audit_env({"DB_PASSWORD": ""})
    assert result.error_count == 1
    assert result.issues[0].severity == "error"
    assert result.issues[0].key == "DB_PASSWORD"


def test_placeholder_sensitive_key_is_warning():
    result = audit_env({"API_SECRET": "changeme"})
    assert result.warn_count == 1
    assert result.issues[0].severity == "warn"


def test_placeholder_detection_case_insensitive():
    result = audit_env({"AUTH_TOKEN": "CHANGEME"})
    assert result.warn_count == 1


def test_empty_non_sensitive_key_is_warning():
    result = audit_env({"LOG_LEVEL": ""})
    assert result.warn_count == 1
    assert result.issues[0].severity == "warn"
    assert "empty value" in result.issues[0].message


def test_multiple_issues_counted_correctly():
    env = {
        "APP_KEY": "",          # error: sensitive + empty
        "SECRET_TOKEN": "todo", # warn: sensitive + placeholder
        "REGION": "",           # warn: empty non-sensitive
    }
    result = audit_env(env)
    assert result.error_count == 1
    assert result.warn_count == 2
    assert result.has_issues


def test_summary_reflects_counts():
    env = {"DB_PASS": "", "CACHE_URL": ""}
    result = audit_env(env)
    summary = result.summary()
    assert "error" in summary
    assert "warning" in summary


def test_audit_issue_str_format():
    issue = AuditIssue(key="MY_KEY", message="Some problem.", severity="warn")
    assert str(issue) == "[WARN] MY_KEY: Some problem."


def test_non_sensitive_placeholder_not_flagged_as_error():
    result = audit_env({"ENV_NAME": "placeholder"})
    # non-sensitive key with placeholder — only an empty-value warn would fire,
    # but value is non-empty, so no issues at all
    assert not result.has_issues


def test_angle_bracket_placeholder_triggers_warn_for_sensitive():
    result = audit_env({"PRIVATE_KEY": "<your-key-here>"})
    assert result.warn_count == 1
