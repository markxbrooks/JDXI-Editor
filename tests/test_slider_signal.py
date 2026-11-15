"""A Slider emits valueChanged once per change, so a move sends one message."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from jdxi_editor.ui.widgets.slider.slider import Slider  # noqa: E402


def test_value_changed_fires_once_per_change():
    QApplication.instance() or QApplication([])
    slider = Slider("Level", min_value=0, max_value=127, midi_helper=None)
    received = []
    slider.valueChanged.connect(received.append)
    slider.setValue(64)
    slider.setValue(64)  # unchanged: no signal
    slider.setValue(100)
    assert received == [64, 100]
    assert slider.value_label.text() == "100"


def test_set_value_silently_emits_nothing():
    QApplication.instance() or QApplication([])
    slider = Slider("Level", min_value=0, max_value=127, midi_helper=None)
    received = []
    slider.valueChanged.connect(received.append)
    slider.setValueSilently(42)
    assert received == []
    assert slider.value() == 42
