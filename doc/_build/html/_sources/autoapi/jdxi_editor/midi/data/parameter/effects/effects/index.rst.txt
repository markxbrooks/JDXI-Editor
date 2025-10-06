jdxi_editor.midi.data.parameter.effects.effects
===============================================

.. py:module:: jdxi_editor.midi.data.parameter.effects.effects

.. autoapi-nested-parse::

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

   Function        Address Value Type      Description
   EFX2 Type       00 00   0–5 or 0–8      Sets effect type (e.g., Thru, Distortion, Fuzz)
   EFX2 Level      00 01   0–127   Overall effect output
   EFX2 Delay Send Level   00 02   0–127   Send to Delay effect
   EFX2 Reverb Send Level  00 03   0–127   Send to Reverb effect
   EFX2 Parameter 1        00 11   Signed 4-byte int       Meaning depends on EFX2 Type
   EFX2 Parameter 2        00 15   Signed 4-byte int       As above
   ...     ...     ...     Up to Param 32 at 01 0D
   Example for Distortion (EFX2_TYPE = 01)
   Param # Address Meaning
   Param 1 00 11   Drive
   Param 2 00 15   Presence
   Param 3 00 19   (possibly unused or Level)




Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.effects.effects.AddressParameterEffect1
   jdxi_editor.midi.data.parameter.effects.effects.AddressParameterEffect2
   jdxi_editor.midi.data.parameter.effects.effects.AddressParameterDelay
   jdxi_editor.midi.data.parameter.effects.effects.AddressParameterReverb


Module Contents
---------------

.. py:class:: AddressParameterEffect1(address: int, min_val: int, max_val: int, display_min: Optional[int] = None, display_max: Optional[int] = None, tooltip: Optional[str] = None)

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Effect parameters with address and value range


   .. py:attribute:: display_min
      :value: None



   .. py:attribute:: display_max
      :value: None



   .. py:attribute:: tooltip
      :value: None



   .. py:method:: get_display_value() -> Tuple[int, int]

      Get the display range for the parameter

      :return: Tuple[int, int] The display range



   .. py:attribute:: EFX1_TYPE


   .. py:attribute:: EFX1_LEVEL
      :value: (1, 0, 127, 0, 127, 'Sets the level of the effect.')



   .. py:attribute:: EFX1_DELAY_SEND_LEVEL
      :value: (2, 0, 127, 0, 127, 'Depth of delay applied to the sound from effect 1.')



   .. py:attribute:: EFX1_REVERB_SEND_LEVEL
      :value: (3, 0, 127, 0, 127, 'Depth of reverb applied to the sound from effect 1.')



   .. py:attribute:: EFX1_OUTPUT_ASSIGN


   .. py:attribute:: EFX1_PARAM_1
      :value: (17, 32768, 32895, 0, 127, 'Sets the first parameter of the effect.')



   .. py:attribute:: EFX1_PARAM_1_BITCRUSHER_LEVEL
      :value: (17, 32768, 32895, 0, 127, 'Sets the output volume.')



   .. py:attribute:: EFX1_PARAM_1_FUZZ_LEVEL
      :value: (17, 32767, 32894, 0, 127, 'Adjusts the volume.')



   .. py:attribute:: EFX1_PARAM_1_DISTORTION_LEVEL
      :value: (17, 32768, 32895, 0, 127, 'Adjusts the volume.')



   .. py:attribute:: EFX1_PARAM_1_COMPRESSOR_THRESHOLD
      :value: (17, 32768, 32895, 0, 127, 'Level at which compression is applied')



   .. py:attribute:: EFX1_PARAM_2
      :value: (21, 32767, 32894, 0, 127, 'Sets the second parameter of the effect.')



   .. py:attribute:: EFX1_PARAM_2_BITCRUSHER_RATE
      :value: (21, 32767, 32894, 0, 127, 'Adjusts the sampling frequency.')



   .. py:attribute:: EFX1_PARAM_2_FUZZ_DRIVE
      :value: (21, 32767, 32894, 0, 127, 'Sets the second parameter of the effect.')



   .. py:attribute:: EFX1_PARAM_2_DISTORTION_DRIVE
      :value: (21, 32768, 32895, 0, 127, 'Adjusts the depth of distortion')



   .. py:attribute:: EFX1_PARAM_2_COMPRESSOR_RATIO
      :value: (21, 32768, 32887, 0, 19, 'Compression ratio')



   .. py:attribute:: EFX1_PARAM_3
      :value: (25, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_3_BITCRUSHER_DEPTH
      :value: (25, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_3_DISTORTION_TYPE
      :value: (25, 32822, 32827, 0, 5)



   .. py:attribute:: EFX1_PARAM_3_FUZZ_TYPE
      :value: (25, 32822, 32827, 0, 5)



   .. py:attribute:: EFX1_PARAM_3_COMPRESSOR_ATTACK
      :value: (25, 32822, 32854, 0, 32, 'Attack time (ms)')



   .. py:attribute:: EFX1_PARAM_4
      :value: (29, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_4_BITCRUSHER_FILTER
      :value: (29, 32768, 32895, 0, 127, 'Adjusts the filter depth')



   .. py:attribute:: EFX1_PARAM_4_COMPRESSOR_RELEASE
      :value: (29, 32822, 32854, 0, 32, 'Release time (ms)')



   .. py:attribute:: EFX1_PARAM_5
      :value: (33, 32768, 32895, 0, 127, '')



   .. py:attribute:: EFX1_PARAM_5_COMPRESSOR_LEVEL
      :value: (33, 32768, 32895, 0, 127, 'Adjusts the volume.')



   .. py:attribute:: EFX1_PARAM_6
      :value: (37, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_7
      :value: (41, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_7_COMPRESSOR_SIDE_LEVEL
      :value: (41, 32768, 32895, 0, 127, 'Side level which to be applied')



   .. py:attribute:: EFX1_PARAM_8
      :value: (45, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_8_COMPRESSOR_SIDE_NOTE
      :value: (45, 32768, 32895, 0, 127, 'Side note to be applied')



   .. py:attribute:: EFX1_PARAM_9
      :value: (49, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_9_COMPRESSOR_SIDE_TIME
      :value: (49, 32768, 32895, 0, 127, 'Side time to be applied')



   .. py:attribute:: EFX1_PARAM_10
      :value: (53, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_10_COMPRESSOR_SIDE_RELEASE
      :value: (53, 32768, 32895, 0, 127, 'Side release to be applied')



   .. py:attribute:: EFX1_PARAM_11
      :value: (57, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_12
      :value: (61, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_13
      :value: (65, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_14
      :value: (69, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_15
      :value: (73, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_16
      :value: (77, 32768, 32895, 0, 127)



   .. py:attribute:: EFX1_PARAM_32
      :value: (29, 32768, 32895, 0, 127, 'Sets the third parameter of the effect.')



   .. py:attribute:: EFX1_PARAM_32_DISTORTION_PRESENCE
      :value: (29, 32768, 32895, 0, 127, 'Adjusts the character of the ultra-high-frequency region')



   .. py:attribute:: EFX1_PARAM_32_FUZZ_PRESENCE
      :value: (29, 32768, 32895, 0, 127, 'Adjusts the character of the ultra-high-frequency region')



   .. py:method:: get_address_by_name(name: str) -> Optional[int]
      :classmethod:


      Look up an effect parameter address by its name
      :param name: str The parameter name
      :return: Optional[int] The address



   .. py:method:: get_by_address(address: int) -> Optional[object]
      :classmethod:


      Look up an effect parameter by its address
      :param address: int The address
      :return: Optional[object] The parameter



   .. py:method:: get_by_name(name: str) -> Optional[object]
      :classmethod:


      Look up an effect parameter by its name
      :param name: str The parameter name
      :return: Optional[object] The parameter



   .. py:method:: convert_to_midi(display_value: int) -> int

      Convert from display value to MIDI value
      :param display_value: int The display value
      :return: int The MIDI value



   .. py:attribute:: convert_from_display


   .. py:method:: get_midi_value(param_name: str, value: int) -> Optional[int]
      :staticmethod:


      Get the MIDI value for address parameter by name and value.

      :param param_name: str The parameter name
      :param value: int The value
      :return: Optional[int] The MIDI value



   .. py:method:: get_common_param_by_name(name: str) -> Optional[jdxi_editor.midi.data.parameter.effects.common.AddressParameterEffectCommon]
      :classmethod:


      Look up an effect parameter's category using address dictionary mapping

      :param name: str The parameter name
      :return: Optional[AddressParameterEffectCommon] The category



.. py:class:: AddressParameterEffect2(address: int, min_val: int, max_val: int, display_min: Optional[int] = None, display_max: Optional[int] = None, tooltip: Optional[str] = None)

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Effect parameters with address and value range


   .. py:attribute:: display_min
      :value: None



   .. py:attribute:: display_max
      :value: None



   .. py:attribute:: tooltip
      :value: None



   .. py:method:: get_display_value() -> Tuple[int, int]

      Get the display range for the parameter

      :return: Tuple[int, int] The display range



   .. py:attribute:: EFX2_TYPE
      :value: (0, 0, 8, 0, 8)



   .. py:attribute:: EFX2_LEVEL
      :value: (1, 0, 127, 0, 127)



   .. py:attribute:: EFX2_DELAY_SEND_LEVEL
      :value: (2, 0, 127, 0, 127)



   .. py:attribute:: EFX2_REVERB_SEND_LEVEL
      :value: (3, 0, 127, 0, 127)



   .. py:attribute:: EFX2_PARAM_1
      :value: (17, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_1_FLANGER_RATE_NOTE_SWITCH
      :value: (17, 32768, 32869, 0, 1, '[Rate] / [Note] Switch')



   .. py:attribute:: EFX2_PARAM_1_PHASER_RATE_NOTE_SWITCH
      :value: (17, 32768, 32869, 0, 1, '[Rate] / [Note] Switch')



   .. py:attribute:: EFX2_PARAM_2
      :value: (21, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_2_FLANGER_RATE
      :value: (21, 32768, 32895, 0, 127, 'Frequency of modulation')



   .. py:attribute:: EFX2_PARAM_2_PHASER_RATE
      :value: (21, 32768, 32895, 0, 127, 'Frequency of modulation')



   .. py:attribute:: EFX2_PARAM_3
      :value: (25, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_3_FLANGER_NOTE
      :value: (25, 32768, 32895, 0, 127, 'Note used for modulation')



   .. py:attribute:: EFX2_PARAM_3_PHASER_NOTE
      :value: (25, 32768, 32895, 0, 127, 'Note used for modulation')



   .. py:attribute:: EFX2_PARAM_4
      :value: (29, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_4_FLANGER_DEPTH
      :value: (29, 32768, 32895, 0, 127, 'Depth of modulation')



   .. py:attribute:: EFX2_PARAM_4_PHASER_DEPTH
      :value: (29, 32768, 32895, 0, 127, 'Depth of modulation')



   .. py:attribute:: EFX2_PARAM_5
      :value: (33, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_5_FLANGER_FEEDBACK
      :value: (33, 32768, 32895, 0, 127, 'Proportion of the flanger sound that is returned to the input')



   .. py:attribute:: EFX2_PARAM_5_PHASER_CENTER_FREQ
      :value: (33, 32768, 32895, 0, 127, 'Proportion of the flanger sound that is returned to the input')



   .. py:attribute:: EFX2_PARAM_6
      :value: (37, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_6_FLANGER_MANUAL
      :value: (37, 32768, 32895, 0, 127, 'Adjusts the basic frequency from which the sound will be modulated.')



   .. py:attribute:: EFX2_PARAM_7
      :value: (41, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_7_FLANGER_DRY_WET
      :value: (41, 32768, 32895, 0, 127, 'Volume balance between the direct sound (D) and the effect sound (W)')



   .. py:attribute:: EFX2_PARAM_8
      :value: (45, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_8_FLANGER_LEVEL
      :value: (45, 32768, 32895, 0, 127, 'Output volume')



   .. py:attribute:: EFX2_PARAM_9
      :value: (49, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_10
      :value: (53, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_11
      :value: (57, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_12
      :value: (61, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_13
      :value: (65, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_14
      :value: (69, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_15
      :value: (73, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_16
      :value: (77, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_17
      :value: (81, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_18
      :value: (85, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_19
      :value: (89, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_20
      :value: (93, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_21
      :value: (97, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_22
      :value: (101, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_23
      :value: (105, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_24
      :value: (109, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_25
      :value: (113, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_32
      :value: (13, 32768, 32895, 0, 127)



   .. py:attribute:: EFX2_PARAM_32_PHASER_EFFECT_LEVEL
      :value: (13, 32768, 32895, 0, 127)



   .. py:method:: get_address_by_name(name: str) -> Optional[int]
      :classmethod:


      Look up an effect parameter address by its name
      :param name: str The parameter name
      :return: Optional[int] The address



   .. py:method:: get_by_address(address: int) -> Optional[object]
      :classmethod:


      Look up an effect parameter by its address
      :param address: int The address
      :return: Optional[object] The parameter



   .. py:method:: get_by_name(name: str) -> Optional[object]
      :classmethod:


      Look up an effect parameter by its name
      :param name: str The parameter name
      :return: Optional[object] The parameter



   .. py:method:: convert_to_midi_old(display_value: int) -> int

      Convert from display value to MIDI value
      :param display_value: int The display value
      :return: int The MIDI value



   .. py:method:: convert_to_midi(display_value: int) -> int

      Convert from display value to MIDI value
      :param display_value: int The display value
      :return: int The MIDI value



   .. py:attribute:: convert_from_display


   .. py:method:: get_midi_value(param_name: str, value: int) -> Optional[int]
      :staticmethod:


      Get the MIDI value for address parameter by name and value.

      :param param_name: str The parameter name
      :param value: int The value
      :return: Optional[int] The MIDI value



   .. py:method:: get_common_param_by_name(name: str) -> Optional[jdxi_editor.midi.data.parameter.effects.common.AddressParameterEffectCommon]
      :classmethod:


      Look up an effect parameter's category using address dictionary mapping

      :param name: str The parameter name
      :return: Optional[AddressParameterEffectCommon] The category



.. py:class:: AddressParameterDelay(address: int, min_val: int, max_val: int, display_min: Optional[int] = None, display_max: Optional[int] = None, tooltip: Optional[str] = None)

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Effect parameters with address and value range


   .. py:attribute:: display_min
      :value: None



   .. py:attribute:: display_max
      :value: None



   .. py:attribute:: tooltip
      :value: None



   .. py:method:: get_display_value() -> Tuple[int, int]

      Get the display range for the parameter

      :return: Tuple[int, int] The display range



   .. py:attribute:: DELAY_LEVEL
      :value: (1, 0, 127, 0, 127, 'Sets the level of the delay effect.')



   .. py:attribute:: DELAY_PARAM_1
      :value: (8, 32768, 32895, 0, 127, 'Sets the first parameter of the delay effect.')



   .. py:attribute:: DELAY_PARAM_2
      :value: (12, 32768, 32895, 0, 127, 'Sets the second parameter of the delay effect.')



   .. py:attribute:: DELAY_PARAM_24
      :value: (96, 32768, 32895, 0, 127, 'Sets the third parameter of the delay effect.')



   .. py:attribute:: DELAY_REVERB_SEND_LEVEL
      :value: (6, 0, 127, 0, 127, 'Depth of reverb applied to the sound from delay.')



   .. py:method:: get_address_by_name(name: str) -> Optional[int]
      :classmethod:


      Look up an effect parameter address by its name
      :param name: str The parameter name
      :return: Optional[int] The address



   .. py:method:: get_by_address(address: int) -> Optional[object]
      :classmethod:


      Look up an effect parameter by its address
      :param address: int The address
      :return: Optional[object] The parameter



   .. py:method:: get_by_name(name: str) -> Optional[object]
      :classmethod:


      Look up an effect parameter by its name
      :param name: str The parameter name
      :return: Optional[object] The parameter



   .. py:method:: convert_to_midi(display_value: int) -> int

      Convert from display value to MIDI value
      :param display_value: int The display value
      :return: int The MIDI value



   .. py:attribute:: convert_from_display


   .. py:method:: get_midi_value(param_name: str, value: int) -> Optional[int]
      :staticmethod:


      Get the MIDI value for address parameter by name and value.

      :param param_name: str The parameter name
      :param value: int The value
      :return: Optional[int] The MIDI value



   .. py:method:: get_common_param_by_name(name: str) -> Optional[jdxi_editor.midi.data.parameter.effects.common.AddressParameterEffectCommon]
      :classmethod:


      Look up an effect parameter's category using address dictionary mapping

      :param name: str The parameter name
      :return: Optional[AddressParameterEffectCommon] The category



.. py:class:: AddressParameterReverb(address: int, min_val: int, max_val: int, display_min: Optional[int] = None, display_max: Optional[int] = None, tooltip: Optional[str] = None)

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Effect parameters with address and value range


   .. py:attribute:: display_min
      :value: None



   .. py:attribute:: display_max
      :value: None



   .. py:attribute:: tooltip
      :value: None



   .. py:method:: get_display_value() -> Tuple[int, int]

      Get the display range for the parameter

      :return: Tuple[int, int] The display range



   .. py:attribute:: REVERB_LEVEL
      :value: (3, 0, 127, 0, 127, 'Sets the level of the reverb effect.')



   .. py:attribute:: REVERB_PARAM_1
      :value: (7, 32768, 32895, 0, 127, 'Sets the first parameter of the reverb effect.')



   .. py:attribute:: REVERB_PARAM_2
      :value: (11, 32768, 32895, 0, 127, 'Sets the second parameter of the reverb effect.')



   .. py:attribute:: REVERB_PARAM_24
      :value: (95, 32768, 32895, 0, 127, 'Sets the third parameter of the reverb effect.')



   .. py:method:: get_address_by_name(name: str) -> Optional[int]
      :classmethod:


      Look up an effect parameter address by its name
      :param name: str The parameter name
      :return: Optional[int] The address



   .. py:method:: get_by_address(address: int) -> Optional[object]
      :classmethod:


      Look up an effect parameter by its address
      :param address: int The address
      :return: Optional[object] The parameter



   .. py:method:: get_by_name(name: str) -> Optional[object]
      :classmethod:


      Look up an effect parameter by its name
      :param name: str The parameter name
      :return: Optional[object] The parameter



   .. py:method:: convert_to_midi(display_value: int) -> int

      Convert from display value to MIDI value
      :param display_value: int The display value
      :return: int The MIDI value



   .. py:attribute:: convert_from_display


   .. py:method:: get_midi_value(param_name: str, value: int) -> Optional[int]
      :staticmethod:


      Get the MIDI value for address parameter by name and value.

      :param param_name: str The parameter name
      :param value: int The value
      :return: Optional[int] The MIDI value



   .. py:method:: get_common_param_by_name(name: str) -> Optional[jdxi_editor.midi.data.parameter.effects.common.AddressParameterEffectCommon]
      :classmethod:


      Look up an effect parameter's category using address dictionary mapping

      :param name: str The parameter name
      :return: Optional[AddressParameterEffectCommon] The category



