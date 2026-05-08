"""CLI sub-command: normalize a .env file and display or write the result."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.normalizer import normalize_env


def build_normalize_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "normalize",
        help="Normalize a .env file (strip whitespace, remove inline comments).",
    )
    p.add_argument("file", help="Path to the .env file to normalize.")
    p.add_argument(
        "--uppercase-keys",
        action="store_true",
        default=False,
        help="Convert all keys to UPPER_CASE.",
    )
    p.add_argument(
        "--no-strip",
        action="store_true",
        default=False,
        help="Do not strip surrounding whitespace from values.",
    )
    p.add_argument(
        "--no-comments",
        action="store_true",
        default=False,
        help="Do not remove inline comments from values.",
    )
    p.add_argument(
        "--write",
        action="store_true",
        default=False,
        help="Write normalized output back to the file.",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress summary output.",
    )
    return p


def run_normalize(args: argparse.Namespace) -> int:
    path = Path(args.file)

    try:
        env = parse_env_file(str(path))
    except EnvParseError as exc:
        print(f"Error parsing {path}: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError:
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    result = normalize_env(
        env,
        strip_values=not args.no_strip,
        uppercase_keys=args.uppercase_keys,
        remove_inline_comments=not args.no_comments,
    )

    if not args.quiet:
        print(result.summary())

    if args.write:
        lines = [f"{k}={v}\n" for k, v in result.normalized.items()]
        path.write_text("".join(lines))
        if not args.quiet:
            print(f"Written to {path}")
    else:
        for k, v in result.normalized.items():
            print(f"{k}={v}")

    return 0


def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(prog="envdiff-normalize")
    subparsers = parser.add_subparsers(dest="command")
    build_normalize_parser(subparsers)
    args = parser.parse_args()
    sys.exit(run_normalize(args))


if __name__ == "__main__":  # pragma: no cover
    main()
