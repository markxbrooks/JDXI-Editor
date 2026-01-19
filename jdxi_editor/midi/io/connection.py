"""
MIDI Connection Singleton for JD-Xi

This module defines the `MIDIConnection` class, which serves as a singleton for managing
MIDI input and output connections with the Roland JD-Xi synthesizer. It provides methods
for sending MIDI messages, setting input callbacks, and identifying connected devices.

Features:
- Implements a singleton pattern to ensure a single MIDI connection instance.
- Manages MIDI input and output ports.
- Sends MIDI messages with an optional UI indicator blink.
- Sets a callback function for incoming MIDI messages.
- Sends an Identity Request to detect and verify the connected device.
- Retrieves firmware version information from the JD-Xi.

Dependencies:
- `rtmidi` for MIDI communication.
- `logging` for debugging and error handling.
- `DeviceInfo` and `IdentityRequest` for device identification.

Example Usage:
    midi_conn = MIDIConnection()
    midi_conn.initialize(midi_in, midi_out, main_window)
    midi_conn.send_message([0x90, 0x40, 0x7F])  # Send a Note On message
    if midi_conn.identify_device():
        print("Connected to JD-Xi:", midi_conn.device_version)
"""

from typing import Iterable, Optional

import rtmidi
from PySide6.QtWidgets import QMainWindow

from decologr import Decologr as log
from jdxi_editor.midi.message.identity_request.message import IdentityRequestMessage
from jdxi_editor.midi.sysex.device import DeviceInfo


class MIDIConnection:
    """Midi connection object"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MIDIConnection, cls).__new__(cls)
            cls._instance._midi_in = None
            cls._instance._midi_out = None
            cls._instance._main_window = None
        return cls._instance

    def __init__(self):
        self._midi_in = None
        self._midi_out = None
        self._main_window = None
        self.device_info: Optional[DeviceInfo] = None

    @property
    def midi_in(self):
        """Get MIDI input port"""
        return self._midi_in

    @property
    def midi_out(self):
        """Get MIDI output port"""
        return self._midi_out

    def initialize(
        self,
        midi_in: rtmidi.MidiIn,
        midi_out: rtmidi.MidiOut,
        main_window=Optional[QMainWindow],
    ) -> None:
        """
        Initialize MIDI connection with input and output ports

        :param midi_in: rtmidi.MidiIn
        :param midi_out: rtmidi.MidiOut
        :param main_window: Optional[QMainWindow] for UI interaction
        :return: None
        """
        self._midi_in = midi_in
        self._midi_out = midi_out
        self._main_window = main_window
        log.message("MIDI Connection singleton initialized")

    def send_message(self, message: Iterable[int]) -> None:
        """
        Send MIDI message and trigger indicator

        :param message: Iterable[int], MIDI message to send
        :return: None
        """
        try:
            if self._midi_out:
                self._midi_out.send_message(message)
                # --- Blink indicator if main window exists
                if self._main_window and hasattr(
                    self._main_window, "midi_out_indicator"
                ):
                    self._main_window.midi_out_indicator.blink()
                log.parameter("Sent MIDI message", message)
            else:
                log.warning("No MIDI output port available")

        except Exception as ex:
            log.error(f"Error sending MIDI message: {str(ex)}")

    def identify_device(self) -> None:
        """Send Identity Request and verify response"""
        request = IdentityRequestMessage()
        self.send_message(request)
        log.message(f"sending identity_request request message: {request}")

    @property
    def is_connected(self) -> bool:
        """Check if connected to JD-Xi"""
        return self.device_info is not None and self.device_info.is_jdxi

    @property
    def device_version(self) -> str:
        """Get device firmware version"""
        if self.device_info:
            return self.device_info.version_string
        return "unknown"
