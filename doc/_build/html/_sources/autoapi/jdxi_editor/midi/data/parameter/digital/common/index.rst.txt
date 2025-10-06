jdxi_editor.midi.data.parameter.digital.common
==============================================

.. py:module:: jdxi_editor.midi.data.parameter.digital.common

.. autoapi-nested-parse::

   Module: AddressParameterDigitalCommon

   This module defines the AddressParameterDigitalCommon class, which represents common parameters
   for Digital/SuperNATURAL synth tones. These parameters are shared across all partials and
   define various synthesizer settings, such as tone name, tone level, performance parameters,
   partial switches, and additional effects.

   The class provides methods to:

   - Retrieve a human-readable display name for each parameter.
   - Identify if a parameter is a switch (binary or enum).
   - Get appropriate display text for switch values.
   - Validate and convert parameter values within their defined range.
   - Retrieve the partial number (1-3) for partial-specific parameters.
   - Get a parameter by its name.

   Parameters include:
   - Tone name parameters (12 ASCII characters)
   - Tone level
   - Performance parameters (e.g., Portamento switch, Mono switch)
   - Partial switches (e.g., Partial 1 switch, Partial 2 switch)
   - Additional effect parameters (e.g., Ring Mod, Unison, Analog Feel)

   Usage example:
       # Initialize a parameter object
       param = AddressParameterDigitalCommon(address=0x00, min_val=0, max_val=127)

       # Get the display name for the parameter
       print(param.display_name)

       # Validate and convert a value for the parameter
       valid_value = param.validate_value(64)

       # Get the switch text for a given value
       switch_text = param.get_switch_text(1)



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.digital.common.AddressParameterDigitalCommon


Module Contents
---------------

.. py:class:: AddressParameterDigitalCommon(address: int, min_val: int, max_val: int, tooltip: str = '')

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Common parameters for Digital/SuperNATURAL synth tones.
   These parameters are shared across all partials.


   .. py:attribute:: address


   .. py:attribute:: min_val


   .. py:attribute:: max_val


   .. py:attribute:: tooltip
      :value: ''



   .. py:attribute:: TONE_NAME_1
      :value: (0, 32, 127)



   .. py:attribute:: TONE_NAME_2
      :value: (1, 32, 127)



   .. py:attribute:: TONE_NAME_3
      :value: (2, 32, 127)



   .. py:attribute:: TONE_NAME_4
      :value: (3, 32, 127)



   .. py:attribute:: TONE_NAME_5
      :value: (4, 32, 127)



   .. py:attribute:: TONE_NAME_6
      :value: (5, 32, 127)



   .. py:attribute:: TONE_NAME_7
      :value: (6, 32, 127)



   .. py:attribute:: TONE_NAME_8
      :value: (7, 32, 127)



   .. py:attribute:: TONE_NAME_9
      :value: (8, 32, 127)



   .. py:attribute:: TONE_NAME_10
      :value: (9, 32, 127)



   .. py:attribute:: TONE_NAME_11
      :value: (10, 32, 127)



   .. py:attribute:: TONE_NAME_12
      :value: (11, 32, 127)



   .. py:attribute:: TONE_LEVEL
      :value: (12, 0, 127, 'Adjusts the overall volume of the tone')



   .. py:attribute:: PORTAMENTO_SWITCH
      :value: (18, 0, 1, 'Specifies whether the portamento effect will be applied (ON) or not applied (OFF)')



   .. py:attribute:: PORTAMENTO_TIME


   .. py:attribute:: MONO_SWITCH
      :value: (20, 0, 1, 'Specifies whether notes will sound polyphonically (POLY) or monophonically (MONO)')



   .. py:attribute:: OCTAVE_SHIFT
      :value: (21, 61, 67, 'Specifies the octave of the tone')



   .. py:attribute:: PITCH_BEND_UP


   .. py:attribute:: PITCH_BEND_DOWN


   .. py:attribute:: PARTIAL1_SWITCH
      :value: (25, 0, 1, 'Partial 1 turn on (OFF, ON)')



   .. py:attribute:: PARTIAL1_SELECT
      :value: (26, 0, 1, 'Partial 1 select and edit (OFF, ON)')



   .. py:attribute:: PARTIAL2_SWITCH
      :value: (27, 0, 1, 'Partial 2 turn on (OFF, ON)')



   .. py:attribute:: PARTIAL2_SELECT
      :value: (28, 0, 1, 'Partial 2 select and edit (OFF, ON)')



   .. py:attribute:: PARTIAL3_SWITCH
      :value: (29, 0, 1, 'Partial 1 turn on (OFF, ON)')



   .. py:attribute:: PARTIAL3_SELECT
      :value: (30, 0, 1, 'Partial 3 select and edit (OFF, ON)')



   .. py:attribute:: RING_SWITCH


   .. py:attribute:: UNISON_SWITCH


   .. py:attribute:: PORTAMENTO_MODE


   .. py:attribute:: LEGATO_SWITCH


   .. py:attribute:: ANALOG_FEEL


   .. py:attribute:: WAVE_SHAPE


   .. py:attribute:: TONE_CATEGORY
      :value: (54, 0, 127, 'Selects the tone’s category.')



   .. py:attribute:: UNISON_SIZE


   .. py:property:: display_name
      :type: str


      Get display name for the parameter


   .. py:property:: is_switch
      :type: bool


      Returns True if parameter is address binary/enum switch


   .. py:method:: get_switch_text(value: int) -> str

      Get display text for switch values



   .. py:method:: validate_value(value: int) -> int

      Validate and convert parameter value



   .. py:method:: get_partial_number() -> Optional[int]

      Returns the partial number (1-3) if this is address partial parameter, None otherwise



   .. py:method:: get_by_name(param_name)
      :staticmethod:


      Get the Parameter by name.



   .. py:method:: get_address_for_partial(partial_number: int = 0)

      Get the address for the partial number.

      :param partial_number: int
      :return: int default area to be subclassed



