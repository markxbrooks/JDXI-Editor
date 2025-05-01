import logging

from jdxi_editor.log.message import log_message
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.jdxi.preset.lists import JDXIPresets
from jdxi_editor.jdxi.synth.type import JDXISynth


class JDXIPresetManager:
    _instance = None
    """Singleton class to manage presets."""
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(JDXIPresetManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialize tone-related attributes
        self.current_preset_number = 1
        self.current_preset_index = self.current_preset_number - 1
        self.current_preset_name = "Init Tone"
        self.current_preset_names = {
            JDXISynth.DIGITAL_1: "Init Tone",
            JDXISynth.DIGITAL_2: "Init Tone",
            JDXISynth.ANALOG: "Init Tone",
            JDXISynth.DRUM: "Init Tone"
        }
        self.preset_channel_map = {
            MidiChannel.ANALOG: JDXIPresets.ANALOG_ENUMERATED,
            MidiChannel.DIGITAL1: JDXIPresets.DIGITAL_ENUMERATED,
            MidiChannel.DIGITAL2: JDXIPresets.DIGITAL_ENUMERATED,
            MidiChannel.DRUM: JDXIPresets.DRUM_ENUMERATED,
        }
        self.preset_synth_map = {
            JDXISynth.ANALOG: JDXIPresets.ANALOG_ENUMERATED,
            JDXISynth.DIGITAL_1: JDXIPresets.DIGITAL_ENUMERATED,
            JDXISynth.DIGITAL_2: JDXIPresets.DIGITAL_ENUMERATED,
            JDXISynth.DRUM: JDXIPresets.DRUM_ENUMERATED,
        }

    def get_preset_name_by_type_and_index(self, synth_type: JDXISynth, preset_index: int) -> str:
        """Get the name of the currently selected preset"""
        try:
            presets = self.preset_synth_map.get(synth_type, JDXIPresets.DIGITAL_ENUMERATED)
            preset_name = presets[preset_index]
            log_message(f"preset_name: {preset_name}")
            return preset_name
        except IndexError:
            return "Index Error for current preset"

    def get_presets_for_synth(self, synth: JDXISynth) -> JDXIPresets:
        """Get the available presets for the given synth type."""
        presets = self.preset_synth_map.get(synth, JDXIPresets.DIGITAL_ENUMERATED)
        return presets

    def get_presets_for_channel(self, channel: MidiChannel) -> JDXIPresets:
        """Get the available presets for the given channel."""
        presets = self.preset_channel_map.get(channel, JDXIPresets.DIGITAL_ENUMERATED)
        return presets

    def set_current_preset_name(self, preset_name: str):
        """Set the current global tone name."""
        self.current_preset_name = preset_name
        self._update_display()

    def set_preset_name_by_type(self, preset_type: str, preset_name: str):
        """Set the tone name for a specific tone type."""
        if preset_type in self.current_preset_names:
            self.current_preset_names[preset_type] = preset_name
            self._update_display()

    def get_preset_name_by_type(self, tone_type: JDXISynth) -> str:
        """Get the tone name for a specific tone type."""
        return self.current_preset_names.get(tone_type, "Unknown Tone")

    def reset_all_presets(self):
        """Reset all tone names to 'Init Tone'."""
        self.current_preset_number = 1
        self.current_preset_name = "Init Tone"
        for tone_type in self.current_preset_names:
            self.current_preset_names[tone_type] = "Init Tone"
        self._update_display()

    def _update_display(self):
        """Update the display."""
        # Implementation for updating the display
        pass
