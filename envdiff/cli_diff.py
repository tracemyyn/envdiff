"""CLI sub-command: envdiff diff — show a line-level diff between two .env files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.differ import diff_envs


def build_diff_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the 'diff' sub-command."""
    p = subparsers.add_parser(
        "diff",
        help="Show a line-level diff between two .env files.",
    )
    p.add_argument("base", help="Base .env file path.")
    p.add_argument("target", help="Target .env file path.")
    p.add_argument(
        "--ignore-values",
        action="store_true",
        default=False,
        help="Report only missing keys; ignore value changes.",
    )
    p.add_argument(
        "--only",
        choices=["added", "removed", "changed", "unchanged"],
        default=None,
        help="Limit output to a specific diff kind.",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 when differences are found.",
    )
    return p


def run_diff(args: argparse.Namespace) -> int:
    """Execute the diff sub-command.

    Returns:
        Exit code (0 = no differences or --exit-code not set, 1 = differences found).
    """
    try:
        base_env = parse_env_file(Path(args.base))
        target_env = parse_env_file(Path(args.target))
    except EnvParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    file_diff = diff_envs(base_env, target_env, ignore_values=args.ignore_values)

    diffs = file_diff.diffs
    if args.only:
        diffs = [d for d in diffs if d.kind == args.only]

    if not diffs:
        print("No differences found.")
    else:
        for line_diff in diffs:
            print(line_diff)

    if args.exit_code and file_diff.has_differences():
        return 1
    return 0


def main() -> None:  # pragma: no cover
    """Standalone entry point for the diff sub-command."""
    parser = argparse.ArgumentParser(prog="envdiff-diff")
    subparsers = parser.add_subparsers(dest="command")
    build_diff_parser(subparsers)
    args = parser.parse_args()
    sys.exit(run_diff(args))
