"""Constants for Roland JD-Xi MIDI protocol"""

from enum import auto
from dataclasses import dataclass

from jdxi_editor.midi.message.roland import RolandSysEx
from .sysex import SETUP_AREA, DT1_COMMAND_12, PROGRAM_AREA, SYSTEM_AREA, SYSTEM_COMMON, SYSTEM_CONTROLLER

# Import other module constants as needed
from .digital import *
from .vocal_fx import *
from ..parameter.synth import SynthParameter


class Waveform(Enum):
    """Waveform types available on JD-Xi"""

    SAW = 0x00  # Sawtooth wave
    SQUARE = 0x01  # Square wave
    PW_SQUARE = 0x02  # Pulse width square wave
    TRIANGLE = 0x03  # Triangle wave
    SINE = 0x04  # Sine wave
    NOISE = 0x05  # Noise
    SUPER_SAW = 0x06  # Super saw
    PCM = 0x07  # PCM waveform


class DigitalGroup(Enum):
    """Digital synth parameter groups"""

    COMMON = 0x00  # Common parameters
    PARTIAL = 0x20  # Partial parameters
    LFO = 0x40  # LFO parameters
    ENV = 0x60  # Envelope parameters


class FilterMode(Enum):
    """Filter modes available on JD-Xi"""

    BYPASS = 0x00
    LPF = 0x01  # Low Pass Filter
    HPF = 0x02  # High Pass Filter
    BPF = 0x03  # Band Pass Filter
    PKG = 0x04  # Peaking Filter
    LPF2 = 0x05  # Low Pass Filter 2
    LPF3 = 0x06  # Low Pass Filter 3
    LPF4 = 0x07  # Low Pass Filter 4


# System Common Parameters (0x02 00)
class SystemCommon(Enum):
    """System Common parameters"""

    MASTER_TUNE = 0x00  # Master Tune (24-2024: -100.0 to +100.0 cents)
    MASTER_KEY_SHIFT = 0x04  # Master Key Shift (40-88: -24 to +24 semitones)
    MASTER_LEVEL = 0x05  # Master Level (0-127)

    # Reserved space (0x06-0x10)

    PROGRAM_CTRL_CH = 0x11  # Program Control Channel (0-16: 1-16, OFF)

    # Reserved space (0x12-0x28)

    RX_PROGRAM_CHANGE = 0x29  # Receive Program Change (0: OFF, 1: ON)
    RX_BANK_SELECT = 0x2A  # Receive Bank Select (0: OFF, 1: ON)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Master Tune
            cents = (value - 1024) / 10  # Convert 24-2024 to -100.0/+100.0
            return f"{cents:+.1f} cents"
        elif param == 0x04:  # Master Key Shift
            semitones = value - 64  # Convert 40-88 to -24/+24
            return f"{semitones:+d} st"
        elif param == 0x11:  # Program Control Channel
            return "OFF" if value == 0 else str(value)
        elif param in (0x29, 0x2A):  # Switches
            return "ON" if value else "OFF"
        return str(value)


@dataclass
class SystemCommonMessage(RolandSysEx):
    """System Common parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SYSTEM_AREA  # 0x02: System area
    section: int = SYSTEM_COMMON  # 0x00: Common section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Common section (0x00)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]


"""
# Example usage:
# Set master tune to +50 cents
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_TUNE.value,
    value=1024 + (50 * 10),  # Convert +50.0 cents to 1524
)

# Set master key shift to -12 semitones
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_KEY_SHIFT.value, value=52  # Convert -12 to 52 (64-12)
)

# Set program control channel to 1
msg = SystemCommonMessage(
    param=SystemCommon.PROGRAM_CTRL_CH.value, value=1  # Channel 1
)

# Enable program change reception
msg = SystemCommonMessage(param=SystemCommon.RX_PROGRAM_CHANGE.value, value=1)  # ON
"""


# System Controller Parameters (0x02 03)
class SystemController(Enum):
    """System Controller parameters"""

    TX_PROGRAM_CHANGE = 0x00  # Transmit Program Change (0: OFF, 1: ON)
    TX_BANK_SELECT = 0x01  # Transmit Bank Select (0: OFF, 1: ON)
    KEYBOARD_VELOCITY = 0x02  # Keyboard Velocity (0: REAL, 1-127: Fixed)
    VELOCITY_CURVE = 0x03  # Keyboard Velocity Curve (0: LIGHT, 1: MEDIUM, 2: HEAVY)
    VELOCITY_OFFSET = 0x04  # Keyboard Velocity Curve Offset (54-73: -10 to +9)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param in (0x00, 0x01):  # Switches
            return "ON" if value else "OFF"
        elif param == 0x02:  # Keyboard velocity
            return "REAL" if value == 0 else str(value)
        elif param == 0x03:  # Velocity curve
            return ["LIGHT", "MEDIUM", "HEAVY"][value]
        elif param == 0x04:  # Velocity offset
            return f"{value - 64:+d}"  # Convert 54-73 to -10/+9
        return str(value)


@dataclass
class SystemControllerMessage(RolandSysEx):
    """System Controller parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SYSTEM_AREA  # 0x02: System area
    section: int = SYSTEM_CONTROLLER  # 0x03: Controller section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Controller section (0x03)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]

"""
# Example usage:
# Enable program change transmission
msg = SystemControllerMessage(
    param=SystemController.TX_PROGRAM_CHANGE.value, value=1  # ON
)

# Set keyboard velocity to REAL
msg = SystemControllerMessage(
    param=SystemController.KEYBOARD_VELOCITY.value, value=0  # REAL
)

# Set velocity curve to MEDIUM
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_CURVE.value, value=1  # MEDIUM
)

# Set velocity offset to +5
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_OFFSET.value, value=69  # Convert +5 to 69 (64+5)
)
"""


# Parameter Groups
class ToneGroup(Enum):
    """Tone parameter groups"""

    COMMON = 0x00  # Common parameters
    OSC = 0x01  # Oscillator parameters
    FILTER = 0x02  # Filter parameters
    AMP = 0x03  # Amplifier parameters
    LFO = 0x04  # LFO parameters
    EFFECTS = 0x05  # Effects parameters


# Program Area Structure (0x18)
class ProgramArea(Enum):
    """Program memory areas"""

    COMMON = 0x00  # 00 00 00: Program Common
    VOCAL_FX = 0x01  # 00 01 00: Program Vocal Effect
    EFFECT_1 = 0x02  # 00 02 00: Program Effect 1
    EFFECT_2 = 0x04  # 00 04 00: Program Effect 2
    DELAY = 0x06  # 00 06 00: Program Delay
    REVERB = 0x08  # 00 08 00: Program Reverb

    # Program Parts
    DIGITAL_1_PART = 0x20  # 00 20 00: Digital Synth Part 1
    DIGITAL_2_PART = 0x21  # 00 21 00: Digital Synth Part 2
    ANALOG_PART = 0x22  # 00 22 00: Analog Synth Part
    DRUMS_PART = 0x23  # 00 23 00: Drums Part

    # Program Zones
    DIGITAL_1_ZONE = 0x30  # 00 30 00: Digital Synth Zone 1
    DIGITAL_2_ZONE = 0x31  # 00 31 00: Digital Synth Zone 2
    ANALOG_ZONE = 0x32  # 00 32 00: Analog Synth Zone
    DRUMS_ZONE = 0x33  # 00 33 00: Drums Zone

    CONTROLLER = 0x40  # 00 40 00: Program Controller


@dataclass
class DigitalToneMessage(RolandSysEx):
    """SuperNATURAL Synth Tone parameter message"""

    command: int = DT1_COMMAND_12
    area: int = 0x19  # Temporary area
    tone_type: int = 0x01  # Digital tone (0x01 or 0x02)
    section: int = 0x00  # Section from DigitalToneSection
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Temporary area (0x19)
            self.tone_type,  # Digital 1 or 2 (0x01/0x02)
            self.section,  # Section (Common/Partial/Modify)
            self.param,  # Parameter number
        ]
        self.data = [self.value]

"""
# Example usage:
# Set common parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.COMMON.value,
    param=0x00,  # Common parameter
    value=64,
)

# Set partial parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.PARTIAL_1.value,
    param=0x00,  # Partial parameter
    value=64,
)

# Set modify parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.MODIFY.value,
    param=0x00,  # Modify parameter
    value=64,
)
"""


class DigitalToneCommon:
    """SuperNATURAL Synth Tone Common parameters"""

    # Tone name (12 characters)
    NAME_1 = 0x00  # Character 1 (ASCII 32-127)
    NAME_2 = 0x01  # Character 2
    NAME_3 = 0x02  # Character 3
    NAME_4 = 0x03  # Character 4
    NAME_5 = 0x04  # Character 5
    NAME_6 = 0x05  # Character 6
    NAME_7 = 0x06  # Character 7
    NAME_8 = 0x07  # Character 8
    NAME_9 = 0x08  # Character 9
    NAME_10 = 0x09  # Character 10
    NAME_11 = 0x0A  # Character 11
    NAME_12 = 0x0B  # Character 12

    # Basic parameters
    LEVEL = 0x0C  # Tone Level (0-127)
    PORTAMENTO_SW = 0x12  # Portamento Switch (0-1)
    PORTA_TIME = 0x13  # Portamento Time (0-127)
    MONO_SW = 0x14  # Mono Switch (0-1)
    OCTAVE = 0x15  # Octave Shift (-3/+3)
    BEND_UP = 0x16  # Pitch Bend Range Up (0-24)
    BEND_DOWN = 0x17  # Pitch Bend Range Down (0-24)

    # Partial switches
    PART1_SW = 0x19  # Partial 1 Switch (0-1)
    PART1_SEL = 0x1A  # Partial 1 Select (0-1)
    PART2_SW = 0x1B  # Partial 2 Switch (0-1)
    PART2_SEL = 0x1C  # Partial 2 Select (0-1)
    PART3_SW = 0x1D  # Partial 3 Switch (0-1)
    PART3_SEL = 0x1E  # Partial 3 Select (0-1)

    # Advanced parameters
    RING_SW = 0x1F  # Ring Switch (0: OFF, 1: ---, 2: ON)
    UNISON_SW = 0x2E  # Unison Switch (0-1)
    PORTA_MODE = 0x31  # Portamento Mode (0: NORMAL, 1: LEGATO)
    LEGATO_SW = 0x32  # Legato Switch (0-1)
    ANALOG_FEEL = 0x34  # Analog Feel (0-127)
    WAVE_SHAPE = 0x35  # Wave Shape (0-127)
    CATEGORY = 0x36  # Tone Category (0-127)
    UNISON_SIZE = 0x3C  # Unison Size (0-3: 2,4,6,8 voices)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x00 <= param <= 0x0B:  # Name characters
            return chr(value) if 32 <= value <= 127 else "?"
        elif param == 0x15:  # Octave shift
            return f"{value - 64:+d}"  # Convert 61-67 to -3/+3
        elif param in (
            0x12,
            0x14,
            0x19,
            0x1A,
            0x1B,
            0x1C,
            0x1D,
            0x1E,
            0x2E,
            0x32,
        ):  # Switches
            return "ON" if value else "OFF"
        elif param == 0x1F:  # Ring switch
            return ["OFF", "---", "ON"][value]
        elif param == 0x31:  # Portamento mode
            return "LEGATO" if value else "NORMAL"
        elif param == 0x3C:  # Unison size
            return str([2, 4, 6, 8][value])  # Convert 0-3 to actual voice count
        return str(value)


class DigitalTonePartial(Enum):
    """Partial parameters for SuperNATURAL Synth Tone"""

    WAVE = 0x00  # Wave number (0-255)
    LEVEL = 0x01  # Partial level (0-127)
    COARSE = 0x02  # Coarse tune (-24 to +24)
    FINE = 0x03  # Fine tune (-50 to +50)
    DETUNE = 0x04  # Detune (-50 to +50)
    ATTACK = 0x05  # Attack time (0-127)
    DECAY = 0x06  # Decay time (0-127)
    SUSTAIN = 0x07  # Sustain level (0-127)
    RELEASE = 0x08  # Release time (0-127)
    PAN = 0x09  # Pan position (-64 to +63)
    FILTER_TYPE = 0x0A  # Filter preset_type (0: OFF, 1: LPF, 2: HPF)
    CUTOFF = 0x0B  # Filter cutoff (0-127)
    RESONANCE = 0x0C  # Filter resonance (0-127)
    ENV_DEPTH = 0x0D  # Filter envelope depth (-63 to +63)
    ENV_VELOCITY = 0x0E  # Filter envelope velocity (-63 to +63)
    ENV_ATTACK = 0x0F  # Filter envelope attack (0-127)
    ENV_DECAY = 0x10  # Filter envelope decay (0-127)
    ENV_SUSTAIN = 0x11  # Filter envelope sustain (0-127)
    ENV_RELEASE = 0x12  # Filter envelope release (0-127)


class DigitalToneModify:
    """SuperNATURAL Synth Tone Modify parameters"""

    ATTACK_SENS = 0x01  # Attack Time Interval Sens (0-127)
    RELEASE_SENS = 0x02  # Release Time Interval Sens (0-127)
    PORTA_SENS = 0x03  # Portamento Time Interval Sens (0-127)
    ENV_LOOP_MODE = 0x04  # Envelope Loop Mode (0-2)
    ENV_LOOP_SYNC = 0x05  # Envelope Loop Sync Note (0-19)
    CHROM_PORTA = 0x06  # Chromatic Portamento (0-1)

    # Envelope Loop Mode values
    LOOP_OFF = 0  # OFF
    LOOP_FREE = 1  # FREE-RUN
    LOOP_SYNC = 2  # TEMPO-SYNC

    # Sync note values (for ENV_LOOP_SYNC)
    SYNC_16 = 0  # 16
    SYNC_12 = 1  # 12
    SYNC_8 = 2  # 8
    SYNC_4 = 3  # 4
    SYNC_2 = 4  # 2
    SYNC_1 = 5  # 1
    SYNC_3_4 = 6  # 3/4
    SYNC_2_3 = 7  # 2/3
    SYNC_1_2 = 8  # 1/2
    SYNC_3_8 = 9  # 3/8
    SYNC_1_3 = 10  # 1/3
    SYNC_1_4 = 11  # 1/4
    SYNC_3_16 = 12  # 3/16
    SYNC_1_6 = 13  # 1/6
    SYNC_1_8 = 14  # 1/8
    SYNC_3_32 = 15  # 3/32
    SYNC_1_12 = 16  # 1/12
    SYNC_1_16 = 17  # 1/16
    SYNC_1_24 = 18  # 1/24
    SYNC_1_32 = 19  # 1/32

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x04:  # Envelope Loop Mode
            return ["OFF", "FREE-RUN", "TEMPO-SYNC"][value]
        elif param == 0x05:  # Envelope Loop Sync Note
            notes = [
                "16",
                "12",
                "8",
                "4",
                "2",
                "1",
                "3/4",
                "2/3",
                "1/2",
                "3/8",
                "1/3",
                "1/4",
                "3/16",
                "1/6",
                "1/8",
                "3/32",
                "1/12",
                "1/16",
                "1/24",
                "1/32",
            ]
            return notes[value] if 0 <= value <= 19 else str(value)
        elif param == 0x06:  # Chromatic Portamento
            return "ON" if value else "OFF"
        return str(value)


# System Common Parameters (0x02 00)
class SystemCommon(Enum):
    """System Common parameters"""

    MASTER_TUNE = 0x00  # Master Tune (24-2024: -100.0 to +100.0 cents)
    MASTER_KEY_SHIFT = 0x04  # Master Key Shift (40-88: -24 to +24 semitones)
    MASTER_LEVEL = 0x05  # Master Level (0-127)

    # Reserved space (0x06-0x10)

    PROGRAM_CTRL_CH = 0x11  # Program Control Channel (0-16: 1-16, OFF)

    # Reserved space (0x12-0x28)

    RX_PROGRAM_CHANGE = 0x29  # Receive Program Change (0: OFF, 1: ON)
    RX_BANK_SELECT = 0x2A  # Receive Bank Select (0: OFF, 1: ON)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Master Tune
            cents = (value - 1024) / 10  # Convert 24-2024 to -100.0/+100.0
            return f"{cents:+.1f} cents"
        elif param == 0x04:  # Master Key Shift
            semitones = value - 64  # Convert 40-88 to -24/+24
            return f"{semitones:+d} st"
        elif param == 0x11:  # Program Control Channel
            return "OFF" if value == 0 else str(value)
        elif param in (0x29, 0x2A):  # Switches
            return "ON" if value else "OFF"
        return str(value)


@dataclass
class SystemCommonMessage(RolandSysEx):
    """System Common parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SYSTEM_AREA  # 0x02: System area
    section: int = SYSTEM_COMMON  # 0x00: Common section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Common section (0x00)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]

"""
# Example usage:
# Set master tune to +50 cents
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_TUNE.value,
    value=1024 + (50 * 10),  # Convert +50.0 cents to 1524
)

# Set master key shift to -12 semitones
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_KEY_SHIFT.value, value=52  # Convert -12 to 52 (64-12)
)

# Set program control channel to 1
msg = SystemCommonMessage(
    param=SystemCommon.PROGRAM_CTRL_CH.value, value=1  # Channel 1
)

# Enable program change reception
msg = SystemCommonMessage(param=SystemCommon.RX_PROGRAM_CHANGE.value, value=1)  # ON
"""



@dataclass
class SystemControllerMessage(RolandSysEx):
    """System Controller parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SYSTEM_AREA  # 0x02: System area
    section: int = SYSTEM_CONTROLLER  # 0x03: Controller section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Controller section (0x03)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]

""" 
# Example usage:
# Enable program change transmission
msg = SystemControllerMessage(
    param=SystemController.TX_PROGRAM_CHANGE.value, value=1  # ON
)

# Set keyboard velocity to REAL
msg = SystemControllerMessage(
    param=SystemController.KEYBOARD_VELOCITY.value, value=0  # REAL
)

# Set velocity curve to MEDIUM
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_CURVE.value, value=1  # MEDIUM
)

# Set velocity offset to +5
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_OFFSET.value, value=69  # Convert +5 to 69 (64+5)
)
"""


@dataclass
class DigitalToneMessage(RolandSysEx):
    """SuperNATURAL Synth Tone parameter message"""

    command: int = DT1_COMMAND_12
    area: int = 0x19  # Temporary area
    tone_type: int = 0x01  # Digital tone (0x01 or 0x02)
    section: int = 0x00  # Section from DigitalToneSection
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Temporary area (0x19)
            self.tone_type,  # Digital 1 or 2 (0x01/0x02)
            self.section,  # Section (Common/Partial/Modify)
            self.param,  # Parameter number
        ]
        self.data = [self.value]

""" 
# Example usage:
# Set common parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.COMMON.value,
    param=0x00,  # Common parameter
    value=64,
)

# Set partial parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.PARTIAL_1.value,
    param=0x00,  # Partial parameter
    value=64,
)

# Set modify parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.MODIFY.value,
    param=0x00,  # Modify parameter
    value=64,
)
"""


@dataclass
class SystemCommonMessage(RolandSysEx):
    """System Common parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SYSTEM_AREA  # 0x02: System area
    section: int = SYSTEM_COMMON  # 0x00: Common section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Common section (0x00)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]

"""
# Example usage:
# Set master tune to +50 cents
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_TUNE.value,
    value=1024 + (50 * 10),  # Convert +50.0 cents to 1524
)

# Set master key shift to -12 semitones
msg = SystemCommonMessage(
    param=SystemCommon.MASTER_KEY_SHIFT.value, value=52  # Convert -12 to 52 (64-12)
)

# Set program control channel to 1
msg = SystemCommonMessage(
    param=SystemCommon.PROGRAM_CTRL_CH.value, value=1  # Channel 1
)

# Enable program change reception
msg = SystemCommonMessage(param=SystemCommon.RX_PROGRAM_CHANGE.value, value=1)  # ON
"""


@dataclass
class SystemControllerMessage(RolandSysEx):
    """System Controller parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SYSTEM_AREA  # 0x02: System area
    section: int = SYSTEM_CONTROLLER  # 0x03: Controller section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # System area (0x02)
            self.section,  # Controller section (0x03)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]

"""
# Example usage:
# Enable program change transmission
msg = SystemControllerMessage(
    param=SystemController.TX_PROGRAM_CHANGE.value, value=1  # ON
)

# Set keyboard velocity to REAL
msg = SystemControllerMessage(
    param=SystemController.KEYBOARD_VELOCITY.value, value=0  # REAL
)

# Set velocity curve to MEDIUM
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_CURVE.value, value=1  # MEDIUM
)

# Set velocity offset to +5
msg = SystemControllerMessage(
    param=SystemController.VELOCITY_OFFSET.value, value=69  # Convert +5 to 69 (64+5)
)
"""


# SuperNATURAL Synth Tone Structure (0x19 01/02)
class DigitalToneSection(Enum):
    """SuperNATURAL Synth Tone sections"""

    COMMON = 0x00  # 00 00 00: Common parameters
    PARTIAL_1 = 0x20  # 00 20 00: Partial 1
    PARTIAL_2 = 0x21  # 00 21 00: Partial 2
    PARTIAL_3 = 0x22  # 00 22 00: Partial 3
    MODIFY = 0x50  # 00 50 00: Tone Modify parameters


@dataclass
class DigitalToneMessage(RolandSysEx):
    """SuperNATURAL Synth Tone parameter message"""

    command: int = DT1_COMMAND_12
    area: int = 0x19  # Temporary area
    tone_type: int = 0x01  # Digital tone (0x01 or 0x02)
    section: int = 0x00  # Section from DigitalToneSection
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Temporary area (0x19)
            self.tone_type,  # Digital 1 or 2 (0x01/0x02)
            self.section,  # Section (Common/Partial/Modify)
            self.param,  # Parameter number
        ]
        self.data = [self.value]

"""
# Example usage:
# Set common parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.COMMON.value,
    param=0x00,  # Common parameter
    value=64,
)

# Set partial parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.PARTIAL_1.value,
    param=0x00,  # Partial parameter
    value=64,
)

# Set modify parameter
msg = DigitalToneMessage(
    tone_type=TEMP_DIGITAL_TONE,  # Digital 1
    section=DigitalToneSection.MODIFY.value,
    param=0x00,  # Modify parameter
    value=64,
)
"""


class DrumKitSection(Enum):
    """Drum Kit sections"""

    COMMON = 0x00  # 00 00 00: Common parameters
    PAD_36 = 0x2E  # 00 2E 00: Pad 36 (C1)
    PAD_37 = 0x30  # 00 30 00: Pad 37 (C#1)
    PAD_38 = 0x32  # 00 32 00: Pad 38 (D1)
    # ... continue for all pads
    PAD_72 = 0x76  # 00 76 00: Pad 72 (C4)

    @staticmethod
    def get_pad_offset(note: int) -> int:
        """Get pad offset from MIDI note number"""
        if 36 <= note <= 72:
            return 0x2E + ((note - 36) * 2)
        return 0x00


class Waveform(Enum):
    """Waveform types available on the JD-Xi"""

    SAW = auto()  # Sawtooth wave
    SQUARE = auto()  # Square wave
    TRIANGLE = auto()  # Triangle wave
    SINE = auto()  # Sine wave
    NOISE = auto()  # Noise
    SUPER_SAW = auto()  # Super saw
    PCM = auto()  # PCM waveform

    @property
    def display_name(self) -> str:
        """Get display name for waveform"""
        names = {
            Waveform.SAW: "SAW",
            Waveform.SQUARE: "SQR",
            Waveform.TRIANGLE: "TRI",
            Waveform.SINE: "SIN",
            Waveform.NOISE: "NOISE",
            Waveform.SUPER_SAW: "S.SAW",
            Waveform.PCM: "PCM",
        }
        return names[self]

    @property
    def midi_value(self) -> int:
        """Get MIDI value for waveform"""
        values = {
            Waveform.SAW: OSC_WAVE_SAW,
            Waveform.SQUARE: OSC_WAVE_SQUARE,
            Waveform.TRIANGLE: OSC_WAVE_TRIANGLE,
            Waveform.SINE: OSC_WAVE_SINE,
            Waveform.NOISE: OSC_WAVE_NOISE,
            Waveform.SUPER_SAW: OSC_WAVE_SUPER_SAW,
            Waveform.PCM: OSC_WAVE_PCM,
        }
        return values[self]

    @classmethod
    def from_midi_value(cls, value: int) -> "Waveform":
        """Create Waveform from MIDI value"""
        for waveform in cls:
            if waveform.midi_value == value:
                return waveform
        raise ValueError(f"Invalid waveform value: {value}")


class DrumKitCommon(Enum):
    """Common parameters for Drum Kit"""

    NAME_1 = 0x00  # Character 1 of name (ASCII)
    NAME_2 = 0x01  # Character 2 of name
    NAME_3 = 0x02  # Character 3 of name
    NAME_4 = 0x03  # Character 4 of name
    NAME_5 = 0x04  # Character 5 of name
    NAME_6 = 0x05  # Character 6 of name
    NAME_7 = 0x06  # Character 7 of name
    NAME_8 = 0x07  # Character 8 of name
    NAME_9 = 0x08  # Character 9 of name
    NAME_10 = 0x09  # Character 10 of name
    NAME_11 = 0x0A  # Character 11 of name
    NAME_12 = 0x0B  # Character 12 of name
    CATEGORY = 0x0C  # Kit category
    LEVEL = 0x0D  # Kit level (0-127)


class DrumPadParam(Enum):
    """Parameters for each drum pad"""

    WAVE = 0x00  # Wave number (0-127, 0=OFF)
    LEVEL = 0x01  # Level (0-127)
    PAN = 0x02  # Pan (-64 to +63)
    TUNE = 0x03  # Tune (-64 to +63)
    DECAY = 0x04  # Decay time (0-127)
    MUTE_GROUP = 0x05  # Mute area (0-31, 0=OFF)
    OUTPUT_EFX = 0x06  # Output/EFX select (0-3)
    REVERB_SEND = 0x07  # Reverb send level (0-127)
    DELAY_SEND = 0x08  # Delay send level (0-127)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Wave
            return "OFF" if value == 0 else str(value)
        elif param == 0x02:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"R{value - 64}"
            return "C"
        elif param in (0x03,):  # Tune
            return f"{value - 64:+d}"
        elif param == 0x05:  # Mute area
            return "OFF" if value == 0 else str(value)
        elif param == 0x06:  # Output/EFX
            return ["OUTPUT", "EFX1", "EFX2", "DLY"][value]
        return str(value)


@dataclass
class DrumKitMessage(RolandSysEx):
    """Drum Kit parameter message"""

    command: int = DT1_COMMAND_12
    area: int = 0x19  # Temporary area
    tone_type: int = 0x10  # Drum Kit
    section: int = 0x00  # Section (Common or Pad offset)
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Temporary area (0x19)
            self.tone_type,  # Drum Kit (0x10)
            self.section,  # Section (Common/Pad offset)
            self.param,  # Parameter number
        ]
        self.data = [self.value]

"""
# Example usage:
# Set kit name
msg = DrumKitMessage(
    section=DrumKitSection.COMMON.value,
    param=DrumKitCommon.NAME_1.value,
    value=0x41,  # 'A'
)

# Set pad parameter
msg = DrumKitMessage(
    section=DrumKitSection.get_pad_offset(36),  # Pad C1
    param=DrumPadParam.WAVE.value,
    value=1,  # Wave number
)
"""

# Setup Area Structure (0x01)
class SetupParam(Enum):
    """Setup parameters"""

    # Reserved space (0x00-0x03)
    RESERVED_1 = 0x00  # Reserved
    RESERVED_2 = 0x01  # Reserved
    RESERVED_3 = 0x02  # Reserved
    RESERVED_4 = 0x03  # Reserved

    # Program selection (0x04-0x06)
    BANK_MSB = 0x04  # Program Bank Select MSB (CC#0) (0-127)
    BANK_LSB = 0x05  # Program Bank Select LSB (CC#32) (0-127)
    PROGRAM = 0x06  # Program Change Number (0-127)

    # More reserved space (0x07-0x3A)
    # Total size: 0x3B bytes


@dataclass
class SetupMessage(RolandSysEx):
    """Setup parameter message"""

    command: int = DT1_COMMAND_12
    area: int = SETUP_AREA  # 0x01: Setup area
    section: int = 0x00  # Always 0x00
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Setup area (0x01)
            self.section,  # Always 0x00
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]


@dataclass
class ProgramCommonParameterMessage(RolandSysEx):
    """Program Common parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA  # 0x18: Program area
    section: int = 0x00  # 0x00: Common section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Program area (0x18)
            self.section,  # Common section (0x00)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]


# Program Vocal Effect Parameters (0x18 01)
class VocalEffect(Enum):
    """Program Vocal Effect parameters"""

    LEVEL = 0x00  # Level (0-127)
    PAN = 0x01  # Pan (0-127: L64-63R)
    DELAY_SEND = 0x02  # Delay Send Level (0-127)
    REVERB_SEND = 0x03  # Reverb Send Level (0-127)
    OUTPUT_ASSIGN = 0x04  # Output Assign (0: EFX1, 1: EFX2, 2: DLY, 3: REV, 4: DIR)

    # Auto Pitch parameters
    AUTO_PITCH_SW = 0x05  # Auto Pitch Switch (0: OFF, 1: ON)
    AUTO_PITCH_TYPE = 0x06  # Type (0: SOFT, 1: HARD, 2: ELECTRIC1, 3: ELECTRIC2)
    AUTO_PITCH_SCALE = 0x07  # Scale (0: CHROMATIC, 1: Maj(Min))
    AUTO_PITCH_KEY = 0x08  # Key (0-23: C-Bm)
    AUTO_PITCH_NOTE = 0x09  # Note (0-11: C-B)
    AUTO_PITCH_GENDER = 0x0A  # Gender (-10 to +10)
    AUTO_PITCH_OCTAVE = 0x0B  # Octave (-1 to +1)
    AUTO_PITCH_BAL = 0x0C  # Balance (0-100: D100:0W - D0:100W)

    # Vocoder parameters
    VOCODER_SW = 0x0D  # Vocoder Switch (0: OFF, 1: ON)
    VOCODER_ENV = 0x0E  # Envelope (0: SHARP, 1: SOFT, 2: LONG)
    VOCODER_PARAM = 0x0F  # Parameter (0-127)
    VOCODER_MIC_SENS = 0x10  # Mic Sensitivity (0-127)
    VOCODER_SYNTH_LVL = 0x11  # Synth Level (0-127)
    VOCODER_MIC_MIX = 0x12  # Mic Mix Level (0-127)
    VOCODER_MIC_HPF = 0x13  # Mic HPF (0: BYPASS, 1-13: 1000-16000Hz)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x01:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"R{value - 64}"
            return "C"
        elif param == 0x04:  # Output Assign
            return ["EFX1", "EFX2", "DLY", "REV", "DIR"][value]
        elif param in (0x05, 0x0D):  # Switches
            return "ON" if value else "OFF"
        elif param == 0x06:  # Auto Pitch Type
            return ["SOFT", "HARD", "ELECTRIC1", "ELECTRIC2"][value]
        elif param == 0x07:  # Auto Pitch Scale
            return ["CHROMATIC", "Maj(Min)"][value]
        elif param == 0x08:  # Auto Pitch Key
            keys = [
                "C",
                "Db",
                "D",
                "Eb",
                "E",
                "F",
                "F#",
                "G",
                "Ab",
                "A",
                "Bb",
                "B",
                "Cm",
                "C#m",
                "Dm",
                "D#m",
                "Em",
                "Fm",
                "F#m",
                "Gm",
                "G#m",
                "Am",
                "Bbm",
                "Bm",
            ]
            return keys[value]
        elif param == 0x09:  # Auto Pitch Note
            notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            return notes[value]
        elif param == 0x0A:  # Auto Pitch Gender
            return f"{value - 10:+d}"  # Convert 0-20 to -10/+10
        elif param == 0x0B:  # Auto Pitch Octave
            return f"{value - 1:+d}"  # Convert 0-2 to -1/+1
        elif param == 0x0C:  # Auto Pitch Balance
            return f"D{100 - value}:W{value}"  # Convert 0-100 to ratio
        elif param == 0x0E:  # Vocoder Envelope
            return ["SHARP", "SOFT", "LONG"][value]
        elif param == 0x13:  # Vocoder Mic HPF
            if value == 0:
                return "BYPASS"
            freqs = [
                1000,
                1250,
                1600,
                2000,
                2500,
                3150,
                4000,
                5000,
                6300,
                8000,
                10000,
                12500,
                16000,
            ]
            return f"{freqs[value - 1]}Hz"
        return str(value)


@dataclass
class VocalEffectMessage(RolandSysEx):
    """Program Vocal Effect parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA  # 0x18: Program area
    section: int = 0x01  # 0x01: Vocal Effect section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Program area (0x18)
            self.section,  # Vocal Effect section (0x01)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        self.data = [self.value]

"""
# Example usage:
# Set vocal effect level
msg = VocalEffectMessage(param=VocalEffect.LEVEL.value, value=100)  # Level 100

# Set auto pitch parameters
msg = VocalEffectMessage(param=VocalEffect.AUTO_PITCH_SW.value, value=1)  # ON

msg = VocalEffectMessage(param=VocalEffect.AUTO_PITCH_TYPE.value, value=0)  # SOFT

# Set vocoder parameters
msg = VocalEffectMessage(param=VocalEffect.VOCODER_SW.value, value=1)  # ON

msg = VocalEffectMessage(param=VocalEffect.VOCODER_ENV.value, value=1)  # SOFT
"""

# Program Effect 1 Parameters (0x18 02)


"""
# Example usage:
# Set effect preset_type
msg = Effect1Message(param=Effect1.TYPE.value, value=1)  # DISTORTION

# Set effect level
msg = Effect1Message(param=Effect1.LEVEL.value, value=100)  # Level 100

# Set effect parameter 1 to +5000
msg = Effect1Message(
    param=Effect1.get_param_offset(1), value=5000  # Will be converted to 37768
)

# Set output to EFX2
msg = Effect1Message(param=Effect1.OUTPUT_ASSIGN.value, value=1)  # EFX2
"""

# Program Effect 2 Parameters (0x18 04)


"""
# Example usage:
# Set effect preset_type
msg = Effect2Message(param=Effect2.TYPE.value, value=5)  # PHASER

# Set effect level
msg = Effect2Message(param=Effect2.LEVEL.value, value=100)  # Level 100

# Set effect parameter 1 to +5000
msg = Effect2Message(
    param=Effect2.get_param_offset(1), value=5000  # Will be converted to 37768
)

# Set send levels
msg = Effect2Message(param=Effect2.DELAY_SEND.value, value=64)  # Send to delay

msg = Effect2Message(param=Effect2.REVERB_SEND.value, value=64)  # Send to reverb
"""


# Program Delay Parameters (0x18 06)
class Delay(Enum):
    """Program Delay parameters"""

    # Reserved (0x00)
    LEVEL = 0x01  # Delay Level (0-127)
    # Reserved (0x02)
    REVERB_SEND = 0x03  # Delay Reverb Send Level (0-127)

    # Parameters start at 0x04 and go up to 0x60
    # Each parameter is 4 bytes (12768-52768: -20000 to +20000)
    PARAM_1 = 0x04  # Parameter 1
    PARAM_2 = 0x08  # Parameter 2
    # ... continue for all 24 parameters
    PARAM_24 = 0x60  # Parameter 24

    @staticmethod
    def get_param_offset(param_num: int) -> int:
        """Get parameter offset from parameter number (1-24)"""
        if 1 <= param_num <= 24:
            return 0x04 + ((param_num - 1) * 4)
        return 0x00

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x04 <= param <= 0x60:  # Effect parameters
            return f"{value - 32768:+d}"  # Convert 12768-52768 to -20000/+20000
        return str(value)


@dataclass
class DelayMessage(RolandSysEx):
    """Program Delay parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA  # 0x18: Program area
    section: int = 0x06  # 0x06: Delay section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Program area (0x18)
            self.section,  # Delay section (0x06)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        # Handle 4-byte parameters
        if 0x04 <= self.param <= 0x60:
            # Convert -20000/+20000 to 12768-52768
            value = self.value + 32768
            self.data = [
                (value >> 24) & 0x0F,  # High nibble
                (value >> 16) & 0x0F,
                (value >> 8) & 0x0F,
                value & 0x0F,  # Low nibble
            ]
        else:
            self.data = [self.value]

"""
# Example usage:
# Set delay level
msg = DelayMessage(param=Delay.LEVEL.value, value=100)  # Level 100

# Set reverb send level
msg = DelayMessage(param=Delay.REVERB_SEND.value, value=64)  # Send to reverb

# Set delay parameter 1 to +5000
msg = DelayMessage(
    param=Delay.get_param_offset(1), value=5000  # Will be converted to 37768
)
"""


# Program Reverb Parameters (0x18 08)
class Reverb(Enum):
    """Program Reverb parameters"""

    # Reserved (0x00)
    LEVEL = 0x01  # Reverb Level (0-127)
    # Reserved (0x02)

    # Parameters start at 0x03 and go up to 0x5F
    # Each parameter is 4 bytes (12768-52768: -20000 to +20000)
    PARAM_1 = 0x03  # Parameter 1
    PARAM_2 = 0x07  # Parameter 2
    # ... continue for all 24 parameters
    PARAM_24 = 0x5F  # Parameter 24

    @staticmethod
    def get_param_offset(param_num: int) -> int:
        """Get parameter offset from parameter number (1-24)"""
        if 1 <= param_num <= 24:
            return 0x03 + ((param_num - 1) * 4)
        return 0x00

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x03 <= param <= 0x5F:  # Effect parameters
            return f"{value - 32768:+d}"  # Convert 12768-52768 to -20000/+20000
        return str(value)


@dataclass
class ReverbMessage(RolandSysEx):
    """Program Reverb parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA  # 0x18: Program area
    section: int = 0x08  # 0x08: Reverb section
    group: int = 0x00  # Always 0x00
    param: int = 0x00  # Parameter number
    value: int = 0x00  # Parameter value

    def __post_init__(self):
        """Set up address and data"""
        self.address = [
            self.area,  # Program area (0x18)
            self.section,  # Reverb section (0x08)
            self.group,  # Always 0x00
            self.param,  # Parameter number
        ]
        # Handle 4-byte parameters
        if 0x03 <= self.param <= 0x5F:
            # Convert -20000/+20000 to 12768-52768
            value = self.value + 32768
            self.data = [
                (value >> 24) & 0x0F,  # High nibble
                (value >> 16) & 0x0F,
                (value >> 8) & 0x0F,
                value & 0x0F,  # Low nibble
            ]
        else:
            self.data = [self.value]


# Example usage:
# Set reverb level
msg = ReverbMessage(param=Reverb.LEVEL.value, value=100)  # Level 100

# Set reverb parameter 1 to +5000
msg = ReverbMessage(
    param=Reverb.get_param_offset(1), value=5000  # Will be converted to 37768
)


class Zone:
    """Program Zone parameters"""

    ARPEGGIO_SWITCH = 0x03  # Arpeggio Switch (0-1)
    OCTAVE_SHIFT = 0x19  # Zone Octave Shift (-3/+3)


@dataclass
class ZoneMessage(RolandSysEx):
    """Program Zone parameter message"""

    command: int = DT1_COMMAND_12
    area: int = PROGRAM_AREA
    section: int = 0x01  # Zone section


class Controller:
    """Program Controller parameters"""

    # Arpeggio parameters
    ARP_GRID = 0x01  # Arpeggio Grid (0-8)
    ARP_DURATION = 0x02  # Arpeggio Duration (0-9)
    ARP_SWITCH = 0x03  # Arpeggio Switch (0-1)
    ARP_STYLE = 0x05  # Arpeggio Style (0-127)
    ARP_MOTIF = 0x06  # Arpeggio Motif (0-11)
    ARP_OCTAVE = 0x07  # Arpeggio Octave Range (-3/+3)
    ARP_ACCENT = 0x09  # Arpeggio Accent Rate (0-100)
    ARP_VELOCITY = 0x0A  # Arpeggio Velocity (0-127, 0=REAL)

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

    @staticmethod
    def get_grid_name(value: int) -> str:
        """Get grid name from value"""
        names = ["04_", "08_", "08L", "08H", "08t", "16_", "16L", "16H", "16t"]
        return names[value] if 0 <= value <= 8 else str(value)

    @staticmethod
    def get_duration_name(value: int) -> str:
        """Get duration name from value"""
        names = ["30", "40", "50", "60", "70", "80", "90", "100", "120", "FUL"]
        return names[value] if 0 <= value <= 9 else str(value)

    @staticmethod
    def get_motif_name(value: int) -> str:
        """Get motif name from value"""
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
        """Convert raw value to display value"""
        if param == 0x01:  # Grid
            return Controller.get_grid_name(value)
        elif param == 0x02:  # Duration
            return Controller.get_duration_name(value)
        elif param == 0x03:  # Switch
            return "ON" if value else "OFF"
        elif param == 0x05:  # Style
            return str(value + 1)  # Convert 0-127 to 1-128
        elif param == 0x06:  # Motif
            return Controller.get_motif_name(value)
        elif param == 0x07:  # Octave Range
            return f"{value - 64:+d}"  # Convert 61-67 to -3/+3
        elif param == 0x09:  # Accent Rate
            return f"{value}%"
        elif param == 0x0A:  # Velocity
            return "REAL" if value == 0 else str(value)
        return str(value)


class DigitalTonePartial:
    """SuperNATURAL Synth Tone Partial parameters"""

    # Oscillator parameters
    OSC_WAVE = 0x00  # OSC Wave (0-7)
    OSC_VARIATION = 0x01  # OSC Wave Variation (0-2)
    OSC_PITCH = 0x03  # OSC Pitch (-24/+24)
    OSC_DETUNE = 0x04  # OSC Detune (-50/+50)
    OSC_PWM_DEPTH = 0x05  # OSC Pulse Width Mod Depth (0-127)
    OSC_PW = 0x06  # OSC Pulse Width (0-127)
    OSC_PW_SHIFT = 0x2A  # OSC Pulse Width Shift (0-127)

    # Pitch envelope
    PITCH_ENV_ATK = 0x07  # OSC Pitch Env Attack Time (0-127)
    PITCH_ENV_DCY = 0x08  # OSC Pitch Env Decay (0-127)
    PITCH_ENV_DEPTH = 0x09  # OSC Pitch Env Depth (-63/+63)

    # Filter parameters
    FILTER_MODE = 0x0A  # Filter Mode (0-7)
    FILTER_SLOPE = 0x0B  # Filter Slope (0-1)
    FILTER_CUTOFF = 0x0C  # Filter Cutoff (0-127)
    FILTER_KF = 0x0D  # Filter Cutoff Keyfollow (-100/+100)
    FILTER_VEL = 0x0E  # Filter Env Velocity Sens (-63/+63)
    FILTER_RES = 0x0F  # Filter Resonance (0-127)
    HPF_CUTOFF = 0x39  # HPF Cutoff (0-127)

    # Filter envelope
    FILTER_ENV_ATK = 0x10  # Filter Env Attack Time (0-127)
    FILTER_ENV_DCY = 0x11  # Filter Env Decay Time (0-127)
    FILTER_ENV_SUS = 0x12  # Filter Env Sustain Level (0-127)
    FILTER_ENV_REL = 0x13  # Filter Env Release Time (0-127)
    FILTER_ENV_DEPTH = 0x14  # Filter Env Depth (-63/+63)

    # Amplifier parameters
    AMP_LEVEL = 0x15  # AMP Level (0-127)
    AMP_VEL = 0x16  # AMP Level Velocity Sens (-63/+63)
    AMP_KF = 0x3C  # AMP Level Keyfollow (-100/+100)

    # Amplifier envelope
    AMP_ENV_ATK = 0x17  # AMP Env Attack Time (0-127)
    AMP_ENV_DCY = 0x18  # AMP Env Decay Time (0-127)
    AMP_ENV_SUS = 0x19  # AMP Env Sustain Level (0-127)
    AMP_ENV_REL = 0x1A  # AMP Env Release Time (0-127)
    AMP_PAN = 0x1B  # AMP Pan (L64-63R)

    # LFO parameters
    LFO_SHAPE = 0x1C  # LFO Shape (0-5)
    LFO_RATE = 0x1D  # LFO Rate (0-127)
    LFO_SYNC = 0x1E  # LFO Tempo Sync Switch (0-1)
    LFO_NOTE = 0x1F  # LFO Tempo Sync Note (0-19)
    LFO_FADE = 0x20  # LFO Fade Time (0-127)
    LFO_KEYTRIG = 0x21  # LFO Key Trigger (0-1)

    # LFO depths
    LFO_PITCH = 0x22  # LFO Pitch Depth (-63/+63)
    LFO_FILTER = 0x23  # LFO Filter Depth (-63/+63)
    LFO_AMP = 0x24  # LFO Amp Depth (-63/+63)
    LFO_PAN = 0x25  # LFO Pan Depth (-63/+63)

    # Modulation LFO
    MOD_LFO_SHAPE = 0x26  # Mod LFO Shape (0-5)
    MOD_LFO_RATE = 0x27  # Mod LFO Rate (0-127)
    MOD_LFO_SYNC = 0x28  # Mod LFO Tempo Sync Switch (0-1)
    MOD_LFO_NOTE = 0x29  # Mod LFO Tempo Sync Note (0-19)
    MOD_LFO_RATE_CTRL = 0x3B  # Mod LFO Rate Control (-63/+63)

    # Modulation depths
    MOD_LFO_PITCH = 0x2C  # Mod LFO Pitch Depth (-63/+63)
    MOD_LFO_FILTER = 0x2D  # Mod LFO Filter Depth (-63/+63)
    MOD_LFO_AMP = 0x2E  # Mod LFO Amp Depth (-63/+63)
    MOD_LFO_PAN = 0x2F  # Mod LFO Pan Depth (-63/+63)

    # Aftertouch sensitivities
    AT_CUTOFF = 0x30  # Cutoff Aftertouch Sens (-63/+63)
    AT_LEVEL = 0x31  # Level Aftertouch Sens (-63/+63)

    # Wave parameters
    WAVE_GAIN = 0x34  # Wave Gain (-6/0/+6/+12 dB)
    WAVE_NUMBER = 0x35  # Wave Number (0=OFF, 1-16384)
    SUPER_SAW = 0x3A  # Super Saw Detune (0-127)

    # Filter modes
    FILTER_BYPASS = 0  # Bypass
    FILTER_LPF = 1  # Low Pass Filter
    FILTER_HPF = 2  # High Pass Filter
    FILTER_BPF = 3  # Band Pass Filter
    FILTER_PKG = 4  # Peak/Gain
    FILTER_LPF2 = 5  # Low Pass Filter 2
    FILTER_LPF3 = 6  # Low Pass Filter 3
    FILTER_LPF4 = 7  # Low Pass Filter 4

    # LFO shapes
    LFO_TRI = 0  # Triangle
    LFO_SIN = 1  # Sine
    LFO_SAW = 2  # Sawtooth
    LFO_SQR = 3  # Square
    LFO_SH = 4  # Sample & Hold
    LFO_RND = 5  # Random

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if param == 0x00:  # Wave preset_type
            return DigitalTonePartial.get_wave_name(value)
        elif param == 0x01:  # Wave variation
            return DigitalTonePartial.get_variation_name(value)
        elif param == 0x03:  # OSC Pitch
            return f"{value - 64:+d}"  # Convert 40-88 to -24/+24
        elif param == 0x04:  # OSC Detune
            return f"{value - 64:+d}"  # Convert 14-114 to -50/+50
        elif param == 0x09:  # Pitch Env Depth
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        elif param == 0x0A:  # Filter Mode
            modes = ["BYPASS", "LPF", "HPF", "BPF", "PKG", "LPF2", "LPF3", "LPF4"]
            return modes[value]
        elif param == 0x0B:  # Filter Slope
            return "-12dB" if value == 0 else "-24dB"
        elif param == 0x0D:  # Filter Keyfollow
            return f"{((value - 54) * 200 / 20) - 100:+.0f}"  # Convert to -100/+100
        elif param == 0x0E:  # Filter Velocity Sens
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        elif param == 0x14:  # Filter Env Depth
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        elif param == 0x16:  # Amp Velocity Sens
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        elif param == 0x1B:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"{value - 64}R"
            return "C"
        elif param in [0x1C, 0x26]:  # LFO Shapes
            shapes = ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"]
            return shapes[value]
        elif param in [0x1E, 0x21, 0x28]:  # Switches
            return "ON" if value else "OFF"
        elif param in [0x1F, 0x29]:  # Sync Notes
            notes = [
                "16",
                "12",
                "8",
                "4",
                "2",
                "1",
                "3/4",
                "2/3",
                "1/2",
                "3/8",
                "1/3",
                "1/4",
                "3/16",
                "1/6",
                "1/8",
                "3/32",
                "1/12",
                "1/16",
                "1/24",
                "1/32",
            ]
            return notes[value]
        elif param in [
            0x22,
            0x23,
            0x24,
            0x25,  # LFO depths
            0x2C,
            0x2D,
            0x2E,
            0x2F,  # Mod LFO depths
            0x30,
            0x31,
            0x3B,
        ]:  # Aftertouch and Rate Control
            return f"{value - 64:+d}"  # Convert 1-127 to -63/+63
        elif param == 0x34:  # Wave Gain
            gains = ["-6dB", "0dB", "+6dB", "+12dB"]
            return gains[value]
        elif param == 0x35:  # Wave Number
            return "OFF" if value == 0 else str(value)
        elif param == 0x3C:  # Amp Level Keyfollow
            return f"{((value - 54) * 200 / 20) - 100:+.0f}"  # Convert to -100/+100
        return str(value)


class DrumKitCommon:
    """Drum Kit Common parameters"""

    # Kit name (12 characters)
    NAME_1 = 0x00  # Character 1 (ASCII 32-127)
    NAME_2 = 0x01  # Character 2
    NAME_3 = 0x02  # Character 3
    NAME_4 = 0x03  # Character 4
    NAME_5 = 0x04  # Character 5
    NAME_6 = 0x05  # Character 6
    NAME_7 = 0x06  # Character 7
    NAME_8 = 0x07  # Character 8
    NAME_9 = 0x08  # Character 9
    NAME_10 = 0x09  # Character 10
    NAME_11 = 0x0A  # Character 11
    NAME_12 = 0x0B  # Character 12

    # Kit parameters
    LEVEL = 0x0C  # Kit Level (0-127)

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x00 <= param <= 0x0B:  # Name characters
            return chr(value) if 32 <= value <= 127 else "?"
        return str(value)


class DrumKitPartial:
    """Drum Kit Partial parameters"""

    # Partial name (12 characters)
    NAME_1 = 0x00  # Character 1 (ASCII 32-127)
    NAME_2 = 0x01  # Character 2
    NAME_3 = 0x02  # Character 3
    NAME_4 = 0x03  # Character 4
    NAME_5 = 0x04  # Character 5
    NAME_6 = 0x05  # Character 6
    NAME_7 = 0x06  # Character 7
    NAME_8 = 0x07  # Character 8
    NAME_9 = 0x08  # Character 9
    NAME_10 = 0x09  # Character 10
    NAME_11 = 0x0A  # Character 11
    NAME_12 = 0x0B  # Character 12

    # Basic parameters
    ASSIGN_TYPE = 0x0C  # Assign Type (0: MULTI, 1: SINGLE)
    MUTE_GROUP = 0x0D  # Mute Group (0: OFF, 1-31)
    LEVEL = 0x0E  # Partial Level (0-127)
    COARSE = 0x0F  # Coarse Tune (C-1 to G9)
    FINE = 0x10  # Fine Tune (-50/+50)
    RANDOM_PITCH = 0x11  # Random Pitch Depth (0-30)
    PAN = 0x12  # Pan (L64-63R)
    RANDOM_PAN = 0x13  # Random Pan Depth (0-63)
    ALT_PAN = 0x14  # Alternate Pan Depth (L63-63R)
    ENV_MODE = 0x15  # Envelope Mode (0: NO-SUS, 1: SUSTAIN)

    # Output settings
    OUTPUT_LEVEL = 0x16  # Output Level (0-127)
    CHORUS_SEND = 0x19  # Chorus Send Level (0-127)
    REVERB_SEND = 0x1A  # Reverb Send Level (0-127)
    OUTPUT_ASSIGN = 0x1B  # Output Assign (0-4: EFX1,EFX2,DLY,REV,DIR)

    # Performance settings
    BEND_RANGE = 0x1C  # Pitch Bend Range (0-48)
    RX_EXPRESSION = 0x1D  # Receive Expression (0-1)
    RX_HOLD = 0x1E  # Receive Hold-1 (0-1)

    # Wave Mix Table (WMT) settings
    WMT_VEL_CTRL = 0x20  # WMT Velocity Control (0: OFF, 1: ON, 2: RANDOM)

    # Random pitch depth values
    RANDOM_PITCH_VALUES = [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        100,
        200,
        300,
        400,
        500,
        600,
        700,
        800,
        900,
        1000,
        1100,
        1200,
    ]

    @staticmethod
    def get_display_value(param: int, value: int) -> str:
        """Convert raw value to display value"""
        if 0x00 <= param <= 0x0B:  # Name characters
            return chr(value) if 32 <= value <= 127 else "?"
        elif param == 0x0C:  # Assign Type
            return "SINGLE" if value else "MULTI"
        elif param == 0x0D:  # Mute Group
            return "OFF" if value == 0 else str(value)
        elif param == 0x0F:  # Coarse Tune
            notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            octave = (value // 12) - 1  # C-1 to G9
            note = notes[value % 12]
            return f"{note}{octave}"
        elif param == 0x10:  # Fine Tune
            return f"{value - 64:+d}"  # Convert 14-114 to -50/+50
        elif param == 0x11:  # Random Pitch
            return str(DrumKitPartial.RANDOM_PITCH_VALUES[value])
        elif param == 0x12:  # Pan
            if value < 64:
                return f"L{64 - value}"
            elif value > 64:
                return f"{value - 64}R"
            return "C"
        elif param == 0x14:  # Alternate Pan
            return f"{value - 64:+d}"  # Convert 1-127 to L63-63R
        elif param == 0x15:  # Envelope Mode
            return "SUSTAIN" if value else "NO-SUS"
        elif param == 0x1B:  # Output Assign
            return ["EFX1", "EFX2", "DLY", "REV", "DIR"][value]
        elif param in [0x1D, 0x1E]:  # Switches
            return "ON" if value else "OFF"
        elif param == 0x20:  # WMT Velocity Control
            return ["OFF", "ON", "RANDOM"][value]
        return str(value)


# LFO Shape Values
class LFOShape(Enum):
    """LFO waveform shapes"""

    TRIANGLE = 0x00  # Triangle wave
    SINE = 0x01  # Sine wave
    SAW = 0x02  # Sawtooth wave
    SQUARE = 0x03  # Square wave
    SAMPLE_HOLD = 0x04  # Sample & Hold
    RANDOM = 0x05  # Random

    @staticmethod
    def get_display_name(value: int) -> str:
        """Get display name for LFO shape"""
        names = {0: "TRI", 1: "SIN", 2: "SAW", 3: "SQR", 4: "S&H", 5: "RND"}
        return names.get(value, "???")


# LFO Sync Note Values
class LFOSyncNote(Enum):
    """LFO sync note values"""

    BAR_16 = 0  # 16 bars
    BAR_12 = 1  # 12 bars
    BAR_8 = 2  # 8 bars
    BAR_4 = 3  # 4 bars
    BAR_2 = 4  # 2 bars
    BAR_1 = 5  # 1 bar
    BAR_3_4 = 6  # 3/4 bar
    BAR_2_3 = 7  # 2/3 bar
    BAR_1_2 = 8  # 1/2 bar
    BAR_3_8 = 9  # 3/8 bar
    BAR_1_3 = 10  # 1/3 bar
    BAR_1_4 = 11  # 1/4 bar
    BAR_3_16 = 12  # 3/16 bar
    BAR_1_6 = 13  # 1/6 bar
    BAR_1_8 = 14  # 1/8 bar
    BAR_3_32 = 15  # 3/32 bar
    BAR_1_12 = 16  # 1/12 bar
    BAR_1_16 = 17  # 1/16 bar
    BAR_1_24 = 18  # 1/24 bar
    BAR_1_32 = 19  # 1/32 bar

    @staticmethod
    def get_display_name(value: int) -> str:
        """Get display name for sync note value"""
        names = {
            0: "16",
            1: "12",
            2: "8",
            3: "4",
            4: "2",
            5: "1",
            6: "3/4",
            7: "2/3",
            8: "1/2",
            9: "3/8",
            10: "1/3",
            11: "1/4",
            12: "3/16",
            13: "1/6",
            14: "1/8",
            15: "3/32",
            16: "1/12",
            17: "1/16",
            18: "1/24",
            19: "1/32",
        }
        return names.get(value, "???")

    @staticmethod
    def get_all_display_names() -> list:
        """Get list of all display names in order"""
        return [LFOSyncNote.get_display_name(i) for i in range(20)]


# LFO Shape Values
LFO_SHAPE_TRI = 0x00  # Triangle
LFO_SHAPE_SIN = 0x01  # Sine
LFO_SHAPE_SAW = 0x02  # Sawtooth
LFO_SHAPE_SQR = 0x03  # Square
LFO_SHAPE_SH = 0x04  # Sample & Hold
LFO_SHAPE_RND = 0x05  # Random

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
