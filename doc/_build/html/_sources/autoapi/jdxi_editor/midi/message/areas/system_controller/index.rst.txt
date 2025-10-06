jdxi_editor.midi.message.areas.system_controller
================================================

.. py:module:: jdxi_editor.midi.message.areas.system_controller

.. autoapi-nested-parse::

   SystemControllerMessage
   =======================
   # Example usage:
   # Enable program change transmission
   >>> msg = SystemControllerMessage(
   >>>     param=SystemController.TX_PROGRAM_CHANGE.value, value=1  # ON
   >>> )

   # Set keyboard velocity to REAL
   >>> msg = SystemControllerMessage(
   >>>     param=SystemController.KEYBOARD_VELOCITY.value, value=0  # REAL
   >>> )

   # Set velocity curve to MEDIUM
   >>> msg = SystemControllerMessage(
   >>>     param=SystemController.VELOCITY_CURVE.value, value=1  # MEDIUM
   >>> )

   # Set velocity offset to +5
   >>> msg = SystemControllerMessage(
   >>>     param=SystemController.VELOCITY_OFFSET.value, value=69  # Convert +5 to 69 (64+5)
   >>> )



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.areas.system_controller.SystemControllerMessage


Module Contents
---------------

.. py:class:: SystemControllerMessage

   Bases: :py:obj:`jdxi_editor.midi.message.roland.RolandSysEx`


   System Controller parameter message


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



