"""Tests for envdiff.encryptor."""
import pytest
from envdiff.encryptor import (
    EncryptResult,
    _is_sensitive,
    encrypt_env,
    decrypt_env,
)


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "SECRET_TOKEN": "tok_xyz",
    }


def test_is_sensitive_detects_password():
    assert _is_sensitive("DB_PASSWORD") is True


def test_is_sensitive_detects_key():
    assert _is_sensitive("API_KEY") is True


def test_is_sensitive_ignores_normal_key():
    assert _is_sensitive("APP_NAME") is False


def test_encrypt_returns_encrypt_result(sample_env):
    result = encrypt_env(sample_env, "passphrase")
    assert isinstance(result, EncryptResult)


def test_non_sensitive_values_unchanged(sample_env):
    result = encrypt_env(sample_env, "passphrase")
    assert result.encrypted["APP_NAME"] == "myapp"
    assert result.encrypted["DEBUG"] == "true"


def test_sensitive_values_are_encrypted(sample_env):
    result = encrypt_env(sample_env, "passphrase")
    assert result.encrypted["DB_PASSWORD"].startswith("ENC:")
    assert result.encrypted["API_KEY"].startswith("ENC:")
    assert result.encrypted["SECRET_TOKEN"].startswith("ENC:")


def test_encrypt_count_matches_sensitive_keys(sample_env):
    result = encrypt_env(sample_env, "passphrase")
    assert result.encrypt_count == 3


def test_was_modified_true_when_sensitive_keys_present(sample_env):
    result = encrypt_env(sample_env, "passphrase")
    assert result.was_modified is True


def test_was_modified_false_for_clean_env():
    result = encrypt_env({"APP": "val", "DEBUG": "1"}, "passphrase")
    assert result.was_modified is False


def test_roundtrip_encrypt_decrypt(sample_env):
    passphrase = "my-secret-pass"
    encrypted = encrypt_env(sample_env, passphrase).encrypted
    decrypted = decrypt_env(encrypted, passphrase)
    assert decrypted["DB_PASSWORD"] == "s3cr3t"
    assert decrypted["API_KEY"] == "abc123"
    assert decrypted["SECRET_TOKEN"] == "tok_xyz"


def test_wrong_passphrase_gives_wrong_plaintext(sample_env):
    encrypted = encrypt_env(sample_env, "correct").encrypted
    decrypted = decrypt_env(encrypted, "wrong")
    assert decrypted["DB_PASSWORD"] != "s3cr3t"


def test_summary_lists_encrypted_keys(sample_env):
    result = encrypt_env(sample_env, "passphrase")
    summary = result.summary()
    assert "3" in summary or "Encrypted" in summary


def test_empty_sensitive_value_not_encrypted():
    env = {"DB_PASSWORD": ""}
    result = encrypt_env(env, "passphrase")
    assert result.encrypted["DB_PASSWORD"] == ""
    assert result.encrypt_count == 0
