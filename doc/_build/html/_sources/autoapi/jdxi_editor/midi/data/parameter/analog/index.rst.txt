jdxi_editor.midi.data.parameter.analog
======================================

.. py:module:: jdxi_editor.midi.data.parameter.analog

.. autoapi-nested-parse::

   AnalogParameter: JD-Xi Digital Synthesizer Parameter Mapping
   ============================================================

   This class defines digital synthesizer parameters for the Roland JD-Xi, mapping
   various synthesis parameters to their corresponding memory addresses and valid
   value ranges.

   The parameters include:
   - Oscillator settings (waveform, pitch, detune, envelope, etc.)
   - Filter settings (cutoff, resonance, envelope, key follow, etc.)
   - Amplitude settings (level, velocity, envelope, pan, etc.)
   - LFO (Low-Frequency Oscillator) settings (waveform, rate, depth, sync, etc.)
   - Modulation LFO settings (waveform, rate, depth, sync, etc.)
   - Additional synthesis controls (aftertouch, wave gain, super saw detune, etc.)
   - PCM wave settings (wave number, gain, high-pass filter cutoff, etc.)

   Each parameter is stored as address tuple containing:
       (memory_address, min_value, max_value)

   .. attribute:: - OSC_WAVE

      Defines the oscillator waveform preset_type.

   .. attribute:: - FILTER_CUTOFF

      Controls the filter cutoff frequency.

   .. attribute:: - AMP_LEVEL

      Sets the overall amplitude level.

   .. attribute:: - LFO_RATE

      Adjusts the rate of the low-frequency oscillator.

   .. attribute:: - MOD_LFO_PITCH_DEPTH

      Modulates pitch using the secondary LFO.

   .. attribute:: -

      

      :type: :py:class:`Other parameters follow address similar structure.`

   .. method:: __init__(self, address

      int, min_val: int, max_val: int):
      Initializes address DigitalParameter instance with an address and value range.
      

   Usage Example:
       filter_cutoff = DigitalParameter(0x0C, 0, 127)  # Filter Cutoff Frequency
       log.message(filter_cutoff.address)  # Output: 0x0C

   This class helps structure and manage parameter mappings for JD-Xi SysEx processing.



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.analog.AddressParameterAnalog


Module Contents
---------------

.. py:class:: AddressParameterAnalog(address: int, min_val: int, max_val: int, display_min: Optional[int] = None, display_max: Optional[int] = None, tooltip: Optional[str] = None)

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Analog synth parameters with area, address, and value range.


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



   .. py:attribute:: LFO_SHAPE


   .. py:attribute:: LFO_RATE


   .. py:attribute:: LFO_FADE_TIME


   .. py:attribute:: LFO_TEMPO_SYNC_SWITCH


   .. py:attribute:: LFO_TEMPO_SYNC_NOTE


   .. py:attribute:: LFO_PITCH_DEPTH


   .. py:attribute:: LFO_FILTER_DEPTH


   .. py:attribute:: LFO_AMP_DEPTH


   .. py:attribute:: LFO_KEY_TRIGGER


   .. py:attribute:: OSC_WAVEFORM
      :value: (22, 0, 2, 0, 2, 'Selects the waveform; SAW, TRI, PW-SQR')



   .. py:attribute:: OSC_PITCH_COARSE


   .. py:attribute:: OSC_PITCH_FINE


   .. py:attribute:: OSC_PULSE_WIDTH


   .. py:attribute:: OSC_PULSE_WIDTH_MOD_DEPTH


   .. py:attribute:: OSC_PITCH_ENV_VELOCITY_SENSITIVITY


   .. py:attribute:: OSC_PITCH_ENV_ATTACK_TIME
      :value: (28, 0, 127, 0, 127, 'Attack time for pitch envelope')



   .. py:attribute:: OSC_PITCH_ENV_DECAY_TIME
      :value: (29, 0, 127, 0, 127, 'Decay time for pitch envelope')



   .. py:attribute:: OSC_PITCH_ENV_DEPTH


   .. py:attribute:: SUB_OSCILLATOR_TYPE


   .. py:attribute:: FILTER_MODE_SWITCH
      :value: (32, 0, 1, 0, 1, 'Specifies whether to use the analog LPF or not use it (BYPASS).')



   .. py:attribute:: FILTER_CUTOFF
      :value: (33, 0, 127, 0, 127, 'Specifies the cutoff frequency')



   .. py:attribute:: FILTER_CUTOFF_KEYFOLLOW


   .. py:attribute:: FILTER_RESONANCE


   .. py:attribute:: FILTER_ENV_VELOCITY_SENSITIVITY


   .. py:attribute:: FILTER_ENV_ATTACK_TIME
      :value: (37, 0, 127, 0, 127, 'Attack time for filter envelope')



   .. py:attribute:: FILTER_ENV_DECAY_TIME
      :value: (38, 0, 127, 0, 127, 'Decay time for filter envelope')



   .. py:attribute:: FILTER_ENV_SUSTAIN_LEVEL
      :value: (39, 0, 127, 0, 127, 'Sustain level for filter envelope')



   .. py:attribute:: FILTER_ENV_RELEASE_TIME
      :value: (40, 0, 127, 0, 127, 'Release time for filter envelope')



   .. py:attribute:: FILTER_ENV_DEPTH


   .. py:attribute:: AMP_LEVEL


   .. py:attribute:: AMP_LEVEL_KEYFOLLOW


   .. py:attribute:: AMP_LEVEL_VELOCITY_SENSITIVITY


   .. py:attribute:: AMP_ENV_ATTACK_TIME
      :value: (45, 0, 127, 0, 127, 'Attack time for amplitude envelope')



   .. py:attribute:: AMP_ENV_DECAY_TIME
      :value: (46, 0, 127, 0, 127, 'Decay time for amplitude envelope')



   .. py:attribute:: AMP_ENV_SUSTAIN_LEVEL
      :value: (47, 0, 127, 0, 127, 'Sustain level for amplitude envelope')



   .. py:attribute:: AMP_ENV_RELEASE_TIME
      :value: (48, 0, 127, 0, 127, 'Release time for amplitude envelope')



   .. py:attribute:: PORTAMENTO_SWITCH


   .. py:attribute:: PORTAMENTO_TIME


   .. py:attribute:: LEGATO_SWITCH


   .. py:attribute:: OCTAVE_SHIFT


   .. py:attribute:: PITCH_BEND_UP


   .. py:attribute:: PITCH_BEND_DOWN


   .. py:attribute:: LFO_PITCH_MODULATION_CONTROL


   .. py:attribute:: LFO_FILTER_MODULATION_CONTROL


   .. py:attribute:: LFO_AMP_MODULATION_CONTROL


   .. py:attribute:: LFO_RATE_MODULATION_CONTROL


   .. py:attribute:: display_min
      :value: None



   .. py:attribute:: display_max
      :value: None



   .. py:attribute:: tooltip
      :value: None



   .. py:attribute:: switches
      :value: ['FILTER_SWITCH', 'PORTAMENTO_SWITCH', 'LEGATO_SWITCH', 'LFO_TEMPO_SYNC_SWITCH']



   .. py:attribute:: bipolar_parameters
      :value: ['LFO_PITCH_DEPTH', 'LFO_FILTER_DEPTH', 'LFO_AMP_DEPTH', 'FILTER_ENV_VELOCITY_SENSITIVITY',...



   .. py:method:: get_bipolar_parameters()


   .. py:method:: validate_value(value: int) -> int

      Validate that the parameter value is within the allowed range.



   .. py:method:: get_by_name(param_name: str) -> Optional[object]
      :staticmethod:


      Get the AnalogParameter by name.

      :param param_name: str The parameter name
      :return: Optional[object] The parameter



   .. py:method:: get_name_by_address(address: int) -> Optional[str]
      :staticmethod:


      Return the parameter name for address given address.

      :param address: int The address
      :return: Optional[str] The parameter name



   .. py:property:: display_name
      :type: str


      Get display name for the parameter


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



   .. py:method:: get_address_for_partial(partial_number: int = 0) -> Tuple[int, int]

      Get parameter area and address adjusted for partial number.

      :param partial_number: int The partial number
      :return: Tuple[int, int] The parameter area and address



   .. py:method:: get_envelope_param_type()

      Returns a envelope_param_type, if the parameter is part of an envelope,
      otherwise returns None.



