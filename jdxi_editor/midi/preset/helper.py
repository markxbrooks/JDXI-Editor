"""
Module: preset_handler
======================

This module defines the `PresetHandler` class, which extends `PresetHelper` to manage
preset selection and navigation for a MIDI-enabled synthesizer.

Classes:
--------
- `PresetHandler`: Handles preset loading, switching, and signaling for UI updates.

Dependencies:
-------------
- `PySide6.QtCore` (Signal, QObject) for event-driven UI interaction.
- `jdxi_manager.midi.data.presets.type.PresetType` for managing preset types.
- `jdxi_manager.midi.preset.loader.PresetLoader` as the base class for preset loading.

Functionality:
--------------
- Loads presets via MIDI.
- Emits signals when a preset changes (`preset_changed`).
- Supports navigation through available presets (`next_tone`, `previous_tone`).
- Retrieves current preset details (`get_current_preset`).

Usage:
------
This class is typically used within a larger MIDI control application to handle
preset changes and communicate them to the UI and MIDI engine.

"""

import logging

from PySide6.QtCore import Signal, QObject

from jdxi_editor.midi.data.constants.constants import MIDI_CHANNEL_ANALOG, MIDI_CHANNEL_DRUMS
from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST
from jdxi_editor.midi.data.programs.presets import DIGITAL_PRESET_LIST
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.preset.type import SynthType
from jdxi_editor.midi.sysex.requests import PROGRAM_TONE_NAME_PARTIAL_REQUESTS
from jdxi_editor.ui.editors.helpers.program import get_preset_parameter_value, log_midi_info


def get_preset_values(preset_index, preset_list=DIGITAL_PRESET_LIST):
    """Retrieve MSB, LSB, and PC values for a given preset."""
    msb = get_preset_parameter_value("msb", preset_index, preset_list)
    lsb = get_preset_parameter_value("lsb", preset_index, preset_list)
    pc = get_preset_parameter_value("pc", preset_index, preset_list)

    if None in [msb, lsb, pc]:
        logging.error(f"Could not retrieve preset parameters for program {preset_index}")
        return None, None, None

    logging.info(f"Retrieved MSB, LSB, PC: {msb}, {lsb}, {pc}")
    return msb, lsb, pc


class PresetHelper(QObject):
    """ Preset Loading Class """
    update_display = Signal(int, int, int)
    preset_changed = Signal(int, int)  # Signal emitted when preset changes

    def __init__(self, midi_helper, presets, channel=1, preset_type=SynthType.DIGITAL_1):
        super().__init__()
        self.presets = presets
        self.channel = channel
        self.type = preset_type
        self.preset_number = 1
        self.current_preset_zero_indexed = 0
        self.midi_requests = PROGRAM_TONE_NAME_PARTIAL_REQUESTS
        self.midi_helper = midi_helper
        self.sysex_message = RolandSysEx()

    def next_tone(self):
        """Increase the tone index and return the new preset."""
        if self.current_preset_zero_indexed < len(self.presets) - 1:
            self.current_preset_zero_indexed += 1
            self.load_preset_by_program_change(self.current_preset_zero_indexed)
            self.preset_changed.emit(self.current_preset_zero_indexed, self.channel)
        return self.get_current_preset()

    def previous_tone(self):
        """Decrease the tone index and return the new preset."""
        if self.current_preset_zero_indexed > 0:
            self.current_preset_zero_indexed -= 1
            self.load_preset_by_program_change(self.current_preset_zero_indexed)
            self.preset_changed.emit(self.current_preset_zero_indexed, self.channel)
        return self.get_current_preset()

    def get_current_preset(self):
        """Get the current preset details."""
        return {
            "index": self.current_preset_zero_indexed,
            "preset": self.presets[self.current_preset_zero_indexed],
            "channel": self.channel,
        }

    def get_available_presets(self):
        """Get the available presets."""
        return self.presets

    def load_preset_by_program_change(self, preset_index):
        """Load a preset using program change."""
        logging.info(f"Preset index: {preset_index}")

        msb, lsb, pc = get_preset_values(preset_index)
        if None in [msb, lsb, pc]:
            return

        self.send_program_change(self.channel, msb, lsb, pc)

    def load_preset(self, preset_data):
        """Load the preset based on the provided data."""
        logging.info(f"Loading preset: {preset_data}")
        program_number, channel = preset_data.current_selection, preset_data.channel

        # Select the correct preset list based on the channel
        preset_list = {
            MIDI_CHANNEL_DRUMS: DRUM_KIT_LIST,
            MIDI_CHANNEL_ANALOG: ANALOG_PRESET_LIST
        }.get(channel, DIGITAL_PRESET_LIST)

        msb, lsb, pc = get_preset_values(program_number, preset_list)
        if None in [msb, lsb, pc]:
            return

        self.send_program_change(channel, msb, lsb, pc)

    def data_request(self):
        for midi_request in self.midi_requests:
            byte_list_message = bytes.fromhex(midi_request)
            self.midi_helper.send_raw_message(byte_list_message)

    def send_program_change(self, channel, msb, lsb, pc):
        """Send a Bank Select and Program Change message."""
        log_midi_info(msb, lsb, pc)

        if pc is None:
            logging.error("Program Change value is None, aborting.")
            return

        # Convert 1-based PC to 0-based
        self.midi_helper.send_bank_select_and_program_change(channel, msb, lsb, pc - 1)
        self.data_request()

