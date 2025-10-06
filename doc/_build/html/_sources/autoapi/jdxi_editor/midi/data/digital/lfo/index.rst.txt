jdxi_editor.midi.data.digital.lfo
=================================

.. py:module:: jdxi_editor.midi.data.digital.lfo

.. autoapi-nested-parse::

   Digital LFO



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.digital.lfo.DigitalLFOShape
   jdxi_editor.midi.data.digital.lfo.DigitalLFOTempoSyncNote


Module Contents
---------------

.. py:class:: DigitalLFOShape

   Bases: :py:obj:`enum.IntEnum`


   LFO waveform shapes


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


   .. py:property:: midi_value


.. py:class:: DigitalLFOTempoSyncNote

   Bases: :py:obj:`enum.IntEnum`


   Tempo sync note values


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



   .. py:property:: display_name


   .. py:property:: midi_value


