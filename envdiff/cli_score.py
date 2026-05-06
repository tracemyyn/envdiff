"""CLI entry point for the `envdiff score` command."""

import argparse
import sys

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.linter import lint_env
from envdiff.auditor import audit_env
from envdiff.profiler import profile_env
from envdiff.scorer import score_env


def build_score_parser(parent: argparse._SubParsersAction = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(description="Score an .env file for overall health.")
    if parent is not None:
        parser = parent.add_parser("score", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="envdiff-score", **kwargs)
    parser.add_argument("envfile", help="Path to the .env file to score")
    parser.add_argument(
        "--min-score",
        type=int,
        default=0,
        metavar="N",
        help="Exit with code 1 if score is below N (default: 0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )
    return parser


def run_score(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.envfile)
    except (EnvParseError, OSError) as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 2

    lint = lint_env(env)
    audit = audit_env(env)
    profile = profile_env(env)
    result = score_env(lint, audit, profile)

    if getattr(args, "json", False):
        import json
        print(json.dumps({
            "score": result.score,
            "max_score": result.max_score,
            "grade": result.grade,
            "penalties": result.penalties,
        }))
    else:
        print(result.summary())

    if result.score < args.min_score:
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_score_parser()
    args = parser.parse_args()
    sys.exit(run_score(args))


if __name__ == "__main__":  # pragma: no cover
    main()
