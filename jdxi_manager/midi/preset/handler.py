from PySide6.QtCore import QObject, Signal
from jdxi_manager.data.presets.type import PresetType


class PresetHandler(QObject):
    preset_changed = Signal(int)  # Signal emitted when preset changes
    update_display = Signal(int, int, int)

    def __init__(self, presets, channel=1, type=PresetType.DIGITAL_1):
        super().__init__()
        self.presets = presets
        self.channel = channel
        self.type = type
        self.current_preset_index = 0

    def next_tone(self):
        """Increase the tone index and return the new preset."""
        if self.current_preset_index < len(self.presets) - 1:
            self.current_preset_index += 1
            self.preset_changed.emit(self.current_preset_index)  # Emit signal
            self.update_display.emit(
                self.type, self.current_preset_index, self.channel
            )  # Emit signal
        return self.get_current_preset()

    def previous_tone(self):
        """Decrease the tone index and return the new preset."""
        if self.current_preset_index < len(self.presets) - 1:
            self.current_preset_index -= 1
            self.preset_changed.emit(self.current_preset_index)  # Emit signal
            self.update_display.emit(
                self.type, self.current_preset_index, self.channel
            )  # Emit signal
        return self.get_current_preset()

    def get_current_preset(self):
        """Get the current preset details."""
        return {
            "index": self.current_preset_index,
            "preset": self.presets[self.current_preset_index],
            "channel": self.channel,
        }

    def set_channel(self, channel):
        """Set the MIDI channel."""
        self.channel = channel

    def set_preset(self, index):
        """Set the preset manually and emit the signal."""
        if 0 <= index < len(self.presets):
            self.current_preset_index = index
            self.preset_changed.emit(self.current_preset_index)
            self.update_display.emit(
                self.type, self.current_preset_index, self.channel
            )  # Emit signal
