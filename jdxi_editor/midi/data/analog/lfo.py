"""Analog LFO"""

from enum import Enum, IntEnum

LFO_RANGES = {
    "shape": (0, 5),
    "rate": (0, 127),
    "fade": (0, 127),
    "sync": (0, 1),
    "sync_note": (0, 19),
    "pitch": (-63, 63),
    "filter": (-63, 63),
    "amp": (-63, 63),
    "key_trig": (0, 1),
}

LFO_TEMPO_SYNC_NOTES = [
    "16",  # 0
    "12",  # 1
    "8",  # 2
    "4",  # 3
    "2",  # 4
    "1",  # 5
    "3/4",  # 6
    "2/3",  # 7
    "1/2",  # 8
    "3/8",  # 9
    "1/3",  # 10
    "1/4",  # 11
    "3/16",  # 12
    "1/6",  # 13
    "1/8",  # 14
    "3/32",  # 15
    "1/12",  # 16
    "1/16",  # 17
    "1/24",  # 18
    "1/32",  # 19
]


class AnalogLFOShape(Enum):
    """Analog LFO waveform shapes"""

    TRIANGLE = 0  # Triangle wave
    SINE = 1  # Sine wave
    SAW = 2  # Sawtooth wave
    SQUARE = 3  # Square wave
    SAMPLE_HOLD = 4  # Sample & Hold
    RANDOM = 5  # Random

    @property
    def display_name(self) -> str:
        """Get display name for LFO shape"""
        names = {0: "TRI", 1: "SIN", 2: "SAW", 3: "SQR", 4: "S&H", 5: "RND"}
        return names.get(self.value, "???")


class AnalogLFOTempoSyncNote(Enum):
    """LFO tempo sync note values"""

    NOTE_16 = 0  # 16 bars
    NOTE_12 = 1  # 12 bars
    NOTE_8 = 2  # 8 bars
    NOTE_4 = 3  # 4 bars
    NOTE_2 = 4  # 2 bars
    NOTE_1 = 5  # 1 bar
    NOTE_3_4 = 6  # 3/4
    NOTE_2_3 = 7  # 2/3
    NOTE_1_2 = 8  # 1/2
    NOTE_3_8 = 9  # 3/8
    NOTE_1_3 = 10  # 1/3
    NOTE_1_4 = 11  # 1/4
    NOTE_3_16 = 12  # 3/16
    NOTE_1_6 = 13  # 1/6
    NOTE_1_8 = 14  # 1/8
    NOTE_3_32 = 15  # 3/32
    NOTE_1_12 = 16  # 1/12
    NOTE_1_16 = 17  # 1/16
    NOTE_1_24 = 18  # 1/24
    NOTE_1_32 = 19  # 1/32


class AnalogLFOWaveShape(IntEnum):
    """Analog LFO Waves"""

    TRI = 0
    SINE = 1
    SAW = 2
    SQUARE = 3
    SAMPLE_HOLD = 4
    RANDOM = 5

    @property
    def display_name(self) -> str:
        names = {0: "TRI", 1: "SIN", 2: "SAW", 3: "SQR", 4: "S&H", 5: "RND"}
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        return self.value


class AnalogLFOWaveType:
    """Analog LFO Waves"""

    TRI: str = "TRI"
    SINE: str = "SINE"
    SAW: str = "SAW"
    SQUARE: str = "SQR"
    SAMPLE_HOLD: str = "S&H:"
    RANDOM: str = "RND"
