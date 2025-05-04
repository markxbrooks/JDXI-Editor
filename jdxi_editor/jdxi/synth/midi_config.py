"""
Midi Synth Config
"""

from dataclasses import dataclass
from typing import List

from jdxi_editor.jdxi.synth.type import JDXISynth


@dataclass
class MidiSynthConfig:
    """
    Midi Synth Config
    """

    midi_requests: List[str]
    midi_channel: int
    presets: List[str]
    preset_list: List[str]
    preset_type: JDXISynth
