"""Tests for envdiff.watcher module."""

import os
import time
import pytest
from unittest.mock import MagicMock, patch

from envdiff.watcher import EnvWatcher
from envdiff.comparator import EnvDiffResult


@pytest.fixture
def tmp_env_pair(tmp_path):
    base = tmp_path / ".env.base"
    target = tmp_path / ".env.target"
    base.write_text("FOO=bar\nBAZ=qux\n")
    target.write_text("FOO=bar\nBAZ=qux\n")
    return str(base), str(target)


def test_watcher_triggers_callback_on_change(tmp_env_pair):
    base_path, target_path = tmp_env_pair
    callback = MagicMock()
    watcher = EnvWatcher(base_path, target_path, on_change=callback)

    # First check seeds the mtimes and fires callback
    watcher.check_once()
    assert callback.call_count == 1


def test_watcher_no_callback_when_unchanged(tmp_env_pair):
    base_path, target_path = tmp_env_pair
    callback = MagicMock()
    watcher = EnvWatcher(base_path, target_path, on_change=callback)

    watcher.check_once()  # seeds mtimes
    callback.reset_mock()

    watcher.check_once()  # no change
    callback.assert_not_called()


def test_watcher_detects_file_modification(tmp_env_pair):
    base_path, target_path = tmp_env_pair
    callback = MagicMock()
    watcher = EnvWatcher(base_path, target_path, on_change=callback)

    watcher.check_once()  # seed
    callback.reset_mock()

    # Modify target file
    time.sleep(0.05)
    with open(target_path, "w") as f:
        f.write("FOO=changed\n")

    watcher.check_once()
    assert callback.call_count == 1
    result: EnvDiffResult = callback.call_args[0][0]
    assert result.value_mismatches or result.missing_in_target or result.missing_in_base


def test_watcher_callback_receives_diff_result(tmp_env_pair):
    base_path, target_path = tmp_env_pair
    received = []
    watcher = EnvWatcher(base_path, target_path, on_change=received.append)

    watcher.check_once()
    assert len(received) == 1
    assert isinstance(received[0], EnvDiffResult)


def test_watcher_watch_runs_limited_iterations(tmp_env_pair):
    base_path, target_path = tmp_env_pair
    callback = MagicMock()
    watcher = EnvWatcher(
        base_path, target_path, on_change=callback, poll_interval=0.0
    )

    with patch("time.sleep"):
        watcher.watch(max_iterations=3)

    # callback fires once on first iteration (mtime seed), then silent
    assert callback.call_count == 1


def test_watcher_ignore_values_flag(tmp_env_pair):
    base_path, target_path = tmp_env_pair
    with open(target_path, "w") as f:
        f.write("FOO=different\nBAZ=qux\n")

    received = []
    watcher = EnvWatcher(
        base_path, target_path, on_change=received.append, ignore_values=True
    )
    watcher.check_once()

    assert len(received) == 1
    result = received[0]
    assert not result.value_mismatches
