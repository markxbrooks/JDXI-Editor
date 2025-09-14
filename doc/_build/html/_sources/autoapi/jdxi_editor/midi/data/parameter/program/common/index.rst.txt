jdxi_editor.midi.data.parameter.program.common
==============================================

.. py:module:: jdxi_editor.midi.data.parameter.program.common

.. autoapi-nested-parse::

   ProgramCommonParameter
   ======================
   Defines the ProgramCommonParameter class for managing common program-level
   parameters in the JD-Xi synthesizer.

   This class provides attributes and methods for handling program-wide settings,
   such as program name, level, tempo, and vocal effects. It also includes
   methods for retrieving display values, validating parameter values, and
   handling partial-specific addressing.

   Example usage:

   # Create an instance for Program Level
   program_level = ProgramCommonParameter(*ProgramCommonParameter.PROGRAM_LEVEL)

   # Validate a value within range
   validated_value = program_level.validate_value(100)

   # Get the display name of a parameter
   display_name = program_level.display_name  # "Program Level"

   # Get display value range
   display_range = program_level.get_display_value()  # (0, 127)

   # Retrieve a parameter by name
   param = ProgramCommonParameter.get_by_name("PROGRAM_TEMPO")
   if param:
       print(param.name, param.min_val, param.max_val)

   # Get switch text representation
   switch_text = program_level.get_switch_text(1)  # "ON" or "---"



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.program.common.AddressParameterSystemCommon
   jdxi_editor.midi.data.parameter.program.common.AddressParameterProgramCommon


Module Contents
---------------

.. py:class:: AddressParameterSystemCommon(address: int, min_val: Optional[int] = None, max_val: Optional[int] = None, display_min: Optional[int] = None, display_max: Optional[int] = None, tooltip: Optional[str] = None)

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Program Common parameters


   .. py:attribute:: display_min
      :value: None



   .. py:attribute:: display_max
      :value: None



   .. py:attribute:: tooltip
      :value: None



   .. py:attribute:: MASTER_TUNE


   .. py:attribute:: MASTER_KEY_SHIFT


   .. py:attribute:: MASTER_LEVEL
      :value: (5, 0, 127, 0, 127, 'Volume of the program')



   .. py:method:: get_display_value() -> Tuple[int, int]

      Get the display value range (min, max) for the parameter



   .. py:property:: display_name
      :type: str


      Get display name for the parameter


   .. py:method:: get_address_for_partial(partial_number: int = 0) -> Tuple[int, int]

      Get parameter area and address adjusted for partial number.

      :param partial_number: int The partial number
      :return: Tuple[int, int] The address



   .. py:property:: is_switch
      :type: bool


      Returns True if parameter is address binary/enum switch


   .. py:method:: get_switch_text(value: int) -> str

      Get display text for switch values
      :param value: int The value
      :return: str The display text



   .. py:method:: validate_value(value: int) -> int

      Validate and convert parameter value
      :param value: int The value
      :return: int The validated value



   .. py:method:: get_partial_number() -> Optional[int]

      Returns the partial number (1-3) if this is address partial parameter, None otherwise



   .. py:method:: get_by_name(param_name: str) -> Optional[object]
      :staticmethod:


      Get the Parameter by name.
      :param param_name: str The parameter name
      :return: Optional[object] The parameter
      Return the parameter member by name, or None if not found



.. py:class:: AddressParameterProgramCommon(address: int, min_val: Optional[int] = None, max_val: Optional[int] = None, display_min: Optional[int] = None, display_max: Optional[int] = None, tooltip: Optional[str] = None)

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Program Common parameters


   .. py:attribute:: display_min
      :value: None



   .. py:attribute:: display_max
      :value: None



   .. py:attribute:: tooltip
      :value: None



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



   .. py:attribute:: PROGRAM_LEVEL
      :value: (16, 0, 127, 0, 127, 'Volume of the program')



   .. py:attribute:: PROGRAM_TEMPO


   .. py:attribute:: VOCAL_EFFECT
      :value: (22, 0, 2, 0, 2)



   .. py:attribute:: VOCAL_EFFECT_NUMBER
      :value: (28, 0, 20, 0, 20)



   .. py:attribute:: VOCAL_EFFECT_PART
      :value: (29, 0, 1, 0, 1)



   .. py:attribute:: AUTO_NOTE_SWITCH
      :value: (30, 0, 1, 0, 1)



   .. py:method:: get_display_value() -> Tuple[int, int]

      Get the display value range (min, max) for the parameter



   .. py:property:: display_name
      :type: str


      Get display name for the parameter


   .. py:method:: get_address_for_partial(partial_number: int = 0) -> Tuple[int, int]

      Get parameter area and address adjusted for partial number.

      :param partial_number: int The partial number
      :return: Tuple[int, int] The address



   .. py:property:: is_switch
      :type: bool


      Returns True if parameter is address binary/enum switch


   .. py:method:: get_switch_text(value: int) -> str

      Get display text for switch values
      :param value: int The value
      :return: str The display text



   .. py:method:: validate_value(value: int) -> int

      Validate and convert parameter value
      :param value: int The value
      :return: int The validated value



   .. py:method:: get_partial_number() -> Optional[int]

      Returns the partial number (1-3) if this is address partial parameter, None otherwise



   .. py:method:: get_by_name(param_name: str) -> Optional[object]
      :staticmethod:


      Get the Parameter by name.
      :param param_name: str The parameter name
      :return: Optional[object] The parameter
      Return the parameter member by name, or None if not found



