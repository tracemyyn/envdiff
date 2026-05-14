"""CLI entry point for the key-rotation checker."""
from __future__ import annotations

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.pinner import load_pin
from envdiff.rotator import check_rotation


def build_rotate_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff rotate",
        description="Check sensitive keys for staleness against a pin file.",
    )
    p.add_argument("env_file", help="Path to the .env file to check.")
    p.add_argument("pin_file", help="Path to the pin JSON file produced by 'envdiff pin'.")
    p.add_argument(
        "--max-age",
        type=int,
        default=90,
        metavar="DAYS",
        help="Maximum allowed age in days for an unchanged sensitive value (default: 90).",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 when rotation issues are found.",
    )
    return p


def run_rotate(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.env_file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error reading env file: {exc}", file=sys.stderr)
        return 2

    try:
        pins = load_pin(args.pin_file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error reading pin file: {exc}", file=sys.stderr)
        return 2

    result = check_rotation(env, pins, max_age_days=args.max_age)

    print(result.summary())
    if result.has_issues:
        for issue in result.issues:
            print(f"  ! {issue}")

    if args.exit_code and result.has_issues:
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_rotate_parser()
    args = parser.parse_args()
    sys.exit(run_rotate(args))


if __name__ == "__main__":  # pragma: no cover
    main()
