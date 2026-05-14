"""Tests for envdiff.patcher."""
import pytest

from envdiff.patcher import (
    PatchOp,
    PatchResult,
    apply_patches,
    parse_patch_line,
)


# ---------------------------------------------------------------------------
# parse_patch_line
# ---------------------------------------------------------------------------

def test_parse_set_op():
    op = parse_patch_line("SET FOO=bar")
    assert op is not None
    assert op.action == "set"
    assert op.key == "FOO"
    assert op.value == "bar"


def test_parse_set_op_case_insensitive():
    op = parse_patch_line("set DB_HOST=localhost")
    assert op.action == "set"
    assert op.key == "DB_HOST"


def test_parse_delete_op():
    op = parse_patch_line("DELETE OLD_KEY")
    assert op is not None
    assert op.action == "delete"
    assert op.key == "OLD_KEY"
    assert op.value is None


def test_parse_blank_line_returns_none():
    assert parse_patch_line("") is None
    assert parse_patch_line("   ") is None


def test_parse_comment_line_returns_none():
    assert parse_patch_line("# this is a comment") is None


def test_parse_unknown_directive_raises():
    with pytest.raises(ValueError, match="Unknown patch directive"):
        parse_patch_line("REPLACE FOO=bar")


def test_parse_set_value_with_equals():
    op = parse_patch_line("SET URL=http://host:5432/db")
    assert op.value == "http://host:5432/db"


# ---------------------------------------------------------------------------
# apply_patches
# ---------------------------------------------------------------------------

@pytest.fixture
def base_env():
    return {"FOO": "foo", "BAR": "bar", "BAZ": "baz"}


def test_apply_set_adds_new_key(base_env):
    ops = [PatchOp(action="set", key="NEW", value="val")]
    result = apply_patches(base_env, ops)
    assert result.patched["NEW"] == "val"
    assert result.change_count == 1


def test_apply_set_updates_existing_key(base_env):
    ops = [PatchOp(action="set", key="FOO", value="updated")]
    result = apply_patches(base_env, ops)
    assert result.patched["FOO"] == "updated"


def test_apply_delete_removes_key(base_env):
    ops = [PatchOp(action="delete", key="BAR")]
    result = apply_patches(base_env, ops)
    assert "BAR" not in result.patched
    assert result.change_count == 1


def test_apply_delete_missing_key_is_skipped(base_env):
    ops = [PatchOp(action="delete", key="MISSING")]
    result = apply_patches(base_env, ops, skip_missing_deletes=True)
    assert len(result.skipped) == 1
    assert result.change_count == 0


def test_apply_does_not_mutate_original(base_env):
    original = dict(base_env)
    ops = [PatchOp(action="set", key="FOO", value="changed")]
    apply_patches(base_env, ops)
    assert base_env == original


def test_was_modified_false_when_no_ops(base_env):
    result = apply_patches(base_env, [])
    assert not result.was_modified


def test_summary_string(base_env):
    ops = [
        PatchOp(action="set", key="A", value="1"),
        PatchOp(action="delete", key="MISSING"),
    ]
    result = apply_patches(base_env, ops)
    assert "1 patch(es) applied" in result.summary()
    assert "1 skipped" in result.summary()


def test_patch_op_str_set():
    op = PatchOp(action="set", key="X", value="y")
    assert str(op) == "SET X=y"


def test_patch_op_str_delete():
    op = PatchOp(action="delete", key="X")
    assert str(op) == "DELETE X"
