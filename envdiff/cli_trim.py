"""CLI entry point for the `envdiff trim` subcommand."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.trimmer import trim_env


def build_trim_parser(subparsers=None) -> argparse.ArgumentParser:
    """Build (or register) the argument parser for the trim command."""
    kwargs = dict(
        description="Trim leading/trailing whitespace from .env values.",
        help="Trim whitespace from env values.",
    )
    if subparsers is not None:
        parser = subparsers.add_parser("trim", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("file", help="Path to the .env file to trim.")
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        help="Write trimmed output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--in-place", "-i",
        action="store_true",
        help="Overwrite the input file with the trimmed result.",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress summary output.",
    )
    return parser


def run_trim(args: argparse.Namespace) -> int:
    """Execute the trim command; return an exit code."""
    try:
        env = parse_env_file(args.file)
    except EnvParseError as exc:
        print(f"envdiff trim: parse error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError:
        print(f"envdiff trim: file not found: {args.file}", file=sys.stderr)
        return 2

    result = trim_env(env)

    lines = [f"{k}={v}" for k, v in result.trimmed.items()]
    output_text = "\n".join(lines) + ("\n" if lines else "")

    if args.in_place:
        Path(args.file).write_text(output_text)
    elif args.output:
        Path(args.output).write_text(output_text)
    else:
        print(output_text, end="")

    if not args.quiet:
        print(result.summary(), file=sys.stderr)

    return 0


def main() -> None:  # pragma: no cover
    parser = build_trim_parser()
    args = parser.parse_args()
    sys.exit(run_trim(args))


if __name__ == "__main__":  # pragma: no cover
    main()
