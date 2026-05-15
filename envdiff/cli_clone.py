"""CLI entry-point for the `envdiff clone` sub-command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.cloner import clone_env
from envdiff.parser import parse_env_file, EnvParseError


def build_clone_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(description="Clone a .env file with optional value transformations.")
    parser = parent.add_parser("clone", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("file", help="Source .env file to clone.")
    parser.add_argument("-o", "--output", default="-", help="Output path (default: stdout).")
    parser.add_argument(
        "--redact",
        action="store_true",
        help="Replace sensitive values with a placeholder.",
    )
    parser.add_argument(
        "--blank",
        action="store_true",
        help="Blank all values (useful for sharing template envs).",
    )
    parser.add_argument(
        "--placeholder",
        default="REDACTED",
        metavar="TEXT",
        help="Placeholder text used when --redact is active (default: REDACTED).",
    )
    parser.add_argument(
        "--extra-sensitive",
        nargs="*",
        metavar="KEY",
        help="Additional key names to treat as sensitive.",
    )
    return parser


def run_clone(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except (EnvParseError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = clone_env(
        env,
        redact_sensitive=args.redact,
        blank_all=args.blank,
        placeholder=args.placeholder,
        extra_sensitive=args.extra_sensitive,
    )

    lines = [f"{k}={v}" for k, v in result.cloned.items()]
    output = "\n".join(lines) + ("\n" if lines else "")

    if args.output == "-":
        print(output, end="")
    else:
        Path(args.output).write_text(output)

    print(result.summary(), file=sys.stderr)
    return 0


def main() -> None:  # pragma: no cover
    parser = build_clone_parser()
    sys.exit(run_clone(parser.parse_args()))


if __name__ == "__main__":  # pragma: no cover
    main()
