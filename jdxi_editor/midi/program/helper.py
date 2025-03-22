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
from jdxi_editor.midi.io import MidiIOHelper


def get_previous_program_bank_and_number(program_number: int, bank_letter: str):
    """ get previous program bank number """
    if program_number > 1:
        program_number -= 1
    elif bank_letter == "A":
        program_number = 64  # wrap around to 64
        bank_letter = "H"
    else:
        program_number = 64  # wrap around to 64
        bank_letter = chr(ord(bank_letter) - 1)
    return bank_letter, program_number


def get_next_program_bank_and_number(program_number, bank_letter):
    if program_number < 64:
        program_number += 1
    elif bank_letter == "H":
        program_number = 1  # reset program number, wrap around to 1
        bank_letter = "A"  # reset bank letter
    else:
        program_number = 1  # reset program number
        bank_letter = chr(ord(bank_letter) + 1)
    return program_number, bank_letter


class ProgramHelper(QObject):
    """ Preset Loading Class """
    program_changed = Signal(str, int)  # Signal emitted when preset changes bank, program

    def __init__(self, midi_helper: Optional[MidiIOHelper], channel: int):
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
            "F0 41 10 00 00 00 0E 11 19 01 00 00 00 00 00 40 26 F7",  # digital1 common controls
            "F0 41 10 00 00 00 0E 11 19 01 20 00 00 00 00 3D 09 F7",  # digital1 partial 1 request
            "F0 41 10 00 00 00 0E 11 19 01 21 00 00 00 00 3D 08 F7",  # digital1 partial 2 request
            "F0 41 10 00 00 00 0E 11 19 01 22 00 00 00 00 3D 07 F7",  # digital1 partial 3 request
            "F0 41 10 00 00 00 0E 11 19 01 50 00 00 00 00 25 71 F7",  # digital1 modify request
            "F0 41 10 00 00 00 0E 11 19 21 00 00 00 00 00 40 06 F7",  # digital2 common controls
            "F0 41 10 00 00 00 0E 11 19 21 20 00 00 00 00 3D 69 F7",  # digital2 partial 1 request
            "F0 41 10 00 00 00 0E 11 19 21 21 00 00 00 00 3D 68 F7",  # digital2 partial 2 request
            "F0 41 10 00 00 00 0E 11 19 21 22 00 00 00 00 3D 67 F7",  # digital2 partial 3 request
            "F0 41 10 00 00 00 0E 11 19 21 50 00 00 00 00 25 51 F7",  # digital2 modify request
            "F0 41 10 00 00 00 0E 11 19 42 00 00 00 00 00 40 65 F7",  # analog request
            "F0 41 10 00 00 00 0E 11 19 70 00 00 00 00 00 12 65 F7",  # drums requests
            "F0 41 10 00 00 00 0E 11 19 70 00 00 00 00 00 12 65 F7",
            "F0 41 10 00 00 00 0E 11 19 70 2E 00 00 00 01 43 05 F7",
            "F0 41 10 00 00 00 0E 11 19 70 30 00 00 00 01 43 03 F7",
            "F0 41 10 00 00 00 0E 11 19 70 32 00 00 00 01 43 01 F7",
            "F0 41 10 00 00 00 0E 11 19 70 34 00 00 00 01 43 7F F7",
            "F0 41 10 00 00 00 0E 11 19 70 36 00 00 00 01 43 7D F7",
        ]

    def next_program(self):
        """Increase the tone index and return the new preset."""
        self.current_program_number, self.current_bank_letter = get_next_program_bank_and_number(
            self.current_program_number, self.current_bank_letter)
        self.load_program(self.current_bank_letter, self.current_program_number)

    def previous_program(self):
        """Decrease the tone index and return the new preset."""
        self.current_bank_letter, self.current_program_number = get_previous_program_bank_and_number(
            self.current_program_number, self.current_bank_letter)
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
