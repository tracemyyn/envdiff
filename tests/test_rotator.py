"""Tests for envdiff.rotator."""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import List

import pytest

from envdiff.pinner import PinEntry
from envdiff.rotator import RotateResult, RotationIssue, check_rotation, _is_sensitive


def _pin(key: str, value: str, days_ago: int = 10) -> PinEntry:
    pinned_at = (datetime.now(tz=timezone.utc) - timedelta(days=days_ago)).isoformat()
    value_hash = hashlib.sha256(value.encode()).hexdigest()
    return PinEntry(key=key, value_hash=value_hash, pinned_at=pinned_at)


@pytest.fixture
def sample_env():
    return {
        "DB_PASSWORD": "supersecret",
        "API_KEY": "abc123",
        "APP_NAME": "myapp",
        "DEBUG": "true",
    }


def test_is_sensitive_detects_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_detects_api_key():
    assert _is_sensitive("API_KEY") is True


def test_is_sensitive_ignores_normal_key():
    assert _is_sensitive("APP_NAME") is False


def test_clean_env_no_issues(sample_env):
    pins = [
        _pin("DB_PASSWORD", "supersecret", days_ago=5),
        _pin("API_KEY", "abc123", days_ago=5),
    ]
    result = check_rotation(sample_env, pins, max_age_days=90)
    assert isinstance(result, RotateResult)
    assert not result.has_issues


def test_stale_key_flagged(sample_env):
    pins = [
        _pin("DB_PASSWORD", "supersecret", days_ago=100),
        _pin("API_KEY", "abc123", days_ago=5),
    ]
    result = check_rotation(sample_env, pins, max_age_days=90)
    assert result.has_issues
    keys = [i.key for i in result.issues]
    assert "DB_PASSWORD" in keys


def test_missing_pin_flagged(sample_env):
    pins = [_pin("API_KEY", "abc123", days_ago=5)]
    result = check_rotation(sample_env, pins, max_age_days=90)
    assert result.has_issues
    keys = [i.key for i in result.issues]
    assert "DB_PASSWORD" in keys


def test_rotated_value_not_flagged(sample_env):
    # Value changed since pin — should NOT be flagged as stale
    pins = [
        _pin("DB_PASSWORD", "old_secret", days_ago=200),
        _pin("API_KEY", "abc123", days_ago=5),
    ]
    result = check_rotation(sample_env, pins, max_age_days=90)
    # DB_PASSWORD hash differs so no stale flag, but missing pin for new value is OK
    keys = [i.key for i in result.issues]
    assert "DB_PASSWORD" not in keys


def test_checked_count_only_sensitive(sample_env):
    pins = [
        _pin("DB_PASSWORD", "supersecret"),
        _pin("API_KEY", "abc123"),
    ]
    result = check_rotation(sample_env, pins)
    assert result.checked == 2


def test_summary_clean():
    result = RotateResult(issues=[], checked=3)
    assert "fresh" in result.summary()


def test_summary_with_issues():
    issue = RotationIssue(key="API_KEY", reason="stale", days_old=100)
    result = RotateResult(issues=[issue], checked=2)
    assert "1" in result.summary()


def test_rotation_issue_str():
    issue = RotationIssue(key="DB_PASSWORD", reason="too old", days_old=120)
    text = str(issue)
    assert "DB_PASSWORD" in text
    assert "120" in text


def test_empty_env_no_issues():
    result = check_rotation({}, [], max_age_days=90)
    assert not result.has_issues
    assert result.checked == 0
