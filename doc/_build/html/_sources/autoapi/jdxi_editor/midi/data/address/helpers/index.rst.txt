jdxi_editor.midi.data.address.helpers
=====================================

.. py:module:: jdxi_editor.midi.data.address.helpers

.. autoapi-nested-parse::

   helpers.py
   Helper functions for SysEx address manipulation and parsing.
   This module provides utilities to apply address offsets, convert addresses to hex strings,
   and parse SysEx addresses into a JSON-like structure.
   It also includes functions to find matching symbols in provided base classes.
   Functions:
   - apply_address_offset: Applies an offset to a base SysEx address.
   - address_to_hex_string: Converts a SysEx address to a hex string.
   - parse_sysex_address_json: Parses a SysEx address into a JSON-like structure.
   - find_matching_symbol: Finds a matching symbol in provided base classes.



Functions
---------

.. autoapisummary::

   jdxi_editor.midi.data.address.helpers.apply_address_offset
   jdxi_editor.midi.data.address.helpers.address_to_hex_string
   jdxi_editor.midi.data.address.helpers.parse_sysex_address_json
   jdxi_editor.midi.data.address.helpers.find_matching_symbol


Module Contents
---------------

.. py:function:: apply_address_offset(base_address: jdxi_editor.midi.data.address.address.RolandSysExAddress, param: jdxi_editor.midi.data.parameter.synth.AddressParameter) -> jdxi_editor.midi.data.address.address.RolandSysExAddress

   Applies the offset of a parameter to a base address.

   :param base_address: RolandSysExAddress
   :param param: AddressParameter
   :return: RolandSysExAddress


.. py:function:: address_to_hex_string(address: Tuple[int, int, int, int]) -> str

   Converts a 4-byte SysEx address into a hex string.

   :param address: Tuple[int, int, int, int]
   :return: str


.. py:function:: parse_sysex_address_json(address: Tuple[int, int, int, int], base_classes: Tuple[Type[Any], Ellipsis]) -> Dict[str, Any]

   Parses a SysEx address into a JSON-like structure.

   :param address: Tuple[int, int, int, int]
   :param base_classes: Tuple[Type[Any], ...]
   :return: Dict[str, Any]


.. py:function:: find_matching_symbol(value: int, base_classes: Tuple[Type[Any], Ellipsis]) -> Union[Dict[str, Any], None]

   Finds a matching symbol in the provided base classes.

   :param value: int
   :param base_classes: Tuple[Type[Any], ...]
   :return: Union[Dict[str, Any], None]


