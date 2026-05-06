"""CLI entry-point for the lint sub-command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from envdiff.linter import lint_env
from envdiff.parser import parse_env_file, EnvParseError


def build_lint_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Lint a .env file for style and quality issues."
    if subparsers is not None:
        parser = subparsers.add_parser("lint", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff lint", description=description)

    parser.add_argument("file", help="Path to the .env file to lint")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any warnings are found (not just errors)",
    )
    parser.add_argument(
        "--no-info",
        dest="no_info",
        action="store_true",
        help="Suppress info-level messages",
    )
    return parser


def run_lint(args: argparse.Namespace) -> int:
    path = Path(args.file)
    try:
        raw_lines: List[str] = path.read_text(encoding="utf-8").splitlines(keepends=True)
        env = parse_env_file(str(path))
    except EnvParseError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"Cannot read file '{path}': {exc}", file=sys.stderr)
        return 2

    result = lint_env(env, raw_lines)

    for issue in result.issues:
        if args.no_info and issue.severity == "info":
            continue
        print(issue)

    print()
    print(result.summary())

    if args.strict and result.has_issues:
        return 1
    if result.error_count > 0:
        return 1
    return 0


def main(argv=None) -> None:
    parser = build_lint_parser()
    args = parser.parse_args(argv)
    sys.exit(run_lint(args))


if __name__ == "__main__":
    main()
