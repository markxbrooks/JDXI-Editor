"""
jdxi_editor.ui.windows.jdxi.follow
The instrument window follows the JD-Xi.

What is changed on the instrument itself reaches the window:

- at start (once the MIDI ports are open) the window reads the program, the
  four tones and the Digital partials, so it does not start on "Init Tone"
- the part shown (Digital 1, Digital 2, Analog, Drums) is read again every
  couple of seconds: a tone chosen with the JD-Xi's own buttons appears on the
  display, the OCTAVE buttons light as on the instrument and the panel sliders
  move to the tone's values. Nothing is read while a MIDI file or pattern plays,
  while the app is minimised, or for a few seconds after a click, a key or a
  value sent from the app (a reply on its way must not undo what was just set)
- a program change from the JD-Xi on a part's channel reads that part at once
- the notes played on the JD-Xi light the window's keys, and their channel
  tells the part selected on the JD-Xi: the window selects it too

The replies go through the usual path (tone names, editors), so an editor that
is open follows too.
"""

from __future__ import annotations

import os
import time
from typing import Dict, Optional

from PySide6.QtCore import QEvent, QObject, QTimer, Qt
from PySide6.QtWidgets import QApplication

from decologr import Decologr as log

from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.midi.io import program_channel
from jdxi_editor.midi.io.delay import send_with_delay
from jdxi_editor.midi.playback.activity import playback_activity
from jdxi_editor.midi.sysex.request.data import (
    TEMPORARY_PROGRAM_RQ11_HEADER,
    TEMPORARY_TONE_RQ11_HEADER,
)
from jdxi_editor.midi.sysex.request.factory import create_request
from jdxi_editor.midi.sysex.request.hex import JDXISysExHex
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.ui.widgets.wheel.mod import MODULATION_CC
from jdxi_editor.ui.widgets.wheel.pitch import value_from_pitch

STARTUP_DELAY_MS = 1200  # the ports are open and the window is drawn
POLL_INTERVAL_MS = 2000
QUIET_AFTER_INPUT_S = 3.0  # no reading just after the user acted in the app

SYSTEM_COMMON = (0x02, 0x00, 0x00)
PROGRAM_CTRL_CH, RX_PROGRAM_CHANGE, RX_BANK_SELECT = 0x11, 0x29, 0x2A
ROLAND_DT1 = (0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12)
TEMPORARY_TONE = 0x19
TEMPORARY_PROGRAM = 0x18
PARTIAL_1 = 0x20

# part: (MIDI channel, temporary tone byte, program zone byte)
PARTS = {
    JDXiSynth.DIGITAL_SYNTH_1: (0, 0x01, 0x30),
    JDXiSynth.DIGITAL_SYNTH_2: (1, 0x21, 0x31),
    JDXiSynth.ANALOG_SYNTH: (2, 0x42, 0x32),
    JDXiSynth.DRUM_KIT: (9, 0x70, 0x33),
}

# Octave shift: in the tone (Digital common, Analog tone) and in the program zone
DIGITAL_COMMON_OCTAVE = 0x15
ANALOG_OCTAVE = 0x34
ZONE_OCTAVE = 0x19
OCTAVE_CENTRE = 64
FOLLOW_NOTES = 3  # notes in a row on a part's channel before the window selects that part
FOLLOW_PAUSE_S = 2.0

# panel slider -> offset in the Digital partial 1 / in the Analog tone
DIGITAL_SLIDERS = {
    "cutoff": 0x0C,
    "resonance": 0x0F,
    "level": 0x15,
    "lfo_rate": 0x1D,
    "lfo_pitch": 0x22,
    "lfo_filter": 0x23,
    "lfo_amp": 0x24,
}
ANALOG_SLIDERS = {
    "cutoff": 0x21,
    "resonance": 0x23,
    "level": 0x2A,
    "lfo_rate": 0x0E,
    "lfo_pitch": 0x12,
    "lfo_filter": 0x13,
    "lfo_amp": 0x14,
}

# The JD-Xi's knobs (MIDI Implementation, "Control Change Message List", knob
# operation) -> panel slider. A Digital tone's knob sends one controller per
# partial: the window's sliders show partial 1 (102, 105...), as they do from
# the SysEx values. The effects' knobs are not a part's (any channel).
KNOB_CC = {102: "cutoff", 105: "resonance", 117: "level", 16: "lfo_rate"}
KNOB_CC_EFFECTS = {12: "reverb", 13: "delay"}
KNOB_NRPN = {(0, 124): "envelope", (0, 15): "lfo_pitch", (0, 18): "lfo_filter", (0, 21): "lfo_amp"}
CC_NRPN_LSB, CC_NRPN_MSB, CC_DATA_ENTRY = 98, 99, 6
NRPN_NULL = 127


def _zone_request(area: str) -> str:
    return create_request(TEMPORARY_PROGRAM_RQ11_HEADER, area, "00 00 00 23")


PART_REQUESTS = {
    JDXiSynth.DIGITAL_SYNTH_1: [
        MidiRequests.DIGITAL1_COMMON,
        MidiRequests.DIGITAL1_PARTIAL1,
        _zone_request(JDXISysExHex.PROGRAM_ZONE_DIGITAL1_AREA),
    ],
    JDXiSynth.DIGITAL_SYNTH_2: [
        MidiRequests.DIGITAL2_COMMON,
        MidiRequests.DIGITAL2_PARTIAL1,
        _zone_request(JDXISysExHex.PROGRAM_ZONE_DIGITAL2_AREA),
    ],
    JDXiSynth.ANALOG_SYNTH: [
        create_request(TEMPORARY_TONE_RQ11_HEADER, JDXISysExHex.ANALOG, "00 00 00 00 00 40"),
        _zone_request(JDXISysExHex.PROGRAM_ZONE_ANALOG_AREA),
    ],
    JDXiSynth.DRUM_KIT: [
        create_request(TEMPORARY_TONE_RQ11_HEADER, JDXISysExHex.DRUMS, "00 00 00 00 00 12"),
        _zone_request(JDXISysExHex.PROGRAM_ZONE_DRUMS_AREA),
    ],
}


def parse_dt1(data) -> Optional[tuple]:
    """(address, values) of a Roland DT1 from the JD-Xi (SysEx data without F0/F7)."""
    data = [int(b) for b in data]
    if data and data[0] == 0xF0:
        data = data[1:]
    if data and data[-1] == 0xF7:
        data = data[:-1]
    if len(data) < len(ROLAND_DT1) + 5 or tuple(data[: len(ROLAND_DT1)]) != ROLAND_DT1:
        return None
    address = tuple(data[7:11])
    return address, data[11:-1]  # the last byte is the checksum


def _value_at(address: tuple, values: list, block: tuple, offset: int) -> Optional[int]:
    """The byte at *block* + *offset* if this DT1 (at *address*) holds it."""
    if address[:3] != block:
        return None
    index = offset - address[3]
    if 0 <= index < len(values):
        return values[index]
    return None


class InstrumentFollower(QObject):
    """Keeps the instrument window in step with the JD-Xi (see the module doc)."""

    def __init__(self, window, parent: Optional[QObject] = None):
        super().__init__(parent or window)
        self.window = window
        self.midi_helper = window.midi_helper
        self._last_input = 0.0
        self._lit: Dict[tuple, object] = {}  # (channel, note received) -> key lit
        # per part: octave as stored in the tone and in the program zone
        self._tone_octave: Dict[str, int] = {}
        self._zone_octave: Dict[str, int] = {}
        self._part = None
        self._recent_channels: list = []
        self._part_followed_at = -FOLLOW_PAUSE_S
        self._nrpn: Dict[int, list] = {}  # channel -> [msb, lsb] chosen by CC 99/98

        self.timer = QTimer(self)
        self.timer.setInterval(POLL_INTERVAL_MS)
        self.timer.timeout.connect(self.poll)

        helper = self.midi_helper
        helper.midi_message_incoming.connect(self.on_incoming)
        helper.midi_message_outgoing.connect(self.on_outgoing)
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    # ------------------------------------------------------------ start
    def start(self) -> None:
        self._stopped = False
        if os.environ.get("JDXI_FOLLOW", "1") == "0":
            return  # not following the JD-Xi (the tests set this)
        QTimer.singleShot(STARTUP_DELAY_MS, self, self.read_all)
        self.timer.start()

    def stop(self) -> None:
        """The program is closing: no more readings."""
        self._stopped = True
        self.timer.stop()
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)

    def read_all(self) -> None:
        """Program, tones and partials: what the window shows at start."""
        if not self._connected() or getattr(self, "_stopped", False):
            return
        now = time.monotonic()
        if now - getattr(self, "_read_all_at", -60.0) < 5.0:
            return  # the ports opened and the start-up reading came together
        self._read_all_at = now
        # the SYSTEM settings first: which channel the JD-Xi takes programs on
        send_with_delay(self.midi_helper, [MidiRequests.SYSTEM_COMMON])
        self.window.data_request()

    # ------------------------------------------------------------ reading
    def _connected(self) -> bool:
        from jdxi_editor.midi.io.connection import can_talk

        return can_talk(self.midi_helper)

    def _quiet(self) -> bool:
        """Nothing in the way of a reading: no playback, no recent input, app shown."""
        if getattr(self, "_stopped", False):
            return False
        if playback_activity().is_playing:
            return False
        if time.monotonic() - self._last_input < QUIET_AFTER_INPUT_S:
            return False
        if QApplication.mouseButtons() != Qt.MouseButton.NoButton:
            return False
        if self.window.isMinimized():
            return False
        return True

    def current_part(self):
        part = getattr(self.window, "current_synth_type", None)
        return part if part in PARTS else None

    def poll(self) -> None:
        """Read the part shown again (its tone name, octave and the sliders' values)."""
        part = self.current_part()
        if part != self._part:
            self._part = part
            self._show_part_octave()
        if part is None or not self._connected() or not self._quiet():
            return
        self.request_part(part)

    def poll_now(self) -> None:
        """The part shown changed: read it straight away."""
        self._last_input = 0.0
        self.poll()

    def request_part(self, part) -> None:
        send_with_delay(self.midi_helper, PART_REQUESTS[part])

    # ------------------------------------------------------------ MIDI in
    def on_outgoing(self, message) -> None:
        """A value, note or program sent from the app: wait before reading."""
        data = self._bytes(message)
        if not data:
            return
        if data[0] == 0xF0 and len(data) > 7 and data[7] == 0x11:
            return  # a request (ours or an editor's)
        self._last_input = time.monotonic()
        if 0xC0 <= data[0] <= 0xCF:
            self._new_program()  # a program or tone chosen in the app

    def on_incoming(self, message) -> None:
        kind = getattr(message, "type", None)
        if kind in ("note_on", "note_off"):
            on = kind == "note_on" and getattr(message, "velocity", 0) > 0
            self.light_key(message.note, on, getattr(message, "channel", None))
            if on:
                self.follow_part(getattr(message, "channel", None))
        elif kind == "pitchwheel":
            self.show_wheel("pitch_wheel", value_from_pitch(message.pitch))
        elif kind == "control_change" and message.control == MODULATION_CC:
            self.show_wheel("mod_wheel", message.value / 127)
        elif kind == "control_change":
            self.knob_moved(message.channel, message.control, message.value)
        elif kind == "program_change":
            self._new_program()  # chosen on the JD-Xi
            channel = getattr(message, "channel", None)
            if channel == program_channel.channel():
                return  # a program (the window reads it again)
            for part, (part_channel, _tone, _zone) in PARTS.items():
                if channel == part_channel and self._connected():
                    self.request_part(part)
        elif kind == "sysex":
            parsed = parse_dt1(message.data)
            if parsed is not None:
                self.on_dt1(*parsed)

    def on_dt1(self, address: tuple, values: list) -> None:
        if address[:3] == SYSTEM_COMMON:
            self._system_read(address, values)
            return
        for part, (_channel, tone, zone) in PARTS.items():
            tone_octave = None
            if part in (JDXiSynth.DIGITAL_SYNTH_1, JDXiSynth.DIGITAL_SYNTH_2):
                tone_octave = _value_at(address, values, (TEMPORARY_TONE, tone, 0x00), DIGITAL_COMMON_OCTAVE)
                self._show_sliders(part, address, values, (TEMPORARY_TONE, tone, PARTIAL_1), DIGITAL_SLIDERS)
            elif part == JDXiSynth.ANALOG_SYNTH:
                tone_octave = _value_at(address, values, (TEMPORARY_TONE, tone, 0x00), ANALOG_OCTAVE)
                self._show_sliders(part, address, values, (TEMPORARY_TONE, tone, 0x00), ANALOG_SLIDERS)
            zone_octave = _value_at(address, values, (TEMPORARY_PROGRAM, 0x00, zone), ZONE_OCTAVE)
            if tone_octave is not None:
                self._octave_read(part, self._tone_octave, tone_octave - OCTAVE_CENTRE)
            if zone_octave is not None:
                self._octave_read(part, self._zone_octave, zone_octave - OCTAVE_CENTRE)

    # ------------------------------------------------------------ system
    def _system_read(self, address, values) -> None:
        found = [
            _value_at(address, values, SYSTEM_COMMON, offset)
            for offset in (PROGRAM_CTRL_CH, RX_PROGRAM_CHANGE, RX_BANK_SELECT)
        ]
        if None in found:
            return
        program_channel.set_from_system(*found)
        problem = program_channel.problem()
        if problem:
            text = (
                f"The JD-Xi does not take program changes ({problem}): "
                "on the JD-Xi, MENU › SYSTEM › MIDI"
            )
            log.warning(text, scope="InstrumentFollower")
            status = getattr(self.window, "statusBar", None)
            if callable(status):
                status().showMessage(text, 30000)
        elif program_channel.channel() != program_channel.DEFAULT:
            log.message(
                f"The JD-Xi takes program changes on channel {program_channel.channel() + 1}",
                scope="InstrumentFollower",
            )

    # ------------------------------------------------------------ part
    def follow_part(self, channel) -> None:
        """The JD-Xi plays its keyboard on the channel of the part selected on it:
        the window selects that part too, so its tone buttons, octave and sliders
        act on the part being played (they acted on the part selected in the app,
        and a tone chosen there was not heard until the two were aligned).

        Only after a few notes in a row on that channel, and not more than once
        in a while: a pattern playing several parts does not make it jump."""
        part = next((p for p, (ch, _t, _z) in PARTS.items() if ch == channel), None)
        recent = self._recent_channels
        recent.append(channel)
        del recent[:-FOLLOW_NOTES]
        if part is None or part == self.current_part():
            return
        if len(recent) < FOLLOW_NOTES or any(c != channel for c in recent):
            return
        now = time.monotonic()
        if now - self._part_followed_at < FOLLOW_PAUSE_S:
            return
        self._part_followed_at = now
        select = getattr(self.window, "_select_synth", None)
        if callable(select):
            select(part)

    # ------------------------------------------------------------ octave
    def _octave_read(self, part, store: Dict, octave: int) -> None:
        if not -3 <= octave <= 3:
            return
        before = store.get(part)
        store[part] = octave
        if part != self.current_part():
            return
        if before is None:  # first reading: the shift in use, whichever holds it
            self._show_part_octave()
        elif before != octave:  # changed on the JD-Xi: the one that moved
            self._show_octave(octave)

    def _show_part_octave(self) -> None:
        part = self.current_part()
        zone = self._zone_octave.get(part)
        tone = self._tone_octave.get(part)
        if zone is None and tone is None:
            return
        self._show_octave(zone if zone else (tone or 0))

    def _show_octave(self, octave: int) -> None:
        window = self.window
        if getattr(window, "current_octave", None) == octave:
            return
        window.current_octave = octave
        if hasattr(window, "_ui_update_octave"):
            window._ui_update_octave()

    # ------------------------------------------------------------ sliders
    def _show_sliders(self, part, address, values, block, offsets) -> None:
        if part != self.current_part():
            return
        sliders = getattr(self.window, "panel_sliders", None) or {}
        for name, offset in offsets.items():
            value = _value_at(address, values, block, offset)
            slider = sliders.get(name)
            if value is None or slider is None:
                continue
            if getattr(slider.slider, "isSliderDown", lambda: False)():
                continue  # being moved by hand
            slider.setValueSilently(value)
            if hasattr(slider, "update_style"):
                slider.update_style(value)

    def _new_program(self) -> None:
        """A program loads as saved: the ENV slider (relative to it) back to the middle."""
        slider = (getattr(self.window, "panel_sliders", None) or {}).get("envelope")
        reset = getattr(slider, "reset_to_neutral", None)
        if callable(reset) and not getattr(slider.slider, "isSliderDown", lambda: False)():
            reset()

    def knob_moved(self, channel: int, control: int, value: int) -> None:
        """A knob turned on the JD-Xi (CC or NRPN): the window's slider follows it
        at once; the editors get the value with the next reading."""
        if control == CC_NRPN_MSB:
            self._nrpn[channel] = [value, None]
            return
        if control == CC_NRPN_LSB:
            self._nrpn.setdefault(channel, [None, None])[1] = value
            return
        if control in KNOB_CC_EFFECTS:
            self._show_knob(KNOB_CC_EFFECTS[control], value)
            return
        part = self.current_part()
        if part is None or channel != PARTS[part][0]:
            return  # another part's knobs, or a part not shown
        if control == CC_DATA_ENTRY:
            msb, lsb = self._nrpn.get(channel, [None, None])
            if msb is not None and lsb is not None and NRPN_NULL not in (msb, lsb):
                name = KNOB_NRPN.get((msb, lsb))
                if name:
                    self._show_knob(name, value)
        elif control in KNOB_CC:
            self._show_knob(KNOB_CC[control], value)

    def _show_knob(self, name: str, value: int) -> None:
        slider = (getattr(self.window, "panel_sliders", None) or {}).get(name)
        if slider is None or getattr(slider.slider, "isSliderDown", lambda: False)():
            return
        inner = slider.slider
        value = max(inner.minimum(), min(inner.maximum(), value))
        slider.setValueSilently(value)
        if hasattr(slider, "update_style"):
            slider.update_style(value)

    # ------------------------------------------------------------ keys
    def light_key(self, note: int, on: bool, channel: Optional[int] = None) -> None:
        """Light the window's key under the finger: with an octave shift the JD-Xi
        sends its keys an octave or more away, and the window's keyboard (always
        the 37 keys of the JD-Xi) shows the key that was pressed. A key lit stays
        the one turned off, also if the octave changes while it is held."""
        if on:
            keyboard = getattr(self.window, "piano_keyboard", None)
            keys = getattr(keyboard, "_keys_by_note", None) or {}
            key = keys.get(note - 12 * self.part_octave(channel))
            previous = self._lit.pop((channel, note), None)
            if previous is not None and previous is not key:
                previous.is_pressed = False
                previous.update()
            if key is None:
                return
            self._lit[(channel, note)] = key
        else:
            key = self._lit.pop((channel, note), None)
            if key is None:
                return
        key.is_pressed = on
        key.update()

    def show_wheel(self, name: str, value: float) -> None:
        """The window's pitch or mod wheel shows where the JD-Xi's is."""
        wheel = getattr(self.window, name, None)
        if wheel is not None and hasattr(wheel, "show_value"):
            wheel.show_value(value)

    def part_octave(self, channel: Optional[int]) -> int:
        """Octave shift of the part playing on *channel* (that of the part shown
        when the channel is not a part's)."""
        part = next((p for p, (ch, _t, _z) in PARTS.items() if ch == channel), None)
        if part is None or part == self.current_part():
            octave = getattr(self.window, "current_octave", 0)
            return octave if isinstance(octave, int) else 0
        zone = self._zone_octave.get(part)
        return zone if zone else (self._tone_octave.get(part) or 0)

    # ------------------------------------------------------------ app input
    def eventFilter(self, watched, event) -> bool:
        if event.type() in (
            QEvent.Type.MouseButtonPress,
            QEvent.Type.KeyPress,
            QEvent.Type.Wheel,
        ):
            self._last_input = time.monotonic()
        return False

    @staticmethod
    def _bytes(message):
        if hasattr(message, "bytes"):
            try:
                return message.bytes()
            except Exception:
                return None
        try:
            return [int(b) for b in message]
        except TypeError:
            return None
