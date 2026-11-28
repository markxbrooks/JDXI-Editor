"""The main window shows the connection state beside the MIDI lamps."""

import os
import sys
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel

from jdxi_editor.midi.io import connection as conn
from jdxi_editor.ui.windows.jdxi.instrument import JDXiInstrument

_APP = QApplication.instance() or QApplication(sys.argv)


class _StatusBar:
    def __init__(self):
        self.messages = []

    def showMessage(self, text, timeout=0):
        self.messages.append(text)


def _window(ever_online=False):
    status = _StatusBar()
    return SimpleNamespace(
        connection_label=QLabel(),
        connection=SimpleNamespace(ever_online=ever_online),
        statusBar=lambda: status,
        status=status,
    )


def test_online_shows_jdxi_and_says_so():
    window = _window()
    JDXiInstrument._connection_changed(window, conn.ONLINE)
    assert window.connection_label.text() == "JD-Xi"
    assert window.status.messages and "connected" in window.status.messages[0]


def test_offline_at_start_is_quiet_and_after_online_is_said():
    window = _window()
    JDXiInstrument._connection_changed(window, conn.OFFLINE)
    assert window.connection_label.text() == "Offline"
    assert window.status.messages == []
    window = _window(ever_online=True)
    JDXiInstrument._connection_changed(window, conn.OFFLINE)
    assert "stopped answering" in window.status.messages[0]


def test_unstable_asks_for_a_new_reading():
    window = _window()
    JDXiInstrument._connection_changed(window, conn.UNSTABLE)
    assert window.connection_label.text() == "JD-Xi ?"
    assert "read it again" in window.status.messages[0]
