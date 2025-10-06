jdxi_editor.midi.message.channel
================================

.. py:module:: jdxi_editor.midi.message.channel

.. autoapi-nested-parse::

   MIDI Channel Message Module
   ===========================

   This module defines the `ChannelMessage` class, which represents a MIDI Channel Voice Message.
   It extends the `Message` base class and provides a structured way to handle MIDI messages
   that operate on specific channels, such as Note On, Note Off, and Control Change.

   Classes:
       - ChannelMessage: Represents a MIDI channel message with status, data bytes, and channel information.

   Features:
       - Validates MIDI channel range (0-15).
       - Constructs MIDI messages with status and data bytes.
       - Converts messages to byte lists for transmission.

   Usage Example:
       >>> msg = ChannelMessage(status=0x90, data1=60, data2=127, channel=1)  # Note On for Middle C
       >>> msg.to_message_list()
       [145, 60, 127]  # (0x91 in hex: Note On for channel 1)



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.channel.ChannelMessage


Module Contents
---------------

.. py:class:: ChannelMessage

   Bases: :py:obj:`jdxi_editor.midi.message.midi.MidiMessage`


   MIDI Channel Message


   .. py:attribute:: channel
      :type:  int
      :value: 0



   .. py:attribute:: status
      :type:  int
      :value: 0



   .. py:attribute:: data1
      :type:  Optional[int]
      :value: None



   .. py:attribute:: data2
      :type:  Optional[int]
      :value: None



   .. py:method:: to_message_list() -> List[int]

      Convert to list of bytes for sending



