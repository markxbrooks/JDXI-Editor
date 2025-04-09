from enum import Enum, auto

OSC_WAVE_SAW = 0x00  # Sawtooth
OSC_WAVE_SQUARE = 0x01  # Square
OSC_WAVE_TRIANGLE = 0x02  # Triangle
OSC_WAVE_SINE = 0x03  # Sine
OSC_WAVE_NOISE = 0x04  # Noise
OSC_WAVE_SUPER_SAW = 0x05  # Super saw
OSC_WAVE_PCM = 0x06  # PCM waveform


class Waveform(Enum):
    """Waveform types available on the JD-Xi"""

    SAW = auto()  # Sawtooth wave
    SQUARE = auto()  # Square wave
    TRIANGLE = auto()  # Triangle wave
    SINE = auto()  # Sine wave
    NOISE = auto()  # Noise
    SUPER_SAW = auto()  # Super saw
    PCM = auto()  # PCM waveform

    @property
    def display_name(self) -> str:
        """Get display name for waveform"""
        return self.name.replace("_", " ").title()

    @property
    def midi_value(self) -> int:
        """Get MIDI value for waveform"""
        return {
            Waveform.SAW: OSC_WAVE_SAW,
            Waveform.SQUARE: OSC_WAVE_SQUARE,
            Waveform.TRIANGLE: OSC_WAVE_TRIANGLE,
            Waveform.SINE: OSC_WAVE_SINE,
            Waveform.NOISE: OSC_WAVE_NOISE,
            Waveform.SUPER_SAW: OSC_WAVE_SUPER_SAW,
            Waveform.PCM: OSC_WAVE_PCM,
        }[self]

    @classmethod
    def from_midi_value(cls, value: int) -> "Waveform":
        """Create Waveform from MIDI value"""
        for waveform in cls:
            if waveform.midi_value == value:
                return waveform
        raise ValueError(f"Invalid waveform value: {value}")