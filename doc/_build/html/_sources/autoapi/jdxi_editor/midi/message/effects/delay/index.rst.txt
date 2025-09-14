jdxi_editor.midi.message.effects.delay
======================================

.. py:module:: jdxi_editor.midi.message.effects.delay

.. autoapi-nested-parse::

   DelayMessage
   ============

   # Example usage:
   # Set delay level
   >>> msg = DelayMessage(param=Delay.LEVEL.value, value=100)  # Level 100

   # Set reverb send level
   >>> msg = DelayMessage(param=Delay.REVERB_SEND.value, value=64)  # Send to reverb

   # Set delay parameter 1 to +5000
   >>> msg = DelayMessage(
   >>>     param=Delay.get_param_offset(1), value=5000  # Will be converted to 37768
   >>> )



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.effects.delay.DelayMessage


Module Contents
---------------

.. py:class:: DelayMessage

   Bases: :py:obj:`jdxi_editor.midi.message.roland.RolandSysEx`


   Program Delay parameter message


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



