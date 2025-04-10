from jdxi_editor.midi.data.control_change.base import ControlChange


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


class DigitalSynth1ControlChange(ControlChange):
    """Analog synth CC parameters"""

    # Direct CC parameters
    CUTOFF_CC = 102  # Cutoff (0-127)
    RESONANCE_CC = 105  # Resonance (0-127)
    LEVEL_CC = 117  # Level (0-127)
    LFO_RATE_CC = 16  # LFO Rate (0-127)

    # NRPN parameters (MSB=0)
    NRPN_ENV = 124  # Envelope (0-127)
    NRPN_LFO_SHAPE = 3  # LFO Shape (0-5)
    NRPN_LFO_PITCH = 15  # LFO Pitch Depth (0-127)
    NRPN_LFO_FILTER = 18  # LFO Filter Depth (0-127)
    NRPN_LFO_AMP = 21  # LFO Amp Depth (0-127)
    NRPN_PW = 37  # Pulse Width (0-127)

    @staticmethod
    def get_value_for_partial(value: int, partial_number: int) -> str:
        """Convert raw value to display value"""
        return value + (partial_number - 1)
        
        
class DigitalToneCCGrouped:
    """Grouped version of Control Change (CC) values for easier access."""

    CC = {
        "Cutoff": {
            1: 102,  # Partial 1
            2: 103,  # Partial 2
            3: 104,  # Partial 3
        },
        "Resonance": {
            1: 105,  # Partial 1
            2: 106,  # Partial 2
            3: 107,  # Partial 3
        },
        "Level": {
            1: 117,  # Partial 1
            2: 118,  # Partial 2
            3: 119,  # Partial 3
        },
        "LFO_Rate": {
            1: 16,  # Partial 1
            2: 17,  # Partial 2
            3: 18,  # Partial 3
        }
    }

    NRPN = {
        "Envelope": {
            1: 124,  # Partial 1
            2: 125,  # Partial 2
            3: 126,  # Partial 3
        },
        "LFO_Shape": {
            1: 3,  # Partial 1
            2: 4,  # Partial 2
            3: 5,  # Partial 3
        },
        "LFO_Pitch": {
            1: 15,  # Partial 1
            2: 16,  # Partial 2
            3: 17,  # Partial 3
        },
        "LFO_Filter": {
            1: 18,  # Partial 1
            2: 19,  # Partial 2
            3: 20,  # Partial 3
        },
        "LFO_Amp": {
            1: 21,  # Partial 1
            2: 22,  # Partial 2
            3: 23,  # Partial 3
        }
    }

    @staticmethod
    def get_cc_value(group: str, partial: int) -> int:
        """Retrieve CC value based on group and partial."""
        return DigitalToneCCGrouped.CC.get(group, {}).get(partial)

    @staticmethod
    def get_nrpn_value(group: str, partial: int) -> int:
        """Retrieve NRPN value based on group and partial."""
        return DigitalToneCCGrouped.NRPN.get(group, {}).get(partial)