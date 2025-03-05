"""
EffectParameter Module
=======================

This module defines the `EffectParameter` class, which manages effect-related parameters
for JD-Xi patch data. It provides functionality to retrieve parameter addresses, convert
values between display and MIDI formats, and categorize parameters based on effect types.

Classes
--------

.. class:: EffectParameter(address: int, min_val: int, max_val: int, display_min: Optional[int] = None, display_max: Optional[int] = None)

   Represents an effect parameter with an address, value range, and optional display range.

   **Methods:**

   .. method:: get_display_value() -> Tuple[int, int]

      Returns the display range for the parameter.

   .. method:: get_address_by_name(name: str) -> Optional[int]

      Looks up an effect parameter address by its name.

   .. method:: get_by_address(address: int) -> Optional[EffectParameter]

      Retrieves an effect parameter by its address.

   .. method:: get_by_name(name: str) -> Optional[EffectParameter]

      Retrieves an effect parameter by its name.

   .. method:: convert_to_midi(display_value: int) -> int

      Converts a display value to a corresponding MIDI value.

   .. method:: get_midi_value(param_name: str, value: int) -> Optional[int]

      Returns the MIDI value for an effect parameter given its name and display value.

   .. method:: get_common_param_by_name(name: str) -> Optional[EffectCommonParameter]

      Categorizes an effect parameter into a common effect type.

Constants
---------

This class defines various constants representing effect parameters, such as:

- **EFX1_TYPE**
- **EFX1_LEVEL**
- **DELAY_LEVEL**
- **REVERB_LEVEL**

Each parameter is defined as a tuple containing:

- Address (int)
- Minimum value (int)
- Maximum value (int)
- Display minimum value (Optional[int])
- Display maximum value (Optional[int])

Usage Example
-------------

.. code-block:: python

   param = EffectParameter.get_by_name("EFX1_LEVEL")
   if param:
       midi_value = param.convert_to_midi(64)
       print(f"MIDI Value: {midi_value}")

"""

from typing import Optional, Tuple

from jdxi_manager.data.effects import EffectCommonParameter
from jdxi_manager.data.parameter.synth import SynthParameter


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
    REVERB_LEVEL = (0x03, 0, 127, 0, 127)
    REVERB_PARAM_1 = (0x07, 12768, 52768, -20000, 20000)
    REVERB_PARAM_2 = (0x0B, 12768, 52768, -20000, 20000)
    REVERB_PARAM_24 = (0x5F, 12768, 52768, -20000, 20000)

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

    convert_from_display = convert_to_midi

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
            EffectCommonParameter.PROGRAM_EFFECT_1: {
                "EFX1_TYPE", "EFX1_LEVEL", "EFX1_DELAY_SEND_LEVEL",
                "EFX1_REVERB_SEND_LEVEL", "EFX1_OUTPUT_ASSIGN",
                "EFX1_PARAM_1", "EFX1_PARAM_2", "EFX1_PARAM_32"
            },
            EffectCommonParameter.PROGRAM_EFFECT_2: {
                "EFX2_TYPE", "EFX2_LEVEL", "EFX2_DELAY_SEND_LEVEL",
                "EFX2_REVERB_SEND_LEVEL", "EFX2_PARAM_1", "EFX2_PARAM_2"
            },
            EffectCommonParameter.PROGRAM_DELAY: {
                "DELAY_TYPE", "DELAY_TIME", "DELAY_TAP_TIME",
                "DELAY_FEEDBACK", "DELAY_HF_DAMP", "DELAY_LEVEL",
                "DELAY_REVERB_SEND_LEVEL", "DELAY_PARAM_1", "DELAY_PARAM_2", "DELAY_PARAM_24"
            },
            EffectCommonParameter.PROGRAM_REVERB: {
                "REVERB_OFF_ON", "REVERB_TYPE", "REVERB_TIME", "REVERB_HF_DAMP",
                "REVERB_LEVEL", "REVERB_PARAM_1", "REVERB_PARAM_2", "REVERB_PARAM_24"
            }
        }

        for category, parameters in param_mapping.items():
            if name in parameters:
                return category

        return None  # Return None if no match is found
