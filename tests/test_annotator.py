"""Tests for envdiff.annotator."""

from __future__ import annotations

import pytest

from envdiff.annotator import AnnotateResult, annotate_env, _is_sensitive, _is_placeholder


@pytest.fixture()
def sample_env() -> dict:
    return {
        "DB_PASSWORD": "changeme",
        "APP_NAME": "myapp",
        "API_KEY": "",
        "DEBUG": "true",
        "SECRET_TOKEN": "abc123",
    }


def test_annotate_returns_annotate_result(sample_env):
    result = annotate_env(sample_env)
    assert isinstance(result, AnnotateResult)


def test_all_keys_present_in_result(sample_env):
    result = annotate_env(sample_env)
    assert set(result.annotated.keys()) == set(sample_env.keys())


def test_sensitive_key_gets_sensitive_annotation(sample_env):
    result = annotate_env(sample_env)
    _, comment = result.annotated["DB_PASSWORD"]
    assert "sensitive" in comment


def test_placeholder_value_gets_placeholder_annotation(sample_env):
    result = annotate_env(sample_env)
    _, comment = result.annotated["DB_PASSWORD"]
    assert "placeholder" in comment


def test_empty_value_gets_empty_annotation(sample_env):
    result = annotate_env(sample_env)
    _, comment = result.annotated["API_KEY"]
    assert "empty" in comment


def test_clean_key_has_no_annotation(sample_env):
    result = annotate_env(sample_env)
    _, comment = result.annotated["DEBUG"]
    assert comment == ""


def test_annotation_count_excludes_clean_keys(sample_env):
    result = annotate_env(sample_env)
    # DB_PASSWORD (sensitive+placeholder), APP_NAME (clean), API_KEY (sensitive+empty),
    # DEBUG (clean), SECRET_TOKEN (sensitive)
    assert result.annotation_count == 3


def test_was_annotated_true_when_issues(sample_env):
    result = annotate_env(sample_env)
    assert result.was_annotated() is True


def test_was_annotated_false_for_clean_env():
    result = annotate_env({"DEBUG": "true", "PORT": "8080"})
    assert result.was_annotated() is False


def test_render_includes_comment_for_annotated_key(sample_env):
    result = annotate_env(sample_env)
    rendered = result.render()
    assert "DB_PASSWORD=changeme  #" in rendered


def test_render_no_comment_for_clean_key(sample_env):
    result = annotate_env(sample_env)
    rendered = result.render()
    lines = {ln.split("=")[0]: ln for ln in rendered.splitlines()}
    assert "#" not in lines["DEBUG"]


def test_summary_contains_counts(sample_env):
    result = annotate_env(sample_env)
    s = result.summary()
    assert "annotation" in s


def test_is_sensitive_detects_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_ignores_normal_key():
    assert _is_sensitive("APP_NAME") is False


def test_is_placeholder_detects_changeme():
    assert _is_placeholder("changeme") is True


def test_is_placeholder_ignores_real_value():
    assert _is_placeholder("myapp") is False


def test_empty_env_returns_no_annotations():
    result = annotate_env({})
    assert result.annotation_count == 0
    assert result.annotated == {}
