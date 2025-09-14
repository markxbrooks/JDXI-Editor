jdxi_editor.midi.message.areas.digital_tone
===========================================

.. py:module:: jdxi_editor.midi.message.areas.digital_tone

.. autoapi-nested-parse::

   DigitalToneMessage
   ==================
   # Example usage:
   # Set common parameter
   >>> msg = DigitalToneMessage(
   >>>     tone_type=TEMP_DIGITAL_TONE,  # Digital 1
   >>>     section=DigitalToneSection.COMMON.value,
   >>>     param=0x00,  # Common parameter
   >>>     value=64,
   >>> )

   # Set partial parameter
   >>> msg = DigitalToneMessage(
   >>>     tone_type=TEMP_DIGITAL_TONE,  # Digital 1
   >>>     section=DigitalToneSection.PARTIAL_1.value,
   >>>     param=0x00,  # Partial parameter
   >>>     value=64,
   >>> )

   # Set modify parameter
   msg = DigitalToneMessage(
       tone_type=TEMP_DIGITAL_TONE,  # Digital 1
       section=DigitalToneSection.MODIFY.value,
       param=0x00,  # Modify parameter
       value=64,
   )



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.areas.digital_tone.DigitalToneMessage


Module Contents
---------------

.. py:class:: DigitalToneMessage

   Bases: :py:obj:`jdxi_editor.midi.message.roland.RolandSysEx`


   SuperNATURAL Synth Tone parameter message for JD-Xi.
   Defaults to TEMPORARY_TONE / Digital 1 / Common / Param 0x00


   .. py:attribute:: command
      :type:  int


   .. py:attribute:: msb
      :type:  int


   .. py:attribute:: umb
      :type:  int


   .. py:attribute:: lmb
      :type:  int


   .. py:attribute:: lsb
      :type:  int
      :value: 0



   .. py:attribute:: value
      :type:  int
      :value: 0



   .. py:method:: __post_init__()

      Ensure proper initialization of address, model_id, and data fields.



