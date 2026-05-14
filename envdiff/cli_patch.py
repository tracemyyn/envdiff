"""CLI entry-point for the *patch* subcommand."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.patcher import apply_patches, parse_patch_line


def build_patch_parser(sub: "argparse._SubParsersAction | None" = None) -> argparse.ArgumentParser:
    desc = "Apply a patch file (SET/DELETE directives) to a .env file."
    if sub is not None:
        p = sub.add_parser("patch", help=desc)
    else:
        p = argparse.ArgumentParser(prog="envdiff patch", description=desc)

    p.add_argument("env_file", help="Path to the source .env file")
    p.add_argument("patch_file", help="Path to the patch directives file")
    p.add_argument(
        "-o", "--output",
        default="-",
        help="Output path (default: stdout)",
    )
    p.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit 1 if any patches were applied, 0 otherwise",
    )
    return p


def run_patch(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.env_file)
    except Exception as exc:  # noqa: BLE001
        print(f"error: cannot read env file: {exc}", file=sys.stderr)
        return 2

    try:
        raw_lines = Path(args.patch_file).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(f"error: cannot read patch file: {exc}", file=sys.stderr)
        return 2

    ops = []
    for lineno, line in enumerate(raw_lines, 1):
        try:
            op = parse_patch_line(line)
        except ValueError as exc:
            print(f"error: patch file line {lineno}: {exc}", file=sys.stderr)
            return 2
        if op is not None:
            ops.append(op)

    result = apply_patches(env, ops)

    lines = [f"{k}={v}" for k, v in result.patched.items()]
    output = "\n".join(lines) + ("\n" if lines else "")

    if args.output == "-":
        print(output, end="")
    else:
        Path(args.output).write_text(output, encoding="utf-8")
        print(result.summary())

    if args.exit_code and result.was_modified:
        return 1
    return 0


def main() -> None:
    parser = build_patch_parser()
    args = parser.parse_args()
    sys.exit(run_patch(args))


if __name__ == "__main__":
    main()
