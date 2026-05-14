"""Tests for envdiff.caster."""
import pytest
from envdiff.caster import CastResult, _infer_type, cast_env


# ---------------------------------------------------------------------------
# _infer_type unit tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", ["true", "True", "TRUE", "yes", "1", "on",
                                    "false", "False", "no", "0", "off"])
def test_infer_type_bool(value):
    assert _infer_type(value) == "bool"


@pytest.mark.parametrize("value", ["42", "-7", "0"])
def test_infer_type_int(value):
    assert _infer_type(value) == "int"


@pytest.mark.parametrize("value", ["3.14", "-0.5", "1e10"])
def test_infer_type_float(value):
    assert _infer_type(value) == "float"


@pytest.mark.parametrize("value", ["hello", "some-url", "abc123"])
def test_infer_type_str(value):
    assert _infer_type(value) == "str"


def test_infer_type_empty_string():
    assert _infer_type("") == "empty"


# ---------------------------------------------------------------------------
# cast_env tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_env():
    return {
        "DEBUG": "true",
        "PORT": "8080",
        "RATIO": "0.75",
        "APP_NAME": "myapp",
        "EMPTY_KEY": "",
    }


def test_cast_env_returns_cast_result(sample_env):
    result = cast_env(sample_env)
    assert isinstance(result, CastResult)


def test_cast_env_type_count_matches_env(sample_env):
    result = cast_env(sample_env)
    assert result.type_count == len(sample_env)


def test_cast_env_bool_detected(sample_env):
    result = cast_env(sample_env)
    assert result.types["DEBUG"] == "bool"


def test_cast_env_int_detected(sample_env):
    result = cast_env(sample_env)
    assert result.types["PORT"] == "int"


def test_cast_env_float_detected(sample_env):
    result = cast_env(sample_env)
    assert result.types["RATIO"] == "float"


def test_cast_env_str_detected(sample_env):
    result = cast_env(sample_env)
    assert result.types["APP_NAME"] == "str"


def test_cast_env_empty_detected(sample_env):
    result = cast_env(sample_env)
    assert result.types["EMPTY_KEY"] == "empty"


def test_keys_of_type_filters_correctly(sample_env):
    result = cast_env(sample_env)
    bool_keys = result.keys_of_type("bool")
    assert "DEBUG" in bool_keys
    assert "PORT" not in bool_keys


def test_summary_contains_type_labels(sample_env):
    result = cast_env(sample_env)
    s = result.summary()
    assert "bool" in s
    assert "int" in s
    assert "float" in s
    assert "str" in s


def test_cast_empty_env():
    result = cast_env({})
    assert result.type_count == 0
    assert result.keys_of_type("str") == []
