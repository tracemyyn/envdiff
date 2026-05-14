"""Tests for envdiff.pinner and envdiff.cli_pin."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from envdiff.pinner import (
    PinEntry,
    PinResult,
    check_drift,
    load_pin,
    pin_env,
    save_pin,
)


@pytest.fixture()
def sample_env() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET_KEY": "abc123"}


def test_pin_env_returns_sorted_entries(sample_env):
    entries = pin_env(sample_env)
    keys = [e.key for e in entries]
    assert keys == sorted(sample_env.keys())


def test_pin_entry_has_hash(sample_env):
    entries = pin_env(sample_env)
    for entry in entries:
        assert len(entry.value_hash) == 16


def test_pin_entry_round_trip():
    entry = PinEntry(key="FOO", value_hash="deadbeef12345678")
    restored = PinEntry.from_dict(entry.to_dict())
    assert restored.key == entry.key
    assert restored.value_hash == entry.value_hash


def test_save_and_load_pin(tmp_path, sample_env):
    pin_file = str(tmp_path / "pin.json")
    entries = pin_env(sample_env)
    save_pin(entries, pin_file, label="test")
    loaded = load_pin(pin_file)
    assert {e.key for e in loaded} == set(sample_env.keys())


def test_save_pin_writes_label(tmp_path, sample_env):
    pin_file = str(tmp_path / "pin.json")
    save_pin(pin_env(sample_env), pin_file, label="prod-2024")
    with open(pin_file) as fh:
        data = json.load(fh)
    assert data["label"] == "prod-2024"


def test_load_pin_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_pin(str(tmp_path / "missing.json"))


def test_check_drift_no_drift(sample_env):
    pinned = pin_env(sample_env)
    result = check_drift(sample_env, pinned)
    assert not result.has_drift
    assert result.drift_count == 0


def test_check_drift_detects_changed_value(sample_env):
    pinned = pin_env(sample_env)
    modified = dict(sample_env)
    modified["DB_HOST"] = "remotehost"
    result = check_drift(modified, pinned)
    assert "DB_HOST" in result.drifted
    assert result.has_drift


def test_check_drift_detects_added_key(sample_env):
    pinned = pin_env(sample_env)
    extended = dict(sample_env)
    extended["NEW_KEY"] = "newval"
    result = check_drift(extended, pinned)
    assert "NEW_KEY" in result.added


def test_check_drift_detects_removed_key(sample_env):
    pinned = pin_env(sample_env)
    reduced = {k: v for k, v in sample_env.items() if k != "DB_PORT"}
    result = check_drift(reduced, pinned)
    assert "DB_PORT" in result.removed


def test_summary_no_drift():
    result = PinResult()
    assert "No drift" in result.summary()


def test_summary_with_drift():
    result = PinResult(drifted=["A"], added=["B", "C"], removed=[])
    s = result.summary()
    assert "1 changed" in s
    assert "2 added" in s


# --- CLI integration ---


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _run(args: list[str]) -> int:
    from envdiff.cli_pin import build_pin_parser, run_pin
    parser = build_pin_parser()
    ns = parser.parse_args(args)
    return run_pin(ns)


def test_cli_save_creates_pin_file(tmp_path):
    env_file = tmp_path / ".env"
    pin_file = tmp_path / "pin.json"
    _write(env_file, "FOO=bar\nBAZ=qux\n")
    rc = _run(["save", str(env_file), str(pin_file)])
    assert rc == 0
    assert pin_file.exists()


def test_cli_check_no_drift_exits_zero(tmp_path):
    env_file = tmp_path / ".env"
    pin_file = tmp_path / "pin.json"
    _write(env_file, "FOO=bar\n")
    _run(["save", str(env_file), str(pin_file)])
    rc = _run(["check", str(env_file), str(pin_file), "--exit-code"])
    assert rc == 0


def test_cli_check_drift_exits_one_with_flag(tmp_path):
    env_file = tmp_path / ".env"
    pin_file = tmp_path / "pin.json"
    _write(env_file, "FOO=original\n")
    _run(["save", str(env_file), str(pin_file)])
    _write(env_file, "FOO=changed\n")
    rc = _run(["check", str(env_file), str(pin_file), "--exit-code"])
    assert rc == 1


def test_cli_check_missing_pin_exits_two(tmp_path):
    env_file = tmp_path / ".env"
    _write(env_file, "FOO=bar\n")
    rc = _run(["check", str(env_file), str(tmp_path / "no.json")])
    assert rc == 2
