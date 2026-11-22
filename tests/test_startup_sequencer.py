#!/usr/bin/env python3
"""
The splash screen's 16 step sequencer: squares styled like the Instrument
window's light in order as startup progresses.
"""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from jdxi_editor.ui.widgets.indicator.startup_sequencer import StartupSequencer


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _lit(sequencer):
    return [bool(step.property("active")) for step in sequencer.steps]


def test_starts_dark(app):
    sequencer = StartupSequencer()
    assert len(sequencer.steps) == 16
    assert not any(_lit(sequencer))


@pytest.mark.parametrize(
    "value, lit", [(1, 1), (10, 2), (50, 8), (55, 9), (90, 15), (100, 16)]
)
def test_steps_light_in_order(app, value, lit):
    sequencer = StartupSequencer()
    sequencer.setValue(value)
    assert _lit(sequencer) == [True] * lit + [False] * (16 - lit)


def test_squares_use_the_instrument_sequencer_style(app):
    from jdxi_editor.ui.style.factory import generate_sequencer_button_style

    sequencer = StartupSequencer()
    sequencer.setValue(50)
    assert sequencer.steps[7].styleSheet() == generate_sequencer_button_style(True)
    assert sequencer.steps[8].styleSheet() == generate_sequencer_button_style(False)


def test_value_is_clamped(app):
    sequencer = StartupSequencer()
    sequencer.setValue(150)
    assert sequencer.value() == 100 and all(_lit(sequencer))
    sequencer.setValue(-5)
    assert sequencer.value() == 0 and not any(_lit(sequencer))


def test_splash_screen_uses_the_sequencer(app):
    from jdxi_editor.main import setup_splash_screen

    splash, progress, _status = setup_splash_screen(app)
    try:
        assert isinstance(progress, StartupSequencer)
        progress.setValue(55)
        assert sum(_lit(progress)) == 9
    finally:
        splash.close()
