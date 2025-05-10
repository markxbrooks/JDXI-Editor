"""Effects"""

from dataclasses import dataclass
from enum import Enum

from jdxi_editor.midi.data.address.address import (
    CommandID,
    AddressMemoryAreaMSB,
    AddressOffsetProgramLMB,
)
from jdxi_editor.midi.data.address.sysex import LOW_7_BITS_MASK, LOW_4_BITS_MASK, ZERO_BYTE
from jdxi_editor.midi.message.roland import RolandSysEx


class EffectType(Enum):
    """Effect types available on JD-Xi"""

    THRU = 0x00
    DISTORTION = 0x01
    FUZZ = 0x02
    COMPRESSOR = 0x03
    BITCRUSHER = 0x04
    FLANGER = 0x05
    PHASER = 0x06
    RING_MOD = 0x07
    SLICER = 0x08

    # Common parameters
    LEVEL = 0x00
    MIX = 0x01

    # Effect-specific parameters
    DRIVE = 0x10
    TONE = 0x11
    ATTACK = 0x12
    RELEASE = 0x13
    THRESHOLD = 0x14
    RATIO = 0x15
    BIT_DEPTH = 0x16
    RATE = 0x17
    DEPTH = 0x18
    FEEDBACK = 0x19
    FREQUENCY = 0x1A
    BALANCE = 0x1B
    PATTERN = 0x1C

    # Send levels
    REVERB_SEND = 0x20
    DELAY_SEND = 0x21
    CHORUS_SEND = 0x22

    # Reverb parameters
    REVERB_TYPE = 0x30
    REVERB_TIME = 0x31
    REVERB_PRE_DELAY = 0x32


class FX:
    """Effect parameter ranges and defaults"""

    RANGES = {
        # Common parameters
        "level": (0, 127),
        # Distortion parameters
        "dist_drive": (0, 127),
        "dist_tone": (0, 127),
        # Compressor parameters
        "comp_attack": (0, 127),
        "comp_release": (0, 127),
        "comp_threshold": (0, 127),
        "comp_ratio": (0, 127),
        # Bitcrusher parameters
        "bit_depth": (0, 127),
        "sample_rate": (0, 127),
        # Flanger parameters
        "flanger_rate": (0, 127),
        "flanger_depth": (0, 127),
        "flanger_feedback": (0, 127),
        # Phaser parameters
        "phaser_rate": (0, 127),
        "phaser_depth": (0, 127),
        "phaser_resonance": (0, 127),
        # Ring Modulator parameters
        "ring_freq": (0, 127),
        "ring_balance": (0, 127),
        # Slicer parameters
        "slicer_rate": (0, 127),
        "slicer_pattern": (0, 15),
    }

    DEFAULTS = {
        "level": 100,
        "dist_drive": 64,
        "dist_tone": 64,
        "comp_attack": 0,
        "comp_release": 50,
        "comp_threshold": 0,
        "comp_ratio": 0,
        "bit_depth": 127,
        "sample_rate": 127,
        "flanger_rate": 64,
        "flanger_depth": 64,
        "flanger_feedback": 64,
        "phaser_rate": 64,
        "phaser_depth": 64,
        "phaser_resonance": 64,
        "ring_freq": 64,
        "ring_balance": 64,
        "slicer_rate": 64,
        "slicer_pattern": 0,
    }


@dataclass
class EffectPatch:
    """Effect patch data"""

    # Effect preset_type and common parameters
    type: EffectType = EffectType.THRU
    level: int = 100

    # Effect-specific parameters
    param1: int = 0
    param2: int = 0

    # Send levels
    reverb_send: int = 0
    delay_send: int = 0
    chorus_send: int = 0

    def validate_param(self, param: str, value: int) -> bool:
        """Validate parameter value is in range"""
        if param in FX.RANGES:
            min_val, max_val = FX.RANGES[param]
            return min_val <= value <= max_val
        return False


@dataclass
class EffectParam:
    """Effect parameter definition"""

    name: str
    min_value: int = -20000
    max_value: int = 20000
    default: int = 0
    unit: str = ""


class EfxType(Enum):
    """Effect types for JD-Xi"""

    # Reverb Types (0-7)
    ROOM1 = 0
    ROOM2 = 1
    STAGE1 = 2
    STAGE2 = 3
    HALL1 = 4
    HALL2 = 5
    PLATE = 6
    SPRING = 7

    # Delay Types (0-4)
    STEREO = 0
    PANNING = 1
    MONO = 2
    TAPE_ECHO = 3
    MOD_DELAY = 4

    # FX Types (0-12)
    DISTORTION = 0
    FUZZ = 1
    COMPRESSOR = 2
    BITCRUSHER = 3
    EQUALIZER = 4
    PHASER = 5
    FLANGER = 6
    CHORUS = 7
    TREMOLO = 8
    AUTOPAN = 9
    SLICER = 10
    RING_MOD = 11
    ISOLATOR = 12

    @staticmethod
    def get_display_name(value: int, effect_type: str) -> str:
        """Get display name for effect preset_type"""
        names = {
            "reverb": {
                0: "Room 1",
                1: "Room 2",
                2: "Stage 1",
                3: "Stage 2",
                4: "Hall 1",
                5: "Hall 2",
                6: "Plate",
                7: "Spring",
            },
            "delay": {
                0: "Stereo",
                1: "Panning",
                2: "Mono",
                3: "Tape Echo",
                4: "Mod Delay",
            },
            "fx": {
                0: "Distortion",
                1: "Fuzz",
                2: "Compressor",
                3: "Bitcrusher",
                4: "Equalizer",
                5: "Phaser",
                6: "Flanger",
                7: "Chorus",
                8: "Tremolo",
                9: "Auto Pan",
                10: "Slicer",
                11: "Ring Mod",
                12: "Isolator",
            },
        }
        return names.get(effect_type, {}).get(value, "???")


class EffectGroup(Enum):
    """Effect parameter groups"""

    COMMON = 0x00  # Common parameters
    INSERT = 0x10  # Insert effect parameters
    REVERB = 0x20  # Reverb parameters
    DELAY = 0x30  # Delay parameters


class Effect1(Enum):
    """Program Effect 1 parameters"""

    TYPE = 0x00  # Effect preset_type (0-4)
    LEVEL = 0x01  # Effect level (0-127)
    DELAY_SEND = 0x02  # Delay send level (0-127)
    REVERB_SEND = 0x03  # Reverb send level (0-127)
    OUTPUT_ASSIGN = 0x04  # Output assign (0: DIR, 1: EFX2)

    # Parameters start at 0x11 and go up to 0x10D
    # Each parameter is 4 bytes (12768-52768: -20000 to +20000)
    PARAM_1 = 0x11  # Parameter 1
    PARAM_2 = 0x15  # Parameter 2
    # ... continue for all 32 parameters
    PARAM_32 = 0x10D  # Parameter 32

    @staticmethod
    def get_param_offset(param_num: int) -> int:
        """Get parameter offset from parameter number (1-32)"""
        if 1 <= param_num <= 32:
            return 0x11 + ((param_num - 1) * 4)
        return 0x00

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Effect preset_type
            return ["OFF", "DISTORTION", "FUZZ", "COMPRESSOR", "BITCRUSHER"][value]
        elif param == 0x04:  # Output assign
            return ["DIR", "EFX2"][value]
        elif 0x11 <= param <= 0x10D:  # Effect parameters
            return f"{value - 32768:+d}"  # Convert 12768-52768 to -20000/+20000
        return str(value)


@dataclass
class Effect1Message(RolandSysEx):
    """Program Effect 1 parameter message"""

    command: int = CommandID.DT1
    area: int = AddressMemoryAreaMSB.TEMPORARY_PROGRAM  # 0x18: Program area
    section: int = 0x02  # 0x02: Effect 1 section
    group: int = AddressOffsetProgramLMB.TONE_COMMON  # Always 0x00
    lsb: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.msb,  # Program area (0x18)
            self.section,  # Effect 1 section (0x02)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        # Handle 4-byte parameters
        if 0x11 <= self.param <= 0x10D:
            # Convert -20000/+20000 to 12768-52768
            value = self.value + 32768
            self.data = [
                (value >> 24) & LOW_4_BITS_MASK,  # High nibble
                (value >> 16) & LOW_4_BITS_MASK,
                (value >> 8) & LOW_4_BITS_MASK,
                value & LOW_4_BITS_MASK,  # Low nibble
            ]
        else:
            self.data = [self.value]


class Effect2(Enum):
    """Program Effect 2 parameters"""

    TYPE = 0x00  # Effect preset_type (0, 5-8: OFF, PHASER, FLANGER, DELAY, CHORUS)
    LEVEL = 0x01  # Effect level (0-127)
    DELAY_SEND = 0x02  # Delay send level (0-127)
    REVERB_SEND = 0x03  # Reverb send level (0-127)

    # Reserved (0x04-0x10)

    # Parameters start at 0x11 and go up to 0x10D
    # Each parameter is 4 bytes (12768-52768: -20000 to +20000)
    PARAM_1 = 0x11  # Parameter 1
    PARAM_2 = 0x15  # Parameter 2
    # ... continue for all 32 parameters
    PARAM_32 = 0x10D  # Parameter 32

    @staticmethod
    def get_param_offset(param_num: int) -> int:
        """Get parameter offset from parameter number (1-32)"""
        if 1 <= param_num <= 32:
            return 0x11 + ((param_num - 1) * 4)
        return 0x00

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == ZERO_BYTE:  # Effect preset_type
            if value == 0:
                return "OFF"
            types = ["OFF", "PHASER", "FLANGER", "DELAY", "CHORUS"]
            return types[value - 4] if 5 <= value <= 8 else str(value)
        elif 0x11 <= param <= 0x10D:  # Effect parameters
            return f"{value - 32768:+d}"  # Convert 12768-52768 to -20000/+20000
        return str(value)


@dataclass
class Effect2Message(RolandSysEx):
    """Program Effect 2 parameter message"""

    command: int = CommandID.DT1
    msb: int = AddressMemoryAreaMSB.TEMPORARY_PROGRAM  # 0x18: Program area
    umb: int = 0x04  # 0x04: Effect 2 section
    lmb: int = 0x00  # Always 0x00
    lsb: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self, param):
        """Set up address and data"""
        self.param = param
        self.address = [
            self.msb,  # Program area (0x18)
            self.umb,  # Effect 2 section (0x04)
            self.lmb,  # Always 0x00
            self.param,  # Parameter number
        ]
        # Handle 4-byte parameters
        if 0x11 <= self.param <= 0x10D:
            # Convert -20000/+20000 to 12768-52768
            value = self.value + 32768
            self.data = [
                (value >> 24) & LOW_4_BITS_MASK,  # High nibble
                (value >> 16) & LOW_4_BITS_MASK,
                (value >> 8) & LOW_4_BITS_MASK,
                value & LOW_4_BITS_MASK,  # Low nibble
            ]
        else:
            self.data = [self.value]
