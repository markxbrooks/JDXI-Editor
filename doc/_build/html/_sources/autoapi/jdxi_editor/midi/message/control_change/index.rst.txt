jdxi_editor.midi.message.control_change
=======================================

.. py:module:: jdxi_editor.midi.message.control_change

.. autoapi-nested-parse::

   MIDI Control Change Message Module
   ==================================

   This module defines the `ControlChangeMessage` class, which represents a MIDI Control Change (CC) message.
   It extends the `ChannelMessage` class to handle messages used for real-time parameter adjustments in MIDI devices.

   Classes:
       - ControlChangeMessage: Represents a MIDI Control Change message with controller and value parameters.

   Features:
       - Inherits channel-based messaging from `ChannelMessage`.
       - Automatically assigns controller and value to data bytes.
       - Uses status byte `0xB0` for Control Change messages.

   Usage Example:
       >>> msg = ControlChangeMessage(channel=1, controller=7, value=100)  # Volume control on channel 1
       >>> msg.to_list()
       [177, 7, 100]  # (0xB1 in hex: CC message for channel 1)



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.message.control_change.ControlChangeMessage


Module Contents
---------------

.. py:class:: ControlChangeMessage

   Bases: :py:obj:`jdxi_editor.midi.message.midi.MidiMessage`


   MIDI Control Change message


   .. py:attribute:: channel
      :type:  int


   .. py:attribute:: controller
      :type:  int


   .. py:attribute:: value
      :type:  int


   .. py:attribute:: status
      :type:  int
      :value: 176



   .. py:method:: __post_init__()


   .. py:method:: to_message_list() -> List[int]

      Convert Control Change message to a list of bytes for sending

      :return: list



