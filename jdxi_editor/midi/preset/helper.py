"""
Module: preset helper
=====================

This module provides the `PresetHelper` class, which handles loading and managing
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

from jdxi_editor.midi.data.constants.constants import MIDI_CHANNEL_ANALOG, MIDI_CHANNEL_DRUMS
from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST
from jdxi_editor.midi.data.programs.presets import DIGITAL_PRESET_LIST
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.data.constants.sysex import DEVICE_ID
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.sysex.requests import PROGRAM_TONE_NAME_PARTIAL_REQUESTS
from jdxi_editor.ui.editors.helpers.program import get_preset_parameter_value, log_midi_info


class PresetHelper(QObject):
    """Utility class for loading presets via MIDI"""

    update_display = Signal(int, int, int)

    def __init__(
        self, midi_helper: Optional[MidiIOHelper],
            device_number: int = DEVICE_ID,
            debug: bool = False
    ):
        super().__init__()
        self.midi_channel = None
        self.midi_requests = PROGRAM_TONE_NAME_PARTIAL_REQUESTS
        self.preset_number = 1  # Default preset
        self.midi_helper = midi_helper
        self.device_number = device_number
        self.debug = debug
        self.sysex_message = RolandSysEx()
        pub.subscribe(self.load_preset, "request_load_preset")

    def load_preset(self, preset_data):
        """Load the preset based on the provided data."""
        logging.info(f"Loading preset: {preset_data}")
        program_number, channel = preset_data.current_selection, preset_data.channel
        if channel == MIDI_CHANNEL_DRUMS:
            preset_list = DRUM_KIT_LIST
        elif channel == MIDI_CHANNEL_ANALOG:
            preset_list = ANALOG_PRESET_LIST
        else:
            preset_list = DIGITAL_PRESET_LIST        
        # Get MSB, LSB, PC values from the preset using get_preset_parameter_value
        msb = get_preset_parameter_value("msb", program_number, preset_list)
        lsb = get_preset_parameter_value("lsb", program_number, preset_list)
        pc = get_preset_parameter_value("pc", program_number, preset_list)

        if None in [msb, lsb, pc]:
            logging.error(f"Could not retrieve preset parameters for program {program_number}")
            return

        logging.info(f"retrieved msb, lsb, pc : {msb}, {lsb}, {pc}")
        log_midi_info(msb, lsb, pc)

        # Send bank select and program change
        # Note: PC is 0-based in MIDI, so subtract 1
        self.midi_helper.send_bank_select_and_program_change(
            channel,  # MIDI channel
            msb,  # MSB is already correct
            lsb,  # LSB is already correct
            pc - 2  # Convert 1-based PC to 0-based
        )
        self.data_request()

    def data_request(self):
        for midi_request in self.midi_requests:
            byte_list_message = bytes.fromhex(midi_request)
            self.midi_helper.send_raw_message(byte_list_message)
