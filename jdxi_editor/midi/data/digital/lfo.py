"""Digital LFO"""

from enum import IntEnum


class DigitalLFOShape(IntEnum):
    """LFO waveform shapes"""

    TRI = 0
    SINE = 1
    SAW = 2
    SQUARE = 3
    SAMPLE_HOLD = 4  # S&H
    RANDOM = 5

    @property
    def display_name(self) -> str:
        names = {0: "TRI", 1: "SIN", 2: "SAW", 3: "SQR", 4: "S&H", 5: "RND"}
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        return self.value


class DigitalLFOTempoSyncNote(IntEnum):
    """Tempo sync note values"""

    NOTE_16 = 0  # 16 bars
    NOTE_12 = 1  # 12 bars
    NOTE_8 = 2  # 8 bars
    NOTE_4 = 3  # 4 bars
    NOTE_2 = 4  # 2 bars
    NOTE_1 = 5  # 1 bar
    NOTE_3_4 = 6  # 3/4 (dotted half)
    NOTE_2_3 = 7  # 2/3 (triplet whole)
    NOTE_1_2 = 8  # 1/2 (half)
    NOTE_3_8 = 9  # 3/8 (dotted quarter)
    NOTE_1_3 = 10  # 1/3 (triplet half)
    NOTE_1_4 = 11  # 1/4 (quarter)
    NOTE_3_16 = 12  # 3/16 (dotted eighth)
    NOTE_1_6 = 13  # 1/6 (triplet quarter)
    NOTE_1_8 = 14  # 1/8 (eighth)
    NOTE_3_32 = 15  # 3/32 (dotted sixteenth)
    NOTE_1_12 = 16  # 1/12 (triplet eighth)
    NOTE_1_16 = 17  # 1/16 (sixteenth)
    NOTE_1_24 = 18  # 1/24 (triplet sixteenth)
    NOTE_1_32 = 19  # 1/32 (thirty-second)

    @property
    def display_name(self) -> str:
        names = {
            0: "16",
            1: "12",
            2: "8",
            3: "4",
            4: "2",
            5: "1",
            6: "3/4",
            7: "2/3",
            8: "1/2",
            9: "3/8",
            10: "1/3",
            11: "1/4",
            12: "3/16",
            13: "1/6",
            14: "1/8",
            15: "3/32",
            16: "1/12",
            17: "1/16",
            18: "1/24",
            19: "1/32",
        }
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        return self.value
