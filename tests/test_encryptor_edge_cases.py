"""Edge-case tests for envdiff.encryptor."""
import pytest
from envdiff.encryptor import encrypt_env, decrypt_env, _derive_key, _xor_encrypt


def test_empty_env_returns_empty_encrypted():
    result = encrypt_env({}, "pass")
    assert result.encrypted == {}
    assert result.encrypt_count == 0


def test_all_non_sensitive_keys_unchanged():
    env = {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}
    result = encrypt_env(env, "pass")
    assert result.encrypted == env


def test_encrypted_value_differs_from_original():
    env = {"API_KEY": "plaintext"}
    result = encrypt_env(env, "pass")
    assert result.encrypted["API_KEY"] != "plaintext"


def test_different_passphrases_produce_different_ciphertext():
    env = {"SECRET": "value"}
    r1 = encrypt_env(env, "pass1").encrypted["SECRET"]
    r2 = encrypt_env(env, "pass2").encrypted["SECRET"]
    assert r1 != r2


def test_encrypt_is_deterministic():
    env = {"TOKEN": "abc"}
    r1 = encrypt_env(env, "pass").encrypted["TOKEN"]
    r2 = encrypt_env(env, "pass").encrypted["TOKEN"]
    assert r1 == r2


def test_decrypt_non_enc_value_unchanged():
    env = {"APP": "value", "TOKEN": "plaintext"}
    result = decrypt_env(env, "pass")
    assert result["APP"] == "value"
    assert result["TOKEN"] == "plaintext"


def test_xor_encrypt_roundtrip():
    key = _derive_key("testkey")
    data = b"hello world"
    assert _xor_encrypt(_xor_encrypt(data, key), key) == data


def test_encrypted_keys_list_contains_correct_names():
    env = {"API_KEY": "k", "DB_PASSWORD": "p", "HOST": "h"}
    result = encrypt_env(env, "pass")
    assert set(result.encrypted_keys) == {"API_KEY", "DB_PASSWORD"}


def test_summary_no_encryption_message():
    result = encrypt_env({"HOST": "localhost"}, "pass")
    assert "No sensitive" in result.summary()
