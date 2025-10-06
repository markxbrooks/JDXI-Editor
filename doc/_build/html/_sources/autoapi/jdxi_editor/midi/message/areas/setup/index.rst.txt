jdxi_editor.midi.message.areas.setup
====================================

.. py:module:: jdxi_editor.midi.message.areas.setup


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.areas.setup.SetupMessage


Module Contents
---------------

.. py:class:: SetupMessage

   Bases: :py:obj:`jdxi_editor.midi.message.roland.RolandSysEx`


   Setup parameter message


   .. py:attribute:: command
      :type:  int


   .. py:attribute:: msb
      :type:  int


   .. py:attribute:: umb
      :type:  int
      :value: 0



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



