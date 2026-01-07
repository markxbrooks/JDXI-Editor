"""Drum Kit CC values"""

class DrumKitCC:
    """Drum Kit Control Change parameters"""

    # NRPN MSB values
    MSB_LEVEL = 64  # Level MSB
    MSB_CUTOFF = 89  # Cutoff MSB
    MSB_RESONANCE = 92  # Resonance MSB
    MSB_ENVELOPE = 119  # Envelope MSB

    # Parameter ranges
    MIN_NOTE = 36  # Lowest drum note (C1)
    MAX_NOTE = 72  # Highest drum note (C4)
    MIN_VALUE = 0  # Minimum parameter value
    MAX_VALUE = 127  # Maximum parameter value

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        return str(value)

    @staticmethod
    def validate_note(note: int) -> bool:
        """Validate note is within drum kit range"""
        return DrumKitCC.MIN_NOTE <= note <= DrumKitCC.MAX_NOTE

    @staticmethod
    def validate_msb(msb: int) -> bool:
        """Validate MSB value is valid"""
        return msb in [
            DrumKitCC.MSB_LEVEL,
            DrumKitCC.MSB_CUTOFF,
            DrumKitCC.MSB_RESONANCE,
            DrumKitCC.MSB_ENVELOPE,
        ]

    @staticmethod
    def validate_value(value: int) -> bool:
        """Validate parameter value is within range"""
        return DrumKitCC.MIN_VALUE <= value <= DrumKitCC.MAX_VALUE
