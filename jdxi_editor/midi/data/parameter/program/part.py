"""
Program Part Parameters
======================

Defines the PartParam enum for Program Part parameters (0x18 00 20-23 00).
Per Roland Parameter Address Map (midi_parameters.txt), Program Part has
offsets 0x00-0x4B. Total size 0x4C.

Used for: Digital Synth Part 1 (0x20), Part 2 (0x21), Analog Synth Part (0x22),
Drums Part (0x23).
"""

from typing import Optional, Tuple

from picomidi.sysex.parameter.address import AddressParameter

from jdxi_editor.midi.parameter.spec import ParameterSpec


class PartParam(AddressParameter):
    """Program Part parameters (per Roland Parameter Address Map)"""

    def __init__(
        self,
        address: int,
        min_val: Optional[int] = None,
        max_val: Optional[int] = None,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
        tooltip: Optional[str] = None,
        display_name: Optional[str] = None,
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
        self.tooltip = tooltip if tooltip is not None else ""
        self._display_name = display_name

    # 0x00-0x05
    RECEIVE_CHANNEL = ParameterSpec(0x00, 0, 15)  # 1-16
    PART_SWITCH = ParameterSpec(0x01, 0, 1)  # OFF, ON
    # 0x02-0x05 reserve
    TONE_BANK_SELECT_MSB = ParameterSpec(0x06, 0, 127)  # CC# 0
    TONE_BANK_SELECT_LSB = ParameterSpec(0x07, 0, 127)  # CC# 32
    TONE_PROGRAM_NUMBER = ParameterSpec(0x08, 0, 127)  # PC

    # 0x09-0x1A
    PART_LEVEL = ParameterSpec(0x09, 0, 127)  # CC# 7
    PART_PAN = ParameterSpec(0x0A, 0, 127)  # CC# 10, L64-63R
    PART_COARSE_TUNE = ParameterSpec(0x0B, 16, 112, -48, 48)  # RPN# 2
    PART_FINE_TUNE = ParameterSpec(0x0C, 14, 114, -50, 50)  # RPN# 1
    PART_MONO_POLY = ParameterSpec(0x0D, 0, 2)  # MONO, POLY, TONE
    PART_LEGATO_SWITCH = ParameterSpec(0x0E, 0, 2)  # OFF, ON, TONE
    PART_PITCH_BEND_RANGE = ParameterSpec(0x0F, 0, 25)  # 0-24, TONE
    PART_PORTAMENTO_SWITCH = ParameterSpec(0x10, 0, 2)  # OFF, ON, TONE
    PART_PORTAMENTO_TIME = ParameterSpec(0x11, 0, 128)  # 0-127, TONE (2 bytes)
    # 0x12 reserve
    PART_CUTOFF_OFFSET = ParameterSpec(0x13, 0, 127, -64, 63)  # CC# 74
    PART_RESONANCE_OFFSET = ParameterSpec(0x14, 0, 127, -64, 63)  # CC# 71
    PART_ATTACK_TIME_OFFSET = ParameterSpec(0x15, 0, 127, -64, 63)  # CC# 73
    PART_DECAY_TIME_OFFSET = ParameterSpec(0x16, 0, 127, -64, 63)  # CC# 75
    PART_RELEASE_TIME_OFFSET = ParameterSpec(0x17, 0, 127, -64, 63)  # CC# 72
    PART_VIBRATO_RATE = ParameterSpec(0x18, 0, 127, -64, 63)  # CC# 76
    PART_VIBRATO_DEPTH = ParameterSpec(0x19, 0, 127, -64, 63)  # CC# 77
    PART_VIBRATO_DELAY = ParameterSpec(0x1A, 0, 127, -64, 63)  # CC# 78

    # 0x1B-0x2E
    PART_OCTAVE_SHIFT = ParameterSpec(0x1B, 61, 67, -3, 3)
    PART_VELOCITY_SENS_OFFSET = ParameterSpec(0x1C, 1, 127, -63, 63)
    # 0x1D-0x20 reserve
    VELOCITY_RANGE_LOWER = ParameterSpec(0x21, 1, 127)
    VELOCITY_RANGE_UPPER = ParameterSpec(0x22, 0, 127)
    VELOCITY_FADE_WIDTH_LOWER = ParameterSpec(0x23, 0, 127)
    VELOCITY_FADE_WIDTH_UPPER = ParameterSpec(0x24, 0, 127)
    MUTE_SWITCH = ParameterSpec(0x25, 0, 1)  # OFF, MUTE
    # 0x26-0x29 reserve
    # 0x2A reserve
    PART_DELAY_SEND_LEVEL = ParameterSpec(0x2B, 0, 127)  # CC# 94
    PART_REVERB_SEND_LEVEL = ParameterSpec(0x2C, 0, 127)  # CC# 91
    PART_OUTPUT_ASSIGN = ParameterSpec(0x2D, 0, 4)  # EFX1, EFX2, DLY, REV, DIR
    # 0x2E reserve

    # Scale Tune 0x2F-0x3C
    PART_SCALE_TUNE_TYPE = ParameterSpec(0x2F, 0, 8)
    PART_SCALE_TUNE_KEY = ParameterSpec(0x30, 0, 11)
    PART_SCALE_TUNE_C = ParameterSpec(0x31, 0, 127, -64, 63)
    PART_SCALE_TUNE_CS = ParameterSpec(0x32, 0, 127, -64, 63)
    PART_SCALE_TUNE_D = ParameterSpec(0x33, 0, 127, -64, 63)
    PART_SCALE_TUNE_DS = ParameterSpec(0x34, 0, 127, -64, 63)
    PART_SCALE_TUNE_E = ParameterSpec(0x35, 0, 127, -64, 63)
    PART_SCALE_TUNE_F = ParameterSpec(0x36, 0, 127, -64, 63)
    PART_SCALE_TUNE_FS = ParameterSpec(0x37, 0, 127, -64, 63)
    PART_SCALE_TUNE_G = ParameterSpec(0x38, 0, 127, -64, 63)
    PART_SCALE_TUNE_GS = ParameterSpec(0x39, 0, 127, -64, 63)
    PART_SCALE_TUNE_A = ParameterSpec(0x3A, 0, 127, -64, 63)
    PART_SCALE_TUNE_AS = ParameterSpec(0x3B, 0, 127, -64, 63)
    PART_SCALE_TUNE_B = ParameterSpec(0x3C, 0, 127, -64, 63)

    # Receive switches 0x3D-0x46
    RECEIVE_PROGRAM_CHANGE = ParameterSpec(0x3D, 0, 1)
    RECEIVE_BANK_SELECT = ParameterSpec(0x3E, 0, 1)
    RECEIVE_PITCH_BEND = ParameterSpec(0x3F, 0, 1)
    RECEIVE_POLYPHONIC_KEY_PRESSURE = ParameterSpec(0x40, 0, 1)
    RECEIVE_CHANNEL_PRESSURE = ParameterSpec(0x41, 0, 1)
    RECEIVE_MODULATION = ParameterSpec(0x42, 0, 1)
    RECEIVE_VOLUME = ParameterSpec(0x43, 0, 1)
    RECEIVE_PAN = ParameterSpec(0x44, 0, 1)
    RECEIVE_EXPRESSION = ParameterSpec(0x45, 0, 1)
    RECEIVE_HOLD_1 = ParameterSpec(0x46, 0, 1)

    def get_display_value(self) -> Tuple[int, int]:
        """Get the digital value range (min, max) for the parameter"""
        if hasattr(self, "display_min") and hasattr(self, "display_max"):
            return self.display_min, self.display_max
        return self.min_val, self.max_val

    @property
    def display_name(self) -> str:
        """Get display name for the parameter."""
        if getattr(self, "_display_name", None) is not None:
            return self._display_name
        return self.name.replace("_", " ").title()

    def get_address_for_partial(self, partial_number: int = 0) -> Tuple[int, int]:
        """Get parameter area and address adjusted for part number (0-3)."""
        group_map = {0: 0x20, 1: 0x21, 2: 0x22, 3: 0x23}
        group = group_map.get(partial_number, 0x20)
        return group, self.address

    @staticmethod
    def get_by_name(param_name: str) -> Optional["PartParam"]:
        """Get the Parameter by name."""
        return PartParam.__members__.get(param_name, None)
