jdxi_editor.midi.data.analog.lfo
================================

.. py:module:: jdxi_editor.midi.data.analog.lfo

.. autoapi-nested-parse::

   Analog LFO



Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.data.analog.lfo.LFO_RANGES
   jdxi_editor.midi.data.analog.lfo.LFO_TEMPO_SYNC_NOTES


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.analog.lfo.AnalogLFOShape
   jdxi_editor.midi.data.analog.lfo.AnalogLFOTempoSyncNote


Module Contents
---------------

.. py:data:: LFO_RANGES

.. py:data:: LFO_TEMPO_SYNC_NOTES
   :value: ['16', '12', '8', '4', '2', '1', '3/4', '2/3', '1/2', '3/8', '1/3', '1/4', '3/16', '1/6', '1/8',...


.. py:class:: AnalogLFOShape

   Bases: :py:obj:`enum.Enum`


   Analog LFO waveform shapes


   .. py:attribute:: TRIANGLE
      :value: 0



   .. py:attribute:: SINE
      :value: 1



   .. py:attribute:: SAW
      :value: 2



   .. py:attribute:: SQUARE
      :value: 3



   .. py:attribute:: SAMPLE_HOLD
      :value: 4



   .. py:attribute:: RANDOM
      :value: 5



   .. py:property:: display_name
      :type: str


      Get display name for LFO shape


.. py:class:: AnalogLFOTempoSyncNote

   Bases: :py:obj:`enum.Enum`


   LFO tempo sync note values


   .. py:attribute:: NOTE_16
      :value: 0



   .. py:attribute:: NOTE_12
      :value: 1



   .. py:attribute:: NOTE_8
      :value: 2



   .. py:attribute:: NOTE_4
      :value: 3



   .. py:attribute:: NOTE_2
      :value: 4



   .. py:attribute:: NOTE_1
      :value: 5



   .. py:attribute:: NOTE_3_4
      :value: 6



   .. py:attribute:: NOTE_2_3
      :value: 7



   .. py:attribute:: NOTE_1_2
      :value: 8



   .. py:attribute:: NOTE_3_8
      :value: 9



   .. py:attribute:: NOTE_1_3
      :value: 10



   .. py:attribute:: NOTE_1_4
      :value: 11



   .. py:attribute:: NOTE_3_16
      :value: 12



   .. py:attribute:: NOTE_1_6
      :value: 13



   .. py:attribute:: NOTE_1_8
      :value: 14



   .. py:attribute:: NOTE_3_32
      :value: 15



   .. py:attribute:: NOTE_1_12
      :value: 16



   .. py:attribute:: NOTE_1_16
      :value: 17



   .. py:attribute:: NOTE_1_24
      :value: 18



   .. py:attribute:: NOTE_1_32
      :value: 19



