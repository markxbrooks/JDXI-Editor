"""
Module: preset_helper
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

from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.data.programs.analog import ANALOG_PRESET_LIST
from jdxi_editor.midi.data.programs.drum import DRUM_KIT_LIST
from jdxi_editor.midi.data.programs.presets import DIGITAL_PRESET_LIST
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.preset.type import JDXISynth
from jdxi_editor.midi.preset.utils import get_preset_values
from jdxi_editor.midi.sysex.requests import PROGRAM_TONE_NAME_PARTIAL_REQUESTS
from jdxi_editor.ui.editors.helpers.program import log_midi_info


class PresetHelper(QObject):
    """Preset Loading Class"""

    # This can't be a singleton since there is 1 for each synth
    # _instance = None
    update_display = Signal(int, int, int)
    preset_changed = Signal(int, int)  # Signal emitted when preset changes

    # def __new__(cls, *args, **kwargs):
    #    if cls._instance is None:
    #        cls._instance = super(PresetHelper, cls).__new__(cls)
    #    return cls._instance

    def __init__(
        self, midi_helper, presets, channel=1, preset_type=JDXISynth.DIGITAL_1
    ):
        # if hasattr(self, '_initialized') and self._initialized:
        #    return
        super().__init__()
        self.presets = presets
        self.channel = channel
        self.type = preset_type
        self.preset_number = 1
        self.current_preset_zero_indexed = 0
        self.midi_requests = PROGRAM_TONE_NAME_PARTIAL_REQUESTS
        self.midi_helper = midi_helper
        self.sysex_message = RolandSysEx()
        self._initialized = True

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

    def load_preset_by_program_change(
        self, preset_index, synth_type=JDXISynth.DIGITAL_1
    ):
        """Load a preset using program change."""
        logging.info(f"Preset index: {preset_index}")
        preset_list_map = {
            JDXISynth.DIGITAL_1: DIGITAL_PRESET_LIST,
            JDXISynth.DIGITAL_2: DIGITAL_PRESET_LIST,
            JDXISynth.ANALOG: ANALOG_PRESET_LIST,
            JDXISynth.DRUMS: DRUM_KIT_LIST,
        }
        channel_map = {
            JDXISynth.DIGITAL_1: MidiChannel.DIGITAL1,
            JDXISynth.DIGITAL_2: MidiChannel.DIGITAL2,
            JDXISynth.ANALOG: MidiChannel.ANALOG,
            JDXISynth.DRUMS: MidiChannel.DRUM,
        }
        preset_list = preset_list_map.get(synth_type, DIGITAL_PRESET_LIST)
        channel = channel_map.get(synth_type, MidiChannel.DIGITAL1)

        msb, lsb, pc = get_preset_values(preset_index, preset_list)
        if None in [msb, lsb, pc]:
            return

        self.send_program_change(channel, msb, lsb, pc)

    def load_preset(self, preset_data):
        """Load the preset based on the provided data."""
        logging.info(f"Loading preset: {preset_data}")
        program_number, channel = preset_data.number, preset_data.channel

        # Select the correct preset list based on the channel
        preset_list = {
            MidiChannel.DRUM: DRUM_KIT_LIST,
            MidiChannel.ANALOG: ANALOG_PRESET_LIST,
        }.get(channel, DIGITAL_PRESET_LIST)

        msb, lsb, pc = get_preset_values(program_number, preset_list)
        if None in [msb, lsb, pc]:
            return

        self.send_program_change(channel, msb, lsb, pc)

    def data_request(self):
        for midi_request in self.midi_requests:
            byte_list_message = bytes.fromhex(midi_request)
            # time.sleep(0.075)  # 75ms delay
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
