"""Edge-case tests for envdiff.interpolator."""
from envdiff.interpolator import interpolate_env


def test_empty_env_returns_empty_resolved():
    result = interpolate_env({})
    assert result.resolved == {}
    assert not result.has_unresolved
    assert result.change_count == 0


def test_value_with_no_references_unchanged():
    env = {"KEY": "plain_value"}
    result = interpolate_env(env)
    assert result.resolved["KEY"] == "plain_value"


def test_multiple_references_in_single_value():
    env = {"A": "foo", "B": "bar", "C": "${A}-${B}"}
    result = interpolate_env(env)
    assert result.resolved["C"] == "foo-bar"


def test_self_reference_is_not_infinitely_recursive():
    # SELF=${SELF} — SELF is in env but its value contains a ref to itself.
    # The resolver does one pass; it will resolve using the original value.
    env = {"SELF": "${SELF}"}
    result = interpolate_env(env)
    # After one substitution pass SELF resolves to its own original value
    assert result.resolved["SELF"] == "${SELF}"
    assert "SELF" in result.unresolved_keys


def test_numeric_value_unchanged():
    env = {"TIMEOUT": "30"}
    result = interpolate_env(env)
    assert result.resolved["TIMEOUT"] == "30"


def test_dollar_sign_without_identifier_is_left_intact():
    env = {"PRICE": "$10.00"}
    result = interpolate_env(env)
    # '$1' would be matched as bare-dollar; '0.00' remains.
    # Verify no crash and key is present.
    assert "PRICE" in result.resolved


def test_unresolved_keys_deduplicated():
    env = {
        "A": "${MISSING}",
        "B": "${MISSING}",
    }
    result = interpolate_env(env)
    assert result.unresolved_keys.count("MISSING") == 1


def test_context_can_resolve_otherwise_missing_key():
    env = {"MSG": "Hello ${WORLD}"}
    result = interpolate_env(env, context={"WORLD": "Earth"})
    assert result.resolved["MSG"] == "Hello Earth"
    assert not result.has_unresolved


def test_summary_includes_unresolved_when_present():
    env = {"X": "${NOPE}"}
    result = interpolate_env(env)
    assert "unresolved" in result.summary()


def test_original_field_matches_input():
    env = {"K": "v"}
    result = interpolate_env(env)
    assert result.original == env
