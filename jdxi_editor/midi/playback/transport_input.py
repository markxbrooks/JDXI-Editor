"""
MIDI controller → transport action mapping.

Translates hardware transport controls (MiniLab CCs, VMX-8 note pads or, in
its CC mode, CCs) into play/pause/stop/record/seek commands. Each
controller's buttons are listed under ``transport`` in ``midi_controllers.json``
(see :mod:`jdxi_editor.midi.io.controller_map`). Kept separate from PlaybackEngine's MIDI
output stream: incoming messages never enter the file timeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Sequence, Union

import mido
from PySide6.QtCore import QObject, QTimer, Signal

from jdxi_editor.midi.io.controller_map import (
    CONTROLLER_PROFILES,
    MINILAB3,
    VMX8,
    ControllerProfile,
    TransportAction,
    TransportSpec,
)
from jdxi_editor.midi.io.controller_settings import load_transport_specs

__all__ = [
    "DEFAULT_TRANSPORT_BINDINGS",
    "MINILAB3_TRANSPORT_BINDINGS",
    "VMX8_TRANSPORT_BINDINGS",
    "MidiCCBinding",
    "MidiNoteBinding",
    "TransportAction",
    "TransportBinding",
    "TransportInputMapper",
    "bindings_for_profile",
    "bindings_from_specs",
    "notify_transport_bindings_changed",
    "saved_transport_bindings",
]

# Hold-seek defaults (critique: press-and-hold with configurable rate)
SEEK_TICK_MS = 50
SEEK_RATE = 4.0  # file-seconds advanced per wall-second while held
# Momentary buttons: value at or above this counts as pressed
CC_PRESS_THRESHOLD = 64


@dataclass(frozen=True)
class MidiNoteBinding:
    """Map one MIDI note on a channel to a transport action (e.g. VMX-8)."""

    action: TransportAction
    channel: int
    note: int


@dataclass(frozen=True)
class MidiCCBinding:
    """Map one control-change on a channel to a transport action (e.g. MiniLab)."""

    action: TransportAction
    channel: int
    control: int


TransportBinding = Union[MidiNoteBinding, MidiCCBinding]


def bindings_from_specs(specs: Iterable[TransportSpec]) -> tuple[TransportBinding, ...]:
    """
    Mapper bindings for transport buttons.

    :param specs: Iterable[TransportSpec]
    :return: tuple[TransportBinding, ...]
    """
    return tuple(
        MidiCCBinding(spec.action, spec.channel, spec.number)
        if spec.kind == "cc"
        else MidiNoteBinding(spec.action, spec.channel, spec.number)
        for spec in specs
    )


def bindings_for_profile(profile: ControllerProfile) -> tuple[TransportBinding, ...]:
    """
    The built-in transport bindings of one controller, from its ``transport``
    entries in ``midi_controllers.json``.

    :param profile: ControllerProfile
    :return: tuple[TransportBinding, ...]
    """
    return bindings_from_specs(profile.transport)


def saved_transport_bindings() -> tuple[TransportBinding, ...]:
    """
    Every controller's transport bindings, including buttons learnt in the
    MIDI Controller window.

    :return: tuple[TransportBinding, ...]
    """
    return tuple(
        binding
        for profile in CONTROLLER_PROFILES
        for binding in bindings_from_specs(load_transport_specs(profile=profile))
    )


class _TransportBindingsNotifier(QObject):
    """Tells running mappers that learnt transport buttons changed."""

    changed = Signal()


_notifier: Optional[_TransportBindingsNotifier] = None


def transport_bindings_notifier() -> _TransportBindingsNotifier:
    """
    The object whose ``changed`` signal fires when transport buttons are saved.

    :return: _TransportBindingsNotifier
    """
    global _notifier
    if _notifier is None:
        _notifier = _TransportBindingsNotifier()
    return _notifier


def notify_transport_bindings_changed() -> None:
    """
    Make every mapper using the saved bindings reload them.

    :return: None
    """
    transport_bindings_notifier().changed.emit()


# Arturia MiniLab 3 transport buttons (measured): CC press=127 / release=0
MINILAB3_TRANSPORT_BINDINGS: tuple[TransportBinding, ...] = bindings_for_profile(MINILAB3)

# SINCO VMX-8 transport buttons: notes 91-95 in its default mode, CCs 52-56
# (press 127 / release 0) in CC mode, all on channel 1
VMX8_TRANSPORT_BINDINGS: tuple[TransportBinding, ...] = bindings_for_profile(VMX8)

# Every controller's buttons, so any of them works without swapping maps
DEFAULT_TRANSPORT_BINDINGS: tuple[TransportBinding, ...] = tuple(
    binding
    for profile in CONTROLLER_PROFILES
    for binding in bindings_for_profile(profile)
)


class TransportInputMapper(QObject):
    """
    Translate controller note/CC messages into transport callbacks.

    Play / Pause / Stop / Record fire on press. Rewind and Fast Forward
    start a hold-seek on press and stop on release; release of other
    actions does nothing.

    Without explicit ``bindings`` the mapper uses every controller's saved
    buttons (:func:`saved_transport_bindings`) and reloads them when the MIDI
    Controller window saves a change.
    """

    def __init__(
        self,
        *,
        on_play: Optional[Callable[[], None]] = None,
        on_pause: Optional[Callable[[], None]] = None,
        on_stop: Optional[Callable[[], None]] = None,
        on_record: Optional[Callable[[], None]] = None,
        seek_seconds: Optional[Callable[[float], None]] = None,
        get_position: Optional[Callable[[], float]] = None,
        get_duration: Optional[Callable[[], float]] = None,
        bindings: Optional[Sequence[TransportBinding]] = None,
        seek_rate: float = SEEK_RATE,
        seek_tick_ms: int = SEEK_TICK_MS,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self.on_play = on_play
        self.on_pause = on_pause
        self.on_stop = on_stop
        self.on_record = on_record
        self.seek_seconds = seek_seconds
        self.get_position = get_position
        self.get_duration = get_duration
        self.seek_rate = float(seek_rate)
        self._note_bindings: dict[tuple[int, int], TransportAction] = {}
        self._cc_bindings: dict[tuple[int, int], TransportAction] = {}
        if bindings is None:
            # Saved bindings (including learnt buttons), kept up to date when
            # the MIDI Controller window changes them
            self.set_bindings(saved_transport_bindings())
            transport_bindings_notifier().changed.connect(self.reload_bindings)
        else:
            self.set_bindings(bindings)

        self._hold_action: Optional[TransportAction] = None
        self._seek_timer = QTimer(self)
        self._seek_timer.setInterval(max(1, int(seek_tick_ms)))
        self._seek_timer.timeout.connect(self._on_seek_tick)

    def set_bindings(self, bindings: Iterable[TransportBinding]) -> None:
        """Replace the note/CC → action maps."""
        notes: dict[tuple[int, int], TransportAction] = {}
        ccs: dict[tuple[int, int], TransportAction] = {}
        for binding in bindings:
            if isinstance(binding, MidiNoteBinding):
                notes[(binding.channel, binding.note)] = binding.action
            elif isinstance(binding, MidiCCBinding):
                ccs[(binding.channel, binding.control)] = binding.action
        self._note_bindings = notes
        self._cc_bindings = ccs

    def reload_bindings(self) -> None:
        """
        Pick up transport buttons saved since this mapper was made.

        :return: None
        """
        self.set_bindings(saved_transport_bindings())

    def handle_message(self, message: mido.Message) -> None:
        """
        Handle one incoming MIDI message from a hardware controller.

        :param message: Parsed mido message (note_on / note_off / control_change)
        """
        if message.type in ("note_on", "note_off"):
            self._handle_note(message)
        elif message.type == "control_change":
            self._handle_cc(message)

    def handle_controller_message(
        self, _port: str, message: mido.Message
    ) -> None:
        """Slot for ``ExternalControllerInput.message_received(port, message)``."""
        self.handle_message(message)

    def stop_hold(self) -> None:
        """Stop any active rewind/fast-forward hold."""
        self._hold_action = None
        if self._seek_timer.isActive():
            self._seek_timer.stop()

    def _handle_note(self, message: mido.Message) -> None:
        channel = getattr(message, "channel", None)
        note = getattr(message, "note", None)
        if channel is None or note is None:
            return
        action = self._note_bindings.get((channel, note))
        if action is None:
            return
        is_press = message.type == "note_on" and message.velocity > 0
        if is_press:
            self._on_press(action)
        else:
            self._on_release(action)

    def _handle_cc(self, message: mido.Message) -> None:
        channel = getattr(message, "channel", None)
        control = getattr(message, "control", None)
        if channel is None or control is None:
            return
        action = self._cc_bindings.get((channel, control))
        if action is None:
            return
        if message.value >= CC_PRESS_THRESHOLD:
            self._on_press(action)
        else:
            self._on_release(action)

    def _on_press(self, action: TransportAction) -> None:
        if action == TransportAction.PLAY:
            if self.on_play:
                self.on_play()
            return
        if action == TransportAction.PAUSE:
            if self.on_pause:
                self.on_pause()
            return
        if action == TransportAction.STOP:
            if self.on_stop:
                self.on_stop()
            return
        if action == TransportAction.RECORD:
            if self.on_record:
                self.on_record()
            return
        if action in (TransportAction.REWIND, TransportAction.FAST_FORWARD):
            self._hold_action = action
            if not self._seek_timer.isActive():
                self._seek_timer.start()
            self._on_seek_tick()

    def _on_release(self, action: TransportAction) -> None:
        if action in (TransportAction.REWIND, TransportAction.FAST_FORWARD):
            if self._hold_action == action:
                self.stop_hold()

    def _on_seek_tick(self) -> None:
        if self._hold_action is None:
            self.stop_hold()
            return
        if not self.seek_seconds or not self.get_position or not self.get_duration:
            return
        dt = self._seek_timer.interval() / 1000.0
        delta = self.seek_rate * dt
        if self._hold_action == TransportAction.REWIND:
            delta = -delta
        position = self.get_position()
        duration = max(0.0, self.get_duration())
        target = max(0.0, min(duration, position + delta))
        self.seek_seconds(target)
