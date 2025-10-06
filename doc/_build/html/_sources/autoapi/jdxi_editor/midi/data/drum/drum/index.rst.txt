jdxi_editor.midi.data.drum.drum
===============================

.. py:module:: jdxi_editor.midi.data.drum.drum

.. autoapi-nested-parse::

   Drum



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.drum.drum.MuteGroup
   jdxi_editor.midi.data.drum.drum.Note
   jdxi_editor.midi.data.drum.drum.DrumPad
   jdxi_editor.midi.data.drum.drum.DrumPadSettings
   jdxi_editor.midi.data.drum.drum.DrumKitPatch


Module Contents
---------------

.. py:class:: MuteGroup

   Bases: :py:obj:`enum.Enum`


   Drum pad mute groups


   .. py:attribute:: OFF
      :value: 0



   .. py:attribute:: GROUPS


.. py:class:: Note

   Bases: :py:obj:`enum.Enum`


   MIDI note numbers for drum pads


   .. py:attribute:: PAD_1
      :value: 36



   .. py:attribute:: PAD_2
      :value: 37



   .. py:attribute:: PAD_3
      :value: 38



   .. py:attribute:: PAD_4
      :value: 39



   .. py:attribute:: PAD_5
      :value: 40



   .. py:attribute:: PAD_6
      :value: 41



   .. py:attribute:: PAD_7
      :value: 42



   .. py:attribute:: PAD_8
      :value: 43



   .. py:attribute:: PAD_9
      :value: 44



   .. py:attribute:: PAD_10
      :value: 45



   .. py:attribute:: PAD_11
      :value: 46



   .. py:attribute:: PAD_12
      :value: 47



   .. py:attribute:: PAD_13
      :value: 48



   .. py:attribute:: PAD_14
      :value: 49



   .. py:attribute:: PAD_15
      :value: 50



   .. py:attribute:: PAD_16
      :value: 51



.. py:class:: DrumPad

   Represents address single drum pad's settings


   .. py:attribute:: PARAM_OFFSET
      :value: 16



   .. py:attribute:: WAVE
      :value: 0



   .. py:attribute:: LEVEL
      :value: 1



   .. py:attribute:: PAN
      :value: 2



   .. py:attribute:: MUTE_GROUP
      :value: 3



   .. py:attribute:: TUNE
      :value: 4



   .. py:attribute:: DECAY
      :value: 5



   .. py:attribute:: REVERB_SEND
      :value: 6



   .. py:attribute:: DELAY_SEND
      :value: 7



   .. py:attribute:: FX_SEND
      :value: 8



   .. py:attribute:: wave
      :value: 0



   .. py:attribute:: level
      :value: 100



   .. py:attribute:: pan
      :value: 64



   .. py:attribute:: mute_group
      :value: 0



   .. py:attribute:: tune
      :value: 0



   .. py:attribute:: decay
      :value: 64



   .. py:attribute:: reverb_send
      :value: 0



   .. py:attribute:: delay_send
      :value: 0



   .. py:attribute:: fx_send
      :value: 0



.. py:class:: DrumPadSettings

   Settings for address single drum pad


   .. py:attribute:: wave
      :type:  int
      :value: 0



   .. py:attribute:: level
      :type:  int
      :value: 100



   .. py:attribute:: pan
      :type:  int
      :value: 64



   .. py:attribute:: tune
      :type:  int
      :value: 0



   .. py:attribute:: decay
      :type:  int
      :value: 64



   .. py:attribute:: mute_group
      :type:  int
      :value: 0



   .. py:attribute:: reverb_send
      :type:  int
      :value: 0



   .. py:attribute:: delay_send
      :type:  int
      :value: 0



   .. py:attribute:: fx_send
      :type:  int
      :value: 0



.. py:class:: DrumKitPatch

   Complete drum kit patch data


   .. py:attribute:: level
      :type:  int
      :value: 100



   .. py:attribute:: pan
      :type:  int
      :value: 64



   .. py:attribute:: reverb_send
      :type:  int
      :value: 0



   .. py:attribute:: delay_send
      :type:  int
      :value: 0



   .. py:attribute:: fx_send
      :type:  int
      :value: 0



   .. py:attribute:: pads
      :type:  Dict[int, DrumPadSettings]
      :value: None



   .. py:method:: __post_init__()

      Initialize pad settings



