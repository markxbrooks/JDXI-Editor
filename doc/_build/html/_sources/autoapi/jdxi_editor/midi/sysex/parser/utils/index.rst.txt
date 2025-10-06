jdxi_editor.midi.sysex.parser.utils
===================================

.. py:module:: jdxi_editor.midi.sysex.parser.utils

.. autoapi-nested-parse::

   JD-Xi SysEx Parser Module

   This module provides functions to parse JD-Xi synthesizer SysEx data, extracting relevant tone parameters
   for Digital, Analog, and Drum Kit sounds. It includes utilities for safely retrieving values, mapping
   address bytes to synth areas, extracting tone names, and identifying tone types.

   Functions:
       - safe_get: Safely retrieves values from SysEx data.
       - extract_hex: Extracts address hex value from SysEx data.
       - get_temporary_area: Maps SysEx address bytes to temporary areas.
       - get_synth_tone: Maps byte values to synth tone types.
       - extract_tone_name: Extracts and cleans the tone name from SysEx data.
       - parse_parameters: Parses JD-Xi tone parameters for different synth types.
       - parse_sysex: Parses JD-Xi tone data from SysEx messages.



Attributes
----------

.. autoapisummary::

   jdxi_editor.midi.sysex.parser.utils.UNKNOWN
   jdxi_editor.midi.sysex.parser.utils.UNKNOWN_AREA


Functions
---------

.. autoapisummary::

   jdxi_editor.midi.sysex.parser.utils.get_byte_offset_by_tone_name
   jdxi_editor.midi.sysex.parser.utils.extract_hex
   jdxi_editor.midi.sysex.parser.utils.extract_tone_name
   jdxi_editor.midi.sysex.parser.utils.parse_parameters
   jdxi_editor.midi.sysex.parser.utils.parse_single_parameter
   jdxi_editor.midi.sysex.parser.utils.safe_extract
   jdxi_editor.midi.sysex.parser.utils.address_to_index
   jdxi_editor.midi.sysex.parser.utils.initialize_parameters
   jdxi_editor.midi.sysex.parser.utils._return_minimal_metadata
   jdxi_editor.midi.sysex.parser.utils._get_tone_from_data
   jdxi_editor.midi.sysex.parser.utils.parse_sysex
   jdxi_editor.midi.sysex.parser.utils.update_data_with_parsed_parameters
   jdxi_editor.midi.sysex.parser.utils.update_short_data_with_parsed_parameters


Module Contents
---------------

.. py:data:: UNKNOWN
   :value: 'Unknown'


.. py:data:: UNKNOWN_AREA
   :value: 'Unknown area'


.. py:function:: get_byte_offset_by_tone_name(data: bytes, index: int, offset: int = 12, default: int = 0) -> int

   Safely retrieve values from SysEx data with an optional offset.

   :param data: bytes SysEx message data
   :param index: int index of the byte to parse
   :param offset: int Offset because of TONE_NAME
   :param default: int
   :return: int byte offset


.. py:function:: extract_hex(data: bytes, start: int, end: int, default: str = 'N/A') -> str

   Extract address hex value from data safely.

   :param data: bytes SysEx message data
   :param start: int Starting byte
   :param end: int End byte
   :param default: str
   :return: str hex form of byte string in range


.. py:function:: extract_tone_name(data: bytes) -> str

   Extract and clean the tone name from SysEx data.

   :param data: bytes SysEx message data
   :return: str tone name, cleaned up


.. py:function:: parse_parameters(data: bytes, parameter_type: Iterable) -> Dict[str, int]

   Parses JD-Xi tone parameters from SysEx data for Digital, Analog, and Digital Common types.

   :param data: bytes SysEx message data
   :param parameter_type: Iterable Type
   :return: Dict[str, int]


.. py:function:: parse_single_parameter(data: bytes, parameter_type: jdxi_editor.midi.data.parameter.synth.AddressParameter) -> Dict[str, int]

   Parses JD-Xi tone parameters from SysEx data for Digital, Analog, and Digital Common types.

   :param data: bytes SysEx message data
   :param parameter_type: Type
   :return: Dict[str, int]


.. py:function:: safe_extract(data: bytes, start: int, end: int) -> str

   Safely extract hex data from a byte sequence, or return "Unknown" if out of bounds.

   :param data: bytes
   :param start: int start address position
   :param end: int end address position
   :return: str hex


.. py:function:: address_to_index(msb: int, lsb: int) -> int

   Convert a 2-byte address (MSB, LSB) to a flat integer index.
   For example, MSB=0x01, LSB=0x15 → 0x0115 → 277.
   :param msb: int Most Significant Byte (0–255)
   :param lsb: int Least Significant Byte (0–255)
   :return: int address index


.. py:function:: initialize_parameters(data: bytes) -> Dict[str, str]

   Initialize parameters with essential fields extracted from SysEx data.

   :param data: bytes SysEx message data
   :return: Dict[str, str]


.. py:function:: _return_minimal_metadata(data: bytes) -> Dict[str, str]

   Return minimal metadata for a JD-Xi SysEx message.

   :param data: bytes SysEx message data
   :return: Dict[str, str]


.. py:function:: _get_tone_from_data(data: bytes, temporary_area: str) -> tuple[str, int]

   Determines synth tone type and offset from SysEx data.

   :param data: bytes SysEx Data
   :param temporary_area: str
   :return: tuple[str, int] tone type and byte offset


.. py:function:: parse_sysex(data: bytes) -> Dict[str, str]

   Parses JD-Xi tone data from SysEx messages.

   :param data: bytes SysEx message bytes
   :return: Dict[str, str] Dictionary with parsed tone parameters


.. py:function:: update_data_with_parsed_parameters(data: bytes, parameter_cls: Iterable, parsed_data: dict)

   Update parsed_data with parsed parameters

   :param data: bytes SysEx message data
   :param parameter_cls: Iterable AddressParameter
   :param parsed_data: dict
   :return: None Parsed_data is updated in place


.. py:function:: update_short_data_with_parsed_parameters(data: bytes, parameter_cls: jdxi_editor.midi.data.parameter.synth.AddressParameter, parsed_data: dict)

   Update parsed_data with parsed parameters

   :param data: bytes SysEx message data
   :param parameter_cls: AddressParameter
   :param parsed_data: dict
   :return: None Parsed_data is updated in place


