jdxi_editor.midi.data.effects.effects
=====================================

.. py:module:: jdxi_editor.midi.data.effects.effects

.. autoapi-nested-parse::

   Effects



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.effects.effects.EffectType
   jdxi_editor.midi.data.effects.effects.FX
   jdxi_editor.midi.data.effects.effects.EffectPatch
   jdxi_editor.midi.data.effects.effects.EffectParam
   jdxi_editor.midi.data.effects.effects.EfxType
   jdxi_editor.midi.data.effects.effects.EffectGroup
   jdxi_editor.midi.data.effects.effects.Effect1
   jdxi_editor.midi.data.effects.effects.Effect1Message
   jdxi_editor.midi.data.effects.effects.Effect2
   jdxi_editor.midi.data.effects.effects.Effect2Message


Module Contents
---------------

.. py:class:: EffectType

   Bases: :py:obj:`enum.Enum`


   Effect types available on JD-Xi


   .. py:attribute:: THRU
      :value: 0



   .. py:attribute:: DISTORTION
      :value: 1



   .. py:attribute:: FUZZ
      :value: 2



   .. py:attribute:: COMPRESSOR
      :value: 3



   .. py:attribute:: BITCRUSHER
      :value: 4



   .. py:attribute:: FLANGER
      :value: 5



   .. py:attribute:: PHASER
      :value: 6



   .. py:attribute:: RING_MOD
      :value: 7



   .. py:attribute:: SLICER
      :value: 8



   .. py:attribute:: LEVEL
      :value: 0



   .. py:attribute:: MIX
      :value: 1



   .. py:attribute:: DRIVE
      :value: 16



   .. py:attribute:: TONE
      :value: 17



   .. py:attribute:: ATTACK
      :value: 18



   .. py:attribute:: RELEASE
      :value: 19



   .. py:attribute:: THRESHOLD
      :value: 20



   .. py:attribute:: RATIO
      :value: 21



   .. py:attribute:: BIT_DEPTH
      :value: 22



   .. py:attribute:: RATE
      :value: 23



   .. py:attribute:: DEPTH
      :value: 24



   .. py:attribute:: FEEDBACK
      :value: 25



   .. py:attribute:: FREQUENCY
      :value: 26



   .. py:attribute:: BALANCE
      :value: 27



   .. py:attribute:: PATTERN
      :value: 28



   .. py:attribute:: REVERB_SEND
      :value: 32



   .. py:attribute:: DELAY_SEND
      :value: 33



   .. py:attribute:: CHORUS_SEND
      :value: 34



   .. py:attribute:: REVERB_TYPE
      :value: 48



   .. py:attribute:: REVERB_TIME
      :value: 49



   .. py:attribute:: REVERB_PRE_DELAY
      :value: 50



.. py:class:: FX

   Effect parameter ranges and defaults


   .. py:attribute:: RANGES


   .. py:attribute:: DEFAULTS


.. py:class:: EffectPatch

   Effect patch data


   .. py:attribute:: type
      :type:  EffectType


   .. py:attribute:: level
      :type:  int
      :value: 100



   .. py:attribute:: param1
      :type:  int
      :value: 0



   .. py:attribute:: param2
      :type:  int
      :value: 0



   .. py:attribute:: reverb_send
      :type:  int
      :value: 0



   .. py:attribute:: delay_send
      :type:  int
      :value: 0



   .. py:attribute:: chorus_send
      :type:  int
      :value: 0



   .. py:method:: validate_param(param: str, value: int) -> bool

      Validate parameter value is in range



.. py:class:: EffectParam

   Effect parameter definition


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: min_value
      :type:  int
      :value: -20000



   .. py:attribute:: max_value
      :type:  int
      :value: 20000



   .. py:attribute:: default
      :type:  int
      :value: 0



   .. py:attribute:: unit
      :type:  str
      :value: ''



.. py:class:: EfxType

   Bases: :py:obj:`enum.Enum`


   Effect types for JD-Xi


   .. py:attribute:: ROOM1
      :value: 0



   .. py:attribute:: ROOM2
      :value: 1



   .. py:attribute:: STAGE1
      :value: 2



   .. py:attribute:: STAGE2
      :value: 3



   .. py:attribute:: HALL1
      :value: 4



   .. py:attribute:: HALL2
      :value: 5



   .. py:attribute:: PLATE
      :value: 6



   .. py:attribute:: SPRING
      :value: 7



   .. py:attribute:: STEREO
      :value: 0



   .. py:attribute:: PANNING
      :value: 1



   .. py:attribute:: MONO
      :value: 2



   .. py:attribute:: TAPE_ECHO
      :value: 3



   .. py:attribute:: MOD_DELAY
      :value: 4



   .. py:attribute:: DISTORTION
      :value: 0



   .. py:attribute:: FUZZ
      :value: 1



   .. py:attribute:: COMPRESSOR
      :value: 2



   .. py:attribute:: BITCRUSHER
      :value: 3



   .. py:attribute:: EQUALIZER
      :value: 4



   .. py:attribute:: PHASER
      :value: 5



   .. py:attribute:: FLANGER
      :value: 6



   .. py:attribute:: CHORUS
      :value: 7



   .. py:attribute:: TREMOLO
      :value: 8



   .. py:attribute:: AUTOPAN
      :value: 9



   .. py:attribute:: SLICER
      :value: 10



   .. py:attribute:: RING_MOD
      :value: 11



   .. py:attribute:: ISOLATOR
      :value: 12



   .. py:method:: get_display_name(value: int, effect_type: str) -> str
      :staticmethod:


      Get display name for effect preset_type



.. py:class:: EffectGroup

   Bases: :py:obj:`enum.Enum`


   Effect parameter groups


   .. py:attribute:: COMMON
      :value: 0



   .. py:attribute:: INSERT
      :value: 16



   .. py:attribute:: REVERB
      :value: 32



   .. py:attribute:: DELAY
      :value: 48



.. py:class:: Effect1

   Bases: :py:obj:`enum.Enum`


   Program Effect 1 parameters


   .. py:attribute:: TYPE
      :value: 0



   .. py:attribute:: LEVEL
      :value: 1



   .. py:attribute:: DELAY_SEND
      :value: 2



   .. py:attribute:: REVERB_SEND
      :value: 3



   .. py:attribute:: OUTPUT_ASSIGN
      :value: 4



   .. py:attribute:: PARAM_1
      :value: 17



   .. py:attribute:: PARAM_2
      :value: 21



   .. py:attribute:: PARAM_32
      :value: 269



   .. py:method:: get_param_offset(param_num: int) -> int
      :staticmethod:


      Get parameter offset from parameter number (1-32)



   .. py:method:: get_display_value(param: int, value: int) -> str
      :staticmethod:


      Convert raw value to display value



.. py:class:: Effect1Message

   Bases: :py:obj:`jdxi_editor.midi.message.roland.RolandSysEx`


   Program Effect 1 parameter message


   .. py:attribute:: command
      :type:  int


   .. py:attribute:: area
      :type:  int


   .. py:attribute:: section
      :type:  int
      :value: 2



   .. py:attribute:: group
      :type:  int


   .. py:attribute:: lsb
      :type:  int
      :value: 0



   .. py:attribute:: value
      :type:  int
      :value: 0



   .. py:method:: __post_init__()

      Set up address and data



.. py:class:: Effect2

   Bases: :py:obj:`enum.Enum`


   Program Effect 2 parameters


   .. py:attribute:: TYPE
      :value: 0



   .. py:attribute:: LEVEL
      :value: 1



   .. py:attribute:: DELAY_SEND
      :value: 2



   .. py:attribute:: REVERB_SEND
      :value: 3



   .. py:attribute:: PARAM_1
      :value: 17



   .. py:attribute:: PARAM_2
      :value: 21



   .. py:attribute:: PARAM_32
      :value: 269



   .. py:method:: get_param_offset(param_num: int) -> int
      :staticmethod:


      Get parameter offset from parameter number (1-32)



   .. py:method:: get_display_value(param: int, value: int) -> str
      :staticmethod:


      Convert raw value to display value



.. py:class:: Effect2Message

   Bases: :py:obj:`jdxi_editor.midi.message.roland.RolandSysEx`


   Program Effect 2 parameter message


   .. py:attribute:: command
      :type:  int


   .. py:attribute:: msb
      :type:  int


   .. py:attribute:: umb
      :type:  int
      :value: 4



   .. py:attribute:: lmb
      :type:  int
      :value: 0



   .. py:attribute:: lsb
      :type:  int
      :value: 0



   .. py:attribute:: value
      :type:  int
      :value: 0



   .. py:method:: __post_init__(param)

      Set up address and data



