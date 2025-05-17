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

import threading
from typing import Optional

from PySide6.QtCore import Signal, QObject

from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.io.delay import send_with_delay
from jdxi_editor.midi.program.utils import (
    get_previous_program_bank_and_number,
    get_next_program_bank_and_number,
)
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.ui.editors.helpers.program import (
    calculate_midi_values,
    get_program_by_bank_and_number,
)
from jdxi_editor.midi.io.helper import MidiIOHelper


class JDXiProgramHelper(QObject):
    """Preset Loading Class"""

    program_changed = Signal(
        str, int
    )  # Signal emitted when preset changes bank, program
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(JDXiProgramHelper, cls).__new__(cls)
        return cls._instance

    def __init__(self, midi_helper: Optional[MidiIOHelper], channel: int):
        if not hasattr(self, "_initialized"):
            super().__init__()
            self.midi_helper = midi_helper
            self.channel = channel
            self.current_bank_letter = "A"
            self.current_program_number = 1
            self.digital_1_preset = None
            self.digital_2_preset = None
            self.drums_preset = None
            self.analog_preset = None
            self.midi_requests = MidiRequests.PROGRAM_TONE_NAME_PARTIAL
            self._initialized = True

    def next_program(self):
        """Increase the tone index and load the new program"""
        (
            self.current_program_number,
            self.current_bank_letter,
        ) = get_next_program_bank_and_number(
            self.current_program_number, self.current_bank_letter
        )
        self.load_program(self.current_bank_letter, self.current_program_number)

    def previous_program(self):
        """Decrease the tone index and load the new program."""
        (
            self.current_bank_letter,
            self.current_program_number,
        ) = get_previous_program_bank_and_number(
            self.current_program_number, self.current_bank_letter
        )
        self.load_program(self.current_bank_letter,
                          self.current_program_number)

    def get_current_program(self) -> tuple[str, int]:
        """
        Get current program bank and number
        :return: tuple[str, int]
        """
        return self.current_bank_letter, self.current_program_number

    def load_program(self, bank_letter: str, program_number: int) -> None:
        """
        Load Program
        :param bank_letter: str
        :param program_number: int
        :return: None
        """
        self.current_bank_letter = bank_letter
        self.current_program_number = program_number
        self.program_changed.emit(bank_letter, program_number)
        msb, lsb, pc = calculate_midi_values(bank_letter, program_number)
        log.header_message(f"loading program {bank_letter} {program_number}")
        log.message("calculated msb, lsb, pc :")
        log.parameter("msb", msb)
        log.parameter("lsb", lsb)
        log.parameter("pc", pc)
        self.midi_helper.send_bank_select_and_program_change(self.channel, msb, lsb, pc)
        program_details = get_program_by_bank_and_number(bank_letter, program_number)
        log.message(program_details)
        self.data_request()

    def data_request(self) -> None:
        """
        Request the current value of the NRPN parameter from the device.
        """
        threading.Thread(
            target=send_with_delay,
            args=(
                self.midi_helper,
                self.midi_requests,
            ),
        ).start()
