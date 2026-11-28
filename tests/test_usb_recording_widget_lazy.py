"""The USB recorder lists the audio devices when first shown, not while built."""

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from jdxi_editor.midi.playback.state import MidiPlaybackState
from jdxi_editor.ui.widgets.usb.recording import USBFileRecordingWidget

_APP = QApplication.instance() or QApplication(sys.argv)


def test_devices_are_listed_on_first_show(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "jdxi_editor.midi.utils.usb_recorder.USBRecorder.list_input_devices",
        lambda self: calls.append(1) or [("JD-Xi (test)", 3)],
    )
    widget = USBFileRecordingWidget(MidiPlaybackState())
    assert calls == []  # building the editors does not start PortAudio
    widget.show()
    QTest.qWait(20)
    assert calls == [1]
    assert widget.port_select_combo.currentData() == 3
    widget.hide()
    widget.show()
    QTest.qWait(20)
    assert calls == [1]  # listed once; Refresh lists again
    widget.close()
    widget.deleteLater()
