"""Pin the current state of a .env file, recording key names and value hashes."""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PinEntry:
    key: str
    value_hash: str

    def to_dict(self) -> dict:
        return {"key": self.key, "value_hash": self.value_hash}

    @classmethod
    def from_dict(cls, d: dict) -> "PinEntry":
        return cls(key=d["key"], value_hash=d["value_hash"])


@dataclass
class PinResult:
    entries: List[PinEntry] = field(default_factory=list)
    drifted: List[str] = field(default_factory=list)
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.drifted or self.added or self.removed)

    @property
    def drift_count(self) -> int:
        return len(self.drifted) + len(self.added) + len(self.removed)

    def summary(self) -> str:
        if not self.has_drift:
            return "No drift detected."
        parts = []
        if self.drifted:
            parts.append(f"{len(self.drifted)} changed")
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        return "Drift detected: " + ", ".join(parts) + "."


def _hash_value(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def pin_env(env: Dict[str, str]) -> List[PinEntry]:
    """Create pin entries from an env dict."""
    return [PinEntry(key=k, value_hash=_hash_value(v)) for k, v in sorted(env.items())]


def save_pin(entries: List[PinEntry], path: str, label: Optional[str] = None) -> None:
    """Persist pin entries to a JSON file."""
    data = {
        "label": label or "",
        "entries": [e.to_dict() for e in entries],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def load_pin(path: str) -> List[PinEntry]:
    """Load pin entries from a JSON file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Pin file not found: {path}")
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return [PinEntry.from_dict(e) for e in data.get("entries", [])]


def check_drift(env: Dict[str, str], pinned: List[PinEntry]) -> PinResult:
    """Compare current env against pinned entries and report drift."""
    current = {k: _hash_value(v) for k, v in env.items()}
    pinned_map = {e.key: e.value_hash for e in pinned}

    drifted = [k for k in current if k in pinned_map and current[k] != pinned_map[k]]
    added = [k for k in current if k not in pinned_map]
    removed = [k for k in pinned_map if k not in current]

    entries = pin_env(env)
    return PinResult(entries=entries, drifted=sorted(drifted), added=sorted(added), removed=sorted(removed))
