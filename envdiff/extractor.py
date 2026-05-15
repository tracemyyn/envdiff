"""Extract a subset of keys from an env dict by prefix, suffix, or explicit list."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional


@dataclass
class ExtractResult:
    extracted: Dict[str, str]
    skipped: Dict[str, str]
    matched_keys: List[str] = field(default_factory=list)

    @property
    def extract_count(self) -> int:
        return len(self.extracted)

    @property
    def skip_count(self) -> int:
        return len(self.skipped)

    @property
    def was_filtered(self) -> bool:
        return len(self.skipped) > 0

    def summary(self) -> str:
        return (
            f"Extracted {self.extract_count} key(s), "
            f"skipped {self.skip_count} key(s)."
        )


def extract_env(
    env: Dict[str, str],
    *,
    keys: Optional[List[str]] = None,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    pattern: Optional[str] = None,
) -> ExtractResult:
    """Return a new env dict containing only the matching keys.

    Matching priority: explicit *keys* list beats prefix/suffix/pattern.
    If multiple of prefix, suffix, pattern are given, a key must match ALL
    provided criteria (AND semantics).
    """
    extracted: Dict[str, str] = {}
    skipped: Dict[str, str] = {}
    matched: List[str] = []

    for k, v in env.items():
        if keys is not None:
            keep = k in keys
        else:
            checks = []
            if prefix is not None:
                checks.append(k.startswith(prefix))
            if suffix is not None:
                checks.append(k.endswith(suffix))
            if pattern is not None:
                checks.append(fnmatch(k, pattern))
            keep = all(checks) if checks else True

        if keep:
            extracted[k] = v
            matched.append(k)
        else:
            skipped[k] = v

    return ExtractResult(extracted=extracted, skipped=skipped, matched_keys=matched)
