"""CLI entry-point for encrypting/decrypting sensitive .env values."""
from __future__ import annotations

import argparse
import sys

from envdiff.encryptor import decrypt_env, encrypt_env
from envdiff.parser import EnvParseError, parse_env_file


def build_encrypt_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    desc = "Encrypt or decrypt sensitive values in a .env file."
    if parent is not None:
        p = parent.add_parser("encrypt", help=desc)
    else:
        p = argparse.ArgumentParser(prog="envdiff-encrypt", description=desc)
    p.add_argument("file", help="Path to the .env file")
    p.add_argument("--passphrase", required=True, help="Passphrase used for encryption/decryption")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--encrypt", dest="mode", action="store_const", const="encrypt",
                      help="Encrypt sensitive values (default)")
    mode.add_argument("--decrypt", dest="mode", action="store_const", const="decrypt",
                      help="Decrypt ENC:-prefixed values")
    p.set_defaults(mode="encrypt")
    p.add_argument("--output", "-o", default=None, help="Write result to this file (default: stdout)")
    return p


def run_encrypt(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except (EnvParseError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.mode == "decrypt":
        result_env = decrypt_env(env, args.passphrase)
        lines = [f"{k}={v}" for k, v in result_env.items()]
        output = "\n".join(lines) + "\n"
        _write_output(output, args.output)
        return 0

    # encrypt mode
    result = encrypt_env(env, args.passphrase)
    lines = [f"{k}={v}" for k, v in result.encrypted.items()]
    output = "\n".join(lines) + "\n"
    _write_output(output, args.output)
    print(result.summary(), file=sys.stderr)
    return 0


def _write_output(text: str, path: str | None) -> None:
    if path:
        with open(path, "w") as fh:
            fh.write(text)
    else:
        print(text, end="")


def main() -> None:  # pragma: no cover
    parser = build_encrypt_parser()
    args = parser.parse_args()
    sys.exit(run_encrypt(args))


if __name__ == "__main__":  # pragma: no cover
    main()
