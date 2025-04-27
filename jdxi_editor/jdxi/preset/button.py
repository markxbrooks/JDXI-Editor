from dataclasses import dataclass
from typing import Optional

from jdxi_editor.jdxi.synth.type import JDXISynth
from jdxi_editor.midi.channel.channel import MidiChannel


@dataclass
class JDXIPresetButton:
    type: str = JDXISynth.DIGITAL_1  # Adjust the type as needed
    number: int = 1
    modified: int = 0
    channel: int = MidiChannel.DIGITAL1
    name: Optional[str] = None
