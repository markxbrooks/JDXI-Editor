from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.jdxi.preset.lists import JDXiPresetToneList
from jdxi_editor.jdxi.synth.type import JDXiSynth


class JDXiPresetManager:
    _instance = None
    """Singleton class to manage presets."""

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(JDXiPresetManager, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Initialize tone-related attributes
        self.current_preset_number = 1
        self.current_preset_index = self.current_preset_number - 1
        self.current_preset_name = "Init Tone"
        self.current_preset_names = {
            JDXiSynth.DIGITAL_SYNTH_1: "Init Tone",
            JDXiSynth.DIGITAL_SYNTH_2: "Init Tone",
            JDXiSynth.ANALOG_SYNTH: "Init Tone",
            JDXiSynth.DRUM_KIT: "Init Tone",
        }
        self.preset_channel_map = {
            MidiChannel.ANALOG_SYNTH: JDXiPresetToneList.ANALOG_ENUMERATED,
            MidiChannel.DIGITAL_SYNTH_1: JDXiPresetToneList.DIGITAL_ENUMERATED,
            MidiChannel.DIGITAL_SYNTH_2: JDXiPresetToneList.DIGITAL_ENUMERATED,
            MidiChannel.DRUM_KIT: JDXiPresetToneList.DRUM_ENUMERATED,
        }
        self.preset_synth_map = {
            JDXiSynth.ANALOG_SYNTH: JDXiPresetToneList.ANALOG_ENUMERATED,
            JDXiSynth.DIGITAL_SYNTH_1: JDXiPresetToneList.DIGITAL_ENUMERATED,
            JDXiSynth.DIGITAL_SYNTH_2: JDXiPresetToneList.DIGITAL_ENUMERATED,
            JDXiSynth.DRUM_KIT: JDXiPresetToneList.DRUM_ENUMERATED,
        }

    def get_preset_name_by_type_and_index(
        self, synth_type: JDXiSynth, preset_index: int
    ) -> str:
        """
        Get the name of the currently selected preset

        :param synth_type: JDXISynth The type of synth
        :param preset_index: int The index of the preset
        :return: str The name of the preset
        """
        try:
            presets = self.preset_synth_map.get(
                synth_type, JDXiPresetToneList.DIGITAL_ENUMERATED
            )
            preset_name = presets[preset_index]
            log.message(f"preset_name: {preset_name}")
            return preset_name
        except IndexError:
            return "Index Error for current preset"

    def get_presets_for_synth(self, synth: JDXiSynth) -> JDXiPresetToneList:
        """
        Get the available presets for the given synth type.

        :param synth: JDXISynth The type of synth
        :return: JDXIPresets The available presets
        """
        presets = self.preset_synth_map.get(synth, JDXiPresetToneList.DIGITAL_ENUMERATED)
        return presets

    def get_presets_for_channel(self, channel: MidiChannel) -> JDXiPresetToneList:
        """
        Get the available presets for the given channel.

        :param channel: MidiChannel The MIDI channel
        :return: JDXIPresets The available presets
        """
        presets = self.preset_channel_map.get(channel, JDXiPresetToneList.DIGITAL_ENUMERATED)
        return presets

    def set_current_preset_name(self, preset_name: str):
        """
        Set the current global tone name.

        :param preset_name: str The name of the preset
        """
        self.current_preset_name = preset_name
        self._update_display()

    def set_preset_name_by_type(self, preset_type: str, preset_name: str):
        """
        Set the preset name for a specific tone type.

        :param preset_type: str The type of preset
        :param preset_name: str The name of the preset
        """
        if preset_type in self.current_preset_names:
            self.current_preset_names[preset_type] = preset_name
            self._update_display()

    def get_preset_name_by_type(self, tone_type: JDXiSynth) -> str:
        """
        Get the tone name for a specific tone type.

        :param tone_type: JDXISynth The type of tone
        :return: str The name of the tone
        """
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
