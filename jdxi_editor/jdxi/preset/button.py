from dataclasses import dataclass
from typing import Optional

from jdxi_editor.jdxi.synth.type import JDXISynth
from jdxi_editor.midi.channel.channel import MidiChannel


@dataclass
class JDXIPresetButton:
    """
    A class representing a preset button in the JDXi editor.

    Attributes:
        type: The type of preset button.
        number: The number of the preset button.
        modified: The modified status of the preset button.
        channel: The MIDI channel of the preset button.
        name: The name of the preset button.
    """

    type: str = JDXISynth.DIGITAL_1  # Adjust the type as needed
    number: int = 1
    modified: int = 0
    channel: int = MidiChannel.DIGITAL1
    name: Optional[str] = None
