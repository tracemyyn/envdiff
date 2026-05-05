"""Command-line interface for envdiff."""

import argparse
import sys
from pathlib import Path

from envdiff.comparator import compare_envs
from envdiff.parser import EnvParseError, parse_env_file
from envdiff.reporter import print_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments and flag missing or mismatched keys.",
    )
    parser.add_argument("base", metavar="BASE", help="Path to the base .env file")
    parser.add_argument("target", metavar="TARGET", help="Path to the target .env file")
    parser.add_argument(
        "--ignore-values",
        action="store_true",
        default=False,
        help="Only check for missing keys; ignore value differences",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with a non-zero status code if differences are found",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    """Entry point for the CLI. Returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    base_path = Path(args.base)
    target_path = Path(args.target)

    for path in (base_path, target_path):
        if not path.exists():
            print(f"envdiff: error: file not found: {path}", file=sys.stderr)
            return 2

    try:
        base_env = parse_env_file(base_path)
        target_env = parse_env_file(target_path)
    except EnvParseError as exc:
        print(f"envdiff: parse error: {exc}", file=sys.stderr)
        return 2

    result = compare_envs(
        base_env,
        target_env,
        base_name=str(base_path),
        target_name=str(target_path),
        ignore_values=args.ignore_values,
    )

    print_report(result, use_color=not args.no_color)

    if args.exit_code and result.has_differences():
        return 1
    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
