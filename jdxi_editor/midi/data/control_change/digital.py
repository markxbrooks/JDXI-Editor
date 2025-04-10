"""
DigitalControlChange

Example usage

# Get Cutoff CC value for Partial 2
cutoff_partial_2 = DigitalControlChange.get_cc_value("Cutoff", 2)
print(f"Cutoff (Partial 2): {cutoff_partial_2}")

# Get Envelope NRPN value for Partial 3
envelope_partial_3 = DigitalControlChange.get_nrpn_value("Envelope", 3)
print(f"Envelope (Partial 3): {envelope_partial_3}")

envelope_map = DigitalControlChange.get_nrpn_map("Envelope")
"""

        
class DigitalControlChange:
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
        },
        "Reverb": {
            1: 12,  # NRPN LSB for Partial 1
            2: 12,  # Partial 2
            3: 12,  # Partial 3
        },
        "Delay" : {
            1: 13,  # NRPN LSB for Partial 1
            2: 13,  # Partial 2
            3: 13,  # Partial 3
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
        },
        "LFO_Rate": {
            1: 21,  # Partial 1
            2: 22,  # Partial 2
            3: 23,  # Partial 3
        }
    }

    @staticmethod
    def get_cc_value(group: str, partial: int) -> int:
        """Retrieve CC value based on group and partial."""
        return DigitalControlChange.CC.get(group, {}).get(partial)

    @staticmethod
    def get_nrpn_value(group: str, partial: int) -> int:
        """Retrieve NRPN value based on group and partial."""
        return DigitalControlChange.NRPN.get(group, {}).get(partial)

    @staticmethod
    def get_display_value(value: int, group: str, partial: int) -> str:
        """Convert raw value to display value"""
        param = DigitalControlChange.NRPN.get(group, {}).get(partial)
        if param in [3, 4, 5]:  # LFO Shape
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value] if 0 <= value < len(shapes) else f"Unknown({value})"
        return str(value)

    @staticmethod
    def get_nrpn_map(group: str) -> dict:
        """Return dynamic NRPN values for each partial from the given group."""
        return DigitalControlChange.NRPN.get(group, {}).copy()

    @staticmethod
    def get_cc_map(group: str) -> dict:
        """Return dynamic CC values for each partial from the given group."""
        return DigitalControlChange.CC.get(group, {}).copy()

