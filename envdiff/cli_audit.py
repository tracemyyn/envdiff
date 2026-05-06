"""CLI sub-command: audit a single .env file for common issues."""

from __future__ import annotations

import argparse
import sys

from envdiff.auditor import audit_env
from envdiff.parser import parse_env_file, EnvParseError


def build_audit_parser(subparsers=None) -> argparse.ArgumentParser:
    description = "Audit a .env file for security and quality issues."
    if subparsers is not None:
        parser = subparsers.add_parser("audit", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff audit", description=description)

    parser.add_argument("file", help="Path to the .env file to audit.")
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if any errors are found.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any issues (including warnings) are found.",
    )
    return parser


def run_audit(args: argparse.Namespace) -> int:
    """Execute the audit command. Returns the exit code."""
    try:
        env = parse_env_file(args.file)
    except EnvParseError as exc:
        print(f"Error parsing file: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        return 2

    result = audit_env(env)

    if not result.has_issues:
        print(f"✔  {args.file}: {result.summary()}")
        return 0

    print(f"Audit results for: {args.file}")
    print(f"  {result.summary()}")
    print()
    for issue in result.issues:
        icon = "✖" if issue.severity == "error" else "⚠"
        print(f"  {icon}  {issue}")

    if args.strict and result.has_issues:
        return 1
    if args.exit_code and result.error_count > 0:
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_audit_parser()
    args = parser.parse_args()
    sys.exit(run_audit(args))


if __name__ == "__main__":  # pragma: no cover
    main()
