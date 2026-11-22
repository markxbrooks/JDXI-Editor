#!/usr/bin/env python3
"""
USB recording threads survive being replaced by the next recording (a
playlist's next song starting during the previous one's 10 s tail): deleting
a running QThread aborts the application.
"""

import gc
import os
import threading
from types import SimpleNamespace
from unittest.mock import patch

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QTest

from jdxi_editor.midi.recording.recording_thread import WavRecordingThread
from jdxi_editor.midi.utils import helpers


@pytest.fixture(scope="module")
def app():
    return QCoreApplication.instance() or QCoreApplication([])


def _fake_record(self):
    """Record until stopped (or ~2 s), then report the file once."""
    self.running = True
    for _ in range(200):
        if not self.running:
            break
        threading.Event().wait(0.01)
    self.recording_finished.emit(self.output_file)


def _wait_until(condition, timeout_ms=3000):
    for _ in range(timeout_ms // 20):
        if condition():
            return True
        QTest.qWait(20)
    return condition()


def _start(recorder, name):
    helpers.start_recording(recorder, 1.0, name, 0, 0)


def test_replaced_recording_is_stopped_and_kept_alive(app):
    recorder = SimpleNamespace()
    finished = []
    with patch.object(WavRecordingThread, "record", _fake_record), patch.object(
        helpers, "on_usb_recording_finished", finished.append
    ):
        _start(recorder, "first.wav")
        first = recorder.usb_recording_thread
        QTest.qWait(50)
        _start(recorder, "second.wav")  # replaces the only reference to first
        del first
        gc.collect()
        assert len(helpers._running_threads) == 2  # first is still referenced
        second = recorder.usb_recording_thread
        try:
            # first was told to stop: it saves well before its ~2 s would end
            assert _wait_until(lambda: finished == ["first.wav"], 1500)
        finally:
            second.stop_recording()
            second.wait(3000)
        assert _wait_until(lambda: finished == ["first.wav", "second.wav"])
        assert _wait_until(lambda: not helpers._running_threads)
