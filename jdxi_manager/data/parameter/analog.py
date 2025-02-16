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

Each parameter is stored as a tuple containing:
    (memory_address, min_value, max_value)

Attributes:
    - OSC_WAVE: Defines the oscillator waveform type.
    - FILTER_CUTOFF: Controls the filter cutoff frequency.
    - AMP_LEVEL: Sets the overall amplitude level.
    - LFO_RATE: Adjusts the rate of the low-frequency oscillator.
    - MOD_LFO_PITCH_DEPTH: Modulates pitch using the secondary LFO.
    - (Other parameters follow a similar structure.)

Methods:
    __init__(self, address: int, min_val: int, max_val: int):
        Initializes a DigitalParameter instance with an address and value range.

Usage Example:
    filter_cutoff = DigitalParameter(0x0C, 0, 127)  # Filter Cutoff Frequency
    print(filter_cutoff.address)  # Output: 0x0C

This class helps structure and manage parameter mappings for JD-Xi SysEx processing.
"""


from jdxi_manager.data.parameter.synth import SynthParameter


class AnalogParameter(SynthParameter):
    """Analog synth parameters with group, address, and value range."""

    # LFO Parameters
    LFO_SHAPE = (0x0D, 0, 5)
    LFO_RATE = (0x0E, 0, 127)
    LFO_FADE_TIME = (0x0F, 0, 127)
    LFO_TEMPO_SYNC_SWITCH = (0x10, 0, 1)
    LFO_TEMPO_SYNC_NOTE = (0x11, 0, 19)
    LFO_PITCH_DEPTH = (0x12, 1, 127)
    LFO_FILTER_DEPTH = (0x13, 1, 127)
    LFO_AMP_DEPTH = (0x14, 1, 127)
    LFO_KEY_TRIGGER = (0x15, 0, 1)

    # Oscillator Parameters
    OSC_WAVEFORM = (0x16, 0, 2)
    OSC_PITCH_COARSE = (0x17, 40, 88)  # -24 - +24
    OSC_PITCH_FINE = (0x18, 14, 114)  # -50 - +50

    # OSC_PITCH = (0x03, 40, 88)
    # OSC_DETUNE = (0x04, 14, 114)
    OSC_PULSE_WIDTH = (0x19, 0, 127)
    OSC_PULSE_WIDTH_MOD_DEPTH = (0x1A, 0, 127)
    OSC_PITCH_ENV_VELOCITY_SENS = (0x1B, 1, 127)  # -63 - +63
    OSC_PITCH_ENV_ATTACK_TIME = (0x1C, 0, 127)
    OSC_PITCH_ENV_DECAY = (0x1D, 0, 127)
    OSC_PITCH_ENV_DEPTH = (0x1E, 1, 127)  # -63 - +63
    SUB_OSCILLATOR_TYPE = (0x1F, 0, 2)

    # Filter Parameters
    FILTER_SWITCH = (0x20, 0, 1)  # BYPASS, LPF
    FILTER_CUTOFF = (0x21, 0, 127)  # (54 - 74)
    FILTER_CUTOFF_KEYFOLLOW = (0x22, 54, 74)
    FILTER_RESONANCE = (0x23, 0, 127)
    FILTER_ENV_VELOCITY_SENS = (0x24, 1, 127)
    FILTER_ENV_ATTACK_TIME = (0x25, 0, 127)
    FILTER_ENV_DECAY_TIME = (0x26, 0, 127)
    FILTER_ENV_SUSTAIN_LEVEL = (0x27, 0, 127)
    FILTER_ENV_RELEASE_TIME = (0x28, 0, 127)
    FILTER_ENV_DEPTH = (0x29, 1, 127)

    # Amplifier Parameters
    AMP_LEVEL = (0x2A, 0, 127)
    AMP_LEVEL_KEYFOLLOW = (0x2B, 54, 74)  # -100 - +100
    AMP_LEVEL_VELOCITY_SENS = (0x2C, 1, 127)
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
    LFO_PITCH_MODULATION_CONTROL = (0x38, 1, 127)
    LFO_FILTER_MODULATION_CONTROL = (0x39, 1, 127)
    LFO_AMP_MODULATION_CONTROL = (0x3A, 1, 127)
    LFO_RATE_MODULATION_CONTROL = (0x3B, 1, 127)

    # Reserve
    RESERVE_1 = (0x37, 0, 0)
    RESERVE_2 = (0x3C, 0, 0)

    def __init__(self, address: int, min_val: int, max_val: int):
        self.address = address
        self.min_val = min_val
        self.max_val = max_val

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
        """Return the parameter name for a given address."""
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
        """Returns True if parameter is a binary/enum switch"""
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
        """Get the address of a parameter by name."""
        param = AnalogParameter.get_by_name(param_name)
        if param:
            return param.value[0]
        return None

    @staticmethod
    def get_range(param_name):
        """Get the value range (min, max) of a parameter by name."""
        param = AnalogParameter.get_by_name(param_name)
        if param:
            return param.value[1], param.value[2]
        return None, None
