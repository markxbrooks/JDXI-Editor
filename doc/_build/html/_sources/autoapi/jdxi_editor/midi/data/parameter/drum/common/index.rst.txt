jdxi_editor.midi.data.parameter.drum.common
===========================================

.. py:module:: jdxi_editor.midi.data.parameter.drum.common

.. autoapi-nested-parse::

   This module defines the `DrumCommonParameter` class, which represents
   common parameters for drum tones in the JD-Xi synthesizer.

   These parameters are shared across all partials within a drum kit
   and include settings such as tone name, kit level, and various switches.

   Classes:
       DrumCommonParameter(SynthParameter)
           Represents common drum parameters and provides methods
           for retrieving addresses, validating values, and formatting
           switch-based parameter values.



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.drum.common.AddressParameterDrumCommon


Module Contents
---------------

.. py:class:: AddressParameterDrumCommon(address: int, min_val: int, max_val: int, tooltip: str = '')

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



   .. py:attribute:: KIT_LEVEL


   .. py:property:: display_name
      :type: str


      Get display name for the parameter


   .. py:method:: get_address_for_partial(partial_number: int = 0) -> Tuple[int, int]

      Get parameter area and address adjusted for partial number.



   .. py:property:: is_switch
      :type: bool


      Returns True if parameter is address binary/enum switch


   .. py:method:: get_switch_text(value: int) -> str

      Get display text for switch values



   .. py:method:: validate_value(value: int) -> int

      Validate and convert parameter value



   .. py:method:: get_partial_number() -> Optional[int]

      Returns the partial number (1-3) if this is address partial parameter, None otherwise



