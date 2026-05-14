"""Encrypt and decrypt sensitive values in a parsed .env dictionary."""
from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_PATTERNS = ("SECRET", "PASSWORD", "PASSWD", "TOKEN", "KEY", "PRIVATE", "CREDENTIAL")


def _is_sensitive(key: str) -> bool:
    upper = key.upper()
    return any(p in upper for p in _SENSITIVE_PATTERNS)


def _derive_key(passphrase: str) -> bytes:
    """Derive a 32-byte key from a passphrase using SHA-256."""
    return hashlib.sha256(passphrase.encode()).digest()


def _xor_encrypt(data: bytes, key: bytes) -> bytes:
    """Simple repeating-XOR cipher (not production-grade; for demo/testing)."""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


@dataclass
class EncryptResult:
    encrypted: Dict[str, str]
    encrypted_keys: List[str] = field(default_factory=list)

    @property
    def encrypt_count(self) -> int:
        return len(self.encrypted_keys)

    @property
    def was_modified(self) -> bool:
        return self.encrypt_count > 0

    def summary(self) -> str:
        if not self.was_modified:
            return "No sensitive values found to encrypt."
        keys = ", ".join(self.encrypted_keys)
        return f"Encrypted {self.encrypt_count} sensitive key(s): {keys}"


def encrypt_env(env: Dict[str, str], passphrase: str) -> EncryptResult:
    """Return a copy of *env* with sensitive values XOR-encrypted + base64-encoded."""
    key = _derive_key(passphrase)
    result: Dict[str, str] = {}
    encrypted_keys: List[str] = []
    for k, v in env.items():
        if _is_sensitive(k) and v:
            cipher = _xor_encrypt(v.encode(), key)
            result[k] = "ENC:" + base64.b64encode(cipher).decode()
            encrypted_keys.append(k)
        else:
            result[k] = v
    return EncryptResult(encrypted=result, encrypted_keys=encrypted_keys)


def decrypt_env(env: Dict[str, str], passphrase: str) -> Dict[str, str]:
    """Return a copy of *env* with ENC:-prefixed values decrypted."""
    key = _derive_key(passphrase)
    result: Dict[str, str] = {}
    for k, v in env.items():
        if v.startswith("ENC:"):
            raw = base64.b64decode(v[4:])
            result[k] = _xor_encrypt(raw, key).decode()
        else:
            result[k] = v
    return result
