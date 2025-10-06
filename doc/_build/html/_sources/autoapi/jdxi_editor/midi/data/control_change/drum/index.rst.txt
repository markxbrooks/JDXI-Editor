jdxi_editor.midi.data.control_change.drum
=========================================

.. py:module:: jdxi_editor.midi.data.control_change.drum


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.control_change.drum.DrumKitCC


Module Contents
---------------

.. py:class:: DrumKitCC

   Drum Kit Control Change parameters


   .. py:attribute:: MSB_LEVEL
      :value: 64



   .. py:attribute:: MSB_CUTOFF
      :value: 89



   .. py:attribute:: MSB_RESONANCE
      :value: 92



   .. py:attribute:: MSB_ENVELOPE
      :value: 119



   .. py:attribute:: MIN_NOTE
      :value: 36



   .. py:attribute:: MAX_NOTE
      :value: 72



   .. py:attribute:: MIN_VALUE
      :value: 0



   .. py:attribute:: MAX_VALUE
      :value: 127



   .. py:method:: get_display_value(param: int, value: int) -> str
      :staticmethod:


      Convert raw value to display value



   .. py:method:: validate_note(note: int) -> bool
      :staticmethod:


      Validate note is within drum kit range



   .. py:method:: validate_msb(msb: int) -> bool
      :staticmethod:


      Validate MSB value is valid



   .. py:method:: validate_value(value: int) -> bool
      :staticmethod:


      Validate parameter value is within range



