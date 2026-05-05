"""Watch .env files for changes and report diffs automatically."""

import time
import os
from typing import Callable, Dict, Optional

from envdiff.parser import parse_env_file
from envdiff.comparator import compare_envs, EnvDiffResult


class EnvWatcher:
    """Watches a pair of .env files and triggers a callback on change."""

    def __init__(
        self,
        base_path: str,
        target_path: str,
        on_change: Callable[[EnvDiffResult], None],
        poll_interval: float = 1.0,
        ignore_values: bool = False,
    ) -> None:
        self.base_path = base_path
        self.target_path = target_path
        self.on_change = on_change
        self.poll_interval = poll_interval
        self.ignore_values = ignore_values
        self._last_mtimes: Dict[str, Optional[float]] = {
            base_path: None,
            target_path: None,
        }

    def _get_mtime(self, path: str) -> Optional[float]:
        try:
            return os.path.getmtime(path)
        except FileNotFoundError:
            return None

    def _files_changed(self) -> bool:
        for path in (self.base_path, self.target_path):
            current = self._get_mtime(path)
            if current != self._last_mtimes[path]:
                self._last_mtimes[path] = current
                return True
        return False

    def check_once(self) -> Optional[EnvDiffResult]:
        """Check for changes once. Returns a diff result if files changed."""
        if self._files_changed():
            base_env = parse_env_file(self.base_path)
            target_env = parse_env_file(self.target_path)
            result = compare_envs(base_env, target_env, ignore_values=self.ignore_values)
            self.on_change(result)
            return result
        return None

    def watch(self, max_iterations: Optional[int] = None) -> None:
        """Block and poll for file changes. Stops after max_iterations if set."""
        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            self.check_once()
            time.sleep(self.poll_interval)
            iteration += 1
