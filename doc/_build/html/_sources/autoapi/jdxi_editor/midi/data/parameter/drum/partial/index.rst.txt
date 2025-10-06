jdxi_editor.midi.data.parameter.drum.partial
============================================

.. py:module:: jdxi_editor.midi.data.parameter.drum.partial

.. autoapi-nested-parse::

   Module for defining drum kit parameters in the Roland JD-Xi editor.

   This module provides the `DrumPartialParameter` class, which extends `SynthParameter`
   to define the addresses, value ranges, and characteristics of drum partial parameters.
   It includes various attributes representing different drum-related parameters, such as
   tuning, level, panning, and effects settings.

   Classes:
       DrumPartialParameter -- Represents a drum partial parameter with its address,
                               value range, and optional display range.

   .. attribute:: DRUM_GROUP_MAP -- Mapping of drum groups.

      

   .. attribute:: DRUM_ADDRESS_MAP -- Mapping of parameter names to MIDI addresses.

      

   Example usage:
       drum_param = DrumPartialParameter(0x0F, 0, 127)
       print(drum_param.address)  # Output: 0x0F
       print(drum_param.min_val)  # Output: 0
       print(drum_param.max_val)  # Output: 127



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.drum.partial.AddressParameterDrumPartial


Module Contents
---------------

.. py:class:: AddressParameterDrumPartial(address: int, min_val: int, max_val: int, display_min: Optional[int] = None, display_max: Optional[int] = None, tooltip: Optional[str] = '')

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Drum kit parameters with their addresses and value ranges


   .. py:attribute:: display_min
      :value: None



   .. py:attribute:: display_max
      :value: None



   .. py:attribute:: tooltip
      :value: ''



   .. py:attribute:: bipolar_parameters
      :value: ['PARTIAL_FINE_TUNE', 'PITCH_ENV_DEPTH', 'PARTIAL_PAN', 'PARTIAL_ALTERNATE_PAN_DEPTH',...



   .. py:attribute:: CONVERSION_OFFSETS


   .. py:attribute:: PARTIAL_NAME_1
      :value: (0, 32, 127)



   .. py:attribute:: PARTIAL_NAME_2
      :value: (1, 32, 127)



   .. py:attribute:: PARTIAL_NAME_3
      :value: (2, 32, 127)



   .. py:attribute:: PARTIAL_NAME_4
      :value: (3, 32, 127)



   .. py:attribute:: PARTIAL_NAME_5
      :value: (4, 32, 127)



   .. py:attribute:: PARTIAL_NAME_6
      :value: (5, 32, 127)



   .. py:attribute:: PARTIAL_NAME_7
      :value: (6, 32, 127)



   .. py:attribute:: PARTIAL_NAME_8
      :value: (7, 32, 127)



   .. py:attribute:: PARTIAL_NAME_9
      :value: (8, 32, 127)



   .. py:attribute:: PARTIAL_NAME_10
      :value: (9, 32, 127)



   .. py:attribute:: PARTIAL_NAME_11
      :value: (10, 32, 127)



   .. py:attribute:: PARTIAL_NAME_12
      :value: (11, 32, 127)



   .. py:attribute:: ASSIGN_TYPE


   .. py:attribute:: MUTE_GROUP


   .. py:attribute:: PARTIAL_LEVEL


   .. py:attribute:: PARTIAL_COARSE_TUNE


   .. py:attribute:: PARTIAL_FINE_TUNE


   .. py:attribute:: PARTIAL_RANDOM_PITCH_DEPTH


   .. py:attribute:: PARTIAL_PAN


   .. py:attribute:: PARTIAL_RANDOM_PAN_DEPTH


   .. py:attribute:: PARTIAL_ALTERNATE_PAN_DEPTH


   .. py:attribute:: PARTIAL_ENV_MODE


   .. py:attribute:: PARTIAL_OUTPUT_LEVEL


   .. py:attribute:: PARTIAL_CHORUS_SEND_LEVEL
      :value: (25, 0, 127, 0, 127, 'Specifies the level of the signal sent to the chorus for each partial.')



   .. py:attribute:: PARTIAL_REVERB_SEND_LEVEL
      :value: (26, 0, 127, 0, 127, 'Specifies the level of the signal sent to the reverb for each partial.')



   .. py:attribute:: PARTIAL_OUTPUT_ASSIGN
      :value: (27, 0, 4, 0, 4, 'Specifies how the sound of each partial will be output. (EFX1, EFX2, DLY, REV, DIR)')



   .. py:attribute:: PARTIAL_PITCH_BEND_RANGE


   .. py:attribute:: PARTIAL_RECEIVE_EXPRESSION


   .. py:attribute:: PARTIAL_RECEIVE_HOLD_1


   .. py:attribute:: WMT_VELOCITY_CONTROL


   .. py:attribute:: WMT1_WAVE_SWITCH


   .. py:attribute:: WMT1_WAVE_GROUP_TYPE
      :value: (34, 0, 0, 0, 0, 'Only one preset_type')



   .. py:attribute:: WMT1_WAVE_GROUP_ID
      :value: (35, 0, 16384, 0, 16384, 'OFF, 1 - 16384')



   .. py:attribute:: WMT1_WAVE_NUMBER_L


   .. py:attribute:: WMT1_WAVE_NUMBER_R


   .. py:attribute:: WMT1_WAVE_GAIN


   .. py:attribute:: WMT1_WAVE_FXM_SWITCH
      :value: (48, 0, 1, 0, 1, 'OFF, ON')



   .. py:attribute:: WMT1_WAVE_FXM_COLOR


   .. py:attribute:: WMT1_WAVE_FXM_DEPTH


   .. py:attribute:: WMT1_WAVE_TEMPO_SYNC


   .. py:attribute:: WMT1_WAVE_COARSE_TUNE


   .. py:attribute:: WMT1_WAVE_FINE_TUNE


   .. py:attribute:: WMT1_WAVE_PAN


   .. py:attribute:: WMT1_WAVE_RANDOM_PAN_SWITCH


   .. py:attribute:: WMT1_WAVE_ALTERNATE_PAN_SWITCH


   .. py:attribute:: WMT1_WAVE_LEVEL


   .. py:attribute:: WMT1_VELOCITY_RANGE_LOWER


   .. py:attribute:: WMT1_VELOCITY_RANGE_UPPER


   .. py:attribute:: WMT1_VELOCITY_FADE_WIDTH_LOWER


   .. py:attribute:: WMT1_VELOCITY_FADE_WIDTH_UPPER


   .. py:attribute:: WMT2_WAVE_SWITCH


   .. py:attribute:: WMT2_WAVE_GROUP_TYPE


   .. py:attribute:: WMT2_WAVE_GROUP_ID


   .. py:attribute:: WMT2_WAVE_NUMBER_L


   .. py:attribute:: WMT2_WAVE_NUMBER_R


   .. py:attribute:: WMT2_WAVE_GAIN


   .. py:attribute:: WMT2_WAVE_FXM_SWITCH
      :value: (77, 0, 1, 0, 1, 'Frequency Cross-Modulation (FXM),OFF, ON')



   .. py:attribute:: WMT2_WAVE_FXM_COLOR


   .. py:attribute:: WMT2_WAVE_FXM_DEPTH


   .. py:attribute:: WMT2_WAVE_TEMPO_SYNC


   .. py:attribute:: WMT2_WAVE_COARSE_TUNE


   .. py:attribute:: WMT2_WAVE_FINE_TUNE


   .. py:attribute:: WMT2_WAVE_PAN


   .. py:attribute:: WMT2_WAVE_RANDOM_PAN_SWITCH


   .. py:attribute:: WMT2_WAVE_ALTERNATE_PAN_SWITCH


   .. py:attribute:: WMT2_WAVE_LEVEL


   .. py:attribute:: WMT2_VELOCITY_RANGE_LOWER


   .. py:attribute:: WMT2_VELOCITY_RANGE_UPPER


   .. py:attribute:: WMT2_VELOCITY_FADE_WIDTH_LOWER


   .. py:attribute:: WMT2_VELOCITY_FADE_WIDTH_UPPER


   .. py:attribute:: WMT3_WAVE_SWITCH


   .. py:attribute:: WMT3_WAVE_GROUP_TYPE


   .. py:attribute:: WMT3_WAVE_GROUP_ID


   .. py:attribute:: WMT3_WAVE_NUMBER_L


   .. py:attribute:: WMT3_WAVE_NUMBER_R


   .. py:attribute:: WMT3_WAVE_GAIN


   .. py:attribute:: WMT3_WAVE_FXM_SWITCH
      :value: (106, 0, 1, 0, 1, 'Frequency Cross-Modulation (FXM),OFF, ON')



   .. py:attribute:: WMT3_WAVE_FXM_COLOR


   .. py:attribute:: WMT3_WAVE_FXM_DEPTH


   .. py:attribute:: WMT3_WAVE_TEMPO_SYNC


   .. py:attribute:: WMT3_WAVE_COARSE_TUNE


   .. py:attribute:: WMT3_WAVE_FINE_TUNE


   .. py:attribute:: WMT3_WAVE_PAN


   .. py:attribute:: WMT3_WAVE_RANDOM_PAN_SWITCH


   .. py:attribute:: WMT3_WAVE_ALTERNATE_PAN_SWITCH


   .. py:attribute:: WMT3_WAVE_LEVEL


   .. py:attribute:: WMT3_VELOCITY_RANGE_LOWER


   .. py:attribute:: WMT3_VELOCITY_RANGE_UPPER


   .. py:attribute:: WMT3_VELOCITY_FADE_WIDTH_LOWER


   .. py:attribute:: WMT3_VELOCITY_FADE_WIDTH_UPPER


   .. py:attribute:: WMT4_WAVE_SWITCH


   .. py:attribute:: WMT4_WAVE_GROUP_TYPE


   .. py:attribute:: WMT4_WAVE_GROUP_ID


   .. py:attribute:: WMT4_WAVE_NUMBER_L


   .. py:attribute:: WMT4_WAVE_NUMBER_R


   .. py:attribute:: WMT4_WAVE_GAIN


   .. py:attribute:: WMT4_WAVE_FXM_SWITCH


   .. py:attribute:: WMT4_WAVE_FXM_COLOR


   .. py:attribute:: WMT4_WAVE_FXM_DEPTH


   .. py:attribute:: WMT4_WAVE_TEMPO_SYNC


   .. py:attribute:: WMT4_WAVE_COARSE_TUNE


   .. py:attribute:: WMT4_WAVE_FINE_TUNE


   .. py:attribute:: WMT4_WAVE_PAN


   .. py:attribute:: WMT4_WAVE_RANDOM_PAN_SWITCH


   .. py:attribute:: WMT4_WAVE_ALTERNATE_PAN_SWITCH


   .. py:attribute:: WMT4_WAVE_LEVEL


   .. py:attribute:: WMT4_VELOCITY_RANGE_LOWER


   .. py:attribute:: WMT4_VELOCITY_RANGE_UPPER


   .. py:attribute:: WMT4_VELOCITY_FADE_WIDTH_LOWER


   .. py:attribute:: WMT4_VELOCITY_FADE_WIDTH_UPPER


   .. py:attribute:: PITCH_ENV_DEPTH


   .. py:attribute:: PITCH_ENV_VELOCITY_SENS


   .. py:attribute:: PITCH_ENV_TIME_1_VELOCITY_SENS


   .. py:attribute:: PITCH_ENV_TIME_4_VELOCITY_SENS


   .. py:attribute:: PITCH_ENV_TIME_1


   .. py:attribute:: PITCH_ENV_TIME_2


   .. py:attribute:: PITCH_ENV_TIME_3


   .. py:attribute:: PITCH_ENV_TIME_4


   .. py:attribute:: PITCH_ENV_LEVEL_0


   .. py:attribute:: PITCH_ENV_LEVEL_1


   .. py:attribute:: PITCH_ENV_LEVEL_2


   .. py:attribute:: PITCH_ENV_LEVEL_3


   .. py:attribute:: PITCH_ENV_LEVEL_4


   .. py:attribute:: TVF_FILTER_TYPE


   .. py:attribute:: TVF_CUTOFF_FREQUENCY


   .. py:attribute:: TVF_CUTOFF_VELOCITY_CURVE


   .. py:attribute:: TVF_CUTOFF_VELOCITY_SENS


   .. py:attribute:: TVF_RESONANCE
      :value: (294, 0, 127, 0, 127, 'Sets the resonance of the filter. Higher settings result in a more...



   .. py:attribute:: TVF_RESONANCE_VELOCITY_SENS


   .. py:attribute:: TVF_ENV_DEPTH


   .. py:attribute:: TVF_ENV_VELOCITY_CURVE_TYPE


   .. py:attribute:: TVF_ENV_VELOCITY_SENS


   .. py:attribute:: TVF_ENV_TIME_1_VELOCITY_SENS


   .. py:attribute:: TVF_ENV_TIME_4_VELOCITY_SENS


   .. py:attribute:: TVF_ENV_TIME_1


   .. py:attribute:: TVF_ENV_TIME_2


   .. py:attribute:: TVF_ENV_TIME_3


   .. py:attribute:: TVF_ENV_TIME_4


   .. py:attribute:: TVF_ENV_LEVEL_0


   .. py:attribute:: TVF_ENV_LEVEL_1


   .. py:attribute:: TVF_ENV_LEVEL_2


   .. py:attribute:: TVF_ENV_LEVEL_3


   .. py:attribute:: TVF_ENV_LEVEL_4


   .. py:attribute:: TVA_LEVEL_VELOCITY_CURVE


   .. py:attribute:: TVA_LEVEL_VELOCITY_SENS


   .. py:attribute:: TVA_ENV_TIME_1_VELOCITY_SENS


   .. py:attribute:: TVA_ENV_TIME_4_VELOCITY_SENS


   .. py:attribute:: TVA_ENV_TIME_1


   .. py:attribute:: TVA_ENV_TIME_2


   .. py:attribute:: TVA_ENV_TIME_3


   .. py:attribute:: TVA_ENV_TIME_4


   .. py:attribute:: TVA_ENV_LEVEL_1


   .. py:attribute:: TVA_ENV_LEVEL_2


   .. py:attribute:: TVA_ENV_LEVEL_3


   .. py:attribute:: ONE_SHOT_MODE


   .. py:attribute:: RELATIVE_LEVEL


   .. py:attribute:: DRUM_PART
      :value: (112, 1, 5, 1, 5, 'Sets the drum partial. 1 - 5')



   .. py:attribute:: DRUM_GROUP
      :value: (47, 1, 5, 1, 5, 'Sets the drum group. 1 - 5')



   .. py:method:: validate_value(value: int) -> int

      Validate and convert parameter value to MIDI range (0-127)
      :param value: int The value
      :return: int The validated value



   .. py:method:: convert_to_midi_old(value: int) -> int

      Convert the value to MIDI range (0-127) for sending via MIDI.

      :param value: int value to convert
      :return: int MIDI value



   .. py:method:: convert_from_display(display_value: int) -> int

      Convert from display value to MIDI value (0-127)
      :param display_value: int The display value
      :return: int The MIDI value



   .. py:method:: get_display_value() -> Tuple[int, int]

      Get the display range for the parameter
      :return: Tuple[int, int] The display range



   .. py:method:: get_address_for_partial(partial_index: int) -> tuple

      Get the address for address drum partial by index
      :param partial_index: int The partial index
      :return: tuple The address



   .. py:method:: get_address_for_partial_name(partial_name: str) -> int
      :staticmethod:


      Get parameter area and address adjusted for partial number.
      :param partial_name: str The partial name
      :return: int The address



   .. py:method:: get_by_name(param_name: str) -> Optional[object]
      :staticmethod:


      Get the AnalogParameter by name.
      :param param_name: str The parameter name
      :return: Optional[AddressParameterDrumPartial] The parameter
      Return the parameter member by name, or None if not found



   .. py:method:: convert_from_midi(midi_value: int) -> int

      Convert from MIDI value to display value
      :param midi_value: int The MIDI value
      :return: int The display value



   .. py:method:: get_envelope_param_type()

      Returns a envelope_param_type, if the parameter is part of an envelope,
      otherwise returns None.

      :return: Optional[str] The envelope parameter type



