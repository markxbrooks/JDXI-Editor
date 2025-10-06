jdxi_editor.midi.message.program_change
=======================================

.. py:module:: jdxi_editor.midi.message.program_change

.. autoapi-nested-parse::

   MIDI Program Change Message Module

   This module defines the `ProgramChangeMessage` class, which represents a MIDI Program Change message.
   MIDI Program Change messages are used to change the program (preset) on a MIDI device, selecting a new sound or preset.

   Classes:
       - ProgramChangeMessage: Represents a MIDI Program Change message that can be sent to change the program on a specified channel.

   Features:
       - Inherits from the `ChannelMessage` class, utilizing the standard MIDI channel message format.
       - The message includes a program number to select a new program (preset).
       - Provides automatic initialization of the `data1` field with the program value, with `data2` set to `None` (as Program Change messages only use one data byte).

   Constants:
       - STATUS_BYTE (0xC0): The status byte for a Program Change message in the MIDI protocol.

   Usage Example:
       >>> program_msg = ProgramChangeMessage(program=5)
       >>> program_msg.to_message_list()
       [0xC0, 5]



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.program_change.ProgramChangeMessage


Module Contents
---------------

.. py:class:: ProgramChangeMessage

   Bases: :py:obj:`jdxi_editor.midi.message.channel.ChannelMessage`


   MIDI Program Change message


   .. py:attribute:: status
      :type:  int
      :value: 192



   .. py:attribute:: program
      :type:  int
      :value: 0



   .. py:method:: __post_init__()


