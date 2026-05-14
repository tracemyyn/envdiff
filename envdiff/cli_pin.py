"""CLI entry point for the pin/drift-check feature."""
from __future__ import annotations

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.pinner import check_drift, load_pin, pin_env, save_pin


def build_pin_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff pin",
        description="Pin env values and detect drift over time.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_save = sub.add_parser("save", help="Pin the current state of an env file.")
    p_save.add_argument("env_file", help="Path to the .env file.")
    p_save.add_argument("pin_file", help="Path to write the pin JSON.")
    p_save.add_argument("--label", default="", help="Optional label for this pin.")

    p_check = sub.add_parser("check", help="Check an env file against a saved pin.")
    p_check.add_argument("env_file", help="Path to the .env file.")
    p_check.add_argument("pin_file", help="Path to the saved pin JSON.")
    p_check.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if drift is detected.",
    )

    return parser


def run_pin(args: argparse.Namespace) -> int:
    if args.command == "save":
        try:
            env = parse_env_file(args.env_file)
        except Exception as exc:  # noqa: BLE001
            print(f"Error reading env file: {exc}", file=sys.stderr)
            return 2
        entries = pin_env(env)
        save_pin(entries, args.pin_file, label=args.label)
        print(f"Pinned {len(entries)} keys to {args.pin_file}")
        return 0

    # command == "check"
    try:
        env = parse_env_file(args.env_file)
    except Exception as exc:  # noqa: BLE001
        print(f"Error reading env file: {exc}", file=sys.stderr)
        return 2

    try:
        pinned = load_pin(args.pin_file)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    result = check_drift(env, pinned)
    print(result.summary())

    if result.drifted:
        print("  Changed:", ", ".join(result.drifted))
    if result.added:
        print("  Added  :", ", ".join(result.added))
    if result.removed:
        print("  Removed:", ", ".join(result.removed))

    if args.exit_code and result.has_drift:
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_pin_parser()
    args = parser.parse_args()
    sys.exit(run_pin(args))


if __name__ == "__main__":  # pragma: no cover
    main()
