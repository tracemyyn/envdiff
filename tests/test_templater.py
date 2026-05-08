"""Tests for envdiff.templater and envdiff.cli_template."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

from envdiff.templater import build_template, write_template, TemplateResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_env() -> dict:
    return {
        "APP_ENV": "production",
        "DEBUG": "false",
        "DB_PASSWORD": "supersecret",
        "API_KEY": "abc123",
        "PORT": "8080",
    }


# ---------------------------------------------------------------------------
# build_template
# ---------------------------------------------------------------------------

def test_template_result_is_template_result(sample_env):
    result = build_template(sample_env)
    assert isinstance(result, TemplateResult)


def test_template_total_keys_matches_env(sample_env):
    result = build_template(sample_env)
    assert result.total_keys == len(sample_env)


def test_sensitive_keys_get_descriptive_placeholder(sample_env):
    result = build_template(sample_env, sensitive_placeholder=True)
    rendered = result.render()
    assert "DB_PASSWORD=your_db_password_here" in rendered
    assert "API_KEY=your_api_key_here" in rendered


def test_non_sensitive_keys_are_blanked(sample_env):
    result = build_template(sample_env)
    rendered = result.render()
    assert "APP_ENV=" in rendered
    assert "DEBUG=" in rendered
    assert "PORT=" in rendered


def test_sensitive_keys_in_redacted_list(sample_env):
    result = build_template(sample_env)
    assert "DB_PASSWORD" in result.redacted_keys
    assert "API_KEY" in result.redacted_keys


def test_non_sensitive_keys_in_blanked_list(sample_env):
    result = build_template(sample_env)
    assert "APP_ENV" in result.blanked_keys
    assert "PORT" in result.blanked_keys


def test_keep_values_preserves_value(sample_env):
    result = build_template(sample_env, keep_values=["PORT", "APP_ENV"])
    rendered = result.render()
    assert "PORT=8080" in rendered
    assert "APP_ENV=production" in rendered


def test_no_sensitive_placeholder_blanks_sensitive_keys(sample_env):
    result = build_template(sample_env, sensitive_placeholder=False)
    rendered = result.render()
    assert "DB_PASSWORD=" in rendered
    assert "your_" not in rendered
    assert "DB_PASSWORD" in result.blanked_keys


def test_render_ends_with_newline(sample_env):
    result = build_template(sample_env)
    assert result.render().endswith("\n")


def test_empty_env_produces_empty_template():
    result = build_template({})
    assert result.total_keys == 0
    assert result.render() == "\n"


# ---------------------------------------------------------------------------
# write_template
# ---------------------------------------------------------------------------

def test_write_template_creates_file(tmp_path, sample_env):
    out = tmp_path / "out.env.example"
    result = build_template(sample_env)
    write_template(result, str(out))
    assert out.exists()


def test_write_template_content_matches_render(tmp_path, sample_env):
    out = tmp_path / "out.env.example"
    result = build_template(sample_env)
    write_template(result, str(out))
    assert out.read_text() == result.render()
