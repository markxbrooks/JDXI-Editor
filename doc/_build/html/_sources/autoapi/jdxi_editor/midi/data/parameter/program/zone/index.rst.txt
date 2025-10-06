jdxi_editor.midi.data.parameter.program.zone
============================================

.. py:module:: jdxi_editor.midi.data.parameter.program.zone

.. autoapi-nested-parse::

   ProgramZoneParameter
   ====================

   Defines the ProgramZoneParameter class for managing common program-level
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

   jdxi_editor.midi.data.parameter.program.zone.AddressParameterProgramZone


Module Contents
---------------

.. py:class:: AddressParameterProgramZone(address: int, min_val: Optional[int] = None, max_val: Optional[int] = None, display_min: Optional[int] = None, display_max: Optional[int] = None, partial_number: Optional[int] = 0)

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Program Common parameters


   .. py:attribute:: display_min
      :value: None



   .. py:attribute:: display_max
      :value: None



   .. py:attribute:: partial_number
      :value: 0



   .. py:attribute:: ARPEGGIO_SWITCH
      :value: (3, 0, 1, 0, 1)



   .. py:attribute:: ZONAL_OCTAVE_SHIFT


   .. py:method:: get_display_value() -> Tuple[int, int]

      Get the display value range (min, max) for the parameter

      :return: Tuple[int, int] The display value range



   .. py:method:: get_address_for_partial(partial_number: int = 0) -> Tuple[int, int]

      Get parameter area and address adjusted for partial number.

      :param partial_number: int The partial number
      :return: Tuple[int, int] The parameter area and address



   .. py:property:: is_switch
      :type: bool


      Returns True if parameter is address binary/enum switch

      :return: bool True if parameter is address binary/enum switch


   .. py:method:: get_switch_text(value: int) -> str

      Get display text for switch values

      :param value: int The value
      :return: str The display text



   .. py:method:: validate_value(value: int) -> int

      Validate and convert parameter value

      :param value: int The value
      :return: int The validated value



   .. py:method:: set_partial_number(partial_number: int) -> Optional[int]

      Returns the partial number (1-4) if this is address partial parameter, None otherwise

      :param partial_number: int The partial number
      :return: Optional[int] The partial number



   .. py:method:: get_partial_number() -> Optional[int]

      Returns the partial number (1-4) if this is address partial parameter, None otherwise

      :return: Optional[int] The partial number



   .. py:method:: get_by_name(param_name: str) -> Optional[object]
      :staticmethod:


      Get the Parameter by name.

      :param param_name: str The parameter name
      :return: Optional[object] The parameter
      Return the parameter member by name, or None if not found



