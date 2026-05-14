"""Tests for envdiff.tagger and envdiff.cli_tag."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from envdiff.tagger import tag_env, TagResult, _tags_for_key


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "AWS_ACCESS_KEY_ID": "AKIA...",
        "APP_DEBUG": "true",
        "SMTP_HOST": "smtp.example.com",
        "RANDOM_VALUE": "hello",
    }


def test_tag_returns_tag_result(sample_env):
    result = tag_env(sample_env)
    assert isinstance(result, TagResult)


def test_db_host_tagged_database_and_infra(sample_env):
    result = tag_env(sample_env)
    assert "database" in result.key_tags["DB_HOST"]
    assert "infra" in result.key_tags["DB_HOST"]


def test_db_password_tagged_database_and_auth(sample_env):
    result = tag_env(sample_env)
    tags = result.key_tags["DB_PASSWORD"]
    assert "database" in tags
    assert "auth" in tags


def test_aws_key_tagged_aws_and_auth(sample_env):
    result = tag_env(sample_env)
    tags = result.key_tags["AWS_ACCESS_KEY_ID"]
    assert "aws" in tags
    assert "auth" in tags


def test_smtp_host_tagged_email_and_infra(sample_env):
    result = tag_env(sample_env)
    tags = result.key_tags["SMTP_HOST"]
    assert "email" in tags
    assert "infra" in tags


def test_unrecognised_key_has_no_tags(sample_env):
    result = tag_env(sample_env)
    assert result.key_tags["RANDOM_VALUE"] == set()


def test_tag_count_reflects_unique_tags(sample_env):
    result = tag_env(sample_env)
    assert result.tag_count >= 4


def test_tagged_key_count_excludes_untagged(sample_env):
    result = tag_env(sample_env)
    assert result.tagged_key_count == len(sample_env) - 1  # RANDOM_VALUE is untagged


def test_summary_lists_tags(sample_env):
    result = tag_env(sample_env)
    s = result.summary()
    assert "database" in s
    assert "auth" in s


def test_empty_env_returns_empty_result():
    result = tag_env({})
    assert result.tag_count == 0
    assert result.tagged_key_count == 0
    assert "No tags" in result.summary()


def test_tags_for_key_returns_set():
    tags = _tags_for_key("REDIS_URL")
    assert isinstance(tags, set)
    assert "database" in tags
    assert "infra" in tags


def test_cli_tag_exits_zero(tmp_path: Path):
    from envdiff.cli_tag import run_tag
    import argparse

    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nAPP_DEBUG=true\n")

    ns = argparse.Namespace(file=str(env_file), filter_tag=None, list_tags=False)
    assert run_tag(ns) == 0


def test_cli_tag_list_tags(tmp_path: Path, capsys):
    from envdiff.cli_tag import run_tag
    import argparse

    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\n")

    ns = argparse.Namespace(file=str(env_file), filter_tag=None, list_tags=True)
    run_tag(ns)
    out = capsys.readouterr().out
    assert "database" in out


def test_cli_tag_filter_tag(tmp_path: Path, capsys):
    from envdiff.cli_tag import run_tag
    import argparse

    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nAPP_ENV=production\n")

    ns = argparse.Namespace(file=str(env_file), filter_tag="database", list_tags=False)
    run_tag(ns)
    out = capsys.readouterr().out
    assert "DB_HOST" in out


def test_cli_tag_missing_file_exits_two(tmp_path: Path):
    from envdiff.cli_tag import run_tag
    import argparse

    ns = argparse.Namespace(file=str(tmp_path / "missing.env"), filter_tag=None, list_tags=False)
    assert run_tag(ns) == 2
