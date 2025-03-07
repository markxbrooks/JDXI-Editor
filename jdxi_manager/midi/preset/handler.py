"""
Module: preset_handler
======================

This module defines the `PresetHandler` class, which extends `PresetLoader` to manage
preset selection and navigation for a MIDI-enabled synthesizer.

Classes:
--------
- `PresetHandler`: Handles preset loading, switching, and signaling for UI updates.

Dependencies:
-------------
- `PySide6.QtCore` (Signal, QObject) for event-driven UI interaction.
- `jdxi_manager.data.presets.type.PresetType` for managing preset types.
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


from PySide6.QtCore import Signal

from jdxi_manager.data.presets.type import PresetType
from jdxi_manager.midi.preset.loader import PresetLoader


class PresetHandler(PresetLoader):
    """ Preset Loading Class """
    preset_changed = Signal(int, int)  # Signal emitted when preset changes

    def __init__(self, midi_helper, presets, device_number=0, channel=1, preset_type=PresetType.DIGITAL_1):
        super().__init__(midi_helper, device_number)  # Call PresetLoader's constructor
        self.presets = presets
        self.channel = channel
        self.type = preset_type
        self.current_preset_index = 0

    def next_tone(self):
        """Increase the tone index and return the new preset."""
        if self.current_preset_index < len(self.presets) - 1:
            self.current_preset_index += 1
            self.preset_changed.emit(self.current_preset_index, self.channel)
            self.update_display.emit(self.type, self.current_preset_index, self.channel)
        return self.get_current_preset()

    def previous_tone(self):
        """Decrease the tone index and return the new preset."""
        if self.current_preset_index > 0:
            self.current_preset_index -= 1
            self.preset_changed.emit(self.current_preset_index, self.channel)
            self.update_display.emit(self.type, self.current_preset_index, self.channel)
        return self.get_current_preset()

    def get_current_preset(self):
        """Get the current preset details."""
        return {
            "index": self.current_preset_index,
            "preset": self.presets[self.current_preset_index],
            "channel": self.channel,
        }
