"""Tests for envdiff.flattener."""
import pytest

from envdiff.flattener import (
    FlattenResult,
    flatten_env,
    render_flattened,
)


@pytest.fixture()
def sample_env() -> dict:
    return {
        "db.host": "localhost",
        "db.port": "5432",
        "APP_NAME": "envdiff",
        "aws.s3.bucket": "my-bucket",
    }


def test_flatten_returns_flatten_result(sample_env):
    result = flatten_env(sample_env)
    assert isinstance(result, FlattenResult)


def test_dotted_key_replaced_with_underscore(sample_env):
    result = flatten_env(sample_env)
    assert "DB_HOST" in result.flattened
    assert "DB_PORT" in result.flattened


def test_nested_dotted_key_fully_replaced(sample_env):
    result = flatten_env(sample_env)
    assert "AWS_S3_BUCKET" in result.flattened
    assert "aws.s3.bucket" not in result.flattened


def test_already_flat_key_unchanged(sample_env):
    result = flatten_env(sample_env)
    # APP_NAME has no dot, so it stays (uppercased it's the same)
    assert "APP_NAME" in result.flattened


def test_values_are_preserved(sample_env):
    result = flatten_env(sample_env)
    assert result.flattened["DB_HOST"] == "localhost"
    assert result.flattened["AWS_S3_BUCKET"] == "my-bucket"


def test_change_count_reflects_renamed_keys(sample_env):
    result = flatten_env(sample_env)
    # db.host, db.port, aws.s3.bucket — 3 renamed; APP_NAME stays same
    assert result.change_count == 3


def test_was_modified_true_when_keys_renamed(sample_env):
    assert flatten_env(sample_env).was_modified is True


def test_was_modified_false_when_no_dots():
    env = {"APP_NAME": "x", "DEBUG": "true"}
    assert flatten_env(env).was_modified is False


def test_change_count_zero_when_nothing_renamed():
    env = {"CLEAN": "yes"}
    assert flatten_env(env).change_count == 0


def test_renamed_dict_maps_old_to_new(sample_env):
    result = flatten_env(sample_env)
    assert result.renamed["db.host"] == "DB_HOST"
    assert result.renamed["aws.s3.bucket"] == "AWS_S3_BUCKET"


def test_custom_delimiter_and_separator():
    env = {"db__host": "localhost", "db__port": "5432"}
    result = flatten_env(env, delimiter="__", separator="-", uppercase=False)
    assert "db-host" in result.flattened
    assert "db-port" in result.flattened


def test_uppercase_false_preserves_case():
    env = {"db.host": "localhost"}
    result = flatten_env(env, uppercase=False)
    assert "db_host" in result.flattened
    assert "DB_HOST" not in result.flattened


def test_summary_no_changes():
    env = {"KEY": "val"}
    result = flatten_env(env)
    assert result.summary() == "No keys required flattening."


def test_summary_with_changes(sample_env):
    result = flatten_env(sample_env)
    summary = result.summary()
    assert "flattened" in summary
    assert "db.host" in summary


def test_render_flattened_returns_sorted_lines(sample_env):
    result = flatten_env(sample_env)
    lines = render_flattened(result)
    assert all("=" in line for line in lines)
    keys = [line.split("=", 1)[0] for line in lines]
    assert keys == sorted(keys)


def test_original_env_not_mutated(sample_env):
    original_keys = set(sample_env.keys())
    flatten_env(sample_env)
    assert set(sample_env.keys()) == original_keys
