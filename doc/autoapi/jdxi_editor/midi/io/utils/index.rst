jdxi_editor.midi.io.utils
=========================

.. py:module:: jdxi_editor.midi.io.utils

.. autoapi-nested-parse::

   utility functions



Functions
---------

.. autoapisummary::

   jdxi_editor.midi.io.utils.format_midi_message_to_hex_string
   jdxi_editor.midi.io.utils.increment_if_lsb_exceeds_7bit
   jdxi_editor.midi.io.utils.nibble_data
   jdxi_editor.midi.io.utils.rtmidi_to_mido
   jdxi_editor.midi.io.utils.convert_to_mido_message
   jdxi_editor.midi.io.utils.mido_message_data_to_byte_list
   jdxi_editor.midi.io.utils.handle_identity_request


Module Contents
---------------

.. py:function:: format_midi_message_to_hex_string(message: Iterable[int]) -> str

   Convert a list of MIDI byte values to a space-separated hex string.

   :param message: Iterable[int]
   :return: str A string like "F0 41 10 00 00 00 0E ... F7"


.. py:function:: increment_if_lsb_exceeds_7bit(msb: int, lsb: int) -> int

   Increments the MSB if the LSB exceeds 7-bit maximum (127).

   :param msb: Most significant byte (int)
   :param lsb: Least significant byte (int)
   :return: Adjusted MSB (int)


.. py:function:: nibble_data(data: list[int]) -> list[int]

   Ensures all values in the data list are 7-bit safe (0–127).
   Bytes > 127 are split into two 4-bit nibbles.
   :param data: List of integer byte values (0–255)
   :return: List of 7-bit-safe integers (0–127)


.. py:function:: rtmidi_to_mido(byte_message: bytes) -> Union[bool, mido.Message]

   Convert an rtmidi message to address mido message.

   :param byte_message: bytes
   :return: Union[bool, mido.Message]: mido message on success or False otherwise


.. py:function:: convert_to_mido_message(message_content: List[int]) -> Optional[Union[mido.Message, List[mido.Message]]]

   Convert raw MIDI message content to a mido.Message object or a list of them.

   :param message_content: List[int] byte list
   :return: Optional[Union[mido.Message, List[mido.Message]] either a single mido message or a list of mido messages


.. py:function:: mido_message_data_to_byte_list(message: mido.Message) -> bytes

   mido message data to byte list

   :param message: mido.Message
   :return: bytes


.. py:function:: handle_identity_request(message: mido.Message) -> dict

   Handles an incoming Identity Request

   :param message: mido.Message incoming response to identity request
   :return: dict device details


