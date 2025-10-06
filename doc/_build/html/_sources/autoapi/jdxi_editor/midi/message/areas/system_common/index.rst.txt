jdxi_editor.midi.message.areas.system_common
============================================

.. py:module:: jdxi_editor.midi.message.areas.system_common

.. autoapi-nested-parse::

   SystemCommonMessage
   ===================

   # Example usage:
   # Set master tune to +50 cents
   >>> msg = SystemCommonMessage(
   >>>     param=SystemCommon.MASTER_TUNE.value,
   >>>     value=1024 + (50 * 10),  # Convert +50.0 cents to 1524
   >>> )

   # Set master key shift to -12 semitones
   >>> msg = SystemCommonMessage(
   >>>     param=SystemCommon.MASTER_KEY_SHIFT.value, value=52  # Convert -12 to 52 (64-12)
   >>> )

   # Set program control channel to 1
   >>> msg = SystemCommonMessage(
   >>>     param=SystemCommon.PROGRAM_CTRL_CH.value, value=1  # Channel 1
   >>> )

   # Enable program change reception
   >>> msg = SystemCommonMessage(param=SystemCommon.RX_PROGRAM_CHANGE.value, value=1)  # ON



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.areas.system_common.SystemCommonMessage


Module Contents
---------------

.. py:class:: SystemCommonMessage

   Bases: :py:obj:`jdxi_editor.midi.message.roland.RolandSysEx`


   System Common parameter message


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



