jdxi_editor.midi.sysex.parser.tone_mapper
=========================================

.. py:module:: jdxi_editor.midi.sysex.parser.tone_mapper

.. autoapi-nested-parse::

   tone mapper functions



Functions
---------

.. autoapisummary::

   jdxi_editor.midi.sysex.parser.tone_mapper.get_temporary_area
   jdxi_editor.midi.sysex.parser.tone_mapper.get_partial_address
   jdxi_editor.midi.sysex.parser.tone_mapper.get_drum_tone
   jdxi_editor.midi.sysex.parser.tone_mapper.get_synth_tone


Module Contents
---------------

.. py:function:: get_temporary_area(data: bytes) -> str

   Map address bytes to corresponding temporary area.

   :param data: bytes SysEx message data
   :return: str Temporary Area: TEMPORARY_PROGRAM, ANALOG_SYNTH, DIGITAL_SYNTH_1 ...


.. py:function:: get_partial_address(part_name: str) -> str

   Map partial address to corresponding temporary area.

   :param part_name: str
   :return: str


.. py:function:: get_drum_tone(byte_value: int) -> tuple[str, int]

   Map byte value to corresponding synth tone.

   :param byte_value: int
   :return: str


.. py:function:: get_synth_tone(byte_value: int) -> tuple[str, int]

   Map byte value to corresponding synth tone.

   :param byte_value: int byte value to query
   :return: tuple[str, int]


