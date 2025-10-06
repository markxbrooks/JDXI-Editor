jdxi_editor.midi.sysex.validation
=================================

.. py:module:: jdxi_editor.midi.sysex.validation


Functions
---------

.. autoapisummary::

   jdxi_editor.midi.sysex.validation.validate_raw_sysex_message
   jdxi_editor.midi.sysex.validation.validate_raw_midi_message
   jdxi_editor.midi.sysex.validation.validate_midi_message


Module Contents
---------------

.. py:function:: validate_raw_sysex_message(message: List[int]) -> bool

   Validate JD-Xi SysEx message format


.. py:function:: validate_raw_midi_message(message: Iterable[int]) -> bool

   Validate a raw MIDI message.

   This function checks that the message is non-empty and all values are
   within the valid MIDI byte range (0–255).

   :param message: A MIDI message represented as a list of integers or a bytes object.
   :type message: Iterable[int], can be a list, bytes, tuple, set
   :return: True if the message is valid, False otherwise.
   :rtype: bool


.. py:function:: validate_midi_message(message: Iterable[int]) -> bool

   Validate a raw MIDI message.

   This function checks that the message is non-empty and all values are
   within the valid MIDI byte range (0–255).

   :param message: A MIDI message represented as a list of integers or a bytes object.
   :type message: Iterable[int], can be a list, bytes, tuple, set
   :return: True if the message is valid, False otherwise.
   :rtype: bool


