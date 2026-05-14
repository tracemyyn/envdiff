"""Edge-case tests for envdiff.patcher."""
from envdiff.patcher import PatchOp, apply_patches, parse_patch_line


def test_empty_env_set_adds_key():
    ops = [PatchOp(action="set", key="NEW", value="v")]
    result = apply_patches({}, ops)
    assert result.patched == {"NEW": "v"}


def test_empty_env_delete_is_skipped():
    ops = [PatchOp(action="delete", key="GHOST")]
    result = apply_patches({}, ops)
    assert result.change_count == 0
    assert len(result.skipped) == 1


def test_multiple_sets_applied_in_order():
    env = {"X": "1"}
    ops = [
        PatchOp(action="set", key="X", value="2"),
        PatchOp(action="set", key="X", value="3"),
    ]
    result = apply_patches(env, ops)
    assert result.patched["X"] == "3"
    assert result.change_count == 2


def test_set_empty_value():
    env = {"K": "old"}
    ops = [PatchOp(action="set", key="K", value="")]
    result = apply_patches(env, ops)
    assert result.patched["K"] == ""


def test_parse_set_with_no_value():
    op = parse_patch_line("SET EMPTY=")
    assert op is not None
    assert op.key == "EMPTY"
    assert op.value == ""


def test_all_ops_empty_list_returns_copy():
    env = {"A": "1", "B": "2"}
    result = apply_patches(env, [])
    assert result.patched == env
    assert not result.was_modified


def test_delete_then_set_same_key():
    env = {"K": "original"}
    ops = [
        PatchOp(action="delete", key="K"),
        PatchOp(action="set", key="K", value="reborn"),
    ]
    result = apply_patches(env, ops)
    assert result.patched["K"] == "reborn"
    assert result.change_count == 2


def test_patch_result_skipped_list_populated():
    env = {"A": "1"}
    ops = [
        PatchOp(action="delete", key="MISSING_1"),
        PatchOp(action="delete", key="MISSING_2"),
    ]
    result = apply_patches(env, ops)
    assert len(result.skipped) == 2
    assert result.change_count == 0
