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

from PySide6.QtCore import Signal

from jdxi_editor.midi.preset.type import SynthType
from jdxi_editor.midi.preset.helper import PresetHelper
from jdxi_editor.ui.editors.helpers.program import get_preset_parameter_value, log_midi_info


class PresetHandler(PresetHelper):
    """ Preset Loading Class """
    preset_changed = Signal(int, int)  # Signal emitted when preset changes

    def __init__(self, midi_helper, presets, device_number=0, channel=1, preset_type=SynthType.DIGITAL_1):
        super().__init__(midi_helper, device_number)  # Call PresetLoader's constructor
        self.presets = presets
        self.channel = channel
        self.type = preset_type
        self.current_preset_zero_based = 0

    def next_tone(self):
        """Increase the tone index and return the new preset."""
        if self.current_preset_zero_based < len(self.presets) - 1:
            self.current_preset_zero_based += 1
            self.load_preset_by_program_change(self.current_preset_zero_based)
            self.preset_changed.emit(self.current_preset_zero_based_index, self.channel)
            # self.update_display.emit(self.type, self.current_preset_zero_based_index, self.channel)  # convert to 1-based index
        return self.get_current_preset()

    def previous_tone(self):
        """Decrease the tone index and return the new preset."""
        if self.current_preset_zero_based > 0:
            self.current_preset_zero_based -= 1
            self.load_preset_by_program_change(self.current_preset_zero_based)
            self.preset_changed.emit(self.current_preset_zero_based, self.channel)
            # self.update_display.emit(self.type, self.current_preset_zero_based_index, self.channel)  # convert to 1-based index
        return self.get_current_preset()

    def get_current_preset(self):
        """Get the current preset details."""
        return {
            "index": self.current_preset_zero_based,
            "preset": self.presets[self.current_preset_zero_based],
            "channel": self.channel,
        }

    def get_available_presets(self):
        """Get the available presets."""
        return self.presets

    def save_preset(self, program_number: int, params):
        """Save the current preset to the preset list."""
        name = self.presets[program_number]
        print(f"name: \t{name}")
        print(f"params: \t{params}")
        self.preset_changed.emit(self.current_preset_zero_based, self.channel)
        self.update_display.emit(self.type, self.current_preset_zero_based, self.channel)
        return self.get_current_preset()

    def load_preset_by_program_change(self, preset_index):
        """Load a preset by program change."""
        logging.info(f"preset_index : {preset_index}")

        # Get MSB, LSB, PC values from the preset using get_preset_parameter_value
        msb = get_preset_parameter_value("msb", preset_index)
        lsb = get_preset_parameter_value("lsb", preset_index)
        pc = get_preset_parameter_value("pc", preset_index)

        if None in [msb, lsb, pc]:
            logging.error(f"Could not retrieve preset parameters for program {preset_index}")
            return

        logging.info(f"retrieved msb, lsb, pc : {msb}, {lsb}, {pc}")
        log_midi_info(msb, lsb, pc)

        # Send bank select and program change
        # Note: PC is 0-based in MIDI, so subtract 1
        self.midi_helper.send_bank_select_and_program_change(
            self.channel,  # MIDI channel
            msb,  # MSB is already correct
            lsb,  # LSB is already correct
            pc - 1  # Convert 1-based PC to 0-based
        )
        self.data_request()


