"""CLI entry point for the `envdiff group` command."""
from __future__ import annotations
import argparse
import sys
from envdiff.parser import parse_env_file, EnvParseError
from envdiff.grouper import group_env, top_prefixes


def build_group_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    description = "Group .env keys by prefix and display a summary."
    if parent is not None:
        parser = parent.add_parser("group", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff-group", description=description)

    parser.add_argument("file", help="Path to the .env file")
    parser.add_argument(
        "--separator",
        default="_",
        help="Key prefix separator (default: '_')",
    )
    parser.add_argument(
        "--min-prefix",
        type=int,
        default=2,
        dest="min_prefix",
        help="Minimum prefix length to be considered a group (default: 2)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        help="Show only the top N prefixes by key count",
    )
    return parser


def _print_top_prefixes(result, top: int) -> None:
    """Print the top N prefixes sorted by key count."""
    prefixes = top_prefixes(result, n=top)
    print(f"Top {top} prefixes by key count:")
    for p in prefixes:
        print(f"  {p}: {len(result.groups[p])} key(s)")


def run_group(args: argparse.Namespace) -> int:
    """Execute the group command with the parsed arguments.

    Returns an exit code: 0 on success, 2 on error.
    """
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError as exc:
        print(f"Error: File not found: {exc}", file=sys.stderr)
        return 2
    except EnvParseError as exc:
        print(f"Error: Failed to parse env file: {exc}", file=sys.stderr)
        return 2

    result = group_env(env, separator=args.separator, min_prefix_length=args.min_prefix)

    if args.top > 0:
        _print_top_prefixes(result, args.top)
    else:
        print(result.summary())

    return 0


def main() -> None:
    parser = build_group_parser()
    args = parser.parse_args()
    sys.exit(run_group(args))


if __name__ == "__main__":
    main()
