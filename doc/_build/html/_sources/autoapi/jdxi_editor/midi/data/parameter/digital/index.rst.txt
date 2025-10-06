jdxi_editor.midi.data.parameter.digital
=======================================

.. py:module:: jdxi_editor.midi.data.parameter.digital


Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/jdxi_editor/midi/data/parameter/digital/common/index
   /autoapi/jdxi_editor/midi/data/parameter/digital/helpers/index
   /autoapi/jdxi_editor/midi/data/parameter/digital/mapping/index
   /autoapi/jdxi_editor/midi/data/parameter/digital/modify/index
   /autoapi/jdxi_editor/midi/data/parameter/digital/partial/index


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.digital.AddressParameterDigitalCommon
   jdxi_editor.midi.data.parameter.digital.AddressParameterDigitalModify
   jdxi_editor.midi.data.parameter.digital.AddressParameterDigitalPartial


Package Contents
----------------

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



.. py:class:: AddressParameterDigitalModify(address: int, min_val: int, max_val: int, tooltip: str = '')

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   Modify parameters for Digital/SuperNATURAL synth tones.
   These parameters are shared across all partials.


   .. py:attribute:: address


   .. py:attribute:: min_val


   .. py:attribute:: max_val


   .. py:attribute:: tooltip
      :value: ''



   .. py:attribute:: ATTACK_TIME_INTERVAL_SENS


   .. py:attribute:: RELEASE_TIME_INTERVAL_SENS


   .. py:attribute:: PORTAMENTO_TIME_INTERVAL_SENS


   .. py:attribute:: ENVELOPE_LOOP_MODE


   .. py:attribute:: ENVELOPE_LOOP_SYNC_NOTE


   .. py:attribute:: CHROMATIC_PORTAMENTO


   .. py:method:: get_switch_text(value: int) -> str

      Get display text for switch values



   .. py:method:: get_by_name(param_name)
      :staticmethod:


      Get the Parameter by name.



   .. py:method:: validate_value(value: int) -> int

      Validate and convert parameter value



   .. py:method:: get_address_for_partial(partial_number: int = 0)

      Get the address for the partial number.

      :param partial_number: int
      :return: int default area to be subclassed



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



