"""
External controller input
=========================

MIDI input from a hardware controller such as the Arturia MiniLab 3, separate
from the JD-Xi's. Its messages are shown in the MIDI Monitor and its control
changes are emitted as :attr:`ExternalControllerInput.control_changed`; they
are not passed to the JD-Xi input handler, so editors do not mistake a knob
turn for the synth reporting a change.

Every port the controller exposes is opened, not just the one that looks like
its main port: a MiniLab 3 sends its knobs and faders on the port belonging to
its current mode (Arturia, DAW, Analog Lab), so listening to one port means a
knob turn is missed whenever the device is in another mode. Each port is parsed
separately, because a MIDI parser carries running status from one message to
the next and two interleaved streams would corrupt each other.

:meth:`ExternalControllerInput.rescan` picks up a controller plugged in after
the application started.

RtMidi callbacks must not call into Qt: on macOS, emitting signals (or any
Qt work) from the MIDI thread while another port is still opening deadlocks
CoreMIDI. Incoming bytes are queued and drained on the GUI thread instead.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Optional

import mido
import rtmidi
from decologr import Decologr as log
from PySide6.QtCore import QObject, QTimer, Signal

from jdxi_editor.midi.io.controller_map import find_controller_ports

# How often the GUI thread drains messages queued by RtMidi callbacks.
_PUMP_INTERVAL_MS = 5
# CoreMIDI can deadlock if several ports are opened back-to-back while the
# JD-Xi input is already open; yield to the event loop between opens.
_PORT_OPEN_STAGGER_MS = 50


class ExternalControllerInput(QObject):
    """MIDI input from a hardware controller."""

    #: (port name, mido.Message) for every message received
    message_received = Signal(str, object)
    #: channel (0-15), control (0-127), value (0-127)
    control_changed = Signal(int, int, int)
    #: names of the ports currently listened to, whenever that set changes
    ports_changed = Signal(list)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        """
        Create the input; no port is opened until :meth:`auto_connect`.

        :param parent: Optional[QObject] Qt parent
        """
        super().__init__(parent)
        #: port name -> open RtMidi input
        self._inputs: dict[str, rtmidi.MidiIn] = {}
        #: port name -> parser, kept per port so streams cannot corrupt each other
        self._parsers: dict[str, mido.Parser] = {}
        #: kept for listing ports, so rescanning does not open a MIDI client
        #: of its own every few seconds
        self._probe = rtmidi.MidiIn()
        #: main controller port, or None; also the port reported to the monitor
        self.port_name: Optional[str] = None
        #: (port, mido.Message) written by the RtMidi thread, read by the GUI pump
        self._pending: deque[tuple[str, mido.Message]] = deque()
        self._pump = QTimer(self)
        self._pump.setInterval(_PUMP_INTERVAL_MS)
        self._pump.timeout.connect(self._emit_pending)
        #: port names still waiting for a staggered open
        self._ports_to_open: list[str] = []

    @property
    def port_names(self) -> list[str]:
        """
        Names of every controller port being listened to.

        :return: list[str]
        """
        return list(self._inputs)

    @property
    def is_open(self) -> bool:
        """
        Whether any controller port is open.

        :return: bool
        """
        return bool(self._inputs)

    def available_ports(self) -> list[str]:
        """
        Names of all MIDI input ports.

        :return: list[str]
        """
        return self._probe.get_ports()

    def auto_connect(self) -> bool:
        """
        Open every supported controller port that is connected.

        :return: bool True if at least one controller port was opened
        """
        ports = find_controller_ports(self.available_ports())
        if not ports:
            log.message(
                "No external MIDI controller found", scope=self.__class__.__name__
            )
            return False
        return self.connect_ports(ports)

    def connect_ports(self, port_names: list[str]) -> bool:
        """
        Listen to exactly ``port_names``, closing any other port already open.

        New ports are opened one at a time on a timer so CoreMIDI can breathe
        between opens (opening several back-to-back next to an active JD-Xi
        input deadlocks on macOS). Callbacks are installed only after each
        port's ``open_port`` returns. :attr:`ports_changed` is emitted when
        the batch finishes.

        :param port_names: list[str] MIDI input port names
        :return: bool True if a port is already open or a batch was started
        """
        wanted = list(port_names)
        for name in self.port_names:
            if name not in wanted:
                self._close_port(name)
        self._ports_to_open = [n for n in wanted if n not in self._inputs]
        self.port_name = next(iter(self._inputs), None)
        if not self._ports_to_open:
            if self._inputs:
                if not self._pump.isActive():
                    self._pump.start()
            else:
                self._pump.stop()
            return self.is_open
        # Kick the first open on the next event-loop turn so callers (startup,
        # rescan) are never inside open_port on the same stack as identify.
        QTimer.singleShot(0, self._open_next_port)
        return True

    def _open_next_port(self) -> None:
        """
        Open the next queued controller port, then schedule the rest.

        :return: None
        """
        if not self._ports_to_open:
            self._finish_port_batch()
            return
        name = self._ports_to_open.pop(0)
        self._open_port(name, install_callback=True)
        self.port_name = next(iter(self._inputs), None)
        if self._ports_to_open:
            QTimer.singleShot(_PORT_OPEN_STAGGER_MS, self._open_next_port)
        else:
            self._finish_port_batch()

    def _finish_port_batch(self) -> None:
        """
        Start the GUI pump and announce the ports now listened to.

        :return: None
        """
        self.port_name = next(iter(self._inputs), None)
        if self._inputs:
            if not self._pump.isActive():
                self._pump.start()
            log.message(
                f"Listening to external controller: {', '.join(self.port_names)}",
                scope=self.__class__.__name__,
            )
        else:
            self._pump.stop()
        self.ports_changed.emit(self.port_names)

    def connect_port(self, port_name: str) -> bool:
        """
        Listen to ``port_name`` alone, closing any port already open.

        :param port_name: str MIDI input port name
        :return: bool True if the port was opened
        """
        return self.connect_ports([port_name])

    def rescan(self) -> list[str]:
        """
        Match the open ports to what is plugged in now.

        Opens controller ports that have appeared since the last scan and drops
        ones that have gone, so a controller connected after startup is picked
        up. :attr:`ports_changed` is emitted when the open set changes (after
        any staggered opens finish).

        :return: list[str] names of the ports already open (new ones may still
            be opening)
        """
        if self._ports_to_open:
            return self.port_names
        wanted = find_controller_ports(self.available_ports())
        if set(wanted) == set(self.port_names):
            return self.port_names
        before = list(self.port_names)
        self.connect_ports(wanted)
        # Stub/sync backends finish inside connect_ports; real opens emit from
        # _finish_port_batch once the stagger completes.
        if not self._ports_to_open and set(self.port_names) != set(before):
            self.ports_changed.emit(self.port_names)
        return self.port_names

    def close(self) -> None:
        """
        Close every controller port.

        :return: None
        """
        self._pump.stop()
        self._ports_to_open = []
        for name in self.port_names:
            self._close_port(name)
        self.port_name = None
        self._pending.clear()

    def _open_port(
        self, port_name: str, *, install_callback: bool = True
    ) -> bool:
        """
        Open one port and listen to it, if it is not open already.

        :param port_name: str MIDI input port name
        :param install_callback: bool if False, only open the port; callbacks
            are installed later once every port in the batch is open
        :return: bool True if the port is open afterwards
        """
        if port_name in self._inputs:
            return True
        midi_in = rtmidi.MidiIn()
        try:
            midi_in.open_port(midi_in.get_ports().index(port_name))
        except (ValueError, rtmidi.RtMidiError) as ex:
            log.error(
                f"Could not open controller port {port_name}: {ex}",
                scope=self.__class__.__name__,
            )
            return False
        midi_in.ignore_types(sysex=True, timing=True, active_sense=True)
        self._inputs[port_name] = midi_in
        self._parsers[port_name] = mido.Parser()
        if install_callback:
            self._install_callback(port_name)
            if not self._pump.isActive():
                self._pump.start()
        return True

    def _install_callback(self, port_name: str) -> None:
        """
        Attach the shared RtMidi callback to an already-open port.

        :param port_name: str MIDI input port name
        :return: None
        """
        midi_in = self._inputs.get(port_name)
        if midi_in is None:
            return
        # RtMidi hands the user data back to the callback: the port's name, so
        # one callback can serve every port and tag what it receives.
        midi_in.set_callback(self._on_midi, port_name)

    def _close_port(self, port_name: str) -> None:
        """
        Close one port.

        :param port_name: str MIDI input port name
        :return: None
        """
        midi_in = self._inputs.pop(port_name, None)
        self._parsers.pop(port_name, None)
        if midi_in is None:
            return
        try:
            midi_in.cancel_callback()
            midi_in.close_port()
        except Exception as ex:  # a port that has gone can refuse to close
            log.message(
                f"Controller port {port_name} closed with {type(ex).__name__}: {ex}",
                scope=self.__class__.__name__,
                silent=True,
            )
        if self.port_name == port_name:
            self.port_name = next(iter(self._inputs), None)
        if not self._inputs:
            self._pump.stop()

    def _on_midi(self, event: tuple[list[int], float], data: Any = None) -> None:
        """
        RtMidi callback: parse raw bytes into a queue for the GUI thread.

        Must not emit Qt signals or touch widgets — that deadlocks CoreMIDI
        when ports are still opening.

        :param event: tuple[list[int], float] raw bytes and delta time
        :param data: Any the port's name, passed to RtMidi when the port opened
        :return: None
        """
        raw, _delta = event
        port = data if isinstance(data, str) else (self.port_name or "")
        try:
            parser = self._parsers.setdefault(port, mido.Parser())
            parser.feed(raw)
            for message in parser:
                self._pending.append((port, message))
        except Exception as ex:
            log.error(
                f"Error reading controller message {raw}: {type(ex).__name__}: {ex}",
                scope=self.__class__.__name__,
            )

    def _emit_pending(self) -> None:
        """
        Drain the RtMidi queue and emit signals on the GUI thread.

        :return: None
        """
        while self._pending:
            port, message = self._pending.popleft()
            self.message_received.emit(port, message)
            if message.type == "control_change":
                self.control_changed.emit(
                    message.channel, message.control, message.value
                )
