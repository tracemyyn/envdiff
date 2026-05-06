"""CLI sub-commands for snapshot management: ``save`` and ``compare``."""

from __future__ import annotations

import argparse
import sys

from envdiff.comparator import compare_envs, has_differences
from envdiff.parser import parse_env_file
from envdiff.reporter import format_report
from envdiff.snapshotter import SnapshotError, load_snapshot, save_snapshot, snapshot_metadata


def build_snapshot_parser(parent: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register 'snapshot' sub-commands onto *parent*."""
    snap_parser = parent.add_parser("snapshot", help="Save or compare .env snapshots")
    sub = snap_parser.add_subparsers(dest="snap_cmd", required=True)

    # --- save ---
    save_p = sub.add_parser("save", help="Save a snapshot of an .env file")
    save_p.add_argument("env_file", help="Path to the .env file to snapshot")
    save_p.add_argument("snapshot", help="Destination snapshot file (.json)")
    save_p.add_argument("--label", default="", help="Optional label for this snapshot")

    # --- compare ---
    cmp_p = sub.add_parser("compare", help="Compare a snapshot against a live .env file")
    cmp_p.add_argument("snapshot", help="Snapshot file to use as base")
    cmp_p.add_argument("env_file", help="Live .env file to compare against")
    cmp_p.add_argument("--no-color", action="store_true", help="Disable colored output")
    cmp_p.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 when differences are found",
    )
    cmp_p.add_argument("--ignore-values", action="store_true", help="Only compare keys")


def run_snapshot(args: argparse.Namespace) -> int:
    """Dispatch to the correct snapshot sub-command. Returns exit code."""
    if args.snap_cmd == "save":
        return _cmd_save(args)
    if args.snap_cmd == "compare":
        return _cmd_compare(args)
    return 1


def _cmd_save(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.env_file)
        save_snapshot(env, args.snapshot, label=args.label or None)
        print(f"Snapshot saved to '{args.snapshot}'")
        return 0
    except (OSError, SnapshotError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _cmd_compare(args: argparse.Namespace) -> int:
    try:
        meta = snapshot_metadata(args.snapshot)
        base_env = load_snapshot(args.snapshot)
        target_env = parse_env_file(args.env_file)
    except (OSError, SnapshotError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = compare_envs(
        base_env,
        target_env,
        base_name=f"snapshot({meta['label'] or args.snapshot})",
        target_name=args.env_file,
        ignore_values=args.ignore_values,
    )

    color = not args.no_color
    print(format_report(result, color=color))

    if args.exit_code and has_differences(result):
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(prog="envdiff-snapshot")
    sub = parser.add_subparsers(dest="snap_cmd", required=True)
    _register_directly(sub)
    args = parser.parse_args()
    sys.exit(run_snapshot(args))


def _register_directly(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register save/compare directly (used by standalone entry point)."""
    save_p = sub.add_parser("save")
    save_p.add_argument("env_file")
    save_p.add_argument("snapshot")
    save_p.add_argument("--label", default="")

    cmp_p = sub.add_parser("compare")
    cmp_p.add_argument("snapshot")
    cmp_p.add_argument("env_file")
    cmp_p.add_argument("--no-color", action="store_true")
    cmp_p.add_argument("--exit-code", action="store_true")
    cmp_p.add_argument("--ignore-values", action="store_true")
