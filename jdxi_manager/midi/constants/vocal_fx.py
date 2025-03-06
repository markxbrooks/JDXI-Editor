"""Vocal FX MIDI constants"""

from enum import Enum

# Areas and Parts
VOCAL_FX_AREA = 0x18
VOCAL_FX_PART = 0x00
VOCAL_FX_GROUP = 0x01  # Different area from arpeggiator


class VocalFxSwitch(Enum):
    """Vocal FX switch values"""
    OFF = 0
    ON = 1

    @property
    def display_name(self) -> str:
        """Get display name for switch value"""
        return "ON" if self.value else "OFF"

    @property
    def midi_value(self) -> int:
        """Get MIDI value for switch"""
        return self.value

class AutoNoteSwitch(Enum):
    """Auto Note switch values"""
    OFF = 0
    ON = 1

    @property
    def display_name(self) -> str:
        """Get display name for switch value"""
        return "ON" if self.value else "OFF"

    @property
    def midi_value(self) -> int:
        """Get MIDI value for switch"""
        return self.value

class AutoPitchType(Enum):
    """Auto Pitch preset_type values"""
    SOFT = 0
    HARD = 1
    ELECTRIC1 = 2
    ELECTRIC2 = 3

    @property
    def display_name(self) -> str:
        """Get display name for pitch preset_type"""
        names = {
            0: "SOFT",
            1: "HARD",
            2: "ELECTRIC1",
            3: "ELECTRIC2"
        }
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for pitch preset_type"""
        return self.value 

class OutputAssign(Enum):
    """Output assignment values"""
    EFX1 = 0
    EFX2 = 1
    DLY = 2
    REV = 3
    DIR = 4

    @property
    def display_name(self) -> str:
        """Get display name for output assignment"""
        return self.name

    @property
    def midi_value(self) -> int:
        """Get MIDI value for output assignment"""
        return self.value 

class AutoPitchKey(Enum):
    """Auto Pitch key values"""
    C = 0
    Db = 1
    D = 2
    Eb = 3
    E = 4
    F = 5
    Fsharp = 6
    G = 7
    Ab = 8
    A = 9
    Bb = 10
    B = 11
    Cm = 12
    Csharp_m = 13
    Dm = 14
    Dsharp_m = 15
    Em = 16
    Fm = 17
    Fsharp_m = 18
    Gm = 19
    Gsharp_m = 20
    Am = 21
    Bbm = 22
    Bm = 23

    @property
    def display_name(self) -> str:
        """Get display name for key"""
        names = {
            0: "C", 1: "Db", 2: "D", 3: "Eb", 4: "E", 5: "F",
            6: "F#", 7: "G", 8: "Ab", 9: "A", 10: "Bb", 11: "B",
            12: "Cm", 13: "C#m", 14: "Dm", 15: "D#m", 16: "Em",
            17: "Fm", 18: "F#m", 19: "Gm", 20: "G#m", 21: "Am",
            22: "Bbm", 23: "Bm"
        }
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for key"""
        return self.value 

class OctaveRange(Enum):
    """Octave range values"""
    MINUS_ONE = 0
    ZERO = 1
    PLUS_ONE = 2

    @property
    def display_name(self) -> str:
        """Get display name for octave"""
        names = {0: "-1", 1: "0", 2: "+1"}
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for octave"""
        return self.value 

class AutoPitchNote(Enum):
    """Auto Pitch note values"""
    C = 0
    C_SHARP = 1
    D = 2
    D_SHARP = 3
    E = 4
    F = 5
    F_SHARP = 6
    G = 7
    G_SHARP = 8
    A = 9
    A_SHARP = 10
    B = 11

    @property
    def display_name(self) -> str:
        """Get display name for note"""
        names = {
            0: "C",
            1: "C#",
            2: "D",
            3: "D#",
            4: "E",
            5: "F",
            6: "F#",
            7: "G",
            8: "G#",
            9: "A",
            10: "A#",
            11: "B"
        }
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for note"""
        return self.value 

class VocoderEnvelope(Enum):
    """Vocoder envelope types"""
    SHARP = 0
    SOFT = 1
    LONG = 2

    @property
    def display_name(self) -> str:
        """Get display name for envelope preset_type"""
        return self.name

    @property
    def midi_value(self) -> int:
        """Get MIDI value for envelope preset_type"""
        return self.value

class VocoderHPF(Enum):
    """Vocoder HPF frequencies"""
    BYPASS = 0
    FREQ_1000 = 1
    FREQ_1250 = 2
    FREQ_1600 = 3
    FREQ_2000 = 4
    FREQ_2500 = 5
    FREQ_3150 = 6
    FREQ_4000 = 7
    FREQ_5000 = 8
    FREQ_6300 = 9
    FREQ_8000 = 10
    FREQ_10000 = 11
    FREQ_12500 = 12
    FREQ_16000 = 13

    @property
    def display_name(self) -> str:
        """Get display name for HPF frequency"""
        names = {
            0: "BYPASS",
            1: "1000 Hz",
            2: "1250 Hz",
            3: "1600 Hz",
            4: "2000 Hz",
            5: "2500 Hz",
            6: "3150 Hz",
            7: "4000 Hz",
            8: "5000 Hz",
            9: "6300 Hz",
            10: "8000 Hz",
            11: "10000 Hz",
            12: "12500 Hz",
            13: "16000 Hz"
        }
        return names.get(self.value, "???")

    @property
    def midi_value(self) -> int:
        """Get MIDI value for HPF frequency"""
        return self.value 