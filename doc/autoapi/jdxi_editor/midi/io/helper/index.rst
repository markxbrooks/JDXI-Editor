jdxi_editor.midi.io.helper
==========================

.. py:module:: jdxi_editor.midi.io.helper

.. autoapi-nested-parse::

   MIDI Helper Module
   ==================

   This module provides address unified helper class for MIDI communication with the Roland JD-Xi.
   It integrates both MIDI input and output functionalities by combining the features of
   the MIDIInHandler and MIDIOutHandler classes.

   Classes:
       MIDIHelper: A helper class that inherits from both MIDIInHandler and MIDIOutHandler,
                   offering address consolidated interface for handling MIDI messages (including
                   SysEx messages in JSON format) for the JD-Xi synthesizer.

   Dependencies:
       - PySide6.QtCore.Signal for Qt signal support.
       - jdxi_editor.midi.input_handler.MIDIInHandler for handling incoming MIDI messages.
       - jdxi_editor.midi.output_handler.MIDIOutHandler for handling outgoing MIDI messages.



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.io.helper.MidiIOHelper


Module Contents
---------------

.. py:class:: MidiIOHelper(parent=None)

   Bases: :py:obj:`jdxi_editor.midi.io.input_handler.MidiInHandler`, :py:obj:`jdxi_editor.midi.io.output_handler.MidiOutHandler`


   MidiIOHelper

   Class to handle midi input/output


   .. py:attribute:: _instance
      :value: None



   .. py:attribute:: _current_out_port
      :value: None



   .. py:attribute:: _current_in_port
      :value: None



   .. py:attribute:: in_port_name
      :value: ''



   .. py:attribute:: out_port_name
      :value: ''



   .. py:method:: send_mido_message(msg: mido.Message)

      send_mido_message

      :param msg: mido.Message
      :return:



   .. py:method:: load_patch(file_path: str)

      Load the JSON patch as a string and emit it.

      :param file_path: str
      :return: None



   .. py:method:: __str__()

      __str__

      :return: str String representation



   .. py:method:: __repr__()


   .. py:method:: load_sysx_patch(file_path: str)

      Load the SysEx patch from a file and emit it.

      :param file_path: str File path as a string
      :return: None



   .. py:method:: set_midi_ports(in_port: str, out_port: str) -> bool

      Set MIDI input and output ports

      :param in_port: str
      :param out_port: str
      :return: bool True on success, False otherwise



   .. py:method:: connect_port_names(in_port: str, out_port: str) -> bool

      Attempt to automatically connect to JD-Xi MIDI ports.

      :param in_port: str
      :param out_port: str
      :return: bool True on success, False otherwise



   .. py:method:: reconnect_port_names(in_port: str, out_port: str) -> None

      Reconnect ports

      :param in_port: str
      :param out_port: str
      :return: None



   .. py:method:: auto_connect_jdxi() -> bool

      Attempt to automatically connect to JD-Xi MIDI ports.

      :return: bool True on success, False otherwise



