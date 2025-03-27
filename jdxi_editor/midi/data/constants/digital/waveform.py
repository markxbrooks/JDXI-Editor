from enum import Enum

from jdxi_editor.midi.data.constants.digital import Waveform


class DigitalWaveform(Enum):
    """Waveform types available on the JD-Xi"""

    SAW = 0x00  # Sawtooth wave
    SQUARE = 0x01  # Square wave
    PW_SQUARE = 0x02  # Pulse width square wave
    TRIANGLE = 0x03  # Triangle wave
    SINE = 0x04  # Sine wave
    NOISE = 0x05  # Noise
    SUPER_SAW = 0x06  # Super saw
    PCM = 0x07  # PCM waveform

    @property
    def display_name(self) -> str:
        """Get display name for waveform"""
        names = {
            DigitalWaveform.SAW: "SAW",
            DigitalWaveform.SQUARE: "SQR",
            DigitalWaveform.PW_SQUARE: "PW.SQR",
            DigitalWaveform.TRIANGLE: "TRI",
            DigitalWaveform.SINE: "SIN",
            DigitalWaveform.NOISE: "NOISE",
            DigitalWaveform.SUPER_SAW: "S.SAW",
            DigitalWaveform.PCM: "PCM",
        }
        return names[self]

    @property
    def midi_value(self) -> int:
        """Get MIDI value for waveform"""
        values = {
            Waveform.SAW: OSC_WAVE_SAW,
            Waveform.SQUARE: OSC_WAVE_SQUARE,
            Waveform.TRIANGLE: OSC_WAVE_TRIANGLE,
            Waveform.SINE: OSC_WAVE_SINE,
            Waveform.NOISE: OSC_WAVE_NOISE,
            Waveform.SUPER_SAW: OSC_WAVE_SUPER_SAW,
            Waveform.PCM: OSC_WAVE_PCM,
        }
        return values[self]

    @classmethod
    def from_midi_value(cls, value: int) -> "Waveform":
        """Create Waveform from MIDI value"""
        for waveform in cls:
            if waveform.midi_value == value:
                return waveform
        raise ValueError(f"Invalid waveform value: {value}")
