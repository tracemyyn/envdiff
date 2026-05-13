"""CLI sub-command: interpolate — resolve variable references in a .env file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.interpolator import interpolate_env


def build_interpolate_parser(sub=None) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Resolve $VAR / ${VAR} references inside a .env file."
    )
    if sub is not None:
        parser = sub.add_parser("interpolate", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("file", help="Path to the .env file")
    parser.add_argument(
        "--context",
        metavar="FILE",
        help="Optional second .env file whose values are used as extra context",
    )
    parser.add_argument(
        "--show-unresolved",
        action="store_true",
        help="Exit with code 1 if any references remain unresolved",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output; only set exit code",
    )
    return parser


def run_interpolate(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except (EnvParseError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    context = None
    if args.context:
        try:
            context = parse_env_file(args.context)
        except (EnvParseError, OSError) as exc:
            print(f"error loading context: {exc}", file=sys.stderr)
            return 2

    result = interpolate_env(env, context=context)

    if not args.quiet:
        for key, value in result.resolved.items():
            print(f"{key}={value}")
        print(f"\n# {result.summary()}", file=sys.stderr)
        if result.unresolved_keys:
            print(
                "# unresolved: " + ", ".join(result.unresolved_keys),
                file=sys.stderr,
            )

    if args.show_unresolved and result.has_unresolved:
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_interpolate_parser()
    args = parser.parse_args()
    sys.exit(run_interpolate(args))


if __name__ == "__main__":  # pragma: no cover
    main()
