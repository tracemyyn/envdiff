"""CLI entry point for the annotate command."""

from __future__ import annotations

import argparse
import sys

from envdiff.annotator import annotate_env
from envdiff.parser import EnvParseError, parse_env_file


def build_annotate_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="envdiff annotate",
        description="Annotate .env keys with inline comments about type, sensitivity, and status.",
    )
    if parent is not None:
        parser = parent.add_parser("annotate", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("file", help="Path to the .env file to annotate.")
    parser.add_argument(
        "--output", "-o", default="-", help="Output file path (default: stdout)."
    )
    parser.add_argument(
        "--only-annotated",
        action="store_true",
        help="Only output lines that received an annotation.",
    )
    return parser


def run_annotate(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except (EnvParseError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = annotate_env(env)

    if args.only_annotated:
        lines = [
            f"{key}={value}  # {comment}"
            for key, (value, comment) in result.annotated.items()
            if comment
        ]
        output = "\n".join(lines)
    else:
        output = result.render()

    if args.output == "-":
        print(output)
    else:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output + "\n")
        print(f"Annotated output written to {args.output}", file=sys.stderr)

    print(result.summary(), file=sys.stderr)
    return 0


def main() -> None:  # pragma: no cover
    parser = build_annotate_parser()
    args = parser.parse_args()
    sys.exit(run_annotate(args))


if __name__ == "__main__":  # pragma: no cover
    main()
