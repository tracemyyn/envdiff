"""Command-line interface for envdiff."""

import argparse
import sys
from typing import Optional, List

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.comparator import compare_envs, has_differences
from envdiff.reporter import print_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments.",
    )
    parser.add_argument("base", help="Base .env file path")
    parser.add_argument("target", help="Target .env file path to compare against base")
    parser.add_argument(
        "--ignore-values",
        action="store_true",
        default=False,
        help="Only check for missing keys; ignore value differences",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences are found",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        default=False,
        help="Watch files for changes and report diffs continuously",
    )
    parser.add_argument(
        "--watch-interval",
        type=float,
        default=1.0,
        metavar="SECONDS",
        help="Polling interval in seconds when using --watch (default: 1.0)",
    )
    return parser


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.watch:
            from envdiff.watcher import EnvWatcher

            def _on_change(result):
                print_report(result, use_color=not args.no_color)

            watcher = EnvWatcher(
                args.base,
                args.target,
                on_change=_on_change,
                poll_interval=args.watch_interval,
                ignore_values=args.ignore_values,
            )
            print(f"Watching {args.base} and {args.target} for changes...")
            watcher.watch()
            return 0

        base_env = parse_env_file(args.base)
        target_env = parse_env_file(args.target)
    except EnvParseError as exc:
        print(f"envdiff: parse error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"envdiff: file not found: {exc}", file=sys.stderr)
        return 2

    result = compare_envs(base_env, target_env, ignore_values=args.ignore_values)
    print_report(result, use_color=not args.no_color)

    if args.exit_code and has_differences(result):
        return 1
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
