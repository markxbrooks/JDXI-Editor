jdxi_editor.midi.utils.byte
===========================

.. py:module:: jdxi_editor.midi.utils.byte

.. autoapi-nested-parse::

   byte data processing



Functions
---------

.. autoapisummary::

   jdxi_editor.midi.utils.byte.split_16bit_value_to_bytes
   jdxi_editor.midi.utils.byte.split_8bit_value_to_nibbles
   jdxi_editor.midi.utils.byte.encode_roland_7bit
   jdxi_editor.midi.utils.byte.decode_roland_4byte
   jdxi_editor.midi.utils.byte.encode_roland_4byte
   jdxi_editor.midi.utils.byte.split_16bit_value_to_nibbles
   jdxi_editor.midi.utils.byte.split_32bit_value_to_nibbles
   jdxi_editor.midi.utils.byte.join_nibbles_to_32bit
   jdxi_editor.midi.utils.byte.join_nibbles_to_16bit
   jdxi_editor.midi.utils.byte.encode_14bit_to_7bit_midi_bytes


Module Contents
---------------

.. py:function:: split_16bit_value_to_bytes(value: int) -> list[int]

   Splits a 16-bit integer into two 8-bit bytes: [LMB, LSB]

   :param value: int (0–65535)
   :return: list[int] [Most Significant Byte, Least Significant Byte]


.. py:function:: split_8bit_value_to_nibbles(value: int) -> list[int]

   Splits an 8-bit integer into two 4-bit nibbles.

   :param value: int (0–255)
   :return: list[int] with two 4-bit values [upper_nibble, lower_nibble]


.. py:function:: encode_roland_7bit(value: int) -> list[int]

   Encodes a 28-bit value into 4x 7-bit MIDI bytes (MSB first).


.. py:function:: decode_roland_4byte(data_bytes: list[int]) -> int

   decode_roland_4byte

   :param data_bytes: list[int]
   :return: int
   decode_roland_4byte([0x08, 0x00, 0x00, 0x01])  # → 1048577


.. py:function:: encode_roland_4byte(value: int) -> list[int]

   encode_roland_4byte

   :param value: int
   :return: list[int]
   >>> encode_roland_4byte(0)  # [0x00, 0x00, 0x00, 0x00]
   >>> encode_roland_4byte(1)  # [0x00, 0x00, 0x00, 0x01]
   >>> encode_roland_4byte(1048576)  # [0x08, 0x00, 0x00, 0x00]


.. py:function:: split_16bit_value_to_nibbles(value: int) -> list[int]

   Splits an integer into exactly 4 nibbles (4-bit values), padding with zeros if necessary

   :param value: int
   :return: list[int]


.. py:function:: split_32bit_value_to_nibbles(value: int) -> list[int]

   Splits an integer into 8 nibbles (4-bit values), for 32-bit Roland SysEx DT1 data.

   :param value: int
   :return: list[int]


.. py:function:: join_nibbles_to_32bit(nibbles: list[int]) -> int

   Combines a list of 8 nibbles (4-bit values) into a 32-bit integer

   :param nibbles: list[int]
   :return: int


.. py:function:: join_nibbles_to_16bit(nibbles: list[int]) -> int

   Combines a list of 4 nibbles (4-bit values) into a 16-bit integer

   :param nibbles: list[int]
   :return: int


.. py:function:: encode_14bit_to_7bit_midi_bytes(value: int) -> list[int]

       Encodes a 14-bit integer into two 7-bit MIDI-safe bytes.
       MIDI SysEx requires all data bytes to be in the range 0x00–0x7F.
       # Example usage:
   >>>     value = 0x1234  # 4660 in decimal
   >>>     data_bytes = encode_14bit_to_7bit_midi_bytes(value)
   >>>     print(data_bytes)  # Output: [0x24, 0x34] → [36, 52]




