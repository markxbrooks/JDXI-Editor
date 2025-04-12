from enum import IntEnum, Enum

from jdxi_editor.midi.wave.form import Waveform


class DigitalOscPcmWaveGain(IntEnum):
    """Wave gain values in dB"""

    DB_MINUS_6 = 0  # -6 dB
    DB_0 = 1  # 0 dB
    DB_PLUS_6 = 2  # +6 dB
    DB_PLUS_12 = 3  # +12 dB


class DigitalOscWave(IntEnum):
    """Oscillator waveform types"""

    SAW = 0
    SQUARE = 1
    PW_SQUARE = 2  # Pulse Width Square
    TRIANGLE = 3
    SINE = 4
    NOISE = 5
    SUPER_SAW = 6
    PCM = 7

    @property
    def display_name(self) -> str:
        """Get display name for the waveform"""
        return {
            self.SAW: "SAW",
            self.SQUARE: "SQR",
            self.PW_SQUARE: "PWM",
            self.TRIANGLE: "TRI",
            self.SINE: "SINE",
            self.NOISE: "NOISE",
            self.SUPER_SAW: "S-SAW",
            self.PCM: "PCM",
        }[self]

    @property
    def description(self) -> str:
        """Get full description of the waveform"""
        return {
            self.SAW: "Sawtooth",
            self.SQUARE: "Square",
            self.PW_SQUARE: "Pulse Width Square",
            self.TRIANGLE: "Triangle",
            self.SINE: "Sine",
            self.NOISE: "Noise",
            self.SUPER_SAW: "Super Saw",
            self.PCM: "PCM Wave",
        }[self]


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
