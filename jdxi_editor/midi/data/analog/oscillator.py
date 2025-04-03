from enum import Enum

ANALOG_OSC_GROUP = 0x00  # Oscillator parameters


class AnalogOscWave(Enum):
    """Analog oscillator waveform types"""

    SAW = 0
    TRIANGLE = 1
    PULSE = 2  # Changed from SQUARE to PULSE to match JD-Xi terminology

    @property
    def display_name(self) -> str:
        """Get display name for waveform"""
        names = {0: "SAW", 1: "TRI", 2: "P.W"}  # Updated display name
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for waveform"""
        return self.value


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
