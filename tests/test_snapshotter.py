"""Tests for envdiff.snapshotter."""

from __future__ import annotations

import json
import os
import pytest

from envdiff.snapshotter import (
    SnapshotError,
    load_snapshot,
    save_snapshot,
    snapshot_metadata,
)


@pytest.fixture()
def tmp_snap(tmp_path):
    """Return a helper that writes a raw snapshot JSON and its path."""

    def _write(payload: dict) -> str:
        p = tmp_path / "snap.json"
        p.write_text(json.dumps(payload), encoding="utf-8")
        return str(p)

    return _write


# ---------------------------------------------------------------------------
# save_snapshot
# ---------------------------------------------------------------------------

def test_save_creates_file(tmp_path):
    dest = str(tmp_path / "out.json")
    save_snapshot({"KEY": "value"}, dest)
    assert os.path.exists(dest)


def test_save_stores_env_keys(tmp_path):
    dest = str(tmp_path / "out.json")
    save_snapshot({"A": "1", "B": "2"}, dest)
    with open(dest) as fh:
        data = json.load(fh)
    assert data["env"] == {"A": "1", "B": "2"}


def test_save_stores_label(tmp_path):
    dest = str(tmp_path / "out.json")
    save_snapshot({}, dest, label="production")
    with open(dest) as fh:
        data = json.load(fh)
    assert data["label"] == "production"


def test_save_raises_on_bad_path():
    with pytest.raises(SnapshotError):
        save_snapshot({}, "/no/such/directory/snap.json")


# ---------------------------------------------------------------------------
# load_snapshot
# ---------------------------------------------------------------------------

def test_load_returns_env_dict(tmp_snap):
    path = tmp_snap({"version": 1, "created_at": "", "label": "", "env": {"X": "42"}})
    result = load_snapshot(path)
    assert result == {"X": "42"}


def test_load_raises_when_file_missing(tmp_path):
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot(str(tmp_path / "ghost.json"))


def test_load_raises_on_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    with pytest.raises(SnapshotError):
        load_snapshot(str(bad))


def test_load_raises_on_missing_env_key(tmp_snap):
    path = tmp_snap({"version": 1})
    with pytest.raises(SnapshotError, match="Invalid snapshot"):
        load_snapshot(path)


# ---------------------------------------------------------------------------
# snapshot_metadata
# ---------------------------------------------------------------------------

def test_metadata_returns_label_and_created_at(tmp_snap):
    path = tmp_snap(
        {"version": 1, "created_at": "2024-01-01T00:00:00+00:00", "label": "staging", "env": {}}
    )
    meta = snapshot_metadata(path)
    assert meta["label"] == "staging"
    assert "2024" in meta["created_at"]


def test_metadata_raises_when_file_missing(tmp_path):
    with pytest.raises(SnapshotError):
        snapshot_metadata(str(tmp_path / "nope.json"))
