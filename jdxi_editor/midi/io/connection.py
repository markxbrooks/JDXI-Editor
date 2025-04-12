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

import logging
from typing import Optional
from jdxi_editor.midi.sysex.device import DeviceInfo
from jdxi_editor.midi.message.identity_request import IdentityRequestMessage


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
        self.device_info: Optional[DeviceInfo] = None

    @property
    def midi_in(self):
        return self._midi_in

    @property
    def midi_out(self):
        return self._midi_out

    def initialize(self, midi_in, midi_out, main_window=None):
        """Initialize MIDI connections"""
        self._midi_in = midi_in
        self._midi_out = midi_out
        self._main_window = main_window
        self.identify_device()
        logging.debug("MIDI Connection singleton initialized")

    def send_message(self, message):
        """Send MIDI message and trigger indicator"""
        try:
            if self._midi_out:
                self._midi_out.send_raw_message(message)
                # Blink indicator if main window exists
                if self._main_window and hasattr(
                    self._main_window, "midi_out_indicator"
                ):
                    self._main_window.midi_out_indicator.blink()
                logging.debug(
                    f"Sent MIDI message: {' '.join([hex(b)[2:].upper().zfill(2) for b in message])}"
                )
            else:
                logging.warning("No MIDI output port available")

        except Exception as ex:
            logging.error(f"Error sending MIDI message: {str(ex)}")

    def identify_device(self) -> bool:
        """Send Identity Request and verify response"""
        request = IdentityRequestMessage()
        self.send_message(request)
        logging.info(f"sending identity request message: {request}")

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
