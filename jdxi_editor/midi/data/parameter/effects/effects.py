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

Function	Address	Value Type	Description
EFX2 Type	00 00	0–5 or 0–8	Sets effect type (e.g., Thru, Distortion, Fuzz)
EFX2 Level	00 01	0–127	Overall effect output
EFX2 Delay Send Level	00 02	0–127	Send to Delay effect
EFX2 Reverb Send Level	00 03	0–127	Send to Reverb effect
EFX2 Parameter 1	00 11	Signed 4-byte int	Meaning depends on EFX2 Type
EFX2 Parameter 2	00 15	Signed 4-byte int	As above
...	...	...	Up to Param 32 at 01 0D
Example for Distortion (EFX2_TYPE = 01)
Param #	Address	Meaning
Param 1	00 11	Drive
Param 2	00 15	Presence
Param 3	00 19	(possibly unused or Level)


"""

from typing import Optional, Tuple

from jdxi_editor.midi.data.parameter.effects.common import AddressParameterEffectCommon
from jdxi_editor.midi.data.parameter.synth import AddressParameter


class AddressParameterEffect1(AddressParameter):
    """Effect parameters with address and value range"""

    def __init__(
        self,
        address: int,
        min_val: int,
        max_val: int,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
        tooltip: Optional[str] = None,
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
        self.tooltip = tooltip

    def get_display_value(self) -> Tuple[int, int]:
        """
        Get the display range for the parameter
        :return: Tuple[int, int] The display range
        """
        return self.display_min, self.display_max

    # EFX1 Parameters
    EFX1_TYPE = (0x00, 0, 4, 0, 4, "Selects the type of effect to be applied:\n00: Thru\n01: Distortion\n02: Fuzz\n03: Compressor\n04: Bit Crusher ")
    EFX1_LEVEL = (0x01, 0, 127, 0, 127, "Sets the level of the effect.")
    EFX1_DELAY_SEND_LEVEL = (0x02, 0, 127, 0, 127, "Depth of delay applied to the sound from effect 1.")
    EFX1_REVERB_SEND_LEVEL = (0x03, 0, 127, 0, 127, "Depth of reverb applied to the sound from effect 1.")
    EFX1_OUTPUT_ASSIGN = (0x04, 0, 1, 0, 1, "Selects the output destination for the sound from effect 1.\nDIR: Output to the Output jacks.\nEFX2: Output to Effect 2.\nIf you want to use EFX1 and EFX2 separately for each part, set this parameter to DIR. For details, refer to the effect block diagram.")
    EFX1_PARAM_1 = (0x11, 12768, 52768, -20000, 20000, "Sets the first parameter of the effect.")
    EFX1_PARAM_2 = (0x15, 12768, 52768, -20000, 20000, "Sets the second parameter of the effect.")
    EFX1_PARAM_3 = (0x19, 12768, 52768, -20000, 20000)
    EFX1_PARAM_4 = (0x1D, 12768, 52768, -20000, 20000)
    EFX1_PARAM_5 = (0x21, 12768, 52768, -20000, 20000)
    EFX1_PARAM_6 = (0x25, 12768, 52768, -20000, 20000)
    EFX1_PARAM_7 = (0x29, 12768, 52768, -20000, 20000)
    EFX1_PARAM_8 = (0x2D, 12768, 52768, -20000, 20000)
    EFX1_PARAM_9 = (0x31, 12768, 52768, -20000, 20000)
    EFX1_PARAM_10 = (0x35, 12768, 52768, -20000, 20000)
    EFX1_PARAM_11 = (0x39, 12768, 52768, -20000, 20000)
    EFX1_PARAM_12 = (0x3D, 12768, 52768, -20000, 20000)
    EFX1_PARAM_13 = (0x41, 12768, 52768, -20000, 20000)
    EFX1_PARAM_14 = (0x45, 12768, 52768, -20000, 20000)
    EFX1_PARAM_15 = (0x49, 12768, 52768, -20000, 20000)
    EFX1_PARAM_16 = (0x4D, 12768, 52768, -20000, 20000)
    EFX1_PARAM_32 = (0x1D, 12768, 52768, -20000, 20000, "Sets the third parameter of the effect.")

    @classmethod
    def get_address_by_name(cls, name: str) -> Optional[int]:
        """Look up an effect parameter address by its name
        :param name: str The parameter name
        :return: Optional[int] The address
        """
        member = cls.__members__.get(name, None)
        return member.value[0] if member else None

    @classmethod
    def get_by_address(cls, address: int) -> Optional[object]:
        """Look up an effect parameter by its address
        :param address: int The address
        :return: Optional[object] The parameter
        """
        for param in cls:
            if isinstance(param.value, tuple) and param.value[0] == address:
                return param
        return None  # Return None if no match is found

    @classmethod
    def get_by_name(cls, name: str) -> Optional[object]:
        """Look up an effect parameter by its name
        :param name: str The parameter name
        :return: Optional[object] The parameter
        """
        return cls.__members__.get(name, None)

    def convert_to_midi(self, display_value: int) -> int:
        """Convert from display value to MIDI value
        :param display_value: int The display value
        :return: int The MIDI value
        """
        # Handle special bipolar cases first
        if self in [AddressParameterEffect1.EFX1_TYPE,
                    AddressParameterEffect1.EFX1_LEVEL,
                    AddressParameterEffect1.EFX1_REVERB_SEND_LEVEL,
                    AddressParameterEffect1.EFX1_DELAY_SEND_LEVEL,
                    AddressParameterEffect1.EFX1_OUTPUT_ASSIGN]:
            return display_value  # Already 0–127 or boolean-style
        else:
            return display_value + 20000  # Convert to MIDI value by adding 20000 for bipolar parameters

    convert_from_display = convert_to_midi

    @staticmethod
    def get_midi_value(param_name: str, value: int) -> Optional[int]:
        """
        Get the MIDI value for address parameter by name and value.
        :param param_name: str The parameter name
        :param value: int The value
        :return: Optional[int] The MIDI value
        """
        param = AddressParameterEffect1.get_by_name(param_name)
        if param:
            return param.convert_to_midi(value)
        return None

    @classmethod
    def get_common_param_by_name(
        cls, name: str
    ) -> Optional[AddressParameterEffectCommon]:
        """
        Look up an effect parameter's category using address dictionary mapping
        :param name: str The parameter name
        :return: Optional[AddressParameterEffectCommon] The category
        """
        param_mapping = {
            AddressParameterEffectCommon.PROGRAM_EFFECT_1: {
                "EFX1_TYPE",
                "EFX1_LEVEL",
                "EFX1_DELAY_SEND_LEVEL",
                "EFX1_REVERB_SEND_LEVEL",
                "EFX1_OUTPUT_ASSIGN",
                "EFX1_PARAM_1",
                "EFX1_PARAM_2",
                "EFX1_PARAM_32",
            },
        }

        for category, parameters in param_mapping.items():
            if name in parameters:
                return category

        return None  # Return None if no match is found


class AddressParameterEffect2(AddressParameter):
    """Effect parameters with address and value range"""

    def __init__(
        self,
        address: int,
        min_val: int,
        max_val: int,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
        tooltip: Optional[str] = None,
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
        self.tooltip = tooltip
    def get_display_value(self) -> Tuple[int, int]:
        """
        Get the display range for the parameter
        :return: Tuple[int, int] The display range
        """
        return self.display_min, self.display_max

    # EFX2 Parameters
    EFX2_TYPE = (0x00, 0, 8, 0, 8)
    EFX2_LEVEL = (0x01, 0, 127, 0, 127)
    EFX2_DELAY_SEND_LEVEL = (0x02, 0, 127, 0, 127)
    EFX2_REVERB_SEND_LEVEL = (0x03, 0, 127, 0, 127)
    EFX2_PARAM_1 = (0x11, 12768, 52768, -20000, 20000)
    EFX2_PARAM_2 = (0x15, 12768, 52768, -20000, 20000)
    EFX2_PARAM_3 = (0x19, 12768, 52768, -20000, 20000)
    EFX2_PARAM_4 = (0x1D, 12768, 52768, -20000, 20000)
    EFX2_PARAM_5 = (0x21, 12768, 52768, -20000, 20000)
    EFX2_PARAM_6 = (0x25, 12768, 52768, -20000, 20000)
    EFX2_PARAM_7 = (0x29, 12768, 52768, -20000, 20000)
    EFX2_PARAM_8 = (0x2D, 12768, 52768, -20000, 20000)
    EFX2_PARAM_9 = (0x31, 12768, 52768, -20000, 20000)
    EFX2_PARAM_10 = (0x35, 12768, 52768, -20000, 20000)
    EFX2_PARAM_11 = (0x39, 12768, 52768, -20000, 20000) 
    EFX2_PARAM_12 = (0x3D, 12768, 52768, -20000, 20000)
    EFX2_PARAM_13 = (0x41, 12768, 52768, -20000, 20000)
    EFX2_PARAM_14 = (0x45, 12768, 52768, -20000, 20000)
    EFX2_PARAM_15 = (0x49, 12768, 52768, -20000, 20000)
    EFX2_PARAM_16 = (0x4D, 12768, 52768, -20000, 20000)
    EFX2_PARAM_17 = (0x51, 12768, 52768, -20000, 20000)
    EFX2_PARAM_18 = (0x55, 12768, 52768, -20000, 20000)
    EFX2_PARAM_19 = (0x59, 12768, 52768, -20000, 20000)
    EFX2_PARAM_20 = (0x5D, 12768, 52768, -20000, 20000)
    EFX2_PARAM_21 = (0x61, 12768, 52768, -20000, 20000)
    EFX2_PARAM_22 = (0x65, 12768, 52768, -20000, 20000)
    EFX2_PARAM_23 = (0x69, 12768, 52768, -20000, 20000)
    EFX2_PARAM_24 = (0x6D, 12768, 52768, -20000, 20000)
    EFX2_PARAM_25 = (0x71, 12768, 52768, -20000, 20000)
    EFX2_PARAM_32 = (0x0D, 12768, 52768, -20000, 20000)

    @classmethod
    def get_address_by_name(cls, name: str) -> Optional[int]:
        """Look up an effect parameter address by its name
        :param name: str The parameter name
        :return: Optional[int] The address
        """
        member = cls.__members__.get(name, None)
        return member.value[0] if member else None

    @classmethod
    def get_by_address(cls, address: int) -> Optional[object]:
        """Look up an effect parameter by its address
        :param address: int The address
        :return: Optional[object] The parameter
        """
        for param in cls:
            if isinstance(param.value, tuple) and param.value[0] == address:
                return param
        return None  # Return None if no match is found

    @classmethod
    def get_by_name(cls, name: str) -> Optional[object]:
        """Look up an effect parameter by its name
        :param name: str The parameter name
        :return: Optional[object] The parameter
        """
        return cls.__members__.get(name, None)

    def convert_to_midi(self, display_value: int) -> int:
        """Convert from display value to MIDI value
        :param display_value: int The display value
        :return: int The MIDI value
        """
        # Handle special bipolar cases first
        if self == AddressParameterEffect2.EFX2_PARAM_1:
            return display_value + 32768  #
        elif self == AddressParameterEffect2.EFX2_PARAM_2:
            return display_value + 32768  #
        elif self == AddressParameterEffect2.EFX2_PARAM_32:
            return display_value + 32768  #
        else:
            return display_value

    convert_from_display = convert_to_midi

    @staticmethod
    def get_midi_value(param_name: str, value: int) -> Optional[int]:
        """
        Get the MIDI value for address parameter by name and value.
        :param param_name: str The parameter name
        :param value: int The value
        :return: Optional[int] The MIDI value
        """
        param = AddressParameterReverb.get_by_name(param_name)
        if param:
            return param.convert_to_midi(value)
        return None

    @classmethod
    def get_common_param_by_name(
        cls, name: str
    ) -> Optional[AddressParameterEffectCommon]:
        """
        Look up an effect parameter's category using address dictionary mapping
        :param name: str The parameter name
        :return: Optional[AddressParameterEffectCommon] The category
        """
        param_mapping = {
            AddressParameterEffectCommon.PROGRAM_EFFECT_2: {
                "EFX2_TYPE",
                "EFX2_LEVEL",
                "EFX2_DELAY_SEND_LEVEL",
                "EFX2_REVERB_SEND_LEVEL",
                "EFX2_PARAM_1",
                "EFX2_PARAM_2",
            },
        }

        for category, parameters in param_mapping.items():
            if name in parameters:
                return category

        return None  # Return None if no match is found


class AddressParameterDelay(AddressParameter):
    """Effect parameters with address and value range"""

    def __init__(
        self,
        address: int,
        min_val: int,
        max_val: int,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
        tooltip: Optional[str] = None,
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val

        self.tooltip = tooltip
    def get_display_value(self) -> Tuple[int, int]:
        """
        Get the display range for the parameter
        :return: Tuple[int, int] The display range
        """
        return self.display_min, self.display_max

    # Delay Parameters
    DELAY_LEVEL = (0x01, 0, 127, 0, 127, "Sets the level of the delay effect.")
    DELAY_PARAM_1 = (0x08, 12768, 52768, -20000, 20000, "Sets the first parameter of the delay effect.")
    DELAY_PARAM_2 = (0x0C, 12768, 52768, -20000, 20000, "Sets the second parameter of the delay effect.")
    DELAY_PARAM_24 = (0x60, 12768, 52768, -20000, 20000, "Sets the third parameter of the delay effect.")
    DELAY_REVERB_SEND_LEVEL = (0x06, 0, 127, 0, 127, "Depth of reverb applied to the sound from delay.")

    @classmethod
    def get_address_by_name(cls, name: str) -> Optional[int]:
        """Look up an effect parameter address by its name
        :param name: str The parameter name
        :return: Optional[int] The address
        """
        member = cls.__members__.get(name, None)
        return member.value[0] if member else None

    @classmethod
    def get_by_address(cls, address: int) -> Optional[object]:
        """Look up an effect parameter by its address
        :param address: int The address
        :return: Optional[object] The parameter
        """
        for param in cls:
            if isinstance(param.value, tuple) and param.value[0] == address:
                return param
        return None  # Return None if no match is found

    @classmethod
    def get_by_name(cls, name: str) -> Optional[object]:
        """Look up an effect parameter by its name
        :param name: str The parameter name
        :return: Optional[object] The parameter
        """
        return cls.__members__.get(name, None)

    def convert_to_midi(self, display_value: int) -> int:
        """Convert from display value to MIDI value
        :param display_value: int The display value
        :return: int The MIDI value
        """
        # Handle special bipolar cases first
        if self == AddressParameterDelay.DELAY_PARAM_1:
            return display_value + 32768  #
        elif self == AddressParameterDelay.DELAY_PARAM_2:
            return display_value + 32768  #
        elif self == AddressParameterDelay.DELAY_PARAM_24:
            return display_value + 32768  #
        else:
            return display_value

    convert_from_display = convert_to_midi

    @staticmethod
    def get_midi_value(param_name: str, value: int) -> Optional[int]:
        """
        Get the MIDI value for address parameter by name and value.
        :param param_name: str The parameter name
        :param value: int The value
        :return: Optional[int] The MIDI value
        """
        param = AddressParameterReverb.get_by_name(param_name)
        if param:
            return param.convert_to_midi(value)
        return None

    @classmethod
    def get_common_param_by_name(
        cls, name: str
    ) -> Optional[AddressParameterEffectCommon]:
        """
        Look up an effect parameter's category using address dictionary mapping
        :param name: str The parameter name
        :return: Optional[AddressParameterEffectCommon] The category
        """
        param_mapping = {
            AddressParameterEffectCommon.PROGRAM_DELAY: {
                "DELAY_TYPE",
                "DELAY_TIME",
                "DELAY_TAP_TIME",
                "DELAY_FEEDBACK",
                "DELAY_HF_DAMP",
                "DELAY_LEVEL",
                "DELAY_REVERB_SEND_LEVEL",
                "DELAY_PARAM_1",
                "DELAY_PARAM_2",
                "DELAY_PARAM_24",
            },
        }

        for category, parameters in param_mapping.items():
            if name in parameters:
                return category

        return None  # Return None if no match is found


class AddressParameterReverb(AddressParameter):
    """Effect parameters with address and value range"""

    def __init__(
        self,
        address: int,
        min_val: int,
        max_val: int,
        display_min: Optional[int] = None,
        display_max: Optional[int] = None,
        tooltip: Optional[str] = None,
    ):
        super().__init__(address, min_val, max_val)
        self.display_min = display_min if display_min is not None else min_val
        self.display_max = display_max if display_max is not None else max_val
        self.tooltip = tooltip

    def get_display_value(self) -> Tuple[int, int]:
        """
        Get the display range for the parameter
        :return: Tuple[int, int] The display range
        """
        return self.display_min, self.display_max

    # Reverb Parameters
    REVERB_LEVEL = (0x03, 0, 127, 0, 127, "Sets the level of the reverb effect.")
    REVERB_PARAM_1 = (0x07, 12768, 52768, -20000, 20000, "Sets the first parameter of the reverb effect.")
    REVERB_PARAM_2 = (0x0B, 12768, 52768, -20000, 20000, "Sets the second parameter of the reverb effect.")
    REVERB_PARAM_24 = (0x5F, 12768, 52768, -20000, 20000, "Sets the third parameter of the reverb effect.")

    @classmethod
    def get_address_by_name(cls, name: str) -> Optional[int]:
        """Look up an effect parameter address by its name
        :param name: str The parameter name
        :return: Optional[int] The address
        """
        member = cls.__members__.get(name, None)
        return member.value[0] if member else None

    @classmethod
    def get_by_address(cls, address: int) -> Optional[object]:
        """Look up an effect parameter by its address
        :param address: int The address
        :return: Optional[object] The parameter
        """
        for param in cls:
            if isinstance(param.value, tuple) and param.value[0] == address:
                return param
        return None  # Return None if no match is found

    @classmethod
    def get_by_name(cls, name: str) -> Optional[object]:
        """Look up an effect parameter by its name
        :param name: str The parameter name
        :return: Optional[object] The parameter
        """
        return cls.__members__.get(name, None)

    def convert_to_midi(self, display_value: int) -> int:
        """Convert from display value to MIDI value
        :param display_value: int The display value
        :return: int The MIDI value
        """
        # Handle special bipolar cases first
        if self == AddressParameterReverb.REVERB_PARAM_1:
            return display_value + 32768  #
        elif self == AddressParameterReverb.REVERB_PARAM_2:
            return display_value + 32768  #
        elif self == AddressParameterReverb.REVERB_PARAM_24:
            return display_value + 32768  #
        else:
            return display_value

    convert_from_display = convert_to_midi

    @staticmethod
    def get_midi_value(param_name: str, value: int) -> Optional[int]:
        """
        Get the MIDI value for address parameter by name and value.
        :param param_name: str The parameter name
        :param value: int The value
        :return: Optional[int] The MIDI value
        """
        param = AddressParameterReverb.get_by_name(param_name)
        if param:
            return param.convert_to_midi(value)
        return None

    @classmethod
    def get_common_param_by_name(
        cls, name: str
    ) -> Optional[AddressParameterEffectCommon]:
        """
        Look up an effect parameter's category using address dictionary mapping
        :param name: str The parameter name
        :return: Optional[AddressParameterEffectCommon] The category
        """
        param_mapping = {
            AddressParameterEffectCommon.PROGRAM_REVERB: {
                "REVERB_OFF_ON",
                "REVERB_TYPE",
                "REVERB_TIME",
                "REVERB_HF_DAMP",
                "REVERB_LEVEL",
                "REVERB_PARAM_1",
                "REVERB_PARAM_2",
                "REVERB_PARAM_24",
            },
        }

        for category, parameters in param_mapping.items():
            if name in parameters:
                return category

        return None  # Return None if no match is found
