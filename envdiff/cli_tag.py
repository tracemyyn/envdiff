"""CLI entry-point for the `envdiff tag` command."""
from __future__ import annotations

import argparse
import sys

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.tagger import tag_env


def build_tag_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="envdiff tag",
        description="Tag .env keys with semantic labels.",
    )
    parser = parent.add_parser("tag", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("file", help="Path to the .env file to tag")
    parser.add_argument(
        "--tag",
        dest="filter_tag",
        metavar="TAG",
        help="Only show keys for a specific tag (e.g. database, auth)",
    )
    parser.add_argument(
        "--list-tags",
        action="store_true",
        help="List all detected tags and exit",
    )
    return parser


def run_tag(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except (EnvParseError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = tag_env(env)

    if args.list_tags:
        if not result.tags:
            print("No tags detected.")
        else:
            for tag in sorted(result.tags):
                print(tag)
        return 0

    if args.filter_tag:
        keys = result.tags.get(args.filter_tag, set())
        if not keys:
            print(f"No keys matched tag '{args.filter_tag}'.")
            return 0
        for key in sorted(keys):
            print(f"  {key}")
        return 0

    # Default: print all keys with their tags
    print(result.summary())
    for key in sorted(result.key_tags):
        tags = result.key_tags[key]
        tag_str = ", ".join(sorted(tags)) if tags else "(untagged)"
        print(f"  {key}: {tag_str}")
    return 0


def main() -> None:  # pragma: no cover
    parser = build_tag_parser()
    args = parser.parse_args()
    sys.exit(run_tag(args))


if __name__ == "__main__":  # pragma: no cover
    main()
