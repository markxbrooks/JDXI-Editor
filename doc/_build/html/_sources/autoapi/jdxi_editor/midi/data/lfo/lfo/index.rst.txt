jdxi_editor.midi.data.lfo.lfo
=============================

.. py:module:: jdxi_editor.midi.data.lfo.lfo

.. autoapi-nested-parse::

   LFO data



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.lfo.lfo.LFOSyncNote
   jdxi_editor.midi.data.lfo.lfo.LFOShape


Module Contents
---------------

.. py:class:: LFOSyncNote

   Bases: :py:obj:`enum.Enum`


   LFO sync note values


   .. py:attribute:: BAR_16
      :value: 0



   .. py:attribute:: BAR_12
      :value: 1



   .. py:attribute:: BAR_8
      :value: 2



   .. py:attribute:: BAR_4
      :value: 3



   .. py:attribute:: BAR_2
      :value: 4



   .. py:attribute:: BAR_1
      :value: 5



   .. py:attribute:: BAR_3_4
      :value: 6



   .. py:attribute:: BAR_2_3
      :value: 7



   .. py:attribute:: BAR_1_2
      :value: 8



   .. py:attribute:: BAR_3_8
      :value: 9



   .. py:attribute:: BAR_1_3
      :value: 10



   .. py:attribute:: BAR_1_4
      :value: 11



   .. py:attribute:: BAR_3_16
      :value: 12



   .. py:attribute:: BAR_1_6
      :value: 13



   .. py:attribute:: BAR_1_8
      :value: 14



   .. py:attribute:: BAR_3_32
      :value: 15



   .. py:attribute:: BAR_1_12
      :value: 16



   .. py:attribute:: BAR_1_16
      :value: 17



   .. py:attribute:: BAR_1_24
      :value: 18



   .. py:attribute:: BAR_1_32
      :value: 19



   .. py:method:: get_display_name(value: int) -> str
      :staticmethod:


      Get display name for sync note value



   .. py:method:: get_all_display_names() -> list
      :staticmethod:


      Get list of all display names in order



   .. py:method:: display_name(value: int) -> str
      :staticmethod:


      Get display name for sync note value



.. py:class:: LFOShape

   Bases: :py:obj:`enum.Enum`


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



   .. py:method:: get_display_name(value: int) -> str
      :staticmethod:


      Get display name for LFO shape



