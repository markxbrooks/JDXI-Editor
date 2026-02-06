"""
Analog Specs
"""

from enum import Enum

from jdxi_editor.midi.wave.spec import WaveOscBehavior


class AnalogWaveOsc(WaveOscBehavior, Enum):
    """Analog oscillator waveform types"""

    SAW = 0
    TRI = 1
    SQUARE = 2


class AnalogSubOscType(Enum):
    """Analog sub oscillator types"""

    OFF = 0x00  # Sub oscillator off
    OCT_DOWN_1 = 0x01  # -1 octave
    OCT_DOWN_2 = 0x02  # -2 octaves

    @property
    def display_name(self) -> str:
        """Get display name for sub oscillator preset_type"""
        names = {0x00: "OFF", 0x01: "-1 OCT", 0x02: "-2 OCT"}
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for sub oscillator preset_type"""
        return self.value
