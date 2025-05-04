"""LFO data"""

from enum import Enum


class LFOSyncNote(Enum):
    """LFO sync note values"""

    BAR_16 = 0  # 16 bars
    BAR_12 = 1  # 12 bars
    BAR_8 = 2  # 8 bars
    BAR_4 = 3  # 4 bars
    BAR_2 = 4  # 2 bars
    BAR_1 = 5  # 1 bar
    BAR_3_4 = 6  # 3/4 bar
    BAR_2_3 = 7  # 2/3 bar
    BAR_1_2 = 8  # 1/2 bar
    BAR_3_8 = 9  # 3/8 bar
    BAR_1_3 = 10  # 1/3 bar
    BAR_1_4 = 11  # 1/4 bar
    BAR_3_16 = 12  # 3/16 bar
    BAR_1_6 = 13  # 1/6 bar
    BAR_1_8 = 14  # 1/8 bar
    BAR_3_32 = 15  # 3/32 bar
    BAR_1_12 = 16  # 1/12 bar
    BAR_1_16 = 17  # 1/16 bar
    BAR_1_24 = 18  # 1/24 bar
    BAR_1_32 = 19  # 1/32 bar

    @staticmethod
    def get_display_name(value: int) -> str:
        """Get display name for sync note value"""
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
        return names.get(value, "???")

    @staticmethod
    def get_all_display_names() -> list:
        """Get list of all display names in order"""
        return [LFOSyncNote.get_display_name(i) for i in range(20)]

    @staticmethod
    def display_name(value: int) -> str:
        """Get display name for sync note value"""
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
        return names.get(value, "???")


class LFOShape(Enum):
    """LFO waveform shapes"""

    TRIANGLE = 0x00  # Triangle wave
    SINE = 0x01  # Sine wave
    SAW = 0x02  # Sawtooth wave
    SQUARE = 0x03  # Square wave
    SAMPLE_HOLD = 0x04  # Sample & Hold
    RANDOM = 0x05  # Random

    @staticmethod
    def get_display_name(value: int) -> str:
        """Get display name for LFO shape"""
        names = {0: "TRI", 1: "SIN", 2: "SAW", 3: "SQR", 4: "S&H", 5: "RND"}
        return names.get(value, "???")
