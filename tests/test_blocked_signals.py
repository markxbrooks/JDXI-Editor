"""
``blocked_signals`` is a context manager, and is called as one.

Four of the five call sites added to the digital editor passed the widget;
one was written ``with blocked_signals:``, which has no ``__enter__``. The
pitch-envelope widget had the same slip, where it mattered more: the slot
raises before it emits, so moving the slider sent nothing to the synth.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QSlider

from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.ui.widgets.pitch.slider_spinbox import PitchEnvSliderSpinbox
from picoui.signals.signals_blocked import blocked_signals

_APP = QApplication.instance() or QApplication([])


def test_a_widget_is_blocked_inside_and_released_after():
    slider = QSlider()
    assert not slider.signalsBlocked()
    with blocked_signals(slider):
        assert slider.signalsBlocked()
    assert not slider.signalsBlocked()


def test_an_exception_still_releases_the_signals():
    slider = QSlider()
    with pytest.raises(ValueError):
        with blocked_signals(slider):
            raise ValueError("boom")
    assert not slider.signalsBlocked()


def test_something_that_cannot_block_signals_is_tolerated():
    """
    The guard for this has to yield on both paths. A ``@contextmanager``
    generator that returns without yielding raises "generator didn't yield"
    from ``__enter__``, so a guard that skipped the yield failed on exactly
    the objects it was added for.
    """

    class NotAWidget:
        pass

    entered = False
    with blocked_signals(NotAWidget()):
        entered = True
    assert entered


def _slider_factory(**kwargs):
    """Stands in for the editor's slider builder, which the widget is given."""
    slider = QSlider()
    slider.setMinimum(0)
    slider.setMaximum(127)
    initial = kwargs.get("initial_value")
    if initial is not None:
        slider.setValue(int(initial))
    return slider


def test_moving_the_pitch_env_slider_updates_the_spinbox_and_emits():
    """
    The emits come after the blocked block, so a failure there is silent:
    the spinbox stops following and the parameter never reaches the JD-Xi.
    """
    # A time parameter, with the range the envelope section gives it: the
    # spinbox clamps to its own range, so a 0-1 default would hide the result.
    widget = PitchEnvSliderSpinbox(
        DigitalPartialParam.OSC_PITCH_ENV_ATTACK_TIME,
        min_value=10,
        max_value=5000,
        units="ms",
        label="Attack",
        value=64,
        create_parameter_slider=_slider_factory,
    )
    envelopes: list[dict] = []
    values: list[object] = []
    widget.envelope_changed.connect(envelopes.append)
    widget.valueChanged.connect(values.append)

    widget._slider_changed(100)

    assert widget.spinbox.value() == int(widget.convert_to_envelope(100))
    assert len(envelopes) == 1, "the envelope change never reached the editor"
    assert len(values) == 1, "valueChanged never fired"
