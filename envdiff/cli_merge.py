"""CLI sub-command: ``envdiff merge`` – merge multiple .env files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from envdiff.merger import merge_envs, render_merged
from envdiff.parser import EnvParseError, parse_env_file


def build_merge_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    """Register the *merge* sub-command onto *subparsers*."""
    p = subparsers.add_parser(
        "merge",
        help="Merge multiple .env files into one, flagging conflicts.",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to merge (in priority order).",
    )
    p.add_argument(
        "--strategy",
        choices=("first", "last"),
        default="first",
        help="Conflict-resolution strategy (default: first).",
    )
    p.add_argument(
        "--output", "-o",
        metavar="FILE",
        default=None,
        help="Write merged output to FILE instead of stdout.",
    )
    p.add_argument(
        "--no-comments",
        action="store_true",
        default=False,
        help="Omit conflict comments from the merged output.",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 when conflicts are found.",
    )
    p.set_defaults(func=run_merge)
    return p


def run_merge(args: argparse.Namespace) -> int:
    """Execute the merge sub-command; returns the process exit code."""
    envs = []
    for path_str in args.files:
        path = Path(path_str)
        try:
            mapping = parse_env_file(path)
        except EnvParseError as exc:
            print(f"envdiff merge: parse error in {path_str}: {exc}", file=sys.stderr)
            return 2
        except OSError as exc:
            print(f"envdiff merge: cannot read {path_str}: {exc}", file=sys.stderr)
            return 2
        envs.append((path_str, mapping))

    result = merge_envs(envs, strategy=args.strategy)
    text = render_merged(result, comment_conflicts=not args.no_comments)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)

    if result.has_conflicts:
        print(
            f"envdiff merge: {result.conflict_count()} conflict(s) found.",
            file=sys.stderr,
        )
        if args.exit_code:
            return 1

    return 0
