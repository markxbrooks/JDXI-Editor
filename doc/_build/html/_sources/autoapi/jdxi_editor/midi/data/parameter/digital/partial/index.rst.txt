jdxi_editor.midi.data.parameter.digital.partial
===============================================

.. py:module:: jdxi_editor.midi.data.parameter.digital.partial

.. autoapi-nested-parse::

   DigitalPartialParameter: JD-Xi Digital Synthesizer Parameter Mapping
   ====================================================================

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
       print(filter_cutoff.address)  # Output: 0x0C

   This class helps structure and manage parameter mappings for JD-Xi SysEx processing.



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.digital.partial.AddressParameterDigitalPartial


Module Contents
---------------

.. py:class:: AddressParameterDigitalPartial(address: int, min_val: int, max_val: int, display_min: Optional[int] = None, display_max: Optional[int] = None, tooltip: Optional[str] = None)

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Digital synth parameters with their addresses and value ranges


   .. py:attribute:: display_min
      :value: None



   .. py:attribute:: display_max
      :value: None



   .. py:attribute:: tooltip
      :value: None



   .. py:attribute:: bipolar_parameters
      :value: ['OSC_PITCH', 'OSC_DETUNE', 'OSC_PITCH_ENV_DEPTH', 'FILTER_CUTOFF_KEYFOLLOW',...



   .. py:attribute:: CONVERSION_OFFSETS


   .. py:method:: get_display_value() -> Tuple[int, int]

      Get the display range for the parameter



   .. py:attribute:: OSC_WAVE


   .. py:attribute:: OSC_WAVE_VARIATION
      :value: (1, 0, 2, 0, 2, 'You can select variations of the currently selected WAVE')



   .. py:attribute:: OSC_PITCH


   .. py:attribute:: OSC_DETUNE


   .. py:attribute:: OSC_PULSE_WIDTH_MOD_DEPTH


   .. py:attribute:: OSC_PULSE_WIDTH


   .. py:attribute:: OSC_PITCH_ENV_ATTACK_TIME


   .. py:attribute:: OSC_PITCH_ENV_DECAY_TIME


   .. py:attribute:: OSC_PITCH_ENV_DEPTH


   .. py:attribute:: FILTER_MODE_SWITCH


   .. py:attribute:: FILTER_SLOPE
      :value: (11, 0, 1, 0, 1, 'Selects the slope (steepness) of the filter. -12, -24 [dB]')



   .. py:attribute:: FILTER_CUTOFF
      :value: (12, 0, 127, 0, 127, 'Specifies the cutoff frequency')



   .. py:attribute:: FILTER_CUTOFF_KEYFOLLOW


   .. py:attribute:: FILTER_ENV_VELOCITY_SENSITIVITY


   .. py:attribute:: FILTER_RESONANCE
      :value: (15, 0, 127, 0, 127, 'Emphasizes the sound in the region of the filter cutoff frequency')



   .. py:attribute:: FILTER_ENV_ATTACK_TIME


   .. py:attribute:: FILTER_ENV_DECAY_TIME


   .. py:attribute:: FILTER_ENV_SUSTAIN_LEVEL


   .. py:attribute:: FILTER_ENV_RELEASE_TIME


   .. py:attribute:: FILTER_ENV_DEPTH


   .. py:attribute:: AMP_LEVEL
      :value: (21, 0, 127, 0, 127, 'Partial volume')



   .. py:attribute:: AMP_VELOCITY


   .. py:attribute:: AMP_ENV_ATTACK_TIME


   .. py:attribute:: AMP_ENV_DECAY_TIME


   .. py:attribute:: AMP_ENV_SUSTAIN_LEVEL


   .. py:attribute:: AMP_ENV_RELEASE_TIME


   .. py:attribute:: AMP_PAN


   .. py:attribute:: AMP_LEVEL_KEYFOLLOW


   .. py:attribute:: LFO_SHAPE


   .. py:attribute:: LFO_RATE
      :value: (29, 0, 127, 0, 127, 'Specifies the LFO rate when LFO Tempo Sync Sw is OFF')



   .. py:attribute:: LFO_TEMPO_SYNC_SWITCH
      :value: (30, 0, 1, 0, 1, 'If this is ON, the LFO rate can be specified as a note value relative to the tempo')



   .. py:attribute:: LFO_TEMPO_SYNC_NOTE


   .. py:attribute:: LFO_FADE_TIME
      :value: (32, 0, 127, 0, 127, 'Specifies the time from when the partial sounds until the LFO reaches its...



   .. py:attribute:: LFO_KEY_TRIGGER
      :value: (33, 0, 1, 0, 1, 'If this is on, the LFO cycle will be restarted when you press a key')



   .. py:attribute:: LFO_PITCH_DEPTH


   .. py:attribute:: LFO_FILTER_DEPTH


   .. py:attribute:: LFO_AMP_DEPTH


   .. py:attribute:: LFO_PAN_DEPTH


   .. py:attribute:: MOD_LFO_SHAPE


   .. py:attribute:: MOD_LFO_RATE
      :value: (39, 0, 127, 0, 127, 'Specifies the LFO rate when ModLFO TempoSyncSw is OFF.')



   .. py:attribute:: MOD_LFO_TEMPO_SYNC_SWITCH
      :value: (40, 0, 1, 0, 1, 'If this is ON, the LFO rate can be specified as a note value relative to the tempo')



   .. py:attribute:: MOD_LFO_TEMPO_SYNC_NOTE
      :value: (41, 0, 19, 0, 19, 'Specifies the LFO rate when ModLFO TempoSyncSw is ON')



   .. py:attribute:: OSC_PULSE_WIDTH_SHIFT


   .. py:attribute:: MOD_LFO_PITCH_DEPTH


   .. py:attribute:: MOD_LFO_FILTER_DEPTH


   .. py:attribute:: MOD_LFO_AMP_DEPTH


   .. py:attribute:: MOD_LFO_PAN


   .. py:attribute:: MOD_LFO_RATE_CTRL


   .. py:attribute:: CUTOFF_AFTERTOUCH


   .. py:attribute:: LEVEL_AFTERTOUCH


   .. py:attribute:: HPF_CUTOFF
      :value: (57, 0, 127, 0, 127, 'Specifies the cutoff frequency of an independent -6 dB high-pass filter')



   .. py:attribute:: SUPER_SAW_DETUNE


   .. py:attribute:: PCM_WAVE_GAIN
      :value: (52, 0, 3, 0, 3, 'Sets the gain for PCM waveforms; 0dB, -6dB, +6dB, +12dB')



   .. py:attribute:: PCM_WAVE_NUMBER
      :value: (53, 0, 16384, 0, 16384, 'Selects the PCM waveform; 0-16383 * This is valid only if PCM is...



   .. py:property:: display_name
      :type: str


      Get display name for the parameter


   .. py:method:: get_switch_text(value: int) -> str

      Get display text for switch values



   .. py:method:: validate_value(value: int) -> int

      Validate and convert parameter value to MIDI range (0-127).



   .. py:method:: get_address_for_partial(partial_number: int) -> Tuple[int, int]

      Get parameter area and address adjusted for partial number.

      :param partial_number: int The partial number
      :return: Tuple[int, int] The (group, address) tuple



   .. py:method:: get_by_name(param_name: str) -> Optional[object]
      :staticmethod:


      Get the DigitalParameter by name.

      :param param_name: str The parameter name
      :return: Optional[AddressParameterDigitalPartial] The parameter
      Return the parameter member by name, or None if not found



   .. py:method:: convert_value(value: int, reverse: bool = False) -> int

      Converts value in both directions based on CONVERSION_OFFSETS

      :param value: int The value
      :param reverse: bool The reverse flag
      :return: int The converted value



   .. py:method:: convert_to_midi(slider_value: int) -> int

      Convert from display value to MIDI value

      :param slider_value: int The display value
      :return: int The MIDI value



   .. py:method:: convert_from_midi(midi_value: int) -> int

      Convert from MIDI value to display value

      :param midi_value: int The MIDI value
      :return: int The display value



   .. py:method:: get_envelope_param_type()

      Returns a envelope_param_type, if the parameter is part of an envelope,
      otherwise returns None.

      :return: Optional[str] The envelope parameter type



