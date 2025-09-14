jdxi_editor.midi.message.effects.reverb
=======================================

.. py:module:: jdxi_editor.midi.message.effects.reverb

.. autoapi-nested-parse::

   ReverbMessage
   =============

       Examples
       --------
   # Set reverb level
   >>> msg = ReverbMessage(param=Reverb.LEVEL.value, value=100)  # Level 100

   # Set reverb parameter 1 to +5000
   >>> msg = ReverbMessage(
   >>>     param=Reverb.get_param_offset(1), value=5000  # Will be converted to 37768
   >>> )



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.effects.reverb.ReverbMessage


Module Contents
---------------

.. py:class:: ReverbMessage

   Bases: :py:obj:`jdxi_editor.midi.message.roland.RolandSysEx`


   Program Reverb parameter message


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


   .. py:attribute:: value
      :type:  int
      :value: 0



   .. py:method:: __post_init__()

      Ensure proper initialization of address, model_id, and data fields.



