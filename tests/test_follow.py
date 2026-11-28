"""The instrument window follows the JD-Xi: tone names, octave, sliders, keys, start-up reading."""

from __future__ import annotations

from unittest.mock import Mock

import time
import mido
import pytest
from PySide6.QtWidgets import QApplication

from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.ui.windows.jdxi import follow
from jdxi_editor.ui.windows.jdxi.follow import PART_REQUESTS, parse_dt1


@pytest.fixture(scope="module")
def window():
    app = QApplication.instance() or QApplication([])
    from jdxi_editor.ui.windows.jdxi.instrument import JDXiInstrument

    w = JDXiInstrument()
    w.show()
    for _ in range(10):
        app.processEvents()
    yield w
    w.follower.stop()  # it would keep reading the shared (simulated) JD-Xi in the tests after
    w.close()
    _dispose(w)


@pytest.fixture
def sent(window, monkeypatch):
    requests = []
    monkeypatch.setattr(follow, "send_with_delay", lambda helper, reqs: requests.append(reqs))
    monkeypatch.setattr(window.midi_helper, "midi_out", object(), raising=False)
    monkeypatch.setattr(window.follower, "_connected", lambda: True)  # a JD-Xi there (shared connection)
    window.follower._last_input = 0.0
    return requests


def settle():
    for _ in range(5):
        QApplication.processEvents()


def dt1(address, values):
    checksum = (128 - sum(address + values) % 128) % 128
    return mido.Message("sysex", data=[0x41, 0x10, 0, 0, 0, 0x0E, 0x12] + address + values + [checksum])


def receive(window, message):
    window.midi_helper._handle_midi_message(message)
    settle()


def analog_tone(name=b"Toxic Bass 3", octave=64, cutoff=0, resonance=0):
    values = list(name.ljust(12)) + [0] * (0x40 - 12)
    values[0x34] = octave
    values[0x21] = cutoff
    values[0x23] = resonance
    return values


def no_octave_shift(window):
    """Analog with Octave 0 in its tone and in its program zone."""
    receive(window, dt1([0x18, 0x00, 0x32, 0x00], [64] * 0x23))
    receive(window, dt1([0x19, 0x42, 0x00, 0x00], analog_tone(octave=64)))
    assert window.current_octave == 0


def test_parse_dt1():
    message = dt1([0x19, 0x42, 0x00, 0x10], [1, 2, 3])
    assert parse_dt1(message.data) == ((0x19, 0x42, 0x00, 0x10), [1, 2, 3])
    assert parse_dt1([0x41, 0x10, 0, 0, 0, 0x0E, 0x11, 0x19, 0x42, 0, 0, 0, 0, 0, 0x40, 0x27]) is None


def test_tone_chosen_on_the_jdxi_shows_on_the_display(window):
    window._select_synth(JDXiSynth.ANALOG_SYNTH)
    receive(window, dt1([0x19, 0x42, 0x00, 0x00], analog_tone(b"Toxic Bass 3")))
    assert window.preset_manager.current_preset_names[JDXiSynth.ANALOG_SYNTH] == "Toxic Bass 3"
    assert window.preset_manager.current_preset_name == "Toxic Bass 3"


def test_octave_and_sliders_follow_the_part_shown(window):
    window._select_synth(JDXiSynth.ANALOG_SYNTH)
    receive(window, dt1([0x19, 0x42, 0x00, 0x00], analog_tone(octave=66, cutoff=100, resonance=30)))
    assert window.current_octave == 2
    assert window.octave_up.isChecked() and not window.octave_down.isChecked()
    assert window.panel_sliders["cutoff"].value() == 100
    assert window.panel_sliders["resonance"].value() == 30
    # an octave changed with the JD-Xi's buttons (in the program zone)
    zone = [64] * 0x23
    receive(window, dt1([0x18, 0x00, 0x32, 0x00], zone))
    zone[0x19] = 63
    receive(window, dt1([0x18, 0x00, 0x32, 0x00], zone))
    assert window.current_octave == -1
    assert window.octave_down.isChecked()


def test_another_parts_values_leave_the_sliders(window):
    window._select_synth(JDXiSynth.ANALOG_SYNTH)
    receive(window, dt1([0x19, 0x42, 0x00, 0x00], analog_tone(cutoff=90)))
    partial = [0] * 0x40
    partial[0x0C] = 10
    receive(window, dt1([0x19, 0x01, 0x20, 0x00], partial))  # Digital 1, not shown
    assert window.panel_sliders["cutoff"].value() == 90
    window._select_synth(JDXiSynth.DIGITAL_SYNTH_1)
    receive(window, dt1([0x19, 0x01, 0x20, 0x00], partial))
    assert window.panel_sliders["cutoff"].value() == 10


def test_slider_values_from_the_jdxi_are_not_sent_back(window, monkeypatch):
    calls = Mock()
    monkeypatch.setattr(window.midi_helper, "send_control_change", calls)
    window._select_synth(JDXiSynth.ANALOG_SYNTH)
    receive(window, dt1([0x19, 0x42, 0x00, 0x00], analog_tone(cutoff=77)))
    assert window.panel_sliders["cutoff"].value() == 77
    calls.assert_not_called()


def test_notes_played_on_the_jdxi_light_the_keys(window):
    window._select_synth(JDXiSynth.ANALOG_SYNTH)
    no_octave_shift(window)
    key = window.piano_keyboard._keys_by_note[60]
    receive(window, mido.Message("note_on", note=60, velocity=90, channel=2))
    assert key.is_pressed
    receive(window, mido.Message("note_on", note=60, velocity=0, channel=2))
    assert not key.is_pressed
    receive(window, mido.Message("note_on", note=60, velocity=90, channel=0))
    receive(window, mido.Message("note_off", note=60, channel=0))
    assert not key.is_pressed


def test_with_an_octave_shift_the_key_pressed_lights(window):
    """The JD-Xi at Octave +1 sends its top C as 84: the window's top C lights."""
    window._select_synth(JDXiSynth.ANALOG_SYNTH)
    no_octave_shift(window)
    receive(window, dt1([0x19, 0x42, 0x00, 0x00], analog_tone(octave=65)))
    assert window.current_octave == 1
    keys = window.piano_keyboard._keys_by_note
    receive(window, mido.Message("note_on", note=84, velocity=90, channel=2))
    assert keys[72].is_pressed
    receive(window, mido.Message("note_on", note=60, velocity=90, channel=2))
    assert keys[48].is_pressed and not keys[60].is_pressed
    # the octave changes while the keys are held: the same keys go off
    receive(window, dt1([0x19, 0x42, 0x00, 0x00], analog_tone(octave=63)))
    assert window.current_octave == -1
    receive(window, mido.Message("note_off", note=84, channel=2))
    receive(window, mido.Message("note_off", note=60, channel=2))
    assert not any(key.is_pressed for key in keys.values())
    receive(window, mido.Message("note_on", note=24, velocity=90, channel=2))  # bottom C at -1
    assert keys[36].is_pressed
    receive(window, mido.Message("note_on", note=24, velocity=0, channel=2))
    assert not keys[36].is_pressed
    no_octave_shift(window)


def test_poll_reads_the_part_shown(window, sent):
    window._select_synth(JDXiSynth.ANALOG_SYNTH)
    sent.clear()
    window.follower._last_input = 0.0
    window.follower.poll()
    assert sent == [PART_REQUESTS[JDXiSynth.ANALOG_SYNTH]]


def test_no_poll_just_after_input_or_while_playing(window, sent, monkeypatch):
    window._select_synth(JDXiSynth.DIGITAL_SYNTH_1)
    sent.clear()
    window.follower.on_outgoing([0xB0, 74, 10])  # a value sent from the app
    window.follower.poll()
    assert sent == []
    window.follower._last_input = 0.0
    window.follower.on_outgoing(bytes.fromhex(PART_REQUESTS[JDXiSynth.ANALOG_SYNTH][0].replace(" ", "")))
    window.follower.poll()
    assert sent == [PART_REQUESTS[JDXiSynth.DIGITAL_SYNTH_1]]  # requests do not count as input
    sent.clear()
    playing = Mock(is_playing=True)
    monkeypatch.setattr(follow, "playback_activity", lambda: playing)
    window.follower._last_input = 0.0
    window.follower.poll()
    assert sent == []


def test_no_poll_without_midi_out(window, sent, monkeypatch):
    monkeypatch.setattr(window.midi_helper, "midi_out", None, raising=False)
    monkeypatch.undo()  # the real check: no output port, no connection
    monkeypatch.setattr(follow, "send_with_delay", lambda helper, reqs: sent.append(reqs))
    monkeypatch.setattr(window.midi_helper, "midi_out", None, raising=False)
    window.follower.poll()
    window.follower.read_all()
    assert sent == []


def test_tone_program_change_reads_the_part_not_the_program(window, sent):
    before = getattr(window, "current_program_number", None)
    receive(window, mido.Message("program_change", program=4, channel=2))  # Analog channel
    assert PART_REQUESTS[JDXiSynth.ANALOG_SYNTH] in sent
    assert getattr(window, "current_program_number", None) == before


def test_program_change_on_the_program_channel(window, sent, monkeypatch):
    requested = Mock()
    monkeypatch.setattr(window, "data_request", requested)
    window.set_current_program_number(16, 4)
    assert window.current_program_number == 5
    requested.assert_called_once()


def test_octave_buttons_write_the_part_shown(window, monkeypatch):
    messages = []
    monkeypatch.setattr(window.midi_helper, "send_midi_message", lambda m: messages.append(m) or True)
    window._select_synth(JDXiSynth.ANALOG_SYNTH)
    window.current_octave = 0
    window._midi_send_octave(+1)
    raw = [int(b) for b in messages[-1].to_message_list()]
    at = raw.index(0x12) + 1  # after DT1: address, value
    assert raw[at : at + 5] == [0x19, 0x42, 0x00, 0x34, 0x41]


@pytest.fixture
def program_channel_reset():
    from jdxi_editor.midi.io import program_channel

    program_channel.reset()
    yield program_channel
    program_channel.reset()


def test_programs_go_to_the_jdxis_program_channel(window, program_channel_reset, monkeypatch):
    """SYSTEM › Program Ctrl Ch read at start: programs sent where the JD-Xi listens."""
    raw = []
    monkeypatch.setattr(window.midi_helper, "send_raw_message", lambda m: raw.append(list(m)) or True)
    system = [0] * 0x2B
    system[0x11], system[0x29], system[0x2A] = 2, 1, 1  # Program Ctrl Ch 3
    receive(window, dt1([0x02, 0x00, 0x00, 0x00], system))
    assert program_channel_reset.channel() == 2
    window.midi_helper.send_bank_select_and_program_change(15, 85, 64, 1)
    assert [m for m in raw if m[0] != 0xF0] == [[0xB2, 0, 85], [0xB2, 32, 64], [0xC2, 1]]
    raw.clear()
    window.midi_helper.send_bank_select_and_program_change(0, 95, 64, 1)  # a tone: unchanged
    assert [m for m in raw if m[0] != 0xF0][-1] == [0xC0, 1]


def test_program_changes_off_on_the_jdxi_are_reported(window, program_channel_reset):
    system = [0] * 0x2B
    system[0x11], system[0x29], system[0x2A] = 16, 0, 1  # OFF, Rx Program Change OFF
    receive(window, dt1([0x02, 0x00, 0x00, 0x00], system))
    assert "Program Ctrl Ch: OFF" in program_channel_reset.problem()
    assert "Rx Program Change: OFF" in program_channel_reset.problem()
    assert "MENU" in window.statusBar().currentMessage()
    assert program_channel_reset.channel() == 15  # still sent on 16


def test_tone_arrows_of_the_window_load_the_tone_shown(window, monkeypatch):
    raw = []
    monkeypatch.setattr(window.midi_helper, "send_raw_message", lambda m: raw.append(list(m)) or True)
    window._select_synth(JDXiSynth.DIGITAL_SYNTH_1)
    window.current_preset_index = 0
    window._preset_next()  # 002
    assert [m for m in raw if m[0] != 0xF0][-1] == [0xC0, 1]


def test_a_one_parameter_dt1_sets_that_parameter_only():
    """A DT1 for one parameter (the JD-Xi sends them) used to be read as a whole block: all 0."""
    from jdxi_editor.midi.sysex.parser.utils import parse_sysex

    address, values = [0x19, 0x42, 0x00, 0x21], [110]
    checksum = (128 - sum(address + values) % 128) % 128
    parsed = parse_sysex(bytes([0xF0, 0x41, 0x10, 0, 0, 0, 0x0E, 0x12, *address, *values, checksum, 0xF7]))
    assert parsed["FILTER_CUTOFF"] == 110
    assert "FILTER_RESONANCE" not in parsed and "LFO_RATE" not in parsed


def test_messages_sent_are_heard():
    """midi_message_outgoing reaches its listeners (a signal of the second QObject base did not)."""
    from jdxi_editor.midi.io.helper import MidiIOHelper

    QApplication.instance() or QApplication([])
    helper = MidiIOHelper()
    heard = []
    helper.midi_message_outgoing.connect(heard.append)
    helper.midi_message_outgoing.emit([0xB0, 7, 100])
    helper.midi_message_outgoing.disconnect(heard.append)
    assert heard == [[0xB0, 7, 100]]


def test_the_window_selects_the_part_played_on_the_jdxi(window, monkeypatch):
    """Notes in a row on a part's channel: that part is selected in the window too."""
    monkeypatch.setattr(follow, "FOLLOW_PAUSE_S", 0.0)
    window._select_synth(JDXiSynth.DIGITAL_SYNTH_1)
    window.follower._recent_channels.clear()
    for note in (60, 62):
        receive(window, mido.Message("note_on", note=note, velocity=80, channel=2))
    assert window.current_synth_type == JDXiSynth.DIGITAL_SYNTH_1  # not yet: two notes
    receive(window, mido.Message("note_on", note=64, velocity=80, channel=2))
    assert window.current_synth_type == JDXiSynth.ANALOG_SYNTH
    # a pattern playing several parts: no jumping
    for channel in (0, 9, 0, 1, 0, 9):
        receive(window, mido.Message("note_on", note=60, velocity=80, channel=channel))
    assert window.current_synth_type == JDXiSynth.ANALOG_SYNTH


def _dispose(window) -> None:
    """Delete the window and the message boxes it opened (offline: «MIDI not available»):
    left alive, their timers slow the next tests and their boxes are counted there."""
    from PySide6.QtCore import QEvent
    from PySide6.QtWidgets import QApplication, QMessageBox

    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, QMessageBox):
            widget.close()
            widget.deleteLater()
    for name in ("main_editor", "self_test_dialog"):
        other = getattr(window, name, None)
        if other is not None:
            other.close()
            other.deleteLater()
    window.deleteLater()
    QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    QApplication.processEvents()


def _wheel_output(window, monkeypatch):
    out = []
    monkeypatch.setattr(window.midi_helper, "midi_out", object(), raising=False)
    monkeypatch.setattr(window.midi_helper, "send_raw_message", lambda m: out.append(list(m)) or True)
    monkeypatch.setattr(
        window.midi_helper, "send_control_change", lambda cc, v, channel=0: out.append(["cc", cc, v, channel]) or True
    )
    return out


def _echoes(out) -> list:
    """What would be an echo of a wheel or a knob: channel messages (pitch bend,
    control change) or CCs sent back. SysEx is left out: the readings of a part
    (RQ1) and an editor's change still on its way from an earlier test (DT1)."""
    return [m for m in out if m and (m[0] == "cc" or 0x80 <= int(m[0]) <= 0xEF)]


def test_the_jdxis_wheels_move_the_windows_without_echo(window, monkeypatch):
    out = _wheel_output(window, monkeypatch)
    receive(window, mido.Message("pitchwheel", channel=0, pitch=8191))
    assert window.pitch_wheel.get_value() == pytest.approx(1.0, abs=0.001)
    receive(window, mido.Message("pitchwheel", channel=2, pitch=-4096))
    assert window.pitch_wheel.get_value() == pytest.approx(-0.5)
    receive(window, mido.Message("control_change", channel=0, control=1, value=127))
    assert window.mod_wheel.get_value() == pytest.approx(1.0)
    receive(window, mido.Message("control_change", channel=0, control=1, value=0))
    assert window.mod_wheel.get_value() == 0.0
    receive(window, mido.Message("pitchwheel", channel=0, pitch=0))
    assert window.pitch_wheel.get_value() == 0.0
    assert _echoes(out) == []  # no pitch bend or modulation sent back to the JD-Xi


def test_the_pitch_wheel_sends_its_return_to_the_centre(window, monkeypatch):
    from jdxi_editor.ui.widgets.wheel.pitch import bend_from_value

    out = _wheel_output(window, monkeypatch)
    wheel = window.pitch_wheel
    wheel.set_value(0.5)  # dragged
    assert out[-3:] == [[0xE0 + ch, bend_from_value(0.5) & 0x7F, bend_from_value(0.5) >> 7] for ch in (0, 1, 2)]
    wheel._drag_active = True
    wheel.mouseReleaseEvent(None)  # let go: it springs back
    deadline = time.monotonic() + 2
    while wheel.get_value() != 0.0 and time.monotonic() < deadline:
        QApplication.processEvents()
    assert wheel.get_value() == 0.0
    assert out[-3:] == [[0xE0 + ch, 0x00, 0x40] for ch in (0, 1, 2)]  # centre: 8192


def test_the_mod_wheel_stays_where_it_is_left(window, monkeypatch):
    out = _wheel_output(window, monkeypatch)
    wheel = window.mod_wheel
    wheel.set_value(0.5)
    assert out == [["cc", 1, 64, ch] for ch in (0, 1, 2)]
    wheel._drag_active = True
    wheel.mouseReleaseEvent(None)
    settle()
    assert wheel.get_value() == 0.5
    wheel.set_value(0.0)


def _cc(window, channel, control, value):
    receive(window, mido.Message("control_change", channel=channel, control=control, value=value))


def test_the_jdxis_knobs_move_the_panel_sliders(window, monkeypatch):
    out = _wheel_output(window, monkeypatch)
    sliders = window.panel_sliders
    window._select_synth(JDXiSynth.DIGITAL_SYNTH_1)
    settle()
    _cc(window, 0, 102, 90)  # Cutoff, partial 1
    _cc(window, 0, 103, 10)  # partial 2: the sliders show partial 1
    _cc(window, 0, 105, 40)  # Resonance
    _cc(window, 0, 117, 100)  # Level
    _cc(window, 0, 16, 77)  # LFO Rate
    assert [sliders[n].value() for n in ("cutoff", "resonance", "level", "lfo_rate")] == [90, 40, 100, 77]
    for lsb, name, value in ((124, "envelope", 33), (21, "lfo_amp", 80)):
        for control, v in ((99, 0), (98, lsb), (6, value), (99, 127), (98, 127)):
            _cc(window, 0, control, v)
        assert sliders[name].value() == value
    _cc(window, 2, 102, 5)  # the Analog's knob: not the part shown
    assert sliders["cutoff"].value() == 90
    _cc(window, 15, 12, 64)  # Reverb (effects: any channel)
    _cc(window, 15, 13, 20)  # Delay
    assert (sliders["reverb"].value(), sliders["delay"].value()) == (64, 20)
    window._select_synth(JDXiSynth.ANALOG_SYNTH)
    settle()
    _cc(window, 2, 102, 5)
    assert sliders["cutoff"].value() == 5
    assert _echoes(out) == []  # no controller sent back to the JD-Xi

def test_middle_c_is_marked_where_it_sounds(window):
    """The C4 mark sits on the key that sounds middle C at the octave shown."""
    keys = window.piano_keyboard._keys_by_note

    def marked():
        return [note for note, key in keys.items() if key.middle_c]

    for octave, where in ((0, [60]), (1, [48]), (-1, [72]), (2, [36]), (3, []), (-2, [])):
        window.current_octave = octave
        window._ui_update_octave()
        assert marked() == where, octave
    window.current_octave = 0
    window._ui_update_octave()
    assert marked() == [60]


def test_env_slider_back_to_the_middle_with_every_program(window):
    """The JD-Xi loads a program as saved, its ENV knob counting only once turned."""
    env = window.panel_sliders["envelope"]
    env.setValueSilently(10)  # turned in the app
    receive(window, mido.Message("program_change", channel=15, program=3))  # chosen on the JD-Xi
    assert env.value() == 64
    env.setValueSilently(120)
    window.follower.on_outgoing(mido.Message("program_change", channel=15, program=4))  # chosen in the app
    assert env.value() == 64
