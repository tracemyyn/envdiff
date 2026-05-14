"""CLI entry point for the diff-summary command."""
from __future__ import annotations

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.differ import diff_envs
from envdiff.differ_summary import summarize_diff


def build_differ_summary_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff diff-summary",
        description="Show a concise summary of differences between two .env files.",
    )
    parser.add_argument("base", help="Base .env file")
    parser.add_argument("target", help="Target .env file")
    parser.add_argument(
        "--base-name",
        default="base",
        help="Label for the base file (default: base)",
    )
    parser.add_argument(
        "--target-name",
        default="target",
        help="Label for the target file (default: target)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 when differences are found.",
    )
    return parser


def run_differ_summary(args: argparse.Namespace) -> int:
    try:
        base_env = parse_env_file(args.base)
        target_env = parse_env_file(args.target)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    file_diff = diff_envs(base_env, target_env)
    result = summarize_diff(file_diff, base_name=args.base_name, target_name=args.target_name)

    print(f"Comparing {args.base_name!r} vs {args.target_name!r}")
    print(result.summary())
    for line in result.lines:
        print(line)

    if args.exit_code and not result.is_clean():
        return 1
    return 0


def main() -> None:
    parser = build_differ_summary_parser()
    args = parser.parse_args()
    sys.exit(run_differ_summary(args))


if __name__ == "__main__":
    main()
