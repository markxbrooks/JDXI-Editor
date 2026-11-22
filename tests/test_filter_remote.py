"""MiniLab 3 knobs and faders drive the synth filter and the effect levels."""

from __future__ import annotations

import os
from unittest.mock import Mock

import mido
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from jdxi_editor.midi.io.controller_map import (  # noqa: E402
    EFFECT_CONTROLS,
    MINILAB3_FILTER_MAP,
    FilterControl,
    find_controller_port,
)
from jdxi_editor.midi.io.external_controller import (  # noqa: E402
    ExternalControllerInput,
)
from jdxi_editor.ui.editors.filter_remote import (  # noqa: E402
    FilterRemote,
    scale_to_slider,
    slider_for,
)

CC = {control: cc for cc, control in MINILAB3_FILTER_MAP.items()}
#: every control on its own CC, including those with no MiniLab default
ALL_CC = {control: cc for cc, control in enumerate(FilterControl)}
SYNTH_CONTROLS = [c for c in FilterControl if c not in EFFECT_CONTROLS]
EFFECT_LIST = sorted(EFFECT_CONTROLS, key=lambda c: c.name)


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def digital_editor(qapp):
    from jdxi_editor.ui.editors.digital.editor import DigitalSynthEditor

    midi_helper = Mock()
    midi_helper.send_midi_message = Mock(return_value=True)
    return DigitalSynthEditor(midi_helper=midi_helper, synth_number=1)


@pytest.fixture(scope="module")
def analog_editor(qapp):
    from jdxi_editor.ui.editors.analog.editor import AnalogSynthEditor

    midi_helper = Mock()
    midi_helper.send_midi_message = Mock(return_value=True)
    return AnalogSynthEditor(midi_helper=midi_helper)


def test_minilab_main_port_is_chosen():
    ports = ["JD-Xi", "Minilab3 DIN THRU", "Minilab3 MIDI", "Minilab3 MCU/HUI"]
    assert find_controller_port(ports) == "Minilab3 MIDI"
    assert find_controller_port(["JD-Xi", "Logic Pro Virtual Out"]) is None


@pytest.fixture(scope="module")
def effects_editor(qapp):
    from jdxi_editor.ui.editors.effects.common import EffectsCommonEditor

    midi_helper = Mock()
    midi_helper.send_midi_message = Mock(return_value=True)
    return EffectsCommonEditor(midi_helper=midi_helper)


def test_knobs_and_faders_cover_the_filter():
    # envelope velocity sensitivity is learnable but has no default control
    unmapped = set(FilterControl) - set(MINILAB3_FILTER_MAP.values())
    assert unmapped == {FilterControl.ENV_VELOCITY}
    bottom_knobs = [93, 18, 19, 16]
    assert [MINILAB3_FILTER_MAP[cc] for cc in bottom_knobs] == [
        FilterControl.EFFECT1_LEVEL,
        FilterControl.EFFECT2_LEVEL,
        FilterControl.DELAY_LEVEL,
        FilterControl.REVERB_LEVEL,
    ]
    faders = [82, 83, 85, 17]
    assert [MINILAB3_FILTER_MAP[cc] for cc in faders] == [
        FilterControl.ENV_ATTACK,
        FilterControl.ENV_DECAY,
        FilterControl.ENV_SUSTAIN,
        FilterControl.ENV_RELEASE,
    ]


@pytest.mark.parametrize("editor_name", ["digital_editor", "analog_editor"])
def test_every_filter_control_has_a_slider(request, editor_name):
    from jdxi_editor.ui.editors.filter_remote import controls_for_editor

    controls = controls_for_editor(request.getfixturevalue(editor_name))
    missing = [c for c in SYNTH_CONTROLS if slider_for(controls, c) is None]
    assert missing == []


@pytest.mark.parametrize("editor_name", ["digital_editor", "analog_editor"])
@pytest.mark.parametrize("control", SYNTH_CONTROLS)
def test_cc_moves_slider_and_sends_to_jdxi(request, editor_name, control):
    from jdxi_editor.ui.editors.filter_remote import controls_for_editor

    editor = request.getfixturevalue(editor_name)
    remote = FilterRemote(lambda: editor, cc_map={cc: c for c, cc in ALL_CC.items()})
    slider = slider_for(controls_for_editor(editor), control)
    send = editor.midi_helper.send_midi_message
    for value in (0, 127):
        send.reset_mock()
        assert remote.on_control_change(0, ALL_CC[control], value) is True
        assert slider.value() == scale_to_slider(slider, value)
    assert send.called
    low, high = slider.slider.minimum(), slider.slider.maximum()
    assert (scale_to_slider(slider, 0), scale_to_slider(slider, 127)) == (low, high)


def test_digital_targets_the_selected_partial(digital_editor):
    from jdxi_editor.ui.editors.filter_remote import controls_for_editor

    remote = FilterRemote(lambda: digital_editor)
    panel = digital_editor._current_partial_panel()
    assert controls_for_editor(digital_editor) == panel.all_controls()
    remote.on_control_change(0, CC[FilterControl.RESONANCE], 100)
    slider = slider_for(panel.all_controls(), FilterControl.RESONANCE)
    assert slider.value() == scale_to_slider(slider, 100)


def test_other_tabs_keep_driving_the_last_synth_editor(analog_editor):
    current = {"tab": analog_editor}
    remote = FilterRemote(lambda: current["tab"])
    assert remote.target_controls() is not None
    current["tab"] = None  # e.g. the Effects or Program tab
    assert remote.on_control_change(0, CC[FilterControl.CUTOFF], 64) is True


def test_no_synth_editor_and_unmapped_cc_are_ignored(analog_editor):
    assert FilterRemote(lambda: None).on_control_change(0, 74, 64) is False
    remote = FilterRemote(lambda: analog_editor)
    assert remote.on_control_change(0, 1, 64) is False  # mod wheel
    assert FilterRemote(lambda: analog_editor, channel=1).on_control_change(
        0, 74, 64
    ) is False


def test_controller_input_emits_messages_and_control_changes(qapp):
    controller = ExternalControllerInput()
    controller.port_name = "Minilab3 MIDI"
    messages, changes = [], []
    controller.message_received.connect(lambda port, msg: messages.append((port, msg)))
    controller.control_changed.connect(lambda *args: changes.append(args))
    controller._on_midi((mido.Message("control_change", control=74, value=90).bytes(), 0.0))
    controller._on_midi((mido.Message("note_on", note=60, velocity=100).bytes(), 0.0))
    controller._emit_pending()
    assert [m.type for _, m in messages] == ["control_change", "note_on"]
    assert messages[0][0] == "Minilab3 MIDI"
    assert changes == [(0, 74, 90)]


@pytest.mark.parametrize("control", EFFECT_LIST)
def test_bottom_knobs_drive_effect_levels_from_any_tab(
    analog_editor, effects_editor, control
):
    # the Analog tab is showing; effect levels still reach the Effects editor
    remote = FilterRemote(lambda: analog_editor, effects_editor=lambda: effects_editor)
    slider = slider_for(effects_editor.all_controls(), control)
    send = effects_editor.midi_helper.send_midi_message
    for value in (127, 0):
        send.reset_mock()
        assert remote.on_control_change(0, CC[control], value) is True
        assert slider.value() == scale_to_slider(slider, value)
        assert send.call_count == 1  # one parameter message per change


def test_effect_levels_need_the_effects_editor(analog_editor):
    cc = CC[FilterControl.REVERB_LEVEL]
    assert FilterRemote(lambda: analog_editor).on_control_change(0, cc, 64) is False
    remote = FilterRemote(lambda: analog_editor, effects_editor=lambda: None)
    assert remote.on_control_change(0, cc, 64) is False
