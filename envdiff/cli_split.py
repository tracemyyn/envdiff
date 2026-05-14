"""CLI entry-point for the `envdiff split` sub-command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.splitter import render_split, split_env


def build_split_parser(parent: "argparse._SubParsersAction | None" = None) -> argparse.ArgumentParser:  # noqa: F821
    kwargs = dict(
        prog="envdiff split",
        description="Split a .env file into multiple files by key prefix.",
    )
    parser = (
        parent.add_parser("split", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    )
    parser.add_argument("file", help="Source .env file to split.")
    parser.add_argument(
        "--prefix",
        dest="prefixes",
        metavar="PREFIX",
        action="append",
        default=None,
        help="Prefix to extract (repeatable). Auto-detected when omitted.",
    )
    parser.add_argument(
        "--separator",
        default="_",
        help="Key separator used to detect prefixes (default: '_').",
    )
    parser.add_argument(
        "--strip-prefix",
        action="store_true",
        help="Remove the prefix from keys in output files.",
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Directory to write split files into (default: current dir).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without creating files.",
    )
    return parser


def run_split(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = split_env(
        env,
        prefixes=args.prefixes,
        separator=args.separator,
        strip_prefix=args.strip_prefix,
    )

    if not result.was_split:
        print("No groups detected — nothing to split.")
        return 0

    out_dir = Path(args.out_dir)
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    for group_name in result.groups:
        out_path = out_dir / f"{group_name.lower()}.env"
        content = render_split(result, group_name)
        if args.dry_run:
            print(f"[dry-run] would write {out_path} ({len(result.groups[group_name])} keys)")
        else:
            out_path.write_text(content)
            print(f"wrote {out_path} ({len(result.groups[group_name])} keys)")

    if result.ungrouped:
        print(f"{len(result.ungrouped)} ungrouped key(s) not written to any file.")

    print(result.summary())
    return 0


def main() -> None:  # pragma: no cover
    parser = build_split_parser()
    sys.exit(run_split(parser.parse_args()))


if __name__ == "__main__":  # pragma: no cover
    main()
