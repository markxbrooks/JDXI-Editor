jdxi_editor.ui.windows.midi.helpers.debugger
============================================

.. py:module:: jdxi_editor.ui.windows.midi.helpers.debugger


Functions
---------

.. autoapisummary::

   jdxi_editor.ui.windows.midi.helpers.debugger.validate_checksum


Module Contents
---------------

.. py:function:: validate_checksum(data_bytes: bytes, checksum: int) -> bool

   Validate Roland SysEx checksum (sum of bytes should be 0 mod 128)

   :param data_bytes: bytes
   :param checksum: int
   :return: bool True on success, False otherwise


