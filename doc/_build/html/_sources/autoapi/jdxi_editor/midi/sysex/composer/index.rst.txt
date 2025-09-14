jdxi_editor.midi.sysex.composer
===============================

.. py:module:: jdxi_editor.midi.sysex.composer

.. autoapi-nested-parse::

   JDXiSysExComposer



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.sysex.composer.JDXiSysExComposer


Functions
---------

.. autoapisummary::

   jdxi_editor.midi.sysex.composer.apply_lmb_offset


Module Contents
---------------

.. py:function:: apply_lmb_offset(address: jdxi_editor.midi.data.address.address.RolandSysExAddress, param: jdxi_editor.midi.data.parameter.synth.AddressParameter) -> jdxi_editor.midi.data.address.address.RolandSysExAddress

   Set the LMB (Logical Memory Block) of the address depending on the parameter type.


.. py:class:: JDXiSysExComposer

   SysExComposer


   .. py:attribute:: address
      :value: None



   .. py:attribute:: sysex_message
      :value: None



   .. py:method:: compose_message(address: jdxi_editor.midi.data.address.address.RolandSysExAddress, param: jdxi_editor.midi.data.parameter.synth.AddressParameter, value: int, size: int = 1) -> Optional[jdxi_editor.midi.message.roland.RolandSysEx]

      Compose a SysEx message for the given address and parameter.

      :param address: RolandSysExAddress
      :param param: AddressParameter
      :param value: Parameter display value
      :param size: Optional, number of bytes (1 or 4)
      :return: RolandSysEx object or None on failure



   .. py:method:: _is_valid_sysex() -> bool

      Checks if the SysEx message starts and ends with the correct bytes.



   .. py:method:: _verify_header() -> bool

      Checks if the SysEx header matches the JD-Xi model ID.



