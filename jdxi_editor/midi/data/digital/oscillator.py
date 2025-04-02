from enum import IntEnum


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


