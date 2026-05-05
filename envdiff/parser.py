"""Parser for .env files.

Handles reading and parsing .env files into key-value dictionaries,
skipping comments and blank lines.
"""

import os
from typing import Dict, Optional


class EnvParseError(Exception):
    """Raised when a .env file cannot be parsed."""
    pass


def parse_env_file(filepath: str) -> Dict[str, Optional[str]]:
    """Parse a .env file and return a dict of key-value pairs.

    Args:
        filepath: Path to the .env file.

    Returns:
        A dictionary mapping environment variable names to their values.
        Values may be None if a key is defined without a value.

    Raises:
        FileNotFoundError: If the file does not exist.
        EnvParseError: If a line cannot be parsed.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    env_vars: Dict[str, Optional[str]] = {}

    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, raw_line in enumerate(f, start=1):
            line = raw_line.strip()

            # Skip blank lines and comments
            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                raise EnvParseError(
                    f"Invalid syntax at line {lineno} in '{filepath}': {raw_line.rstrip()!r}"
                )

            key, _, value = line.partition("=")
            key = key.strip()

            if not key:
                raise EnvParseError(
                    f"Empty key at line {lineno} in '{filepath}': {raw_line.rstrip()!r}"
                )

            # Strip optional surrounding quotes from value
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]

            env_vars[key] = value if value else None

    return env_vars
