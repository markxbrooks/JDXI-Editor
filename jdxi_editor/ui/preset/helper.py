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
preset changes and communicate them to the UI and MIDI name.

"""

import threading

from decologr import Decologr as log
from PySide6.QtCore import QObject, Signal

#: The only Bank Select MSBs the JD-Xi has for its tones: SuperNATURAL
#: digital (95), analog (94) and drum kits (86) -- the complete set found in
#: jdxi_editor/ui/preset/tone/*/list.py. A SoundFont's preset list carries GM
#: banks instead (MSB 0, LSB 0, and a GM program number), because it describes
#: the .sf2 FluidSynth plays, not the instrument. Sent to a JD-Xi those pick a
#: bank it does not have, and it answers with an error.
JDXI_TONE_BANK_MSB = frozenset({86, 94, 95})

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.core.synth.type import JDXiSynth
from jdxi_editor.log.midi_info import log_midi_info
from jdxi_editor.midi.channel.channel import MidiChannel
from jdxi_editor.midi.io.delay import send_with_delay
from jdxi_editor.midi.sysex.request.midi_requests import MidiRequests
from jdxi_editor.ui.editors.helpers.preset import preset_to_jdxi_bank_pc
from jdxi_editor.ui.preset.button import JDXiPresetButtonData
from jdxi_editor.ui.preset.utils import get_preset_values


class JDXiPresetHelper(QObject):
    """Preset Loading Class"""

    update_display = Signal(int, int, int)
    preset_changed = Signal(int, int)  # Signal emitted when preset changes

    def __init__(
        self, midi_helper, presets, channel=1, preset_type=JDXiSynth.DIGITAL_SYNTH_1
    ):
        super().__init__()
        self.presets = presets
        self.channel = channel
        self.type = preset_type
        self.preset_number = 1
        self.current_preset_zero_indexed = 0
        self.midi_requests = MidiRequests.PROGRAM_TONE_NAME_PARTIAL
        self.midi_helper = midi_helper
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
        self, preset_index, synth_type=JDXiSynth.DIGITAL_SYNTH_1
    ):
        """Load a preset using program change."""
        log.message(f"Preset index: {preset_index}")
        preset_list_map = {
            JDXiSynth.DIGITAL_SYNTH_1: JDXi.UI.Preset.Digital.PROGRAM_CHANGE,
            JDXiSynth.DIGITAL_SYNTH_2: JDXi.UI.Preset.Digital.PROGRAM_CHANGE,
            JDXiSynth.ANALOG_SYNTH: JDXi.UI.Preset.Analog.PROGRAM_CHANGE,
            JDXiSynth.DRUM_KIT: JDXi.UI.Preset.Drum.PROGRAM_CHANGE,
        }
        channel_map = {
            JDXiSynth.DIGITAL_SYNTH_1: MidiChannel.DIGITAL_SYNTH_1,
            JDXiSynth.DIGITAL_SYNTH_2: MidiChannel.DIGITAL_SYNTH_2,
            JDXiSynth.ANALOG_SYNTH: MidiChannel.ANALOG_SYNTH,
            JDXiSynth.DRUM_KIT: MidiChannel.DRUM_KIT,
        }
        preset_list = preset_list_map.get(
            synth_type, JDXi.UI.Preset.Digital.PROGRAM_CHANGE
        )
        channel = channel_map.get(synth_type, MidiChannel.DIGITAL_SYNTH_1)

        msb, lsb, pc = get_preset_values(preset_index, preset_list)
        if None in [msb, lsb, pc]:
            return

        self.send_program_change(channel, msb, lsb, pc)

    def load_preset(self, preset_data: JDXiPresetButtonData):
        """
        Load the preset based on the provided data

        :param preset_data: JDXIPresetData
        :return: None
        """
        log.message(f"Loading preset: {preset_data}")
        program_number, channel = preset_data.number, preset_data.channel

        # Select the correct preset list based on the channel
        preset_list = {
            MidiChannel.DRUM_KIT: JDXi.UI.Preset.Drum.PROGRAM_CHANGE,
            MidiChannel.ANALOG_SYNTH: JDXi.UI.Preset.Analog.PROGRAM_CHANGE,
        }.get(channel, JDXi.UI.Preset.Digital.PROGRAM_CHANGE)

        msb, lsb, pc = get_preset_values(program_number, preset_list)
        if None in [msb, lsb, pc]:
            return

        self.send_program_change(channel, msb, lsb, pc)

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

    def send_program_change(self, channel: int, msb: int, lsb: int, pc: int) -> None:
        """
        Send a Bank Select and Program Change message

        :param channel: int
        :param msb: int
        :param lsb: int
        :param pc: int
        :return: None
        """
        log_midi_info(msb, lsb, pc)

        if pc is None:
            log.message("Program Change value is None, aborting.")
            return

        # The preset list is a SoundFont's when "Use SoundFont List" is on, and
        # its banks are the .sf2's, not the JD-Xi's. Sending those to the
        # instrument errors it, so say so plainly and send nothing rather than
        # putting a bank it has never heard of on the wire. The values come
        # from the preset data as floats or strings, hence the conversion.
        try:
            bank = int(float(msb))
        except (TypeError, ValueError):
            bank = None
        if bank not in JDXI_TONE_BANK_MSB:
            log.warning(
                scope="PresetHelper",
                message=(
                    f"Bank MSB {msb} is not a JD-Xi tone bank "
                    f"{sorted(JDXI_TONE_BANK_MSB)}, so nothing was sent. This "
                    f"preset list is a SoundFont's: turn off 'Use SoundFont "
                    f"List' in MIDI Configuration to play the JD-Xi's own tones."
                ),
            )
            return

        # Convert to JD-Xi bank format (LSB 65 for presets 129-256)
        bank_msb, bank_lsb, midi_pc = preset_to_jdxi_bank_pc(msb, lsb, pc)
        self.midi_helper.send_bank_select_and_program_change(
            channel, bank_msb, bank_lsb, midi_pc
        )
        # self.data_request() reducing midi flood
