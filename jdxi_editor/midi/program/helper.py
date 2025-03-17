"""
Module: program_handler
======================

This module defines the `PresetHandler` class, which extends `PresetLoader` to manage
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
from typing import Optional

from PySide6.QtCore import Signal, QObject

from jdxi_editor.ui.editors.helpers.program import calculate_midi_values, get_program_by_id, \
    get_program_by_bank_and_number
from jdxi_editor.midi.io import MIDIHelper


class ProgramHelper(QObject):
    """ Preset Loading Class """
    program_changed = Signal(str, int)  # Signal emitted when preset changes bank, program

    def __init__(self, midi_helper: Optional[MIDIHelper], channel: int):
        super().__init__()
        self.midi_helper = midi_helper
        self.channel = channel
        self.current_bank_letter = "A"
        self.current_program_number = 1
        self.digital_1_preset = None
        self.digital_2_preset = None
        self.drums_preset = None
        self.analog_preset = None
        self.midi_requests = [
            "F0 41 10 00 00 00 0E 11 18 00 00 00 00 00 00 40 26 F7",  # Program common
            "F0 41 10 00 00 00 0E 11 19 01 00 00 00 00 00 40 26 F7",  # digital common controls
            "F0 41 10 00 00 00 0E 11 19 01 20 00 00 00 00 3D 09 F7",  # digital partial 1 request
            "F0 41 10 00 00 00 0E 11 19 01 21 00 00 00 00 3D 08 F7",  # digital partial 2 request
            "F0 41 10 00 00 00 0E 11 19 01 22 00 00 00 00 3D 07 F7",  # digital partial 3 request
            "F0 41 10 00 00 00 0E 11 19 01 50 00 00 00 00 25 71 F7",  # digital modify request
            "F0 41 10 00 00 00 0E 11 19 42 00 00 00 00 00 40 65 F7"   # analog request
        ]

    def next_program(self):
        """Increase the tone index and return the new preset."""
        if self.current_program_number <64:
            self.current_program_number += 1
        elif self.current_bank_letter == "H":
            self.current_program_number = 1 # reset program number, wrap around to 1
            self.current_bank_letter = "A" # reset bank letter
        else:
            self.current_program_number = 1 # reset program number
            self.current_bank_letter = chr(ord(self.current_bank_letter) + 1)
        self.load_program(self.current_bank_letter, self.current_program_number)

    def previous_program(self):
        """Decrease the tone index and return the new preset."""
        if self.current_program_number > 1:
            self.current_program_number -= 1
        elif self.current_bank_letter == "A":
            self.current_program_number = 64 # wrap around to 64
            self.current_bank_letter = "H"
        else:
            self.current_program_number = 64 # wrap around to 64
            self.current_bank_letter = chr(ord(self.current_bank_letter) - 1)
        self.load_program(self.current_bank_letter, self.current_program_number)
    
    def get_current_program(self):
        return self.current_bank_letter, self.current_program_number
    
    def load_program(self, bank_letter: str, program_number: int):
        """ load program """
        self.current_bank_letter = bank_letter
        self.current_program_number = program_number
        self.program_changed.emit(bank_letter, program_number)
        msb, lsb, pc = calculate_midi_values(bank_letter, program_number)
        logging.info(f"calculated msb, lsb, pc : {msb}, {lsb}, {pc} ")
        self.midi_helper.send_bank_select_and_program_change(self.channel, msb, lsb, pc)
        program_details = get_program_by_bank_and_number(bank_letter, program_number)
        logging.info(program_details)
        self.data_request()
        # self.update_current_synths(program_details)

    def data_request(self):
        for midi_request in self.midi_requests:
            byte_list_message = bytes.fromhex(midi_request)
            self.midi_helper.send_raw_message(byte_list_message)
