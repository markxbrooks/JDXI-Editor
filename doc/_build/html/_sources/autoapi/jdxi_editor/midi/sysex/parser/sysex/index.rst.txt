jdxi_editor.midi.sysex.parser.sysex
===================================

.. py:module:: jdxi_editor.midi.sysex.parser.sysex

.. autoapi-nested-parse::

   Sysex parser
   # Example usage:
   >>> sysex_data = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x7E, 0x7F, 0x06, 0x01, 0x19, 0x01, 0x00,
   >>>               0xF7]  # Example SysEx data

   >>> parser = JDXiSysExParser(sysex_data)
   >>> parsed_data = parser.parse()
   >>> log.message(f"Parsed Data: {parsed_data}")



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.sysex.parser.sysex.JDXiSysExParser


Module Contents
---------------

.. py:class:: JDXiSysExParser(sysex_data: Optional[bytes] = None)

   SysExParser


   .. py:attribute:: sysex_dict


   .. py:attribute:: log_folder


   .. py:method:: from_bytes(sysex_data: bytes) -> None

      from_bytes

      :param sysex_data: bytes
      :return: None



   .. py:method:: parse()

      parse

      :return: dict sysex dictionary {"JD_XI_HEADER": "f041100000000e", "ADDRESS": "12190150", ...}



   .. py:method:: parse_bytes(sysex_data: bytes)

      parse_bytes

      :param sysex_data: bytes
      :return: dict sysex dictionary {"JD_XI_HEADER": "f041100000000e", "ADDRESS": "12190150", ...}



   .. py:method:: _is_valid_sysex() -> bool

      Checks if the SysEx message starts and ends with the correct bytes.



   .. py:method:: _verify_header() -> bool

      Checks if the SysEx header matches the JD-Xi model ID.



