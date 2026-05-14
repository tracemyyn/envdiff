"""Tag env keys with semantic labels (e.g. database, auth, infra)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

# Mapping from tag name to key-fragment patterns (lowercase)
_TAG_PATTERNS: Dict[str, List[str]] = {
    "database": ["db", "database", "postgres", "mysql", "mongo", "redis", "sqlite"],
    "auth": ["auth", "jwt", "oauth", "token", "secret", "password", "passwd", "api_key"],
    "aws": ["aws", "s3", "ec2", "lambda", "dynamodb", "sqs", "sns"],
    "infra": ["host", "port", "url", "endpoint", "addr", "address"],
    "app": ["app", "debug", "env", "environment", "log", "logging", "version"],
    "email": ["email", "smtp", "mail", "sendgrid", "mailgun"],
}


@dataclass
class TagResult:
    tags: Dict[str, Set[str]] = field(default_factory=dict)   # tag -> set of keys
    key_tags: Dict[str, Set[str]] = field(default_factory=dict)  # key -> set of tags

    @property
    def tag_count(self) -> int:
        return len(self.tags)

    @property
    def tagged_key_count(self) -> int:
        return sum(1 for v in self.key_tags.values() if v)

    def summary(self) -> str:
        if not self.tags:
            return "No tags assigned."
        parts = [f"{tag}({len(keys)})" for tag, keys in sorted(self.tags.items())]
        return "Tags: " + ", ".join(parts)


def _tags_for_key(key: str) -> Set[str]:
    lower = key.lower()
    matched: Set[str] = set()
    for tag, patterns in _TAG_PATTERNS.items():
        for pattern in patterns:
            if pattern in lower:
                matched.add(tag)
                break
    return matched


def tag_env(env: Dict[str, str]) -> TagResult:
    """Assign semantic tags to each key in *env*."""
    result = TagResult()
    for key in env:
        assigned = _tags_for_key(key)
        result.key_tags[key] = assigned
        for tag in assigned:
            result.tags.setdefault(tag, set()).add(key)
    return result
