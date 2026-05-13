"""CLI entry-point for the mask command."""
from __future__ import annotations

import argparse
import sys

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.masker import mask_env


def build_mask_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(description="Mask sensitive values in a .env file.")
    parser = (
        parent.add_parser("mask", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    )
    parser.add_argument("file", help="Path to the .env file")
    parser.add_argument(
        "--visible",
        type=int,
        default=4,
        metavar="N",
        help="Number of leading characters to keep visible (default: 4)",
    )
    parser.add_argument(
        "--extra-patterns",
        nargs="*",
        metavar="PATTERN",
        help="Additional key patterns to treat as sensitive",
    )
    parser.add_argument(
        "--show-keys",
        action="store_true",
        help="Print the list of masked keys",
    )
    return parser


def run_mask(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except (EnvParseError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = mask_env(
        env,
        visible_chars=args.visible,
        extra_patterns=args.extra_patterns or [],
    )

    for key, value in result.masked.items():
        print(f"{key}={value}")

    if args.show_keys:
        print(f"\n# {result.summary()}", file=sys.stderr)

    return 0


def main() -> None:  # pragma: no cover
    parser = build_mask_parser()
    args = parser.parse_args()
    sys.exit(run_mask(args))


if __name__ == "__main__":  # pragma: no cover
    main()
