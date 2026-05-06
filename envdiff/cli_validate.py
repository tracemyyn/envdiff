"""CLI sub-command: validate a .env file against a schema."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.schema_loader import SchemaLoadError, load_schema
from envdiff.validator import validate_env


def build_validate_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "validate",
        help="Validate a .env file against a schema.",
        description="Check that a .env file satisfies required keys, patterns, and allowed values.",
    )
    p.add_argument("env_file", help="Path to the .env file to validate.")
    p.add_argument("schema_file", help="Path to the JSON/YAML schema file.")
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 when validation errors are found.",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress output; only use exit code to signal result.",
    )
    return p


def run_validate(args: argparse.Namespace) -> int:
    """Execute the validate sub-command. Returns the exit code."""
    try:
        env = parse_env_file(args.env_file)
    except Exception as exc:
        print(f"Error reading env file: {exc}", file=sys.stderr)
        return 2

    try:
        schema = load_schema(args.schema_file)
    except SchemaLoadError as exc:
        print(f"Error loading schema: {exc}", file=sys.stderr)
        return 2

    result = validate_env(env, schema)

    if not args.quiet:
        print(result.summary())

    if not result.is_valid and args.exit_code:
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="envdiff-validate")
    subs = parser.add_subparsers(dest="command")
    build_validate_parser(subs)
    parsed = parser.parse_args()
    sys.exit(run_validate(parsed))
