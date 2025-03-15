from dataclasses import dataclass

from jdxi_editor.midi.data.constants import MIDI_CHANNEL_DIGITAL1
from jdxi_editor.midi.data.presets.type import PresetType


@dataclass
class PresetData:
    type: str = PresetType.DIGITAL_1  # Adjust the type as needed
    current_selection: int = 1
    modified: int = 0
    channel: int = MIDI_CHANNEL_DIGITAL1
