"""
A slider sends each change once, and a drag at most every DRAG_EMIT_INTERVAL_MS.
"""

import sys
import time

import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from jdxi_editor.ui.widgets.slider.slider import Slider

_APP = QApplication.instance() or QApplication(sys.argv)


@pytest.fixture
def slider():
    s = Slider("Cutoff", 0, 127, midi_helper=None)
    received = []
    s.valueChanged.connect(received.append)
    s.received = received
    yield s
    s.deleteLater()


def test_slider_emits_each_change_once(slider):
    for value in (10, 11, 12):
        slider.slider.setValue(value)
    assert slider.received == [10, 11, 12]


def test_slider_drag_is_throttled_and_the_release_value_is_sent(slider):
    slider.slider.setSliderDown(True)
    for value in range(1, 60):
        slider.slider.setValue(value)
    # First move at once, the rest coalesced while the interval runs
    assert slider.received == [1]
    # Under load the timer can fire well after DRAG_EMIT_INTERVAL_MS
    deadline = time.monotonic() + 5
    while slider.received[-1] != 59 and time.monotonic() < deadline:
        QTest.qWait(10)
    assert slider.received[-1] == 59
    slider.slider.setValue(64)
    slider.slider.setSliderDown(False)
    slider.slider.sliderReleased.emit()
    assert slider.received[-1] == 64
    assert len(slider.received) < 10


def test_slider_silent_update_does_not_resend(slider):
    slider.setValueSilently(90)
    slider.slider.sliderReleased.emit()
    assert slider.received == []
