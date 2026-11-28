"""The keyboard window's panel sliders send what the JD-Xi's knobs send (doc/control-change-map.md)."""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from jdxi_editor.midi.data.control_change.digital import DigitalControlChange


class _Helper:
    def __init__(self):
        self.cc, self.nrpn = [], []

    def send_control_change(self, controller, value, channel=0):
        self.cc.append((controller, value, channel))
        return True

    def send_nrpn(self, parameter, value, channel=0):
        self.nrpn.append((parameter, value, channel))
        return True

    def send_rpn(self, parameter, value, channel=0):
        return True


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_lfo_rate_sends_cc_16_to_18(app):
    from jdxi_editor.ui.widgets.midi.slider.lfo.rate import LFORateSlider

    helper = _Helper()
    slider = LFORateSlider(helper)
    slider.on_valueChanged(90)
    assert {c for c, _v, _ch in helper.cc} == {16, 17, 18}
    assert all(v == 90 for _c, v, _ch in helper.cc)
    assert helper.nrpn == []  # it sent the LFO Amp Depth's NRPN (21-23)


def test_rate_and_amp_depth_are_different_controls():
    nrpn = DigitalControlChange.NRPN
    assert "LFO_Rate" not in nrpn  # a copy of LFO_Amp's numbers
    assert DigitalControlChange.get_cc_map("LFO_Rate") == {1: 16, 2: 17, 3: 18}
    assert nrpn["LFO_Amp"] == {1: 21, 2: 22, 3: 23}


def test_env_starts_in_the_middle_and_sends_nothing(app):
    """ENV acts relative to the program: the middle is the program as saved (0 silenced it)."""
    from jdxi_editor.ui.widgets.midi.slider.amp.envelope import AmpEnvelopeSlider

    helper = _Helper()
    slider = AmpEnvelopeSlider(helper)
    assert slider.value() == 64
    assert helper.nrpn == [] and helper.cc == []


def test_env_goes_back_to_the_middle_with_every_program(app):
    from types import SimpleNamespace

    from jdxi_editor.ui.widgets.midi.slider.amp.envelope import AmpEnvelopeSlider
    from jdxi_editor.ui.windows.jdxi.instrument import JDXiInstrument

    helper = _Helper()
    slider = AmpEnvelopeSlider(helper)
    slider.setValueSilently(20)
    window = SimpleNamespace(
        panel_sliders={"envelope": slider},
        midi_in_indicator=SimpleNamespace(blink=lambda: None),
        midi_out_indicator=SimpleNamespace(blink=lambda: None),
    )
    window._reset_envelope_slider = lambda: JDXiInstrument._reset_envelope_slider(window)
    JDXiInstrument._midi_blink_output(window, [0xC0, 5])  # a tone chosen in the editor
    assert slider.value() == 64
    slider.setValueSilently(20)
    JDXiInstrument._midi_blink_input(window, SimpleNamespace(type="program_change"))
    assert slider.value() == 64  # chosen on the JD-Xi
    assert helper.nrpn == [] and helper.cc == []
