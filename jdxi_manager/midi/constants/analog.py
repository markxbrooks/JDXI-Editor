"""Analog synth MIDI constants"""

from enum import Enum, IntEnum
from .sysex import TEMPORARY_ANALOG_SYNTH_AREA  # Remove this import

# Areas and Parts
ANALOG_SYNTH_AREA = 0x19  # Changed from 0x1B to 0x19
ANALOG_PART = 0x42  # Changed from 0x00 to 0x42


# Control Change Parameters
class ControlChange(IntEnum):
    """Base class for Synth Control Change parameters"""

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 3:  # LFO Shape
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value]
        return str(value)


# Analog Control Change Parameters
class AnalogControlChange(ControlChange):
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
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 3:  # LFO Shape
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value]
        return str(value)


# Digital Control Change Parameters
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

def get_partial_cc(base_cc: int, partial: int) -> int:
    """Get the CC number for a given partial (1-3) based on the base CC."""
    return base_cc + (partial - 1)

from mido import Message

def send_nrpn(midi_out, msb: int, lsb: int, value: int):
    """Send an NRPN message via MIDI."""
    midi_out.send(Message('control_change', control=99, value=msb))  # NRPN MSB
    midi_out.send(Message('control_change', control=98, value=lsb))  # NRPN LSB
    midi_out.send(Message('control_change', control=6, value=value))  # Data Entry MSB

# send_nrpn(midi_out, 0, 3, 2)  # Set LFO Shape (NRPN MSB: 0, LSB: 3) to value 2

"""
Control Changes for reference:

SuperNATURAL Synth Tone
+-----------------+---------+---------------------------+---------+
| Parameter       | Partial | Controller Number         | Value   |
+-----------------+---------+---------------------------+---------+
| Cutoff          | 1 - 3   | 102 - 104                 | 0 - 127 |
| Resonance       | 1 - 3   | 105 - 107                 | 0 - 127 |
| Level           | 1 - 3   | 117 - 119                 | 0 - 127 |
| Envelope        | 1 - 3   | NRPN MSB:0, LSB:124 - 126 | 0 - 127 |
| LFO Shape       | 1 - 3   | NRPN MSB:0, LSB:3 - 5     | 0 - 5   |
| LFO Rate        | 1 - 3   | 16 - 18                   | 0 - 127 |
| LFO Pitch Depth | 1 - 3   | NRPN MSB:0, LSB:15 - 17   | 0 - 127 |
| LFO Filter Depth| 1 - 3   | NRPN MSB:0, LSB:18 - 20   | 0 - 127 |
| LFO Amp Depth   | 1 - 3   | NRPN MSB:0, LSB:21 - 23   | 0 - 127 |
+-----------------+---------+---------------------------+---------+

Analog Synth Tone
+-----------------+---------------------------+---------+
| Parameter       | Controller Number         | Value   |
+-----------------+---------------------------+---------+
| Cutoff          | 102                       | 0 - 127 |
| Resonance       | 105                       | 0 - 127 |
| Level           | 117                       | 0 - 127 |
| Envelope        | NRPN MSB:0, LSB:124       | 0 - 127 |
| LFO Shape       | NRPN MSB:0, LSB:3         | 0 - 5   |
| LFO Rate        | 16                        | 0 - 127 |
| LFO Pitch Depth | NRPN MSB:0, LSB:15        | 0 - 127 |
| LFO Filter Depth| NRPN MSB:0, LSB:18        | 0 - 127 |
| LFO Amp Depth   | NRPN MSB:0, LSB:21        | 0 - 127 |
| Pulse Width     | NRPN MSB:0, LSB:37        | 0 - 127 |
+-----------------+---------------------------+---------+
Drum Kit
+----------------+---------+---------------------------+---------+
| Parameter      | Note    | Controller Number         | Value   |
+----------------+---------+---------------------------+---------+
| Cutoff         | 36 - 72 | NRPN MSB:89, LSB:Note     | 0 - 127 |
| Resonance      | 36 - 72 | NRPN MSB:92, LSB:Note     | 0 - 127 |
| Level          | 36 - 72 | NRPN MSB:64, LSB:Note     | 0 - 127 |
| Envelope       | 36 - 72 | NRPN MSB:119, LSB:Note    | 0 - 127 |
+----------------+---------+---------------------------+---------+
Effects
+----------------+---------------------------+---------+
| Parameter      | Controller Number         | Value   |
+----------------+---------------------------+---------+
| Effect 1       | 14                        | 0 - 127 |
| Effect 2       | 15                        | 0 - 127 |
| Delay          | 13                        | 0 - 127 |
| Reverb         | 12                        | 0 - 127 |
| Vocoder (Level)| 83                        | 0 - 127 |
+----------------+---------------------------+---------+

Drum Kit Partial
+--------+-----------+----------------------------------------------------+
| Offset | Address   | Description                                        |
+--------+-----------+----------------------------------------------------+
| 00 00  | 0aaa aaaa | Partial Name 1 (32 - 127)                          |
|        |           | 32 - 127 [ASCII]                                   |
| 00 01  | 0aaa aaaa | Partial Name 2 (32 - 127)                          |
|        |           | 32 - 127 [ASCII]                                   |
| 00 02  | 0aaa aaaa | Partial Name 3 (32 - 127)                          |
|        |           | 32 - 127 [ASCII]                                   |
| 00 03  | 0aaa aaaa | Partial Name 4 (32 - 127)                          |
|        |           | 32 - 127 [ASCII]                                   |
| 00 04  | 0aaa aaaa | Partial Name 5 (32 - 127)                          |
|        |           | 32 - 127 [ASCII]                                   |
| 00 05  | 0aaa aaaa | Partial Name 6 (32 - 127)                          |
|        |           | 32 - 127 [ASCII]                                   |
| 00 06  | 0aaa aaaa | Partial Name 7 (32 - 127)                          |
|        |           | 32 - 127 [ASCII]                                   |
| 00 07  | 0aaa aaaa | Partial Name 8 (32 - 127)                          |
|        |           | 32 - 127 [ASCII]                                   |
| 00 08  | 0aaa aaaa | Partial Name 9 (32 - 127)                          |
|        |           | 32 - 127 [ASCII]                                   |
| 00 09  | 0aaa aaaa | Partial Name 10 (32 - 127)                         |
|        |           | 32 - 127 [ASCII]                                   |
| 00 0A  | 0aaa aaaa | Partial Name 11 (32 - 127)                         |
|        |           | 32 - 127 [ASCII]                                   |
| 00 0B  | 0aaa aaaa | Partial Name 12 (32 - 127)                         |
|        |           | 32 - 127 [ASCII]                                   |
+--------+-----------+----------------------------------------------------+
| 00 0C  | 0000 000a | Assign Type (0 - 1)                                |
|        |           | MULTI, SINGLE                                      |
| 00 0D  | 000a aaaa | Mute Group (0 - 31)                                |
|        |           | OFF, 1 - 31                                        |
+--------+-----------+----------------------------------------------------+
| 00 0E  | 0aaa aaaa | Partial Level (0 - 127)                            |
| 00 0F  | 0aaa aaaa | Partial Coarse Tune (0 - 127)                      |
|        |           | C-1 - G9                                           |
| 00 10  | 0aaa aaaa | Partial Fine Tune (14 - 114)                     |
|        |           | -50 - +50                                          |
| 00 11  | 000a aaaa | Partial Random Pitch Depth (0 - 30)                |
|        |           | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,                      |
|        |           | 10, 20, 30, 40, 50, 60, 70, 80,                    |
|        |           | 90, 100, 200, 300, 400, 500,                       |
|        |           | 600, 700, 800, 900, 1000, 1100,                    |
|        |           | 1200                                               |
| 00 12  | 0aaa aaaa | Partial Pan (0 - 127)                              |
|        |           | L64 - 63R                                          |
| 00 13  | 00aa aaaa | Partial Random Pan Depth (0 - 63)                  |
| 00 14  | 0aaa aaaa | Partial Alternate Pan Depth (1 - 127)              |
|        |           | L63 - 63R                                          |
| 00 15  | 0000 000a | Partial Env Mode (0 - 1)                           |
|        |           | NO-SUS, SUSTAIN                                    |
+--------+-----------+----------------------------------------------------+
| 00 16  | 0aaa aaaa | Partial Output Level (0 - 127)                     |
| 00 17  | 0aaa aaaa | (reserve) <*>                                      |
| 00 18  | 0aaa aaaa | (reserve) <*>                                      |
| 00 19  | 0aaa aaaa | Partial Chorus Send Level (0 - 127)                |
| 00 1A  | 0aaa aaaa | Partial Reverb Send Level (0 - 127)                |
| 00 1B  | 0000 aaaa | Partial Output Assign (0 - 4)                      |
|        |           | EFX1, EFX2, DLY, REV, DIR                          |
+--------+-----------+----------------------------------------------------+
| 00 1C  | 00aa aaaa | Partial Pitch Bend Range (0 - 48)                  |
| 00 1D  | 0000 000a | Partial Receive Expression (0 - 1)                 |
|        |           | OFF, ON                                            |
| 00 1E  | 0000 000a | Partial Receive Hold-1 (0 - 1)                     |
|        |           | OFF, ON                                            |
| 00 1F  | 0000 000a | (reserve) <*>                                      |
+--------+-----------+----------------------------------------------------+
| 00 20  | 0000 00aa | WMT Velocity Control (0 - 2)                       |
|        |           | OFF, ON, RANDOM                                    |
+--------+-----------+----------------------------------------------------+
| 00 21  | 0000 000a | WMT1 Wave Switch (0 - 1)                           |
|        |           | OFF, ON                                            |
| 00 22  | 0000 00aa | WMT1 Wave Group Type (0)                           |
| 00 23  | 0000 aaaa | WMT1 Wave Group ID (0 - 16384)                     |
|        |           | OFF, 1 - 16384                                     |
| 00 27  | 0000 aaaa | WMT1 Wave Number L (Mono) (0 - 16384)              |
|        |           | OFF, 1 - 16384                                     |
| 00 2B  | 0000 aaaa | WMT1 Wave Number R (0 - 16384)                     |
|        |           | OFF, 1 - 16384                                     |
| 00 2F  | 0000 00aa | WMT1 Wave Gain (0 - 3)                             |
|        |           | -6, 0, +6, +12 [dB]                                |
| 00 30  | 0000 000a | WMT1 Wave FXM Switch (0 - 1)                       |
|        |           | OFF, ON                                            |
| 00 31  | 0000 00aa | WMT1 Wave FXM Color (0 - 3)                        |
|        |           | 1 - 4                                              |
| 00 32  | 000a aaaa | WMT1 Wave FXM Depth (0 - 16)                       |
| 00 33  | 0000 000a | WMT1 Wave Tempo Sync (0 - 1)                       |
|        |           | OFF, ON                                            |
| 00 34  | 0aaa aaaa | WMT1 Wave Coarse Tune (16 - 112)                   |
|        |           | -48 - +48                                          |
| 00 35  | 0aaa aaaa | WMT1 Wave Fine Tune (14 - 114)                     |
|        |           | -50 - +50                                          |
| 00 36  | 0aaa aaaa | WMT1 Wave Pan (0 - 127)                            |
|        |           | L64 - 63R                                          |
| 00 37  | 0000 000a | WMT1 Wave Random Pan Switch (0 - 1)                |
|        |           | OFF, ON                                            |
| 00 38  | 0000 00aa | WMT1 Wave Alternate Pan Switch (0 - 2)             |
|        |           | OFF, ON, REVERSE                                   |
| 00 39  | 0aaa aaaa | WMT1 Wave Level (0 - 127)                          |
| 00 3A  | 0aaa aaaa | WMT1 Velocity Range Lower (1 - 127)                |
|        |           | 1 - UPPER                                          |
| 00 3B  | 0aaa aaaa | WMT1 Velocity Range Upper (1 - 127)                |
|        |           | LOWER - 127                                        |
| 00 3C  | 0aaa aaaa | WMT1 Velocity Fade Width Lower (0 - 127)           |
| 00 3D  | 0aaa aaaa | WMT1 Velocity Fade Width Upper (0 - 127)           |
+--------+-----------+----------------------------------------------------+
| 00 3E  | 0000 000a | WMT2 Wave Switch (0 - 1)                           |
|        |           | OFF, ON                                            |
| 00 3F  | 0000 00aa | WMT2 Wave Group Type (0)                           |
| 00 40  | 0000 aaaa | WMT2 Wave Group ID (0 - 16384)                     |
|        |           | OFF, 1 - 16384                                     |
| 00 44  | 0000 aaaa | WMT2 Wave Number L (Mono) (0 - 16384)              |
|        |           | OFF, 1 - 16384                                     |
| 00 48  | 0000 aaaa | WMT2 Wave Number R (0 - 16384)                     |
|        |           | OFF, 1 - 16384                                     |
| 00 4C  | 0000 00aa | WMT2 Wave Gain (0 - 3)                             |
|        |           | -6, 0, +6, +12 [dB]                                |
| 00 4D  | 0000 000a | WMT2 Wave FXM Switch (0 - 1)                       |
|        |           | OFF, ON                                            |
| 00 4E  | 0000 00aa | WMT2 Wave FXM Color (0 - 3)                        |
|        |           | 1 - 4                                              |
| 00 4F  | 000a aaaa | WMT2 Wave FXM Depth (0 - 16)                       |
|        |           | OFF, ON                                            |
| 00 50  | 0000 000a | WMT2 Wave Tempo Sync (0 - 1)                       |
|        |           | OFF, ON                                            |
| 00 51  | 0aaa aaaa | WMT2 Wave Coarse Tune (16 - 112)                   |
|        |           | -48 - +48                                          |
| 00 52  | 0aaa aaaa | WMT2 Wave Fine Tune (14 - 114)                     |
|        |           | -50 - +50                                          |
| 00 53  | 0aaa aaaa | WMT2 Wave Pan (0 - 127)                            |
|        |           | L64 - 63R                                          |
| 00 54  | 0000 000a | WMT2 Wave Random Pan Switch (0 - 1)                |
|        |           | OFF, ON                                            |
| 00 55  | 0000 00aa | WMT2 Wave Alternate Pan Switch (0 - 2)             |
|        |           | OFF, ON, REVERSE                                   |
| 00 56  | 0aaa aaaa | WMT2 Wave Level (0 - 127)                          |
|        |           | OFF, ON                                            |
| 00 57  | 0aaa aaaa | WMT2 Velocity Range Lower (1 - 127)                |
|        |           | 1 - UPPER                                          |
| 00 58  | 0aaa aaaa | WMT2 Velocity Range Upper (1 - 127)                |
|        |           | LOWER - 127                                        |
| 00 59  | 0aaa aaaa | WMT2 Velocity Fade Width Lower (0 - 127)           |
| 00 5A  | 0aaa aaaa | WMT2 Velocity Fade Width Upper (0 - 127)           |
+--------+-----------+----------------------------------------------------+
| 00 5B  | 0000 000a | WMT3 Wave Switch (0 - 1)                           |
|        |           | OFF, ON                                            |
| 00 5C  | 0000 00aa | WMT3 Wave Group Type (0)                           |
| 00 5D  | 0000 aaaa | WMT3 Wave Group ID (0 - 16384)                     |
|        |           | OFF, 1 - 16384                                     |
| 00 61  | 0000 aaaa | WMT3 Wave Number L (Mono) (0 - 16384)              |
|        |           | OFF, 1 - 16384                                     |
| 00 69  | 0000 00aa | WMT3 Wave Gain (0 - 3)                             |
|        |           | -6, 0, +6, +12 [dB]                                |
| 00 6A  | 0000 000a | WMT3 Wave FXM Switch (0 - 1)                       |
|        |           | OFF, ON                                            |
| 00 6B  | 0000 00aa | WMT3 Wave FXM Color (0 - 3)                        |
|        |           | 1 - 4                                              |
| 00 6C  | 000a aaaa | WMT3 Wave FXM Depth (0 - 16)                       |
|        |           | OFF, ON                                            |
| 00 6D  | 0000 000a | WMT3 Wave Tempo Sync (0 - 1)                       |
|        |           | OFF, ON                                            |
| 00 6E  | 0aaa aaaa | WMT3 Wave Coarse Tune (16 - 112)                   |
|        |           | -48 - +48                                          |
| 00 6F  | 0aaa aaaa | WMT3 Wave Fine Tune (14 - 114)                     |
|        |           | -50 - +50                                          |
| 00 70  | 0aaa aaaa | WMT3 Wave Pan (0 - 127)                            |
|        |           | L64 - 63R                                          |
| 00 71  | 0000 000a | WMT3 Wave Random Pan Switch (0 - 1)                |
|        |           | OFF, ON                                            |
| 00 72  | 0000 00aa | WMT3 Wave Alternate Pan Switch (0 - 2)             |
|        |           | OFF, ON, REVERSE                                   |
| 00 73  | 0aaa aaaa | WMT3 Wave Level (0 - 127)                          |
|        |           | OFF, ON                                            |
| 00 74  | 0aaa aaaa | WMT3 Velocity Range Lower (1 - 127)                |
|        |           | 1 - UPPER                                          |
| 00 75  | 0aaa aaaa | WMT3 Velocity Range Upper (1 - 127)                |
|        |           | LOWER - 127                                        |
| 00 76  | 0aaa aaaa | WMT3 Velocity Fade Width Lower (0 - 127)           |
| 00 77  | 0aaa aaaa | WMT3 Velocity Fade Width Upper (0 - 127)           |
+--------+-----------+----------------------------------------------------+
| 00 78  | 0000 000a | WMT4 Wave Switch (0 - 1)                           |
|        |           | OFF, ON                                            |
| 00 79  | 0000 00aa | WMT4 Wave Group Type (0)                           |
| 00 7A  | 0000 aaaa | WMT4 Wave Group ID (0 - 16384)                     |
|        |           | OFF, 1 - 16384                                     |
| 00 7E  | 0000 aaaa | WMT4 Wave Number L (Mono) (0 - 16384)              |
|        |           | OFF, 1 - 16384                                     |
| 01 02  | 0000 aaaa | WMT4 Wave Number R (0 - 16384)                     |
|        |           | OFF, 1 - 16384                                     |
| 01 06  | 0000 00aa | WMT4 Wave Gain (0 - 3)                             |
|        |           | -6, 0, +6, +12 [dB]                                |
| 01 07  | 0000 000a | WMT4 Wave FXM Switch (0 - 1)                       |
|        |           | OFF, ON                                            |
| 01 08  | 0000 00aa | WMT4 Wave FXM Color (0 - 3)                        |
|        |           | 1 - 4                                              |
| 01 09  | 000a aaaa | WMT4 Wave FXM Depth (0 - 16)                       |
|        |           | OFF, ON                                            |
| 01 0A  | 0000 000a | WMT4 Wave Tempo Sync (0 - 1)                       |
|        |           | OFF, ON                                            |
| 01 0B  | 0aaa aaaa | WMT4 Wave Coarse Tune (16 - 112)                   |
|        |           | -48 - +48                                          |
| 01 0C  | 0aaa aaaa | WMT4 Wave Fine Tune (14 - 114)                     |
|        |           | -50 - +50                                          |
| 01 0D  | 0aaa aaaa | WMT4 Wave Pan (0 - 127)                            |
|        |           | L64 - 63R                                          |
| 01 0E  | 0000 000a | WMT4 Wave Random Pan Switch (0 - 1)                |
|        |           | OFF, ON                                            |
| 01 0F  | 0000 00aa | WMT4 Wave Alternate Pan Switch (0 - 2)             |
|        |           | OFF, ON, REVERSE                                   |
| 01 10  | 0aaa aaaa | WMT4 Wave Level (0 - 127)                          |
|        |           | OFF, ON                                            |
| 01 11  | 0aaa aaaa | WMT4 Velocity Range Lower (1 - 127)                |
|        |           | 1 - UPPER                                          |
| 01 12  | 0aaa aaaa | WMT4 Velocity Range Upper (1 - 127)                |
|        |           | LOWER - 127                                        |
| 01 13  | 0aaa aaaa | WMT4 Velocity Fade Width Lower (0 - 127)           |
|        |           | OFF, ON                                            |
| 01 14  | 0aaa aaaa | WMT4 Velocity Fade Width Upper (0 - 127)           |
|        |           | OFF, ON                                            |
+--------+-----------+----------------------------------------------------+
| 01 15  | 000a aaaa | Pitch Env Depth (52 - 76)                            |
|        |           | -12 - +12                                          |
| 01 16  | 0aaa aaaa | Pitch Env Velocity Sens (1 - 127)                  |
|        |           | -63 - +63                                          |
| 01 17  | 0aaa aaaa | Pitch Env Time 1 Velocity Sens (1 - 127)            |
|        |           | -63 - +63                                          |
| 01 18  | 0aaa aaaa | Pitch Env Time 4 Velocity Sens (1 - 127)            |
|        |           | -63 - +63                                          |
| 01 19  | 0aaa aaaa | Pitch Env Time 1 (0 - 127)                          |
|        |           | OFF, ON                                            |
| 01 1A  | 0aaa aaaa | Pitch Env Time 2 (0 - 127)                          |
|        |           | OFF, ON                                            |
| 01 1B  | 0aaa aaaa | Pitch Env Time 3 (0 - 127)                          |
|        |           | OFF, ON                                            |
| 01 1C  | 0aaa aaaa | Pitch Env Time 4 (0 - 127)                          |
|        |           | OFF, ON                                            |
| 01 1D  | 0aaa aaaa | Pitch Env Level 0 (1 - 127)                          |
|        |           | -63 - +63                                          |
| 01 1E  | 0aaa aaaa | Pitch Env Level 1 (1 - 127)                          |
|        |           | -63 - +63                                          |
| 01 1F  | 0aaa aaaa | Pitch Env Level 2 (1 - 127)                          |
|        |           | -63 - +63                                          |
| 01 20  | 0aaa aaaa | Pitch Env Level 3 (1 - 127)                          |
|        |           | -63 - +63                                          |
| 01 21  | 0aaa aaaa | Pitch Env Level 4 (1 - 127)                          |
|        |           | -63 - +63                                          |
+--------+-----------+----------------------------------------------------+
| 01 22  | 0000 0aaa | TVF Filter Type (0 - 6)                            |
|        |           | OFF, LPF, BPF, HPF, PKG, LPF2,                      |
|        |           | LPF3                                              |
| 01 23  | 0aaa aaaa | TVF Cutoff Frequency (0 - 127)                      |
|        |           | OFF, ON                                            |
| 01 24  | 0000 0aaa | TVF Cutoff Velocity Curve (0 - 7)                    |
|        |           | FIXED, 1 - 7                                        |
| 01 25  | 0aaa aaaa | TVF Cutoff Velocity Sens (1 - 127)                    |
|        |           | -63 - +63                                          |
| 01 26  | 0aaa aaaa | TVF Resonance (0 - 127)                              |
|        |           | OFF, ON                                            |
| 01 27  | 0aaa aaaa | TVF Resonance Velocity Sens (1 - 127)                |
|        |           | -63 - +63                                          |
| 01 28  | 0aaa aaaa | TVF Env Depth (1 - 127)                              |
|        |           | -63 - +63                                          |
| 01 29  | 0000 0aaa | TVF Env Velocity Curve Type (0 - 7)                    |
|        |           | FIXED, 1 - 7                                        |
| 01 2A  | 0aaa aaaa | TVF Env Velocity Sens (1 - 127)                        |
|        |           | -63 - +63                                          |
| 01 2B  | 0aaa aaaa | TVF Env Time 1 Velocity Sens (1 - 127)                |
|        |           | -63 - +63                                          |
| 01 2C  | 0aaa aaaa | TVF Env Time 4 Velocity Sens (1 - 127)                |
|        |           | -63 - +63                                          |
| 01 2D  | 0aaa aaaa | TVF Env Time 1 (0 - 127)                              |
|        |           | OFF, ON                                            |
| 01 2E  | 0aaa aaaa | TVF Env Time 2 (0 - 127)                              |
|        |           | OFF, ON                                            |
| 01 2F  | 0aaa aaaa | TVF Env Time 3 (0 - 127)                              |
|        |           | OFF, ON                                            |
| 01 30  | 0aaa aaaa | TVF Env Time 4 (0 - 127)                              |
|        |           | OFF, ON                                            |
| 01 31  | 0aaa aaaa | TVF Env Level 0 (0 - 127)                              |
|        |           | OFF, ON                                            |
| 01 32  | 0aaa aaaa | TVF Env Level 1 (0 - 127)                              |
|        |           | OFF, ON                                            |
| 01 33  | 0aaa aaaa | TVF Env Level 2 (0 - 127)                              |
|        |           | OFF, ON                                            |
| 01 34  | 0aaa aaaa | TVF Env Level 3 (0 - 127)                              |
|        |           | OFF, ON                                            |
| 01 35  | 0aaa aaaa | TVF Env Level 4 (0 - 127)                              |
|        |           | OFF, ON                                            |
+--------+-----------+----------------------------------------------------+
| 01 36  | 0000 0aaa | TVA Level Velocity Curve (0 - 7)                          |
|        |           | FIXED, 1 - 7                                          |
| 01 37  | 0aaa aaaa | TVA Level Velocity Sens (1 - 127)                          |
|        |           | -63 - +63                                              |
| 01 38  | 0aaa aaaa | TVA Env Time 1 Velocity Sens (1 - 127)                          |
|        |           | -63 - +63                                              |
| 01 39  | 0aaa aaaa | TVA Env Time 4 Velocity Sens (1 - 127)                          |
|        |           | -63 - +63                                              |
| 01 3A  | 0aaa aaaa | TVA Env Time 1 (0 - 127)                          |
|        |           | OFF, ON                                                |
| 01 3B  | 0aaa aaaa | TVA Env Time 2 (0 - 127)                          |
|        |           | OFF, ON                                                |
| 01 3C  | 0aaa aaaa | TVA Env Time 3 (0 - 127)                          |
|        |           | OFF, ON                                                |
| 01 3D  | 0aaa aaaa | TVA Env Time 4 (0 - 127)                          |
|        |           | OFF, ON                                                |
| 01 3E  | 0aaa aaaa | TVA Env Level 1 (0 - 127)                          |
|        |           | OFF, ON                                                |
| 01 3F  | 0aaa aaaa | TVA Env Level 2 (0 - 127)                          |
|        |           | OFF, ON                                                |
| 01 40  | 0aaa aaaa | TVA Env Level 3 (0 - 127)                          |
|        |           | OFF, ON                                                |
+--------+-----------+----------------------------------------------------+
| 01 41  | 0000 000a | One Shot Mode (0 - 1)                              |
|        |           | OFF, ON                                                |
| 01 42  | 0aaa aaaa | Relative Level (0 - 127)                              |
|        |           | -64 - +63                                              |
+--------+-----------+----------------------------------------------------+
| 00 00 01 43 | Total Size |
+------------------------------------------------------------------------------+

"""
# Parameter Groups
ANALOG_OSC_GROUP = 0x00  # Oscillator parameters
ANALOG_FILTER_GROUP = 0x01  # Filter parameters
ANALOG_AMP_GROUP = 0x02  # Amplifier parameters
ANALOG_LFO_GROUP = 0x03  # LFO parameters


# Waveform
class Waveform(Enum):
    """Analog oscillator waveform types"""

    SAW = 0
    TRIANGLE = 1
    PULSE = 2  # Changed from SQUARE to PULSE to match JD-Xi terminology

    @property
    def display_name(self) -> str:
        """Get display name for waveform"""
        names = {0: "SAW", 1: "TRI", 2: "P.W"}  # Updated display name
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for waveform"""
        return self.value


class SubOscType(Enum):
    """Analog sub oscillator types"""

    OFF = 0x00  # Sub oscillator off
    OCT_DOWN_1 = 0x01  # -1 octave
    OCT_DOWN_2 = 0x02  # -2 octaves

    @property
    def display_name(self) -> str:
        """Get display name for sub oscillator preset_type"""
        names = {0x00: "OFF", 0x01: "-1 OCT", 0x02: "-2 OCT"}
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for sub oscillator preset_type"""
        return self.value


class LFOShape(Enum):
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


# Parameter value ranges
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

# LFO Sync Note Values
LFO_SYNC_NOTES = [
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


class AnalogParameters(IntEnum):
    """Analog synth parameters"""

    # Oscillator
    OSC_WAVE = 0x00  # Oscillator waveform (0-3)
    OSC_MOD = 0x01  # Oscillator mod (0-127)
    OSC_PITCH = 0x02  # Oscillator pitch (-24 to +24)
    OSC_DETUNE = 0x03  # Oscillator detune (-50 to +50)
    OSC_LEVEL = 0x04  # Oscillator level (0-127)

    # Filter
    FILTER_TYPE = 0x10  # Filter preset_type (0-3)
    FILTER_CUTOFF = 0x11  # Filter cutoff (0-127)
    FILTER_RESO = 0x12  # Filter resonance (0-127)
    FILTER_ENV = 0x13  # Filter envelope depth (-63 to +63)
    FILTER_KEY = 0x14  # Filter keyboard follow (0-127)

    # Amplifier
    AMP_LEVEL = 0x20  # Amplifier level (0-127)
    AMP_PAN = 0x21  # Amplifier pan (0-127, 64=center)

    # Envelopes
    FILTER_ATTACK = 0x30  # Filter envelope attack (0-127)
    FILTER_DECAY = 0x31  # Filter envelope decay (0-127)
    FILTER_SUSTAIN = 0x32  # Filter envelope sustain (0-127)
    FILTER_RELEASE = 0x33  # Filter envelope release (0-127)

    AMP_ATTACK = 0x34  # Amplifier envelope attack (0-127)
    AMP_DECAY = 0x35  # Amplifier envelope decay (0-127)
    AMP_SUSTAIN = 0x36  # Amplifier envelope sustain (0-127)
    AMP_RELEASE = 0x37  # Amplifier envelope release (0-127)

    # LFO
    LFO_WAVE = 0x40  # LFO waveform (0-3)
    LFO_RATE = 0x41  # LFO rate (0-127)
    LFO_FADE = 0x42  # LFO fade time (0-127)
    LFO_PITCH = 0x43  # LFO pitch depth (0-127)
    LFO_FILTER = 0x44  # LFO filter depth (0-127)
    LFO_AMP = 0x45  # LFO amplitude depth (0-127)

    # Effects sends
    DELAY_SEND = 0x50  # Delay send level (0-127)
    REVERB_SEND = 0x51  # Reverb send level (0-127)


class OscillatorWave(IntEnum):
    """Analog oscillator waveforms"""

    SAW = 0
    SQUARE = 1
    TRIANGLE = 2
    SINE = 3


class FilterType(IntEnum):
    """Analog filter types"""

    LPF = 0  # Low Pass Filter
    HPF = 1  # High Pass Filter
    BPF = 2  # Band Pass Filter
    PKG = 3  # Peaking Filter


class LFOWave(IntEnum):
    """Analog LFO waveforms"""

    TRIANGLE = 0
    SINE = 1
    SAW = 2
    SQUARE = 3
