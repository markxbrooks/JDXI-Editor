"""
The session logs: one file per start, kept for LOG_KEEP_DAYS days, and the
level chosen in Preferences.

From JD-Xi Studio 73f9d4ba.
"""

from __future__ import annotations

import time
from pathlib import Path

from jdxi_editor.project import __package_name__

LOG_KEEP_DAYS = 14


def log_dir(home: Path | None = None) -> Path:
    """Directory Decologr writes the log files to."""
    return (home or Path.home()) / f".{__package_name__}" / "logs"


def prune_logs(
    folder: Path | None = None, days: int = LOG_KEEP_DAYS, now: float | None = None
) -> int:
    """Delete the session logs older than *days* days; returns how many were deleted."""
    folder = folder or log_dir()
    limit = (now if now is not None else time.time()) - days * 86400
    deleted = 0
    try:
        files = list(folder.glob("*.log*"))
    except OSError:
        return 0
    for path in files:
        try:
            if path.is_file() and path.stat().st_mtime < limit:
                path.unlink()
                deleted += 1
        except OSError:
            pass  # in use (another running copy) or not ours to delete: left
    return deleted


LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}


def saved_level(settings) -> int:
    """The level in Preferences (a number; a name is read too; anything else -> DEBUG)."""
    value = settings.value("log_level", LEVELS["DEBUG"])
    try:
        level = int(str(value))
    except ValueError:
        level = LEVELS.get(str(value).upper(), LEVELS["DEBUG"])
    return level if level in LEVELS.values() else LEVELS["DEBUG"]


def apply_log_level(level: int, *loggers) -> None:
    """Write only the lines from *level* up (the program's loggers, the root and their handlers)."""
    import logging

    targets = {logging.getLogger(), logging.getLogger(__package_name__)}
    targets.update(lg for lg in loggers if isinstance(lg, logging.Logger))
    for logger in targets:
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)
