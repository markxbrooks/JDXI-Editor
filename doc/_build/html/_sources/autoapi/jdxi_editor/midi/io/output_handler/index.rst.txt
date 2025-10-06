jdxi_editor.midi.io.output_handler
==================================

.. py:module:: jdxi_editor.midi.io.output_handler

.. autoapi-nested-parse::

   MIDI Output Handler
   ===================

   This module provides the `MIDIOutHandler` class for managing MIDI output, allowing users to send
   note-on, note-off, and control change messages through address specified MIDI output port.

   Dependencies:
       - rtmidi: A library for working with MIDI messages and ports.

   Example usage:
       handler = MIDIOutHandler("MIDI Output Port")
       handler.send_note_on(60, velocity=100)
       handler.send_note_off(60)
       handler.send_control_change(7, 127)
       handler.close()



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.io.output_handler.MidiOutHandler


Module Contents
---------------

.. py:class:: MidiOutHandler(parent=None)

   Bases: :py:obj:`jdxi_editor.midi.io.controller.MidiIOController`


   Helper class for MIDI communication with the JD-Xi.


   .. py:attribute:: midi_message_outgoing


   .. py:attribute:: parent
      :value: None



   .. py:attribute:: channel
      :value: 1



   .. py:attribute:: sysex_parser


   .. py:method:: send_raw_message(message: Iterable[int]) -> bool

      Send a validated raw MIDI message through the output port.
      This method logs the message, checks the validity using `validate_midi_message`,
      and attempts to send it via the MIDI output port.
      :param message: A MIDI message represented as a list of integers or a bytes object.
      :type message: Union[bytes, List[int]]
      :return: True if the message was successfully sent, False otherwise.
      :rtype: bool



   .. py:method:: send_note_on(note: int = 60, velocity: int = 127, channel: int = 1) -> None

      Send 'Note On' message to the specified MIDI channel.

      :param note: int MIDI note number (0–127), default is 60 (Middle C).
      :param velocity: int Note velocity (0–127), default is 127.
      :param channel: int MIDI channel (1–16), default is 1.



   .. py:method:: send_note_off(note: int = 60, velocity: int = 0, channel: int = 1) -> None

      Send address 'Note Off' message

      :param note: int MIDI note number (0–127), default is 60 (Middle C).
      :param velocity: int Note velocity (0–127), default is 127.
      :param channel: int MIDI channel (1–16), default is 1.



   .. py:method:: send_channel_message(status: int, data1: Optional[int] = None, data2: Optional[int] = None, channel: int = 1) -> None

      Send a MIDI Channel Message.

      :param status: int Status byte (e.g., NOTE_ON, NOTE_OFF, CONTROL_CHANGE).
      :param data1: Optional[int]): First data byte, typically a note or controller number.
      :param data2: Optional[int]): Second data byte, typically velocity or value.
      :param channel: int MIDI channel (1-based, range 1-16).
      :raises: ValueError If the channel is out of range (1-16).



   .. py:method:: send_bank_select(msb: int, lsb: int, channel: int = 0) -> bool

      Send address bank select message.

      :param msb: int Upper byte of the bank.
      :param lsb: int Lower byte of the bank.
      :param channel: int midi channel (0-15).
      :return: bool True if successful, False otherwise.



   .. py:method:: send_identity_request() -> bool

      Send identity request message (Universal System Exclusive).

      :return: bool True if the message was sent successfully, False otherwise.



   .. py:method:: send_midi_message(sysex_message: jdxi_editor.midi.message.MidiMessage) -> bool

      Send SysEx parameter change message using a MidiMessage.

      :param sysex_message: MidiMessage instance to be converted and sent.
      :return: True if the message was successfully sent, False otherwise.



   .. py:method:: send_program_change(program: int, channel: int = 0) -> bool

      Send address program change message.

      :param program: int Program number (0-127).
      :param channel: int MIDI channel (0-15).
      :return: True if successful, False otherwise.



   .. py:method:: send_control_change(controller: int, value: int, channel: int = 0) -> bool

      Send control change message.

      :param controller: int Controller number (0–127).
      :param value: int Controller value (0–127).
      :param channel: int MIDI channel (0–15).
      :return: bool True if successful, False otherwise.



   .. py:method:: send_rpn(parameter: int, value: int, channel: int = 0) -> bool

      Send a Registered Parameter Number (RPN) message via MIDI Control Change.

      :param parameter: int RPN parameter number (0–16383).
      :param value: int Parameter value (0–16383).
      :param channel: int MIDI channel (0–15).
      :return: True if messages sent successfully, False otherwise.



   .. py:method:: send_nrpn(parameter: int, value: int, channel: int = 0, use_14bit: bool = False) -> bool

      Send a Non-Registered Parameter Number (NRPN) message via MIDI Control Change.

      :param parameter: int NRPN parameter number (0–16383).
      :param value: int Parameter value (0–16383 for 14-bit, 0–127 for 7-bit).
      :param channel: int MIDI channel (0–15).
      :param use_14bit: bool If True, send both MSB and LSB for value (14-bit). If False, send only MSB (7-bit).
      :return: True if all messages were sent successfully, False otherwise.



   .. py:method:: send_bank_select_and_program_change(channel: int, bank_msb: int, bank_lsb: int, program: int) -> bool

      Sends Bank Select and Program Change messages.

      :param channel: int MIDI channel (1-16).
      :param bank_msb: int Bank MSB value.
      :param bank_lsb: int Bank LSB value.
      :param program: int Program number.
      :return: bool True if all messages are sent successfully, False otherwise.



   .. py:method:: identify_device() -> None

      Send Identity Request and verify response

      :return: None



   .. py:method:: send_message(message: jdxi_editor.midi.message.MidiMessage) -> None

      unpack the message list and send it

      :param message: MidiMessage
      :return: None



