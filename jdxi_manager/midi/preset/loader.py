"""
Module: preset loader
=====================

This module provides the `PresetLoader` class, which handles loading and managing
presets via MIDI for the Roland JD-Xi synthesizer. It utilizes SysEx messages to
communicate with the synthesizer and update parameter values.

Features:
---------
- Sends MIDI Program Change messages to select presets.
- Uses SysEx messages to modify parameter values and load presets.
- Handles different preset types (Digital1, Digital2, Analog, Drums).
- Emits signals to update the UI with the selected preset.

Dependencies:
-------------
- PySide6 for Qt-based signal handling.
- `pubsub` for event-driven communication.
- `jdxi_manager` package for MIDI handling and preset management.

Usage:
------
Instantiate `PresetLoader` with a `MIDIHelper` instance and subscribe to
preset loading requests. The class listens for `request_load_preset` events
to trigger preset changes.

Example:
--------
```python
midi_helper = MIDIHelper()
preset_loader = PresetLoader(midi_helper)
"""

import logging
from pubsub import pub
from typing import Optional
from PySide6.QtCore import Signal, QObject

from jdxi_manager.midi.io.helper import MIDIHelper
from jdxi_manager.midi.data.presets.type import PresetType
from jdxi_manager.midi.data.constants.sysex import DEVICE_ID
from jdxi_manager.midi.message.roland import RolandSysEx


class PresetLoader(QObject):
    """Utility class for loading presets via MIDI"""

    update_display = Signal(int, int, int)

    def __init__(
        self, midi_helper: Optional[MIDIHelper],
            device_number: int = DEVICE_ID,
            debug: bool = False
    ):
        super().__init__()
        self.preset_number = 1  # Default preset
        self.midi_helper = midi_helper
        self.device_number = device_number
        self.debug = debug
        self.sysex_message = RolandSysEx()
        pub.subscribe(self.load_preset, "request_load_preset")

    def send_parameter_change_message(self, address, value, nr):
        """Send a MIDI parameter change message."""
        logging.info(f"par:[{address}] val:[{value}] len:[{nr}]")
        data = bytes.fromhex(f"{value:0{nr}X}") if nr > 1 else bytes([value])

        # Use SysExMessage helper to construct and send the SysEx message
        self.send_sysex(
            [address[i : i + 2] for i in range(0, len(address), 2)],
            *[f"{b:02X}" for b in data],
            request=False,
        )

    def send_sysex(self, address, *data_bytes, request=False):
        """
        Construct and send a SysEx message.

        :param address: Address bytes in hex string format.
        :param data_bytes: Data bytes in hex string format.
        :param request: SysEx command type (DT1 for write, RQ1 for read).
        """
        message = self.sysex_message.construct_sysex(address, *data_bytes, request=request)
        self.midi_helper.send_message(message)
        logging.debug(f"Sent SysEx: {message}")

    def load_preset(self, preset_data):
        """Load the preset based on the provided data."""
        logging.info(f"Loading preset: {preset_data}")
        program, channel = preset_data["selpreset"], preset_data["channel"]
        self.midi_helper.send_program_change(program=program, channel=channel)

        if preset_data.get("modified", 0) == 0:
            address, msb, lsb = self.get_preset_address(preset_data)
            logging.info(
                f"address msb lsb {address} {msb} {lsb} self.preset_number: {self.preset_number}"
            )
            self.preset_number = program if program <= 128 else program - 128
            self.midi_helper.send_program_change(program, channel)
            self.send_parameter_change_message(address, msb, 1)
            self.send_parameter_change_message(f"{int(address, 16) + 1:08X}", lsb, 1)
            self.send_parameter_change_message(
                 f"{int(address, 16) + 2:08X}", self.preset_number, 1
            )

            # Send additional SysEx messages for preset loading
            self.send_preset_sysex_messages()

            self.update_display.emit(preset_data["preset_type"], program, channel)
            logging.info(f"Preset {program} loaded on channel {channel}")

    def get_preset_address(self, preset_data):
        """Retrieve the preset memory address based on its type."""
        preset_type = preset_data["preset_type"]
        address_map = {
            PresetType.DIGITAL_1: ("18002006", 95, 64),
            PresetType.DIGITAL_2: ("18002106", 95, 64),
            PresetType.ANALOG: ("18002206", 94, 64),
            PresetType.DRUMS: ("18002306", 86, 64),
        }

        address, msb, lsb = address_map.get(preset_type, (None, None, None))
        if address is None:
            raise ValueError("Invalid preset type")

        return address, msb, (65 if self.preset_number > 128 else lsb)

    def send_preset_sysex_messages(self):
        """Send additional SysEx messages for preset initialization."""
        sysex_rq1_data = [
            (["19", "01", "00", "00"], "00", "00", "00", "40"),
            (["19", "01", "20", "00"], "00", "00", "00", "3D"),
            (["19", "01", "21", "00"], "00", "00", "00", "3D"),
            (["19", "01", "22", "00"], "00", "00", "00", "3D"),
            (["19", "01", "50", "00"], "00", "00", "00", "25"),
        ]
        for address, *data in sysex_rq1_data:
            self.send_sysex(address, *data, request=True)
