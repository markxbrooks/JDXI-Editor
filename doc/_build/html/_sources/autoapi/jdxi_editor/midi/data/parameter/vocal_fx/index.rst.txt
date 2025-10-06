jdxi_editor.midi.data.parameter.vocal_fx
========================================

.. py:module:: jdxi_editor.midi.data.parameter.vocal_fx

.. autoapi-nested-parse::

   Module: VocalFXParameter
   ========================

   This module defines the VocalFXParameter class, which represents various vocal effects parameters
   in a synthesizer. These parameters control different aspects of vocal processing, including
   level, pan, delay/reverb send levels, auto pitch settings, vocoder effects, and more.

   The class provides methods to:

   - Initialize vocal FX parameters with a given address, range, and optional display range.
   - Validate and convert parameter values to the MIDI range (0-127).
   - Define a variety of vocal effects parameters with specific ranges, including:
     - Level, pan, delay/reverb send levels, and output assignment
     - Auto pitch settings such as switch, type, scale, key, note, gender, octave, and balance
     - Vocoder parameters such as switch, envelope type, level, mic sensitivity, and mix level

   The class also offers conversion utilities:
   - Convert between MIDI values and display values.
   - Handle special bipolar cases (e.g., pan, auto pitch gender).
   - Retrieve the display value range or MIDI value range for parameters.

   Parameters include:
   - Level, pan, delay and reverb send levels, output assignment, and auto pitch settings
   - Vocoder settings for on/off, envelope, level, mic sensitivity, synth level, and mic mix
   - Auto pitch gender, octave, balance, and key/note configurations

   The class also includes utility functions to get a parameter's address, range, display range,
   and to convert between MIDI values and display values.

   Usage example:
       # Initialize a VocalFXParameter object for the LEVEL parameter
       param = VocalFXParameter(address=0x00, min_val=0, max_val=127)

       # Access display range values
       print(param.display_min)  # Output: 0
       print(param.display_max)  # Output: 127

       # Validate a MIDI value
       midi_value = param.convert_to_midi(64)



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.vocal_fx.AddressParameterVocalFX


Module Contents
---------------

.. py:class:: AddressParameterVocalFX(address: int, min_val: int, max_val: int, display_min: Optional[int] = None, display_max: Optional[int] = None, tooltip: Optional[str] = None)

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Vocal FX parameters


   .. py:attribute:: display_min
      :value: None



   .. py:attribute:: display_max
      :value: None



   .. py:attribute:: tooltip
      :value: None



   .. py:attribute:: LEVEL
      :value: (0, 0, 127, 0, 127, 'Sets the level of the vocal FX.')



   .. py:attribute:: PAN


   .. py:attribute:: DELAY_SEND_LEVEL
      :value: (2, 0, 127, 0, 127, 'Sets the level of the delay send.')



   .. py:attribute:: REVERB_SEND_LEVEL
      :value: (3, 0, 127, 0, 127, 'Sets the level of the reverb send.')



   .. py:attribute:: OUTPUT_ASSIGN
      :value: (4, 0, 4, 0, 4, 'Sets the output assignment.')



   .. py:attribute:: AUTO_PITCH_SWITCH
      :value: (5, 0, 1, 0, 1, 'Sets the auto note on/off.')



   .. py:attribute:: AUTO_PITCH_TYPE
      :value: (6, 0, 3, 0, 3, 'Sets the auto pitch preset_type.')



   .. py:attribute:: AUTO_PITCH_SCALE
      :value: (7, 0, 1, 0, 1, 'Sets the auto pitch scale.')



   .. py:attribute:: AUTO_PITCH_KEY
      :value: (8, 0, 23, 0, 23, 'Sets the auto pitch key.')



   .. py:attribute:: AUTO_PITCH_NOTE
      :value: (9, 0, 11, 0, 11, 'Sets the auto pitch note.')



   .. py:attribute:: AUTO_PITCH_GENDER


   .. py:attribute:: AUTO_PITCH_OCTAVE


   .. py:attribute:: AUTO_PITCH_BALANCE
      :value: (12, 0, 100, 0, 100, 'Sets the auto pitch balance.')



   .. py:attribute:: VOCODER_SWITCH
      :value: (13, 0, 1, 0, 1, 'Sets the vocoder on/off.')



   .. py:attribute:: VOCODER_ENVELOPE
      :value: (14, 0, 2, 0, 2, 'Sets the vocoder envelope preset_type.')



   .. py:attribute:: VOCODER_LEVEL
      :value: (15, 0, 127, 0, 127, 'Sets the vocoder level.')



   .. py:attribute:: VOCODER_MIC_SENS
      :value: (16, 0, 127, 0, 127, 'Sets the vocoder mic sensitivity.')



   .. py:attribute:: VOCODER_SYNTH_LEVEL
      :value: (17, 0, 127, 0, 127, 'Sets the vocoder synth level.')



   .. py:attribute:: VOCODER_MIC_MIX
      :value: (18, 0, 127, 0, 127, 'Sets the vocoder mic mix level.')



   .. py:attribute:: VOCODER_MIC_HPF
      :value: (19, 0, 13, 0, 13, 'Sets the vocoder mic HPF freq.')



   .. py:method:: validate_value(value: int) -> int

      Validate and convert parameter value to MIDI range (0-127)



   .. py:method:: get_name_by_address(address: int) -> Optional[str]
      :staticmethod:


      Return the parameter name for address given address.
      :param address: int The address
      :return: Optional[str] The parameter name



   .. py:property:: display_name
      :type: str


      Get display name for the parameter


   .. py:property:: is_switch
      :type: bool


      Returns True if parameter is address binary/enum switch


   .. py:method:: get_address(param_name: str) -> Optional[int]
      :staticmethod:


      Get the address of address parameter by name.

      :param param_name: str The parameter name
      :return: Optional[int] The address



   .. py:method:: get_range(param_name: str) -> Tuple[int, int]
      :staticmethod:


      Get the value range (min, max) of address parameter by name.

      :param param_name: str The parameter name
      :return: Tuple[int, int] The value range



   .. py:method:: get_display_range(param_name: str) -> Tuple[int, int]
      :staticmethod:


      Get the display value range (min, max) of address parameter by name.

      :param param_name: str The parameter name
      :return: Tuple[int, int] The display value range



   .. py:method:: get_display_value() -> Tuple[int, int]

      Get the display value range (min, max) for the parameter

      :return: Tuple[int, int] The display value range



   .. py:method:: convert_from_display(display_value: int) -> int

      Convert from display value to MIDI value (0-127)

      :param display_value: int The display value
      :return: int The MIDI value



   .. py:method:: convert_to_display(value: int, min_val: int, max_val: int, display_min: int, display_max: int) -> int
      :staticmethod:


      Convert address value to address display value within address range.

      :param value: int The address value
      :param min_val: int The address minimum value
      :param max_val: int The address maximum value
      :param display_min: int The display minimum value
      :param display_max: int The display maximum value
      :return: int The display value



   .. py:method:: convert_to_midi(display_value: int) -> int

      Convert from display value to MIDI value

      :param display_value: int The display value
      :return: int The MIDI value



   .. py:method:: convert_from_midi(midi_value: int) -> int

      Convert from MIDI value to display value

      :param midi_value: int The MIDI value
      :return: int The display value



   .. py:method:: get_display_value_by_name(param_name: str, value: int) -> int
      :staticmethod:


      Get the display value for address parameter by name and value.

      :param param_name: str The parameter name
      :param value: int The value
      :return: int The display value



   .. py:method:: get_midi_range(param_name: str) -> Tuple[int, int]
      :staticmethod:


      Get the MIDI value range (min, max) of address parameter by name.

      :param param_name: str The parameter name
      :return: Tuple[int, int] The MIDI value range



   .. py:method:: get_midi_value(param_name: str, value: int) -> Optional[int]
      :staticmethod:


      Get the MIDI value for address parameter by name and value.

      :param param_name: str The parameter name
      :param value: int The value
      :return: Optional[int] The MIDI value



