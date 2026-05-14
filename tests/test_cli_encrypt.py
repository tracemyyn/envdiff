"""Integration tests for envdiff.cli_encrypt."""
import os
import pytest
from pathlib import Path
from envdiff.cli_encrypt import build_encrypt_parser, run_encrypt


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> str:
    path.write_text(content)
    return str(path)


def _run(args_list):
    parser = build_encrypt_parser()
    args = parser.parse_args(args_list)
    return run_encrypt(args)


def test_build_encrypt_parser_returns_parser():
    p = build_encrypt_parser()
    assert p is not None


def test_encrypt_clean_file_exits_zero(tmp_env):
    f = _write(tmp_env / ".env", "APP_NAME=myapp\nDEBUG=true\n")
    code = _run([f, "--passphrase", "secret"])
    assert code == 0


def test_encrypt_sensitive_file_exits_zero(tmp_env):
    f = _write(tmp_env / ".env", "DB_PASSWORD=hunter2\nAPP=test\n")
    code = _run([f, "--passphrase", "secret"])
    assert code == 0


def test_encrypt_missing_file_exits_two(tmp_env):
    code = _run([str(tmp_env / "missing.env"), "--passphrase", "secret"])
    assert code == 2


def test_encrypt_writes_output_file(tmp_env):
    src = _write(tmp_env / ".env", "DB_PASSWORD=hunter2\nAPP=test\n")
    out = str(tmp_env / "out.env")
    code = _run([src, "--passphrase", "secret", "--output", out])
    assert code == 0
    content = Path(out).read_text()
    assert "ENC:" in content
    assert "APP=test" in content


def test_decrypt_roundtrip(tmp_env):
    src = _write(tmp_env / ".env", "DB_PASSWORD=hunter2\nAPP=test\n")
    enc_out = str(tmp_env / "enc.env")
    dec_out = str(tmp_env / "dec.env")
    _run([src, "--passphrase", "mypass", "--output", enc_out])
    _run([enc_out, "--passphrase", "mypass", "--decrypt", "--output", dec_out])
    content = Path(dec_out).read_text()
    assert "DB_PASSWORD=hunter2" in content


def test_default_mode_is_encrypt(tmp_env):
    parser = build_encrypt_parser()
    args = parser.parse_args([str(tmp_env / "x.env"), "--passphrase", "p"])
    assert args.mode == "encrypt"
