"""CLI entry point for the `envdiff template` command."""

from __future__ import annotations

import argparse
import sys

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.templater import build_template, write_template


def build_template_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Generate a .env.example template from an existing .env file."
    if subparsers is not None:
        parser = subparsers.add_parser("template", description=description, help=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff template", description=description)

    parser.add_argument("env_file", help="Source .env file to template.")
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Write template to this file (default: print to stdout).",
    )
    parser.add_argument(
        "--keep",
        nargs="*",
        metavar="KEY",
        default=[],
        help="Keys whose values should be preserved verbatim.",
    )
    parser.add_argument(
        "--no-sensitive-placeholder",
        action="store_true",
        default=False,
        help="Blank sensitive keys instead of inserting a descriptive placeholder.",
    )
    return parser


def run_template(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.env_file)
    except (EnvParseError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = build_template(
        env,
        keep_values=args.keep,
        sensitive_placeholder=not args.no_sensitive_placeholder,
    )

    if args.output:
        write_template(result, args.output)
        print(
            f"Template written to {args.output} "
            f"({result.total_keys} keys, "
            f"{len(result.redacted_keys)} redacted, "
            f"{len(result.blanked_keys)} blanked)."
        )
    else:
        print(result.render(), end="")

    return 0


def main() -> None:  # pragma: no cover
    parser = build_template_parser()
    args = parser.parse_args()
    sys.exit(run_template(args))


if __name__ == "__main__":  # pragma: no cover
    main()
