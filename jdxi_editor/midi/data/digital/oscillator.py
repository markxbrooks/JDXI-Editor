"""
Digital Oscillator
"""

from enum import Enum, IntEnum

from jdxi_editor.midi.wave.form import (
    OSC_WAVE_NOISE,
    OSC_WAVE_PCM,
    OSC_WAVE_SAW,
    OSC_WAVE_SINE,
    OSC_WAVE_SQUARE,
    OSC_WAVE_SUPER_SAW,
    OSC_WAVE_TRIANGLE,
    Waveform,
)
from jdxi_editor.midi.wave.spec import WaveOscBehavior


class DigitalOscPcmWaveGain(IntEnum):
    """Wave gain values in dB"""

    DB_MINUS_6 = 0  # -6 dB
    DB_0 = 1  # 0 dB
    DB_PLUS_6 = 2  # +6 dB
    DB_PLUS_12 = 3  # +12 dB


class WaveformType:
    """Types of Digital Oscillator Waves"""

    ADSR: str = "adsr"
    UPSAW: str = "upsaw"
    SQUARE: str = "square"
    PWSQU: str = "pwsqu"
    TRIANGLE: str = "triangle"
    SINE: str = "sine"
    SAW: str = "saw"
    SPSAW: str = "spsaw"
    PCM: str = "pcm"
    NOISE: str = "noise"
    LPF_FILTER: str = "lpf_filter"
    HPF_FILTER: str = "hpf_filter"
    BYPASS_FILTER: str = "bypass_filter"
    BPF_FILTER: str = "bpf_filter"
    FILTER_SINE: str = "filter_sine"


class DigitalWaveOsc(WaveOscBehavior, IntEnum):
    """Oscillator waveform types"""

    SAW = 0
    SQUARE = 1
    PW_SQUARE = 2  # Pulse Width Square
    TRI = 3
    SINE = 4
    NOISE = 5
    SUPER_SAW = 6
    PCM = 7


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
    def from_midi_value(cls, value: int) -> Waveform:
        """Create Waveform from MIDI value"""
        for waveform in cls:
            if waveform.midi_value == value:
                return waveform
        raise ValueError(f"Invalid waveform value: {value}")
