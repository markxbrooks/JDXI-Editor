class DigitalToneCC:
    """SuperNATURAL Synth Tone Control Change parameters"""

    # Direct CC parameters (per partial)
    CUTOFF_1 = 102  # Cutoff Partial 1 (0-127)
    CUTOFF_2 = 103  # Cutoff Partial 2 (0-127)
    CUTOFF_3 = 104  # Cutoff Partial 3 (0-127)

    RESONANCE_1 = 105  # Resonance Partial 1 (0-127)
    RESONANCE_2 = 106  # Resonance Partial 2 (0-127)
    RESONANCE_3 = 107  # Resonance Partial 3 (0-127)

    LEVEL_1 = 117  # Level Partial 1 (0-127)
    LEVEL_2 = 118  # Level Partial 2 (0-127)
    LEVEL_3 = 119  # Level Partial 3 (0-127)

    LFO_RATE_1 = 16  # LFO Rate Partial 1 (0-127)
    LFO_RATE_2 = 17  # LFO Rate Partial 2 (0-127)
    LFO_RATE_3 = 18  # LFO Rate Partial 3 (0-127)

    # NRPN parameters (MSB=0)
    NRPN_ENV_1 = 124  # Envelope Partial 1 (0-127)
    NRPN_ENV_2 = 125  # Envelope Partial 2 (0-127)
    NRPN_ENV_3 = 126  # Envelope Partial 3 (0-127)

    NRPN_LFO_SHAPE_1 = 3  # LFO Shape Partial 1 (0-5)
    NRPN_LFO_SHAPE_2 = 4  # LFO Shape Partial 2 (0-5)
    NRPN_LFO_SHAPE_3 = 5  # LFO Shape Partial 3 (0-5)

    NRPN_LFO_PITCH_1 = 15  # LFO Pitch Depth Partial 1 (0-127)
    NRPN_LFO_PITCH_2 = 16  # LFO Pitch Depth Partial 2 (0-127)
    NRPN_LFO_PITCH_3 = 17  # LFO Pitch Depth Partial 3 (0-127)

    NRPN_LFO_FILTER_1 = 18  # LFO Filter Depth Partial 1 (0-127)
    NRPN_LFO_FILTER_2 = 19  # LFO Filter Depth Partial 2 (0-127)
    NRPN_LFO_FILTER_3 = 20  # LFO Filter Depth Partial 3 (0-127)

    NRPN_LFO_AMP_1 = 21  # LFO Amp Depth Partial 1 (0-127)
    NRPN_LFO_AMP_2 = 22  # LFO Amp Depth Partial 2 (0-127)
    NRPN_LFO_AMP_3 = 23  # LFO Amp Depth Partial 3 (0-127)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param in [3, 4, 5]:  # LFO Shape
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value]
        return str(value)
