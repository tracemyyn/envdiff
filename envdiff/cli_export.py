"""CLI sub-command: export diff results to a file or stdout."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.comparator import compare_envs
from envdiff.exporter import EXPORT_FORMATS, export
from envdiff.parser import EnvParseError, parse_env_file


def build_export_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="envdiff export",
        description="Export the diff between two .env files to JSON, YAML, or CSV.",
    )
    if parent is not None:
        parser = parent.add_parser("export", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("base", help="Base .env file path")
    parser.add_argument("target", help="Target .env file path")
    parser.add_argument(
        "--format",
        "-f",
        dest="fmt",
        choices=EXPORT_FORMATS,
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout",
    )
    parser.add_argument("--base-name", default="base", help="Label for the base env")
    parser.add_argument("--target-name", default="target", help="Label for the target env")
    return parser


def run_export(args: argparse.Namespace) -> int:
    """Execute the export sub-command.  Returns an exit code."""
    try:
        base_env = parse_env_file(args.base)
        target_env = parse_env_file(args.target)
    except (EnvParseError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = compare_envs(base_env, target_env)

    try:
        output = export(
            result,
            fmt=args.fmt,
            base_name=args.base_name,
            target_name=args.target_name,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Exported to {args.output}")
    else:
        print(output, end="")

    return 0


def main() -> None:  # pragma: no cover
    parser = build_export_parser()
    args = parser.parse_args()
    sys.exit(run_export(args))


if __name__ == "__main__":  # pragma: no cover
    main()
