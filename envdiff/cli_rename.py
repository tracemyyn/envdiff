"""CLI entry-point for the *rename* sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from envdiff.parser import parse_env_file
from envdiff.renamer import rename_keys


def build_rename_parser(parent: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    desc = "Rename keys in a .env file using a mapping, prefix, or suffix."
    if parent is not None:
        p = parent.add_parser("rename", help=desc, description=desc)
    else:
        p = argparse.ArgumentParser(prog="envdiff rename", description=desc)

    p.add_argument("file", help="Path to the .env file.")
    p.add_argument(
        "--map",
        metavar="OLD=NEW",
        action="append",
        default=[],
        help="Explicit rename OLD_KEY=NEW_KEY (repeatable).",
    )
    p.add_argument("--prefix", default="", help="Prepend PREFIX to every key.")
    p.add_argument("--suffix", default="", help="Append SUFFIX to every key.")
    p.add_argument("--uppercase", action="store_true", help="Convert keys to UPPERCASE.")
    p.add_argument("--lowercase", action="store_true", help="Convert keys to lowercase.")
    p.add_argument("--json", dest="as_json", action="store_true", help="Output result as JSON.")
    p.add_argument("--quiet", action="store_true", help="Suppress informational output.")
    return p


def run_rename(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    explicit_map = {}
    for item in args.map:
        if "=" not in item:
            print(f"error: invalid --map value {item!r} (expected OLD=NEW)", file=sys.stderr)
            return 2
        old, new = item.split("=", 1)
        explicit_map[old.strip()] = new.strip()

    result = rename_keys(
        env,
        mapping=explicit_map,
        prefix=args.prefix,
        suffix=args.suffix,
        uppercase=args.uppercase,
        lowercase=args.lowercase,
    )

    if args.as_json:
        print(json.dumps({"renamed": result.renamed, "env": result.env, "skipped": result.skipped}, indent=2))
    else:
        for new_key, value in result.env.items():
            print(f"{new_key}={value}")
        if not args.quiet:
            print(f"# {result.summary()}", file=sys.stderr)

    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_rename_parser()
    args = parser.parse_args(argv)
    sys.exit(run_rename(args))


if __name__ == "__main__":  # pragma: no cover
    main()
