"""Snapshot support: save and load .env snapshots for later comparison."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional

SNAPSHOT_VERSION = 1


class SnapshotError(Exception):
    """Raised when a snapshot cannot be saved or loaded."""


def save_snapshot(
    env: Dict[str, str],
    path: str,
    label: Optional[str] = None,
) -> None:
    """Persist *env* as a JSON snapshot file at *path*.

    Args:
        env:   Parsed key/value pairs to snapshot.
        path:  Destination file path.
        label: Optional human-readable label stored in the snapshot.
    """
    payload = {
        "version": SNAPSHOT_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "label": label or "",
        "env": env,
    }
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
    except OSError as exc:
        raise SnapshotError(f"Cannot write snapshot to '{path}': {exc}") from exc


def load_snapshot(path: str) -> Dict[str, str]:
    """Load a snapshot file and return the stored env dict.

    Args:
        path: Path to a previously saved snapshot file.

    Returns:
        The key/value pairs stored in the snapshot.

    Raises:
        SnapshotError: If the file is missing, unreadable, or malformed.
    """
    if not os.path.exists(path):
        raise SnapshotError(f"Snapshot file not found: '{path}'")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"Cannot read snapshot '{path}': {exc}") from exc

    if not isinstance(payload, dict) or "env" not in payload:
        raise SnapshotError(f"Invalid snapshot format in '{path}'")

    return dict(payload["env"])


def snapshot_metadata(path: str) -> Dict[str, str]:
    """Return metadata (version, created_at, label) without the full env."""
    if not os.path.exists(path):
        raise SnapshotError(f"Snapshot file not found: '{path}'")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"Cannot read snapshot '{path}': {exc}") from exc

    return {
        "version": str(payload.get("version", "?")),
        "created_at": payload.get("created_at", ""),
        "label": payload.get("label", ""),
    }
