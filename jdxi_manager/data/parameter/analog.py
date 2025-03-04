"""
AnalogParameter: JD-Xi Digital Synthesizer Parameter Mapping

This class defines digital synthesizer parameters for the Roland JD-Xi, mapping
various synthesis parameters to their corresponding memory addresses and valid
value ranges.

The parameters include:
- Oscillator settings (waveform, pitch, detune, envelope, etc.)
- Filter settings (cutoff, resonance, envelope, key follow, etc.)
- Amplifier settings (level, velocity, envelope, pan, etc.)
- LFO (Low-Frequency Oscillator) settings (waveform, rate, depth, sync, etc.)
- Modulation LFO settings (waveform, rate, depth, sync, etc.)
- Additional synthesis controls (aftertouch, wave gain, super saw detune, etc.)
- PCM wave settings (wave number, gain, high-pass filter cutoff, etc.)

Each parameter is stored as address tuple containing:
    (memory_address, min_value, max_value)

Attributes:
    - OSC_WAVE: Defines the oscillator waveform preset_type.
    - FILTER_CUTOFF: Controls the filter cutoff frequency.
    - AMP_LEVEL: Sets the overall amplitude level.
    - LFO_RATE: Adjusts the rate of the low-frequency oscillator.
    - MOD_LFO_PITCH_DEPTH: Modulates pitch using the secondary LFO.
    - (Other parameters follow address similar structure.)

Methods:
    __init__(self, address: int, min_val: int, max_val: int):
        Initializes address DigitalParameter instance with an address and value range.

Usage Example:
    filter_cutoff = DigitalParameter(0x0C, 0, 127)  # Filter Cutoff Frequency
    print(filter_cutoff.address)  # Output: 0x0C

This class helps structure and manage parameter mappings for JD-Xi SysEx processing.
"""
from typing import Optional, Tuple

from jdxi_manager.data.parameter.synth import SynthParameter


def parse_analog_parameters(data: list) -> dict:
    """
    Parses JD-Xi tone parameters from SysEx data, including Oscillator, Filter, and Amplifier parameters.

    Args:
        data (bytes): SysEx message containing tone parameters.

    Returns:
        dict: Parsed parameters.
    """

    # Function to safely retrieve values from `data`
    def safe_get(index, default=0):
        tone_name_length = 12
        index = index + tone_name_length # shift the index by 12 to account for the tone name
        return data[index] if index < len(data) else default

    parameters = {}

    # Mapping DigitalParameter Enum members to their respective positions in SysEx data
    for param in AnalogParameter:
        # Use the parameter's address from the enum and fetch the value from the data
        parameters[param.name] = safe_get(param.address)

    return parameters

"""
For reference
**Analog Synth Tone
+------------------------------------------------------------------------------+
| Offset | |
| Address | Description |
|-------------+----------------------------------------------------------------|
| 00 00 | 0aaa aaaa | Tone Name 1 (32 - 127) |
| | | 32 - 127 [ASCII] |
| 00 01 | 0aaa aaaa | Tone Name 2 (32 - 127) |
| | | 32 - 127 [ASCII] |
| 00 02 | 0aaa aaaa | Tone Name 3 (32 - 127) |
| | | 32 - 127 [ASCII] |
| 00 03 | 0aaa aaaa | Tone Name 4 (32 - 127) |
| | | 32 - 127 [ASCII] |
| 00 04 | 0aaa aaaa | Tone Name 5 (32 - 127) |
| | | 32 - 127 [ASCII] |
| 00 05 | 0aaa aaaa | Tone Name 6 (32 - 127) |
| | | 32 - 127 [ASCII] |
| 00 06 | 0aaa aaaa | Tone Name 7 (32 - 127) |
| | | 32 - 127 [ASCII] |
| 00 07 | 0aaa aaaa | Tone Name 8 (32 - 127) |
| | | 32 - 127 [ASCII] |
| 00 08 | 0aaa aaaa | Tone Name 9 (32 - 127) |
| | | 32 - 127 [ASCII] |
| 00 09 | 0aaa aaaa | Tone Name 10 (32 - 127) |
| | | 32 - 127 [ASCII] |
| 00 0A | 0aaa aaaa | Tone Name 11 (32 - 127) |
| | | 32 - 127 [ASCII] |
| 00 0B | 0aaa aaaa | Tone Name 12 (32 - 127) |
| | | 32 - 127 [ASCII] |
|-------------+-----------+----------------------------------------------------|
| 00 0C | 0aaa aaaa | (reserve) <*> |
|-------------+-----------+----------------------------------------------------|
| 00 0D | 0000 0aaa | LFO Shape (0 - 5) |
| | | TRI, SIN, SAW, SQR, S&H, RND |
| 00 0E | 0aaa aaaa | LFO Rate (0 - 127) |
| 00 0F | 0aaa aaaa | LFO Fade Time (0 - 127) |
| 00 10 | 0000 000a | LFO Tempo Sync Switch (0 - 1) |
| | | OFF, ON |
| 00 11 | 000a aaaa | LFO Tempo Sync Note (0 - 19) |
| | | 16, 12, 8, 4, 2, 1, 3/4, 2/3, 1/2, |
| | | 3/8, 1/3, 1/4, 3/16, 1/6, 1/8, 3/32, |
| | | 1/12, 1/16, 1/24, 1/32 |
| 00 12 | 0aaa aaaa | LFO Pitch Depth (1 - 127) |
| | | -63 - +63 |
| 00 13 | 0aaa aaaa | LFO Filter Depth (1 - 127) |
| | | -63 - +63 |
| 00 14 | 0aaa aaaa | LFO Amp Depth (1 - 127) |
| | | -63 - +63 |
| 00 15 | 0000 000a | LFO Key Trigger (0 - 1) |
| | | OFF, ON |
|-------------+-----------+----------------------------------------------------|
| 00 16 | 0000 0aaa | OSC Waveform (0 - 2) |
| | | SAW, TRI, PW-SQR |
| 00 17 | 00aa aaaa | OSC Pitch Coarse (40 - 88) |
| | | -24 - +24 |
| 00 18 | 0aaa aaaa | OSC Pitch Fine (14 - 114) |
| | | -50 - +50 |
| 00 19 | 0aaa aaaa | OSC Pulse Width (0 - 127) |
| 00 1A | 0aaa aaaa | OSC Pulse Width Mod Depth (0 - 127) |
| 00 1B | 0aaa aaaa | OSC Pitch Env Velocity Sens (1 - 127) |
| | | -63 - +63 |
| 00 1C | 0aaa aaaa | OSC Pitch Env Attack Time (0 - 127) |
| 00 1D | 0aaa aaaa | OSC Pitch Env Decay (0 - 127) |
| 00 1E | 0aaa aaaa | OSC Pitch Env Depth (1 - 127) |
| | | -63 - +63 |
| 00 1F | 0000 00aa | Sub Oscillator Type (0 - 2) |
| | | OFF, OCT-1, OCT-2 |
|-------------+-----------+----------------------------------------------------|
| 00 20 | 0000 0aaa | Filter Switch (0 - 1) |
| | | BYPASS, LPF |
| 00 21 | 0aaa aaaa | Filter Cutoff (0 - 127) |
| 00 22 | 00aa aaaa | Filter Cutoff Keyfollow (54 - 74) |
| | | -100 - +100 |
| 00 23 | 0aaa aaaa | Filter Resonance (0 - 127) |
| 00 24 | 0aaa aaaa | Filter Env Velocity Sens (1 - 127) |
| | | -63 - +63 |
| 00 25 | 0aaa aaaa | Filter Env Attack Time (0 - 127) |
| 00 26 | 0aaa aaaa | Filter Env Decay Time (0 - 127) |
| 00 27 | 0aaa aaaa | Filter Env Sustain Level (0 - 127) |
| 00 28 | 0aaa aaaa | Filter Env Release Time (0 - 127) |
| 00 29 | 0aaa aaaa | Filter Env Depth (1 - 127) |
| | | -63 - +63 |
|-------------+-----------+----------------------------------------------------|
| 00 2A | 0aaa aaaa | AMP Level (0 - 127) |
| 00 2B | 000a aaaa | AMP Level Keyfollow (54 - 74) |
| | | -100 - +100 |
| 00 2C | 0aaa aaaa | AMP Level Velocity Sens (1 - 127) |
| | | -63 - +63 |
| 00 2D | 0aaa aaaa | AMP Env Attack Time (0 - 127) |
| 00 2E | 0aaa aaaa | AMP Env Decay Time (0 - 127) |
| 00 2F | 0aaa aaaa | AMP Env Sustain Level (0 - 127) |
| 00 30 | 0aaa aaaa | AMP Env Release Time (0 - 127) |
|-------------+-----------+----------------------------------------------------|
| 00 31 | 0000 000a | Portamento Switch (0 - 1) |
| | | OFF, ON |
| 00 32 | 0aaa aaaa | Portamento Time (CC# 5) (0 - 127) |
| 00 33 | 0000 000a | Legato Switch (0 - 1) |
| | | OFF, ON |
| 00 34 | 0000 0aaa | Octave Shift (61 - 67) |
| | | -3 - +3 |
| 00 35 | 000a aaaa | Pitch Bend Range Up (0 - 24) |
| 00 36 | 000a aaaa | Pitch Bend Range Down (0 - 24) |
| 00 37 | 0000 0aaa | (reserve) <*> |
|-------------+-----------+----------------------------------------------------|
| 00 38 | 0aaa aaaa | LFO Pitch Modulation Control (1 - 127) |
| | | -63 - +63 |
| 00 39 | 0aaa aaaa | LFO Filter Modulation Control (1 - 127) |
| | | -63 - +63 |
| 00 3A | 0aaa aaaa | LFO Amp Modulation Control (1 - 127) |
| | | -63 - +63 |
| 00 3B | 0aaa aaaa | LFO Rate Modulation Control (1 - 127) |
| | | -63 - +63 |
|-------------+-----------+----------------------------------------------------|
| 00 3C | 0aaa aaaa | (reserve) <*> |
| 00 3D | 0aaa aaaa | (reserve) <*> |
| : | | |
| 00 3F | 0aaa aaaa | (reserve) <*> |
|-------------+----------------------------------------------------------------|
| 00 00 00 40 | Total Size |
+------------------------------------------------------------------------------+
"""

class AnalogParameter(SynthParameter):
    """Analog synth parameters with group, address, and value range."""
    TONE_NAME_1 = (0x00, 32, 127)
    TONE_NAME_2 = (0x01, 32, 127)
    TONE_NAME_3 = (0x02, 32, 127)
    TONE_NAME_4 = (0x03, 32, 127)
    TONE_NAME_5 = (0x04, 32, 127)
    TONE_NAME_6 = (0x05, 32, 127)
    TONE_NAME_7 = (0x06, 32, 127)
    TONE_NAME_8 = (0x07, 32, 127)
    TONE_NAME_9 = (0x08, 32, 127)
    TONE_NAME_10 = (0x09, 32, 127)
    TONE_NAME_11 = (0x0A, 32, 127)
    TONE_NAME_12 = (0x0B, 32, 127)
    
    
    # LFO Parameters
    LFO_SHAPE = (0x0D, 0, 5)
    LFO_RATE = (0x0E, 0, 127)
    LFO_FADE_TIME = (0x0F, 0, 127)
    LFO_TEMPO_SYNC_SWITCH = (0x10, 0, 1)
    LFO_TEMPO_SYNC_NOTE = (0x11, 0, 19)
    LFO_PITCH_DEPTH = (0x12, 1, 127, -63, 63)
    LFO_FILTER_DEPTH = (0x13, 1, 127, -63, 63)
    LFO_AMP_DEPTH = (0x14, 1, 127, -63, 63)
    LFO_KEY_TRIGGER = (0x15, 0, 1)

    # Oscillator Parameters
    OSC_WAVEFORM = (0x16, 0, 2)
    OSC_PITCH_COARSE = (0x17, 40, 88, -24, 24)  # -24 - +24
    OSC_PITCH_FINE = (0x18, 14, 114, -50, 50)  # -50 - +50

    # OSC_PITCH = (0x03, 40, 88)
    # OSC_DETUNE = (0x04, 14, 114)
    OSC_PULSE_WIDTH = (0x19, 0, 127)
    OSC_PULSE_WIDTH_MOD_DEPTH = (0x1A, 0, 127)
    OSC_PITCH_ENV_VELOCITY_SENS = (0x1B, 1, 127, -63, 63)  # -63 - +63
    OSC_PITCH_ENV_ATTACK_TIME = (0x1C, 0, 127)
    OSC_PITCH_ENV_DECAY = (0x1D, 0, 127)
    OSC_PITCH_ENV_DEPTH = (0x1E, 1, 127, -63, 63)  # -63 - +63
    SUB_OSCILLATOR_TYPE = (0x1F, 0, 2)

    # Filter Parameters
    FILTER_SWITCH = (0x20, 0, 1)  # BYPASS, LPF
    FILTER_CUTOFF = (0x21, 0, 127, 54, 74)  # (54 - 74)
    FILTER_CUTOFF_KEYFOLLOW = (0x22, 54, 74)
    FILTER_RESONANCE = (0x23, 0, 127)
    FILTER_ENV_VELOCITY_SENS = (0x24, 1, 127, -63, 63)  # -63 - +63
    FILTER_ENV_ATTACK_TIME = (0x25, 0, 127)
    FILTER_ENV_DECAY_TIME = (0x26, 0, 127)
    FILTER_ENV_SUSTAIN_LEVEL = (0x27, 0, 127)
    FILTER_ENV_RELEASE_TIME = (0x28, 0, 127)
    FILTER_ENV_DEPTH = (0x29, 1, 127, -63, 63)  # -63 - +63

    # Amplifier Parameters
    AMP_LEVEL = (0x2A, 0, 127)
    AMP_LEVEL_KEYFOLLOW = (0x2B, 54, 74, -100, 100)  # -100 - +100
    AMP_LEVEL_VELOCITY_SENS = (0x2C, 1, 127, -63, 63)  # -63 - +63
    AMP_ENV_ATTACK_TIME = (0x2D, 0, 127)
    AMP_ENV_DECAY_TIME = (0x2E, 0, 127)
    AMP_ENV_SUSTAIN_LEVEL = (0x2F, 0, 127)
    AMP_ENV_RELEASE_TIME = (0x30, 0, 127)

    # Portamento and Other Parameters
    PORTAMENTO_SWITCH = (0x31, 0, 1)
    PORTAMENTO_TIME = (0x32, 0, 127)
    LEGATO_SWITCH = (0x33, 0, 1)
    OCTAVE_SHIFT = (0x34, 61, 67)
    PITCH_BEND_RANGE_UP = (0x35, 0, 24)
    PITCH_BEND_RANGE_DOWN = (0x36, 0, 24)

    # LFO Modulation Control
    LFO_PITCH_MODULATION_CONTROL = (0x38, 1, 127, -63, 63)
    LFO_FILTER_MODULATION_CONTROL = (0x39, 1, 127, -63, 63)
    LFO_AMP_MODULATION_CONTROL = (0x3A, 1, 127, -63, 63)
    LFO_RATE_MODULATION_CONTROL = (0x3B, 1, 127, -63, 63)

    # Reserve
    RESERVE_1 = (0x37, 0, 0)
    RESERVE_2 = (0x3C, 0, 0)
    RESERVE_3 = (0x3D, 0, 0)
    RESERVE_4 = (0x3F, 0, 0)

    def __init__(self, address: int, min_val: int, max_val: int,
                 display_min: Optional[int] = None, display_max: Optional[int] = None):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val

    """
    def __init__(self, address: int, min_val: int, max_val: int):
        self.address = address
        self.min_val = min_val
        self.max_val = max_val
    """

    def validate_value(self, value: int) -> int:
        """Validate and convert parameter value to MIDI range (0-127)"""
        if not isinstance(value, int):
            raise ValueError(f"Value must be integer, got {type(value)}")

        if value < self.min_val or value > self.max_val:
            raise ValueError(
                f"Value {value} out of range for {self.name} "
                f"(valid range: {self.min_val}-{self.max_val})"
            )

        return value

    @staticmethod
    def get_by_name(param_name):
        """Get the AnalogParameter by name."""
        # Return the parameter member by name, or None if not found
        return AnalogParameter.__members__.get(param_name, None)

    @staticmethod
    def get_name_by_address(address: int):
        """Return the parameter name for address given address."""
        for param in AnalogParameter:
            if param.address == address:
                return param.name
        return None  # Return None if the address is not found

    @property
    def display_name(self) -> str:
        """Get display name for the parameter"""
        return self.name.replace("_", " ").title()

    @property
    def is_switch(self) -> bool:
        """Returns True if parameter is address binary/enum switch"""
        return self in [
            self.LFO_TEMPO_SYNC_SWITCH,
            self.LFO_KEY_TRIGGER,
            self.PORTAMENTO_SWITCH,
            self.LEGATO_SWITCH,
        ]

    def get_switch_text(self, value: int) -> str:
        """Get display text for switch values"""
        if self.is_switch:
            return "ON" if value else "OFF"
        return str(value)

    @staticmethod
    def get_address(param_name):
        """Get the address of address parameter by name."""
        param = AnalogParameter.get_by_name(param_name)
        if param:
            return param.value[0]
        return None

    @staticmethod
    def get_range(param_name):
        """Get the value range (min, max) of address parameter by name."""
        param = AnalogParameter.get_by_name(param_name)
        if param:
            return param.value[1], param.value[2]
        return None, None
    
    @staticmethod
    def get_display_range(param_name):
        """Get the display value range (min, max) of address parameter by name."""
        param = AnalogParameter.get_by_name(param_name)
        if param:
            return param.display_min, param.display_max
        return None, None
    
    def get_display_value(self) -> Tuple[int, int]:
        """Get the display value range (min, max) for the parameter"""
        if hasattr(self, 'display_min') and hasattr(self, 'display_max'):
            return self.display_min, self.display_max
        return self.min_val, self.max_val

    def convert_from_display(self, display_value: int) -> int:
        """Convert from display value to MIDI value (0-127)"""
        # Handle bipolar parameters
        if self in [
            self.OSC_PITCH_COARSE,
            self.OSC_PITCH_FINE,
            self.FILTER_CUTOFF_KEYFOLLOW,
            self.FILTER_ENV_VELOCITY_SENS,
            self.LFO_AMP_DEPTH,
            self.AMP_LEVEL_KEYFOLLOW,
            self.OSC_PITCH_ENV_DEPTH,
            self.OSC_PITCH_ENV_VELOCITY_SENS,
            self.LFO_PITCH_MODULATION_CONTROL,
            self.LFO_AMP_MODULATION_CONTROL,
            self.LFO_FILTER_MODULATION_CONTROL,
            self.LFO_RATE_MODULATION_CONTROL,
            self.FILTER_ENV_DEPTH,
        ]:

            # Convert from display range to MIDI range
            if self == self.OSC_PITCH_COARSE:
                return display_value + 24
            elif self == self.OSC_PITCH_FINE:
                return display_value + 50
            elif self in [
                self.FILTER_CUTOFF_KEYFOLLOW,
                self.FILTER_ENV_VELOCITY_SENS,
                self.LFO_AMP_DEPTH,
                self.AMP_LEVEL_KEYFOLLOW,
                self.OSC_PITCH_ENV_VELOCITY_SENS,
                self.LFO_PITCH_MODULATION_CONTROL,
                self.LFO_AMP_MODULATION_CONTROL,
                self.LFO_FILTER_MODULATION_CONTROL,
                self.LFO_RATE_MODULATION_CONTROL,
                self.FILTER_ENV_DEPTH,
            ]:
                return display_value + 64  # -63 to +63 -> 0 to 127
            else:
                return display_value + 63  # -63 to +63 -> 0 to 126

        return display_value

    @staticmethod
    def convert_to_display(value, min_val, max_val, display_min, display_max):
        """Convert address value to address display value within address range."""
        if min_val == max_val:
            return display_min
        return int((value - min_val) * (display_max - display_min) / (max_val - min_val) + display_min)

    def convert_to_midi(self, display_value: int) -> int:
        """Convert from display value to MIDI value"""
        # Handle special bipolar cases first
        if self == AnalogParameter.OSC_PITCH_FINE:
            return display_value + 64  # -63 to +63 -> 0 to 127
        elif self == AnalogParameter.OSC_PITCH_COARSE:
            return display_value + 64  # -63 to +63 -> 0 to 127
        
        # For parameters with simple linear scaling
        if hasattr(self, 'display_min') and hasattr(self, 'display_max'):
            return int(self.min_val + (display_value - self.display_min) * 
                      (self.max_val - self.min_val) / (self.display_max - self.display_min))
        return display_value

    def convert_from_midi(self, midi_value: int) -> int:
        """Convert from MIDI value to display value"""
        # Handle special bipolar cases first
        if self == AnalogParameter.OSC_PITCH_FINE:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        elif self == AnalogParameter.OSC_PITCH_COARSE:
            return midi_value - 64  # 0 to 127 -> -63 to +63
        
        # For parameters with simple linear scaling
        if hasattr(self, 'display_min') and hasattr(self, 'display_max'):
            return int(self.display_min + (midi_value - self.min_val) * 
                      (self.display_max - self.display_min) / (self.max_val - self.min_val))
        return midi_value

    @staticmethod
    def get_display_value_by_name(param_name: str, value: int) -> int:
        """Get the display value for address parameter by name and value."""
        param = AnalogParameter.get_by_name(param_name)
        if param:
            return param.convert_from_midi(value)
        return value

    @staticmethod
    def get_midi_range(param_name):
        """Get the MIDI value range (min, max) of address parameter by name."""
        param = AnalogParameter.get_by_name(param_name)
        if param:
            return param.min_val, param.max_val

    @staticmethod
    def get_midi_value(param_name, value):
        """Get the MIDI value for address parameter by name and value."""
        param = AnalogParameter.get_by_name(param_name)
        if param:
            return param.convert_to_midi(value)
        return None