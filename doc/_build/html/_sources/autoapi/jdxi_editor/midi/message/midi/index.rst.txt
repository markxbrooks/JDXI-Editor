jdxi_editor.midi.message.midi
=============================

.. py:module:: jdxi_editor.midi.message.midi

.. autoapi-nested-parse::

   MIDI Message Module
   ===================

   This module provides a base class for handling MIDI messages in a structured manner.
   It defines the `Message` class, which serves as the foundation for various types of
   MIDI messages, ensuring proper formatting and conversion to MIDI-compliant byte sequences.

   Classes:
       - Message: Base class for MIDI messages, enforcing structure and conversion methods.

   Features:
       - Provides constants for MIDI message handling (status mask, channel mask, max value).
       - Ensures subclass implementation of the `to_list` method for MIDI byte conversion.
       - Offers utility methods for converting messages to bytes and hexadecimal string format.

   Usage Example:
       >>> class NoteOnMessage(MidiMessage):
       ...     def to_list(self):
       ...         return [0x90, 60, 127]  # Note On for Middle C with velocity 127
       ...
       >>> msg = NoteOnMessage()
       >>> msg.to_bytes()
       b'<'
   import jdxi_editor.midi.sysex.utils    >>> jdxi_editor.midi.sysex.utils.to_hex_string()
       '90 3C 7F'



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.midi.MidiMessage


Module Contents
---------------

.. py:class:: MidiMessage

   MIDI message base class


   .. py:attribute:: MIDI_MAX_VALUE
      :value: 127



   .. py:attribute:: MIDI_STATUS_MASK
      :value: 240



   .. py:attribute:: MIDI_CHANNEL_MASK
      :value: 15



   .. py:method:: to_message_list() -> List[int]
      :abstractmethod:


      Convert to list of bytes for sending, must be implemented in subclass



   .. py:method:: to_bytes() -> bytes

      Convert to bytes for sending



   .. py:method:: to_hex_string() -> str

      Convert message to a formatted hexadecimal string.



