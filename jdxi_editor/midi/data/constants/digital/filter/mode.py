from enum import Enum


class DigitalFilterMode(Enum):
    """Filter mode types"""
    BYPASS = 0x00
    LPF = 0x01     # Low-pass filter
    HPF = 0x02     # High-pass filter
    BPF = 0x03     # Band-pass filter
    PKG = 0x04     # Peaking filter
    LPF2 = 0x05    # Low-pass filter 2
    LPF3 = 0x06    # Low-pass filter 3
    LPF4 = 0x07    # Low-pass filter 4

    @property
    def display_name(self) -> str:
        """Get display name for filter mode"""
        names = {
            0: "BYPASS",
            1: "LPF",
            2: "HPF",
            3: "BPF",
            4: "PKG",
            5: "LPF2",
            6: "LPF3",
            7: "LPF4"
        }
        return names.get(self.value, "???")
