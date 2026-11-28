"""The log viewer finds the file Decologr is actually writing to."""

from __future__ import annotations

import logging
import os
import time
from logging.handlers import RotatingFileHandler

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from jdxi_editor.ui.widgets.viewer import log as log_viewer  # noqa: E402
from jdxi_editor.ui.widgets.viewer.log import LogViewer, resolve_log_file  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def bare_root_logger():
    """Root logger with no handlers, so only the directory search is tested."""
    root = logging.getLogger()
    saved = root.handlers[:]
    root.handlers = []
    yield root
    root.handlers = saved


def write(path, text="entry\n"):
    path.write_text(text, encoding="utf-8")
    return path


def test_the_installed_handlers_file_is_used(tmp_path, bare_root_logger):
    # Only the handler knows the name of this run's file.
    handler_file = tmp_path / "jdxi_editor-01Feb2026-10-32-09.log"
    handler = RotatingFileHandler(handler_file, encoding="utf-8")
    bare_root_logger.addHandler(handler)
    try:
        # a different, newer file on disk must not win over the handler
        write(tmp_path / "jdxi_editor-02Feb2026-10-32-09.log")
        assert resolve_log_file(tmp_path) == handler_file
    finally:
        bare_root_logger.removeHandler(handler)
        handler.close()


def test_newest_file_is_used_when_no_handler_is_installed(tmp_path, bare_root_logger):
    older = write(tmp_path / "jdxi_editor-01Feb2026-10-00-00.log")
    newer = write(tmp_path / "jdxi_editor-01Feb2026-12-00-00.log")
    os.utime(older, (time.time() - 60, time.time() - 60))
    assert resolve_log_file(tmp_path) == newer


def test_a_rotated_backup_does_not_win_over_the_live_file(tmp_path, bare_root_logger):
    # Rotation renames the live file to ".log.1" and opens a new ".log", so the
    # backup can be the newer of the two while being the wrong one to read.
    live = write(tmp_path / "jdxi_editor-01Feb2026-10-00-00.log")
    backup = write(tmp_path / "jdxi_editor-01Feb2026-10-00-00.log.1")
    os.utime(live, (time.time() - 60, time.time() - 60))
    assert backup.stat().st_mtime > live.stat().st_mtime
    assert resolve_log_file(tmp_path) == live


def test_a_backup_is_used_when_there_is_no_live_file(tmp_path, bare_root_logger):
    backup = write(tmp_path / "jdxi_editor-01Feb2026-10-00-00.log.2")
    assert resolve_log_file(tmp_path) == backup


def test_no_log_file_at_all(tmp_path, bare_root_logger):
    assert resolve_log_file(tmp_path) is None
    assert resolve_log_file(tmp_path / "does-not-exist") is None


def test_viewer_shows_the_log_contents(qapp, tmp_path, monkeypatch):
    log_file = write(tmp_path / "jdxi_editor-01Feb2026-10-00-00.log", "hello log\n")
    monkeypatch.setattr(log_viewer, "resolve_log_file", lambda *args: log_file)

    viewer = LogViewer()
    try:
        assert "hello log" in viewer.log_text.toPlainText()
        assert log_file.name in viewer.windowTitle()
    finally:
        viewer.close()


def test_viewer_explains_itself_when_there_is_no_log_file(qapp, monkeypatch):
    monkeypatch.setattr(log_viewer, "resolve_log_file", lambda *args: None)

    viewer = LogViewer()
    try:
        text = viewer.log_text.toPlainText()
        assert "No log file found." in text
        assert "Log directory:" in text
    finally:
        viewer.close()


def test_viewer_appends_new_entries(qapp, tmp_path, monkeypatch):
    log_file = write(tmp_path / "jdxi_editor-01Feb2026-10-00-00.log", "first\n")
    monkeypatch.setattr(log_viewer, "resolve_log_file", lambda *args: log_file)

    viewer = LogViewer()
    try:
        with open(log_file, "a", encoding="utf-8") as handle:
            handle.write("second\n")
        viewer.refresh_log_file()
        text = viewer.log_text.toPlainText()
        assert "first" in text and "second" in text
        assert text.count("first") == 1
    finally:
        viewer.close()


def test_viewer_follows_the_file_across_rotation(qapp, tmp_path, monkeypatch):
    log_file = write(tmp_path / "jdxi_editor-01Feb2026-10-00-00.log", "a" * 500 + "\n")
    monkeypatch.setattr(log_viewer, "resolve_log_file", lambda *args: log_file)

    viewer = LogViewer()
    try:
        # rotation: the long file is moved aside and a shorter one takes its place
        log_file.rename(tmp_path / "jdxi_editor-01Feb2026-10-00-00.log.1")
        write(log_file, "after rotation\n")
        viewer.refresh_log_file()
        assert "after rotation" in viewer.log_text.toPlainText()
    finally:
        viewer.close()


def test_multibyte_entries_are_not_split(qapp, tmp_path, monkeypatch):
    # The logs are full of emoji; a character count used as a byte offset would
    # resume mid-character and lose or repeat output.
    log_file = write(tmp_path / "jdxi_editor-01Feb2026-10-00-00.log", "ℹ️ start\n")
    monkeypatch.setattr(log_viewer, "resolve_log_file", lambda *args: log_file)

    viewer = LogViewer()
    try:
        with open(log_file, "a", encoding="utf-8") as handle:
            handle.write("⚠️ next\n")
        viewer.refresh_log_file()
        text = viewer.log_text.toPlainText()
        # the emoji are left out of the view; each line appears once, whole
        assert text.splitlines() == ["start", "next"]
    finally:
        viewer.close()
