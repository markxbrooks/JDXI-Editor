jdxi_editor.midi.message.synths.drum
====================================

.. py:module:: jdxi_editor.midi.message.synths.drum

.. autoapi-nested-parse::

   DrumKitMessage
   ==============

   # Example usage:
   # Set kit name
   >>> msg = DrumKitMessage(
   >>>     section=DrumKitSection.COMMON.value,
   >>>     param=DrumKitCommon.NAME_1.value,
   >>>     value=0x41,  # 'A'
   >>> )

   # Set pad parameter
   >>> msg = DrumKitMessage(
   >>>     section=DrumKitSection.get_pad_offset(36),  # Pad C1
   >>>     param=DrumPadParam.WAVE.value,
   >>>     value=1,  # Wave number
   >>> )



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.synths.drum.DrumKitMessage


Module Contents
---------------

.. py:class:: DrumKitMessage

   Bases: :py:obj:`jdxi_editor.midi.message.roland.RolandSysEx`


   Drum Kit parameter message


   .. py:attribute:: command
      :type:  int


   .. py:attribute:: msb
      :type:  int


   .. py:attribute:: umb
      :type:  int


   .. py:attribute:: lmb
      :type:  int
      :value: 0



   .. py:attribute:: lsb
      :type:  int
      :value: 0



   .. py:attribute:: value
      :type:  int
      :value: 0



   .. py:method:: __post_init__()

      Ensure proper initialization of address, model_id, and data fields.



