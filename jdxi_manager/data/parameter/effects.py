from enum import Enum
from typing import Optional, Tuple

from jdxi_manager.data.effects import EffectsCommonParameter
from jdxi_manager.data.parameter.synth import SynthParameter

"""
For reference:

**Program Effect 1
+------------------------------------------------------------------------------+
| Offset | |
| Address | Description |
|-------------+----------------------------------------------------------------|
| 00 00 | 0aaa aaaa | EFX1 Type (0 - 4) |
| 00 01 | 0aaa aaaa | EFX1 Level (0 - 127) |
| 00 02 | 0aaa aaaa | EFX1 Delay Send Level (0 - 127) |
| 00 03 | 0aaa aaaa | EFX1 Reverb Send Level (0 - 127) |
| 00 04 | 0000 00aa | EFX1 Output Assign (0 - 1) |
| | | DIR, EFX2 |
|-------------+-----------+----------------------------------------------------|
| 00 05 | 0aaa aaaa | (reserve) <*> |
| 00 06 | 0aaa aaaa | (reserve) <*> |
| : | | |
| 00 10 | 000a aaaa | (reserve) <*> |
|-------------+-----------+----------------------------------------------------|
|# 00 11 | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | EFX1 Parameter 1 (12768 - 52768) |
| | | -20000 - +20000 |
|# 00 15 | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | EFX1 Parameter 2 (12768 - 52768) |
| | | -20000 - +20000 |
| : | | |
|# 01 0D | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | EFX1 Parameter 32 (12768 - 52768) |
| | | -20000 - +20000 |
|-------------+----------------------------------------------------------------|
| 00 00 01 11 | Total Size |
+------------------------------------------------------------------------------+

**Program Effect 2
+------------------------------------------------------------------------------+
| Offset | |
| Address | Description |
|-------------+----------------------------------------------------------------|
| 00 00 | 0aaa aaaa | EFX2 Type (0, 5 - 8) |
| 00 01 | 0aaa aaaa | EFX2 Level (0 - 127) |
| 00 02 | 0aaa aaaa | EFX2 Delay Send Level (0 - 127) |
| 00 03 | 0aaa aaaa | EFX2 Reverb Send Level (0 - 127) |
| 00 04 | 0000 00aa | (reserve) <*> |
|-------------+-----------+----------------------------------------------------|
| 00 05 | 0aaa aaaa | (reserve) <*> |
| 00 06 | 0aaa aaaa | (reserve) <*> |
| : | | |
| 00 10 | 000a aaaa | (reserve) <*> |
|-------------+-----------+----------------------------------------------------|
|# 00 11 | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | EFX2 Parameter 1 (12768 - 52768) |
| | | -20000 - +20000 |
|# 00 15 | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | EFX2 Parameter 2 (12768 - 52768) |
| | | -20000 - +20000 |
| : | | |
|# 01 0D | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | EFX2 Parameter 32 (12768 - 52768) |
| | | -20000 - +20000 |
|-------------+----------------------------------------------------------------|
| 00 00 01 11 | Total Size |
+------------------------------------------------------------------------------+

**Program Delay
+------------------------------------------------------------------------------+
| Offset | |
| Address | Description |
|-------------+----------------------------------------------------------------|
| 00 00 | 0000 aaaa | (reserve) <*> |
| 00 01 | 0aaa aaaa | Delay Level (0 - 127) |
| 00 02 | 0000 00aa | (reserve) <*> |
| 00 03 | 0aaa aaaa | Delay Reverb Send Level (0 - 127) |
|-------------+-----------+----------------------------------------------------|
|# 00 04 | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | Delay Parameter 1 (12768 - 52768) |
| | | -20000 - +20000 |
|# 00 08 | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | Delay Parameter 2 (12768 - 52768) |
| | | -20000 - +20000 |
| : | | |
|# 00 60 | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | Delay Parameter 24 (12768 - 52768) |
| | | -20000 - +20000 |
|-------------+----------------------------------------------------------------|
| 00 00 00 64 | Total Size |
+------------------------------------------------------------------------------+

**Program Reverb
+------------------------------------------------------------------------------+
| Offset | |
| Address | Description |
|-------------+----------------------------------------------------------------|
| 00 00 | 0000 aaaa | (reserve) <*> |
| 00 01 | 0aaa aaaa | Reverb Level (0 - 127) |
| 00 02 | 0000 00aa | (reserve) <*> |
|-------------+-----------+----------------------------------------------------|
|# 00 03 | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | Reverb Parameter 1 (12768 - 52768) |
| | | -20000 - +20000 |
|# 00 07 | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | Reverb Parameter 2 (12768 - 52768) |
| | | -20000 - +20000 |
| : | | |
|# 00 5F | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | Reverb Parameter 24 (12768 - 52768) |
| | | -20000 - +20000 |
|-------------+----------------------------------------------------------------|
| 00 00 00 63 | Total Size |
+------------------------------------------------------------------------------+

"""


class EffectParameter(SynthParameter):
    """Effect parameters with address and value range"""

    def __init__(self, address: int, min_val: int, max_val: int,
                 display_min: Optional[int] = None, display_max: Optional[int] = None):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val

    def get_display_value(self) -> Tuple[int, int]:
        """Get the display range for the parameter"""
        return self.display_min, self.display_max

    # EFX1 Parameters
    EFX1_TYPE = (0x00, 0, 4, 0, 4)
    EFX1_LEVEL = (0x01, 0, 127, 0, 127)
    EFX1_DELAY_SEND_LEVEL = (0x02, 0, 127, 0, 127)
    EFX1_REVERB_SEND_LEVEL = (0x03, 0, 127, 0, 127)
    EFX1_OUTPUT_ASSIGN = (0x04, 0, 1, 0, 1)
    EFX1_PARAM_1 = (0x11, 12768, 52768, -20000, 20000)
    EFX1_PARAM_2 = (0x15, 12768, 52768, -20000, 20000)
    EFX1_PARAM_32 = (0x0D, 12768, 52768, -20000, 20000)

    # EFX2 Parameters
    EFX2_TYPE = (0x00, 0, 8, 0, 8)
    EFX2_LEVEL = (0x01, 0, 127, 0, 127)
    EFX2_DELAY_SEND_LEVEL = (0x02, 0, 127, 0, 127)
    EFX2_REVERB_SEND_LEVEL = (0x03, 0, 127, 0, 127)
    EFX2_PARAM_1 = (0x11, 12768, 52768, -20000, 20000)
    EFX2_PARAM_2 = (0x15, 12768, 52768, -20000, 20000)
    EFX2_PARAM_32 = (0x0D, 12768, 52768, -20000, 20000)

    #FLANGER_RATE = (0x00, 0, 8) # Fixme: These Flanger values are placeholders
    #FLANGER_DEPTH = (0x00, 0, 8)
    #FLANGER_FEEDBACK = (0x00, 0, 8)
    #FLANGER_MANUAL = (0x00, 0, 8)
    #FLANGER_BALANCE = (0x00, 0, 8)

    # Delay Parameters
    # DELAY_TYPE = (0x00, 0, 1)  # Assuming 0 for SINGLE, 1 for PAN
    DELAY_LEVEL = (0x01, 0, 127, 0, 127)
    # DELAY_TIME = (0x02, 0, 2600)
    # DELAY_TAP_TIME = (0x03, 0, 100)
    # DELAY_FEEDBACK = (0x04, 0, 98)
    # DELAY_HF_DAMP = (0x04, 200, 8000)
    # DELAY_LEVEL = (0x05, 0, 127)
    DELAY_PARAM_1 = (0x08, 12768, 52768, -20000, 20000)
    DELAY_PARAM_2 = (0x0C, 12768, 52768, -20000, 20000)
    DELAY_PARAM_24 = (0x60, 12768, 52768, -20000, 20000)
    DELAY_REVERB_SEND_LEVEL = (0x06, 0, 127, 0, 127)

    # Reverb Parameters
    #REVERB_OFF_ON = (0x00, 0, 1)
    #REVERB_TYPE = (0x00, 0, 5)  # Assuming 0 for ROOM1, 1 for ROOM2, etc.
    #REVERB_TIME = (0x01, 0, 127)
    #REVERB_HF_DAMP = (0x02, 200, 8000)
    REVERB_LEVEL = (0x03, 0, 127, 0, 127)
    REVERB_PARAM_1 = (0x07, 12768, 52768, -20000, 20000)
    REVERB_PARAM_2 = (0x0B, 12768, 52768, -20000, 20000)
    REVERB_PARAM_24 = (0x5F, 12768, 52768, -20000, 20000)

    # Common parameters
    #TYPE = (0x00,)
    #LEVEL = (0x01,)

    # Effect-specific parameters
    #PARAM_1 = (0x02,)
    #PARAM_2 = (0x03,)

    # Send levels
    #REVERB_SEND = (0x04,)
    #DELAY_SEND = (0x05,)
    #CHORUS_SEND = (0x06,)

    @classmethod
    def get_address_by_name(cls, name):
        """Look up an effect parameter address by its name"""
        member = cls.__members__.get(name, None)
        return member.value[0] if member else None

    @classmethod
    def get_by_address(cls, address):
        """Look up an effect parameter by its address"""
        for param in cls:
            if isinstance(param.value, tuple) and param.value[0] == address:
                return param
        return None  # Return None if no match is found

    @classmethod
    def get_by_name(cls, name):
        """Look up an effect parameter by its name"""
        return cls.__members__.get(name, None)

    def convert_to_midi(self, display_value: int) -> int:
        """Convert from display value to MIDI value"""
        # Handle special bipolar cases first
        if self == EffectParameter.EFX1_PARAM_1:
            return display_value + 32768  #
        elif self == EffectParameter.EFX1_PARAM_2:
            return display_value + 32768  #
        elif self == EffectParameter.EFX1_PARAM_32:
            return display_value + 32768  #
        elif self == EffectParameter.EFX2_PARAM_1:
            return display_value + 32768  #
        elif self == EffectParameter.EFX2_PARAM_2:
            return display_value + 32768  #
        elif self == EffectParameter.EFX2_PARAM_32:
            return display_value + 32768  #
        elif self == EffectParameter.DELAY_PARAM_1:
            return display_value + 32768  #
        elif self == EffectParameter.DELAY_PARAM_2:
            return display_value + 32768  #
        elif self == EffectParameter.DELAY_PARAM_24:
            return display_value + 32768  #
        elif self == EffectParameter.REVERB_PARAM_1:
            return display_value + 32768  #
        elif self == EffectParameter.REVERB_PARAM_2:
            return display_value + 32768  #
        elif self == EffectParameter.REVERB_PARAM_24:
            return display_value + 32768  #
        else:
            return display_value

    @staticmethod
    def get_midi_value(param_name, value):
        """Get the MIDI value for address parameter by name and value."""
        param = EffectParameter.get_by_name(param_name)
        if param:
            return param.convert_to_midi(value)
        return None

    @classmethod
    def get_common_param_by_name(cls, name):
        """Look up an effect parameter's category using address dictionary mapping"""
        param_mapping = {
            EffectsCommonParameter.PROGRAM_EFFECT_1: {
                "EFX1_TYPE", "EFX1_LEVEL", "EFX1_DELAY_SEND_LEVEL",
                "EFX1_REVERB_SEND_LEVEL", "EFX1_OUTPUT_ASSIGN",
                "EFX1_PARAM_1", "EFX1_PARAM_2", "EFX1_PARAM_32"
            },
            EffectsCommonParameter.PROGRAM_EFFECT_2: {
                "EFX2_TYPE", "EFX2_LEVEL", "EFX2_DELAY_SEND_LEVEL",
                "EFX2_REVERB_SEND_LEVEL", "EFX2_PARAM_1", "EFX2_PARAM_2"
            },
            EffectsCommonParameter.PROGRAM_DELAY: {
                "DELAY_TYPE", "DELAY_TIME", "DELAY_TAP_TIME",
                "DELAY_FEEDBACK", "DELAY_HF_DAMP", "DELAY_LEVEL",
                "DELAY_REVERB_SEND_LEVEL", "DELAY_PARAM_1", "DELAY_PARAM_2", "DELAY_PARAM_24"
            },
            EffectsCommonParameter.PROGRAM_REVERB: {
                "REVERB_OFF_ON", "REVERB_TYPE", "REVERB_TIME", "REVERB_HF_DAMP",
                "REVERB_LEVEL", "REVERB_PARAM_1", "REVERB_PARAM_2", "REVERB_PARAM_24"
            }
        }

        for category, parameters in param_mapping.items():
            if name in parameters:
                return category

        return None  # Return None if no match is found
