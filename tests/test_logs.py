"""Logs: kept two weeks, the level from Preferences applied, the viewer fixed-width with a warnings tab.

From JD-Xi Studio 73f9d4ba.
"""

from __future__ import annotations

import logging
import os
import time

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from jdxi_editor.log_files import apply_log_level, prune_logs, saved_level


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_old_logs_are_deleted(tmp_path):
    old, new, other = tmp_path / "a.log", tmp_path / "b.log", tmp_path / "keep.txt"
    for path in (old, new, other):
        path.write_text("x")
    past = time.time() - 15 * 86400
    os.utime(old, (past, past))
    os.utime(other, (past, past))
    assert prune_logs(tmp_path, days=14) == 1
    assert not old.exists() and new.exists() and other.exists()


def test_saved_level(tmp_path):
    settings = QSettings(str(tmp_path / "s.ini"), QSettings.Format.IniFormat)
    assert saved_level(settings) == logging.DEBUG
    settings.setValue("log_level", logging.WARNING)
    assert saved_level(settings) == logging.WARNING
    settings.setValue("log_level", 2)  # the row number older versions saved
    assert saved_level(settings) == logging.DEBUG
    settings.setValue("log_level", "ERROR")
    assert saved_level(settings) == logging.ERROR


def test_apply_level():
    root = logging.getLogger()
    before = root.level
    try:
        apply_log_level(logging.WARNING)
        assert root.level == logging.WARNING
    finally:
        root.setLevel(before)


def test_preferences_save_the_level_not_the_row(app, tmp_path):
    from jdxi_editor.ui.dialogs.settings import UiPreferencesDialog

    root = logging.getLogger()
    before = root.level
    dialog = UiPreferencesDialog(None)
    dialog.settings = QSettings(str(tmp_path / "s.ini"), QSettings.Format.IniFormat)
    dialog.ui_setup(dialog)
    try:
        dialog.log_level_combo.setCurrentIndex(2)  # WARNING
        assert int(dialog.settings.value("log_level")) == logging.WARNING
    finally:
        root.setLevel(before)
        dialog.close()


def test_viewer(app, tmp_path, monkeypatch):
    from jdxi_editor.ui.widgets.viewer.log import LogViewer, needs_attention

    log = tmp_path / "jdxi_editor-13Nov2026-10-00-00.log"
    log.write_text(
        "[10:16:12] INFO     [Queue] ℹ️ No reply\n"
        "[10:16:13] WARNING  [Instr] ⚠️ Odd\n"
        "[10:16:14] ERROR    [Midi] ❌ Broken\n"
        "Traceback line\n"
        "[10:16:15] INFO     [Queue] ℹ️ Fine\n",
        encoding="utf-8",
    )
    kept, _ = needs_attention(log.read_text(encoding="utf-8").splitlines())
    assert len(kept) == 3 and kept[2] == "Traceback line"
    from jdxi_editor.ui.widgets.viewer import log as log_viewer

    monkeypatch.setattr(log_viewer, "resolve_log_file", lambda log_dir=None: log)
    viewer = LogViewer()
    if True:
        assert viewer.log_text.font().fixedPitch()
        text = viewer.log_text.toPlainText()
        assert "No reply" in text and "ℹ" not in text  # the emoji are left out
        assert viewer.attention_text.toPlainText().count("\n") == 2
        assert "(2)" in viewer.tabs.tabText(1)
        with open(log, "a", encoding="utf-8") as f:  # a line written in two pieces
            f.write("[10:16:16] WARNING  [X] ⚠️ half")
        viewer.refresh_log_file()
        assert "half" not in viewer.log_text.toPlainText()
        with open(log, "a", encoding="utf-8") as f:
            f.write(" done\n")
        viewer.refresh_log_file()
        assert viewer.log_text.toPlainText().endswith("half done")
        assert "(3)" in viewer.tabs.tabText(1)
        viewer.clear_log()
        viewer.refresh_log_file()
        assert viewer.log_text.toPlainText() == ""  # cleared lines are not read again
        viewer.close()
