"""CLI sub-command: envdiff profile <file>."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.profiler import profile_env


def build_profile_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Profile a .env file and surface statistics and potential issues."
    if subparsers is not None:
        parser = subparsers.add_parser("profile", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff profile", description=description)

    parser.add_argument("file", help="Path to the .env file to profile")
    parser.add_argument(
        "--show-duplicates",
        action="store_true",
        default=False,
        help="List keys that share the same value",
    )
    parser.add_argument(
        "--show-sensitive",
        action="store_true",
        default=False,
        help="List keys identified as sensitive",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if any issues are found",
    )
    return parser


def run_profile(args: argparse.Namespace) -> int:
    path = Path(args.file)
    try:
        env = parse_env_file(path)
    except (EnvParseError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = profile_env(env)
    print(result.summary())

    if args.show_sensitive and result.sensitive_keys:
        print("\nSensitive keys:")
        for key in sorted(result.sensitive_keys):
            print(f"  {key}")

    if args.show_duplicates and result.duplicate_values:
        print("\nDuplicate values:")
        for val, keys in sorted(result.duplicate_values.items()):
            display_val = val[:40] + "..." if len(val) > 40 else val
            print(f"  {display_val!r}: {', '.join(sorted(keys))}")

    if args.exit_code and (
        result.empty_count > 0
        or result.placeholder_count > 0
        or result.duplicate_values
    ):
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_profile_parser()
    args = parser.parse_args()
    sys.exit(run_profile(args))


if __name__ == "__main__":  # pragma: no cover
    main()
