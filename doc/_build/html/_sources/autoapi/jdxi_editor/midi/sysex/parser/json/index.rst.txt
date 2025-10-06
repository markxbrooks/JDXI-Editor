jdxi_editor.midi.sysex.parser.json
==================================

.. py:module:: jdxi_editor.midi.sysex.parser.json

.. autoapi-nested-parse::

   Sysex parser
   # Example usage:
   >>> json_data = [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x7E, 0x7F, 0x06, 0x01, 0x19, 0x01, 0x00,
   >>>               0xF7]  # Example SysEx data

   >>> parser = JDXiSysExParser(json_data)
   >>> parsed_data = parser.parse()
   >>> log.message(f"Parsed Data: {parsed_data}")



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.sysex.parser.json.JDXiJsonSysexParser


Module Contents
---------------

.. py:class:: JDXiJsonSysexParser(json_sysex_data: Optional[str] = None)

   JDXiJsonSysexParser


   .. py:attribute:: sysex_data_json
      :value: None



   .. py:attribute:: log_folder


   .. py:method:: from_json(json_sysex_data: str) -> None

      from json

      :param json_sysex_data: str
      :return: None



   .. py:method:: parse() -> Optional[Dict[str, Any]]

      Parse the stored JSON string into a dictionary.

      :return: Dictionary representation of SysEx data, or None if parsing fails.



   .. py:method:: parse_json(json_sysex_data: str) -> Optional[Dict[str, Any]]

      parse json

      :param json_sysex_data: str
      :return: dict



