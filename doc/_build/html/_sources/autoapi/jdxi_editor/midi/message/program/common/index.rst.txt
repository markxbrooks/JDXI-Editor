jdxi_editor.midi.message.program.common
=======================================

.. py:module:: jdxi_editor.midi.message.program.common


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.program.common.ProgramCommonParameterMessage


Module Contents
---------------

.. py:class:: ProgramCommonParameterMessage

   Bases: :py:obj:`jdxi_editor.midi.message.roland.RolandSysEx`


   Program Common parameter message


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

      Set up address and data



