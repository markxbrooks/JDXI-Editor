"""
Module for controlling arpeggio parameters in a synthesizer or sequencer.

This module defines the `ProgramController` class, which manages various arpeggio-related
parameters, including grid, duration, switch state, style, motif, octave range, accent rate,
and velocity. These parameters are used to configure and control the behavior of arpeggios in
a music production environment.

The class provides static methods to retrieve human-readable display values for each parameter
based on raw numerical values. It also includes predefined constants for each arpeggio-related
parameter, with specific value ranges and corresponding meanings.

Parameters defined in the class include:
- Arpeggio grid, duration, switch, style, motif, octave, accent, and velocity values
- Methods for converting raw integer values to display-friendly strings
- Various grid types (e.g., 04_, 08_, 16_)
- Duration values expressed as percentages (e.g., 30%, 50%, 100%)
- Motif values representing arpeggio patterns and phrases (e.g., UP/L, dn/H, PHRASE)

This module can be used in a synthesizer, sequencer, or other digital audio workstation
to dynamically configure arpeggio settings and translate raw parameter values into readable
formats for display and interaction with users.

Classes:
- ProgramController: Contains the logic for handling arpeggio parameters and converting
  raw values to human-readable strings.

"""
from jdxi_editor.midi.data.parameter.synth import AddressParameter


class AddressParameterProgramController(AddressParameter):
    """Program Controller parameters"""

    # Arpeggio parameters
    ARPEGGIO_GRID = (0x01, 0, 8)  # Arpeggio Grid (0-8)
    ARPEGGIO_DURATION = (0x02, 0, 9)  # Arpeggio Duration (0-9)
    ARPEGGIO_SWITCH = (0x03, 0, 1)  # Arpeggio Switch (0-1)
    ARPEGGIO_STYLE = (0x05, 0, 127)  # Arpeggio Style (0-127)
    ARPEGGIO_MOTIF = (0x06, 0, 11)  # Arpeggio Motif (0-11)
    ARPEGGIO_OCTAVE_RANGE = (0x07, -3, 3)  # Arpeggio Octave Range (-3/+3)
    ARPEGGIO_ACCENT_RATE = (0x09, 0, 100)  # Arpeggio Accent Rate (0-100)
    ARPEGGIO_VELOCITY = (0x0A, 0, 127)  # Arpeggio Velocity (0-127, 0=REAL)

    """ 
    # Grid values
    GRID_4 = 0  # 04_
    GRID_8 = 1  # 08_
    GRID_8L = 2  # 08L
    GRID_8H = 3  # 08H
    GRID_8T = 4  # 08t
    GRID_16 = 5  # 16_
    GRID_16L = 6  # 16L
    GRID_16H = 7  # 16H
    GRID_16T = 8  # 16t

    # Duration values
    DUR_30 = 0  # 30%
    DUR_40 = 1  # 40%
    DUR_50 = 2  # 50%
    DUR_60 = 3  # 60%
    DUR_70 = 4  # 70%
    DUR_80 = 5  # 80%
    DUR_90 = 6  # 90%
    DUR_100 = 7  # 100%
    DUR_120 = 8  # 120%
    DUR_FULL = 9  # FULL

    # Motif values
    MOTIF_UP_L = 0  # UP/L
    MOTIF_UP_H = 1  # UP/H
    MOTIF_UP = 2  # UP/_
    MOTIF_DN_L = 3  # dn/L
    MOTIF_DN_H = 4  # dn/H
    MOTIF_DN = 5  # dn/_
    MOTIF_UD_L = 6  # Ud/L
    MOTIF_UD_H = 7  # Ud/H
    MOTIF_UD = 8  # Ud/_
    MOTIF_RN_L = 9  # rn/L
    MOTIF_RN = 10  # rn/_
    MOTIF_PHRASE = 11  # PHRASE
    """

    @staticmethod
    def get_grid_name(value: int) -> str:
        """
        Get grid name from value
        :param value: int The value
        :return: str The grid name
        """
        names = ["04_", "08_", "08L", "08H", "08t", "16_", "16L", "16H", "16t"]
        return names[value] if 0 <= value <= 8 else str(value)

    @staticmethod
    def get_duration_name(value: int) -> str:
        """
        Get duration name from value
        :param value: int The value
        :return: str The duration name
        """
        names = ["30", "40", "50", "60", "70", "80", "90", "100", "120", "FUL"]
        return names[value] if 0 <= value <= 9 else str(value)

    @staticmethod
    def get_motif_name(value: int) -> str:
        """
        Get motif name from value
        :param value: int The value
        :return: str The motif name
        """
        names = [
            "UP/L",
            "UP/H",
            "UP/_",
            "dn/L",
            "dn/H",
            "dn/_",
            "Ud/L",
            "Ud/H",
            "Ud/_",
            "rn/L",
            "rn/_",
            "PHRASE",
        ]
        return names[value] if 0 <= value <= 11 else str(value)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """
        Convert raw value to display value
        :param param: int The parameter
        :param value: int The value
        :return: str The display value
        """
        if param == AddressParameterProgramController.ARPEGGIO_GRID:  # Grid
            return AddressParameterProgramController.get_grid_name(value)
        elif param == AddressParameterProgramController.ARPEGGIO_DURATION:  # Duration
            return AddressParameterProgramController.get_duration_name(value)
        elif param == AddressParameterProgramController.ARPEGGIO_SWITCH:  # Switch
            return "ON" if value else "OFF"
        elif param == AddressParameterProgramController.ARPEGGIO_STYLE:  # Style
            return str(value + 1)  # Convert 0-127 to 1-128
        elif param == AddressParameterProgramController.ARPEGGIO_MOTIF:  # Motif
            return AddressParameterProgramController.get_motif_name(value)
        elif param == AddressParameterProgramController.ARPEGGIO_OCTAVE_RANGE:  # Octave Range
            return f"{value - 64:+d}"  # Convert 61-67 to -3/+3
        elif param == AddressParameterProgramController.ARPEGGIO_ACCENT_RATE:  # Accent Rate
            return f"{value}%"
        elif param == AddressParameterProgramController.ARPEGGIO_VELOCITY:  # Velocity
            return "REAL" if value == 0 else str(value)
        return str(value)
