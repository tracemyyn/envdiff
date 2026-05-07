"""CLI entry-point for the *summarize* sub-command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.summarizer import summarize_env


def build_summarize_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="envdiff summarize",
        description="Print a statistical summary of a .env file.",
    )
    if parent is not None:
        parser = parent.add_parser("summarize", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument("file", help="Path to the .env file to summarise.")
    parser.add_argument(
        "--long-threshold",
        type=int,
        default=128,
        metavar="N",
        help="Number of characters above which a value is considered long (default: 128).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output summary as JSON.",
    )
    return parser


def run_summarize(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    try:
        env = parse_env_file(path)
    except EnvParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = summarize_env(env, long_value_threshold=args.long_threshold)

    if args.json:
        import json
        data = {
            "total": result.total,
            "empty_keys": result.empty_keys,
            "placeholder_keys": result.placeholder_keys,
            "sensitive_keys": result.sensitive_keys,
            "long_value_keys": result.long_value_keys,
        }
        print(json.dumps(data, indent=2))
    else:
        print(result.summary())

    return 0


def main() -> None:  # pragma: no cover
    parser = build_summarize_parser()
    args = parser.parse_args()
    sys.exit(run_summarize(args))


if __name__ == "__main__":  # pragma: no cover
    main()
