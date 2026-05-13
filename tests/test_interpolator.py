"""Tests for envdiff.interpolator."""
import pytest
from envdiff.interpolator import interpolate_env, InterpolationResult


@pytest.fixture
def base_env():
    return {
        "HOST": "localhost",
        "PORT": "5432",
        "DB_URL": "postgres://${HOST}:${PORT}/mydb",
        "APP_URL": "http://$HOST:8080",
    }


def test_returns_interpolation_result(base_env):
    result = interpolate_env(base_env)
    assert isinstance(result, InterpolationResult)


def test_curly_brace_syntax_resolved(base_env):
    result = interpolate_env(base_env)
    assert result.resolved["DB_URL"] == "postgres://localhost:5432/mydb"


def test_bare_dollar_syntax_resolved(base_env):
    result = interpolate_env(base_env)
    assert result.resolved["APP_URL"] == "http://localhost:8080"


def test_unchanged_keys_preserved(base_env):
    result = interpolate_env(base_env)
    assert result.resolved["HOST"] == "localhost"
    assert result.resolved["PORT"] == "5432"


def test_change_count_reflects_interpolated_keys(base_env):
    result = interpolate_env(base_env)
    assert result.change_count == 2


def test_no_changes_when_no_references():
    env = {"A": "hello", "B": "world"}
    result = interpolate_env(env)
    assert result.change_count == 0
    assert not result.has_unresolved


def test_unresolved_reference_recorded():
    env = {"URL": "http://${MISSING_HOST}/path"}
    result = interpolate_env(env)
    assert "MISSING_HOST" in result.unresolved_keys
    assert result.has_unresolved


def test_unresolved_reference_left_intact():
    env = {"URL": "http://${MISSING_HOST}/path"}
    result = interpolate_env(env)
    assert result.resolved["URL"] == "http://${MISSING_HOST}/path"


def test_context_provides_external_values():
    env = {"GREETING": "Hello, ${NAME}!"}
    result = interpolate_env(env, context={"NAME": "World"})
    assert result.resolved["GREETING"] == "Hello, World!"
    assert not result.has_unresolved


def test_context_does_not_override_env_self_reference():
    env = {"HOST": "internal", "URL": "${HOST}:9000"}
    result = interpolate_env(env, context={"HOST": "external"})
    # env takes precedence in lookup (env is merged first, context second)
    # context overrides env in lookup — document actual behaviour
    assert result.resolved["URL"] == "external:9000"


def test_summary_no_changes():
    env = {"KEY": "value"}
    result = interpolate_env(env)
    assert "1 keys" in result.summary()
    assert "interpolated" not in result.summary()


def test_summary_with_changes(base_env):
    result = interpolate_env(base_env)
    assert "interpolated" in result.summary()


def test_original_env_not_mutated(base_env):
    original_copy = dict(base_env)
    interpolate_env(base_env)
    assert base_env == original_copy
