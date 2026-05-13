"""Tests for envdiff.renamer and envdiff.cli_rename."""
from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path

import pytest

from envdiff.renamer import RenameResult, rename_keys


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_env() -> dict:
    return {"db_host": "localhost", "db_port": "5432", "app_name": "myapp"}


# ---------------------------------------------------------------------------
# Unit tests – rename_keys()
# ---------------------------------------------------------------------------

def test_no_transforms_returns_unchanged(sample_env):
    result = rename_keys(sample_env)
    assert result.env == sample_env
    assert result.change_count == 0
    assert not result.was_modified


def test_prefix_added_to_all_keys(sample_env):
    result = rename_keys(sample_env, prefix="TEST_")
    assert "TEST_db_host" in result.env
    assert "TEST_db_port" in result.env
    assert "TEST_app_name" in result.env
    assert result.change_count == 3


def test_suffix_added_to_all_keys(sample_env):
    result = rename_keys(sample_env, suffix="_V2")
    assert "db_host_V2" in result.env
    assert result.change_count == 3


def test_uppercase_converts_keys(sample_env):
    result = rename_keys(sample_env, uppercase=True)
    assert "DB_HOST" in result.env
    assert "APP_NAME" in result.env
    assert result.change_count == 3


def test_lowercase_converts_keys():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = rename_keys(env, lowercase=True)
    assert "db_host" in result.env
    assert result.change_count == 2


def test_uppercase_wins_over_lowercase(sample_env):
    result = rename_keys(sample_env, uppercase=True, lowercase=True)
    assert all(k == k.upper() for k in result.env)


def test_explicit_mapping_renames_specific_key(sample_env):
    result = rename_keys(sample_env, mapping={"db_host": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.env
    assert "db_host" not in result.env
    assert result.change_count == 1


def test_explicit_mapping_takes_precedence_over_prefix(sample_env):
    result = rename_keys(sample_env, mapping={"db_host": "DATABASE_HOST"}, prefix="X_")
    # explicit mapping wins for db_host
    assert "DATABASE_HOST" in result.env
    # prefix applied to the rest
    assert "X_db_port" in result.env


def test_values_are_preserved_after_rename(sample_env):
    result = rename_keys(sample_env, uppercase=True)
    assert result.env["DB_HOST"] == "localhost"
    assert result.env["DB_PORT"] == "5432"


def test_summary_no_changes():
    result = rename_keys({"KEY": "val"})
    assert result.summary() == "No keys renamed."


def test_summary_with_changes():
    result = rename_keys({"key": "val"}, uppercase=True)
    assert "key -> KEY" in result.summary()


def test_skipped_keys_listed(sample_env):
    # no transforms => all keys skipped (unchanged)
    result = rename_keys(sample_env)
    assert set(result.skipped) == set(sample_env.keys())


def test_empty_env_returns_empty_result():
    result = rename_keys({})
    assert result.env == {}
    assert result.change_count == 0
    assert result.skipped == []
