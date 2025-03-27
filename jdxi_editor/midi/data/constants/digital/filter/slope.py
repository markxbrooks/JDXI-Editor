from enum import Enum


class DigitalFilterSlope(Enum):
    """Filter slope values"""
    DB_12 = 0x00  # -12 dB/octave
    DB_24 = 0x01  # -24 dB/octave

    @property
    def display_name(self) -> str:
        """Get display name for filter slope"""
        names = {
            0: "-12dB",
            1: "-24dB"
        }
        return names.get(self.value, "???")
