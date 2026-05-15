"""CLI entry-point for the cascade command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.cascader import cascade_envs
from envdiff.parser import parse_env_file, EnvParseError


def build_cascade_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    kwargs = dict(
        prog="envdiff cascade",
        description="Cascade multiple .env files; later files override earlier ones.",
    )
    parser = (
        parent.add_parser("cascade", **kwargs)
        if parent is not None
        else argparse.ArgumentParser(**kwargs)
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Env files in priority order (lowest first).",
    )
    parser.add_argument(
        "--show-overrides",
        action="store_true",
        default=False,
        help="Print each key that was overridden.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress output; use exit code only.",
    )
    return parser


def run_cascade(args: argparse.Namespace) -> int:
    envs = []
    names = []
    for path_str in args.files:
        p = Path(path_str)
        if not p.exists():
            print(f"error: file not found: {path_str}", file=sys.stderr)
            return 2
        try:
            envs.append(parse_env_file(p))
            names.append(p.name)
        except EnvParseError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    result = cascade_envs(envs, names)

    if not args.quiet:
        print(result.summary())
        if args.show_overrides and result.was_overridden:
            print()
            for key, old_val, new_val, fname in result.overrides:
                print(f"  {key}: '{old_val}' -> '{new_val}'  [{fname}]")

    return 0


def main() -> None:  # pragma: no cover
    parser = build_cascade_parser()
    args = parser.parse_args()
    sys.exit(run_cascade(args))


if __name__ == "__main__":  # pragma: no cover
    main()
