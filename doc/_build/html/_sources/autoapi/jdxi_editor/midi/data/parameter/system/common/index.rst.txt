jdxi_editor.midi.data.parameter.system.common
=============================================

.. py:module:: jdxi_editor.midi.data.parameter.system.common


Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.parameter.system.common.AddressParameterSystemCommon


Module Contents
---------------

.. py:class:: AddressParameterSystemCommon(address: int, min_val: int, max_val: int)

   Bases: :py:obj:`jdxi_editor.midi.data.parameter.synth.AddressParameter`


   System Common parameters


   .. py:attribute:: MASTER_TUNE


   .. py:attribute:: MASTER_KEY_SHIFT


   .. py:attribute:: MASTER_LEVEL
      :value: (5, 0, 127)



   .. py:attribute:: PROGRAM_CTRL_CH
      :value: (17, 0, 16)



   .. py:attribute:: RX_PROGRAM_CHANGE
      :value: (41, 0, 1)



   .. py:attribute:: RX_BANK_SELECT
      :value: (42, 0, 1)



   .. py:method:: get_display_value(param: int, value: int) -> str
      :staticmethod:


      Convert raw value to display value



   .. py:method:: get_nibbled_byte_size() -> int

      Get the nibbled byte size of the parameter



