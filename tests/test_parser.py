"""Tests for envdiff.parser module."""

import os
import tempfile
import pytest

from envdiff.parser import parse_env_file, EnvParseError


def write_temp_env(content: str) -> str:
    """Write content to a temporary file and return its path."""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False)
    tmp.write(content)
    tmp.close()
    return tmp.name


def test_parse_basic_key_value():
    path = write_temp_env("DATABASE_URL=postgres://localhost/mydb\nDEBUG=true\n")
    try:
        result = parse_env_file(path)
        assert result == {"DATABASE_URL": "postgres://localhost/mydb", "DEBUG": "true"}
    finally:
        os.unlink(path)


def test_parse_skips_comments_and_blank_lines():
    content = "# This is a comment\n\nAPP_ENV=production\n"
    path = write_temp_env(content)
    try:
        result = parse_env_file(path)
        assert result == {"APP_ENV": "production"}
    finally:
        os.unlink(path)


def test_parse_value_with_equals_sign():
    path = write_temp_env("SECRET_KEY=abc=def==\n")
    try:
        result = parse_env_file(path)
        assert result["SECRET_KEY"] == "abc=def=="
    finally:
        os.unlink(path)


def test_parse_quoted_values():
    path = write_temp_env('GREETING="hello world"\nNAME=\'Alice\'\n')
    try:
        result = parse_env_file(path)
        assert result["GREETING"] == "hello world"
        assert result["NAME"] == "Alice"
    finally:
        os.unlink(path)


def test_parse_empty_value_returns_none():
    path = write_temp_env("EMPTY_KEY=\n")
    try:
        result = parse_env_file(path)
        assert result["EMPTY_KEY"] is None
    finally:
        os.unlink(path)


def test_parse_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_env_file("/nonexistent/path/.env")


def test_parse_invalid_line_raises_error():
    path = write_temp_env("VALID_KEY=value\nINVALID LINE\n")
    try:
        with pytest.raises(EnvParseError, match="Invalid syntax at line 2"):
            parse_env_file(path)
    finally:
        os.unlink(path)


def test_parse_empty_key_raises_error():
    path = write_temp_env("=value_without_key\n")
    try:
        with pytest.raises(EnvParseError, match="Empty key at line 1"):
            parse_env_file(path)
    finally:
        os.unlink(path)
