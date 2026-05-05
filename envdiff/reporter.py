"""Formats and outputs EnvDiffResult reports to stdout or a stream."""

import sys
from io import StringIO
from typing import List, Optional, TextIO

from envdiff.comparator import EnvDiffResult


ANSI_RED = "\033[31m"
ANSI_YELLOW = "\033[33m"
ANSI_GREEN = "\033[32m"
ANSI_RESET = "\033[0m"


def _colorize(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def format_report(
    results: List[EnvDiffResult],
    use_color: bool = True,
    show_values: bool = False,
) -> str:
    """Render a list of EnvDiffResult objects into a human-readable report string.

    Args:
        results: List of comparison results to include in the report.
        use_color: Whether to include ANSI color codes in output.
        show_values: Whether to display actual values for mismatches.

    Returns:
        Formatted report as a string.
    """
    buf = StringIO()

    for result in results:
        buf.write(f"=== {result.base_name} vs {result.target_name} ===\n")

        if not result.has_differences:
            buf.write(_colorize("  ✓ No differences found.\n", ANSI_GREEN, use_color))
            continue

        if result.missing_in_target:
            label = _colorize("  MISSING in target:", ANSI_RED, use_color)
            buf.write(label + f" ({result.target_name})\n")
            for key in sorted(result.missing_in_target):
                buf.write(f"    - {key}\n")

        if result.missing_in_base:
            label = _colorize("  EXTRA in target:", ANSI_YELLOW, use_color)
            buf.write(label + f" ({result.target_name})\n")
            for key in sorted(result.missing_in_base):
                buf.write(f"    + {key}\n")

        if result.mismatched_keys:
            label = _colorize("  MISMATCHED values:", ANSI_YELLOW, use_color)
            buf.write(label + "\n")
            for key in sorted(result.mismatched_keys):
                if show_values:
                    base_v = result.mismatched_keys[key]["base"]
                    tgt_v = result.mismatched_keys[key]["target"]
                    buf.write(f"    ~ {key}: '{base_v}' → '{tgt_v}'\n")
                else:
                    buf.write(f"    ~ {key}\n")

    return buf.getvalue()


def print_report(
    results: List[EnvDiffResult],
    stream: Optional[TextIO] = None,
    use_color: bool = True,
    show_values: bool = False,
) -> None:
    """Print a formatted report to the given stream (default: stdout)."""
    if stream is None:
        stream = sys.stdout
    report = format_report(results, use_color=use_color, show_values=show_values)
    stream.write(report)
