jdxi_editor.midi.data.address.sysex_byte
========================================

.. py:module:: jdxi_editor.midi.data.address.sysex_byte

.. autoapi-nested-parse::

   SysEx Byte



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.data.address.sysex_byte.SysExByte


Module Contents
---------------

.. py:class:: SysExByte

   Bases: :py:obj:`enum.IntEnum`


   Base class for SysEx message byte positions.


   .. py:method:: message_position()
      :classmethod:

      :abstractmethod:


      Return the fixed message position for command bytes.



   .. py:method:: get_parameter_by_address(address: int) -> Optional[T]
      :classmethod:


      Get parameter by address

      :param address: int The address
      :return: Optional[T] The parameter



