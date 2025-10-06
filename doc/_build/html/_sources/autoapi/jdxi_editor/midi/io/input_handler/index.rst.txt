jdxi_editor.midi.io.input_handler
=================================

.. py:module:: jdxi_editor.midi.io.input_handler

.. autoapi-nested-parse::

   MIDIInHandler Module
   ====================

   This module provides the MIDIInHandler class for handling MIDI communication with the Roland JD-Xi.
   It supports processing of SysEx, Control Change, Program Change, Note On/Off, and Clock messages.
   The handler decodes incoming MIDI messages, routes them to appropriate sub-handlers, and emits Qt signals
   for integration with PySide6-based applications.

   Classes:
       MIDIInHandler: Processes incoming MIDI messages, handles SysEx tone data parsing, and emits signals
                      for further processing in the application.

   Usage:
       Instantiate MIDIInHandler and connect to its signals to integrate MIDI data handling with your application.

   Dependencies:
       - PySide6.QtCore.Signal for signal emission.
       - pubsub for publish/subscribe messaging.
       - jdxi_manager modules for data handling, parsing, and MIDI processing.



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.io.input_handler.MidiInHandler


Functions
---------

.. autoapisummary::

   jdxi_editor.midi.io.input_handler.add_or_replace_program_and_save
   jdxi_editor.midi.io.input_handler.add_or_replace_program_and_save_old
   jdxi_editor.midi.io.input_handler.load_programs
   jdxi_editor.midi.io.input_handler.save_programs
   jdxi_editor.midi.io.input_handler.save_programs_old


Module Contents
---------------

.. py:function:: add_or_replace_program_and_save(new_program: jdxi_editor.jdxi.program.program.JDXiProgram) -> bool

   Add a new program to the list, replacing any with matching ID or PC.

   :param new_program: JDXiProgram to add or replace.
   :return: True if successfully added/replaced and saved, False otherwise.


.. py:function:: add_or_replace_program_and_save_old(new_program: jdxi_editor.jdxi.program.program.JDXiProgram) -> bool

   add_or_replace_program_and_save

   :param new_program:
   :return:


.. py:function:: load_programs() -> List[Dict[str, str]]

.. py:function:: save_programs(program_list: List[Dict[str, str]]) -> None

   Save the program list to USER_PROGRAMS_FILE, creating the file and directory if needed.

   :param program_list: List of program dictionaries.


.. py:function:: save_programs_old(program_list: List[Dict[str, str]]) -> None

   save_programs

   :param program_list: List[Dict[str, str]]
   :return: None


.. py:class:: MidiInHandler(parent: Optional[Any] = None)

   Bases: :py:obj:`jdxi_editor.midi.io.controller.MidiIOController`


   Helper class for MIDI communication with the JD-Xi.

   This class listens to incoming MIDI messages, processes them based on
   their preset_type, and emits corresponding signals. It handles SysEx, Control
   Change, Program Change, Note On/Off, and Clock messages.


   .. py:attribute:: update_tone_name


   .. py:attribute:: update_program_name


   .. py:attribute:: midi_message_incoming


   .. py:attribute:: midi_program_changed


   .. py:attribute:: midi_control_changed


   .. py:attribute:: midi_sysex_json


   .. py:attribute:: parent
      :value: None



   .. py:attribute:: callbacks
      :type:  List[Callable]
      :value: []



   .. py:attribute:: channel
      :type:  int
      :value: 1



   .. py:attribute:: preset_number
      :type:  int
      :value: 0



   .. py:attribute:: cc_msb_value
      :type:  int
      :value: 0



   .. py:attribute:: cc_lsb_value
      :type:  int
      :value: 0



   .. py:attribute:: sysex_parser


   .. py:attribute:: _incoming_preset_data


   .. py:method:: midi_callback(message: list[Any], data: Any) -> None

      callback for rtmidi
      mido doesn't have callbacks, so we convert
      :param message: list[Any]
      :param data: Any



   .. py:method:: reopen_input_port_name(in_port: str) -> bool

      Reopen the current MIDI input port and reattach the callback.

      :param in_port: str
      :return: bool



   .. py:method:: set_callback(callback: Callable) -> None

      Set address callback for MIDI messages.

      :param callback: The callback function to be set.



   .. py:method:: _handle_midi_message(message: Any) -> None

      Routes MIDI messages to appropriate handlers

      :param message: Any
      :return: None



   .. py:method:: _handle_note_change(message: mido.Message, preset_data: dict) -> None

      Handle Note On and Note Off MIDI messages.

      :param message: Any The MIDI message.
      :param preset_data: Dictionary for preset data modifications.



   .. py:method:: _handle_clock(message: mido.Message, preset_data: dict) -> None

      Handle MIDI Clock messages quietly.

      :param message: mido.Message The MIDI message.
      :param preset_data: Dictionary for preset data modifications.



   .. py:method:: _handle_sysex_message(message: mido.Message, preset_data: dict) -> None

      Handle SysEx MIDI messages from the Roland JD-Xi.

      Processes SysEx data, attempts to parse tone data, and extracts command
      and parameter information for further processing.

      :param message: mido.Message The MIDI SysEx message.
      :param preset_data: Dictionary for preset data modifications.



   .. py:method:: _handle_control_change(message: mido.Message, preset_data: dict) -> None

      Handle Control Change (CC) MIDI messages.

      :param message: mido.Message The MIDI Control Change message.
      :param preset_data: Dictionary for preset data modifications.



   .. py:method:: _handle_program_change(message: mido.Message, preset_data: dict) -> None

      Handle Program Change (PC) MIDI messages.

      Processes program changes and maps them to preset changes based on
      CC values.

      :param message: mido.Message The MIDI Program Change message.
      :param preset_data: Dictionary for preset data modifications.



   .. py:method:: _emit_program_or_tone_name(parsed_data: dict) -> None

      Emits the appropriate Qt signal for the extracted tone name.
      :param parsed_data: dict



   .. py:method:: _auto_add_current_program()

      _auto_add_current_program

      :return: None

      For reference:
      BANK SELECT|  PROGRAM | GROUP|                   NUMBER
      MSB | LSB | NUMBER    |                         |
      -----+-----------+-----------+----------------------------+-----------
      085 | 064 | 001 - 064 | Preset Bank Program (A) | A01 - A64     Banks to 64
      085 | 064 | 065 - 128 | Preset Bank Program (B) | B01 - B64     Banks to 128
      085 | 065 | 001 - 064 | Preset Bank Program (C) | C01 - C64     Banks to 192
      085 | 065 | 065 - 128 | Preset Bank Program (D) | D01 - D64     Banks to 256
      -----+-----------+-----------+----------------------------+-----------
      085 | 000 | 001 - 064 | User Bank Program (E) | E01 - E64       Banks to 320
      085 | 000 | 065 - 128 | User Bank Program (F) | F01 - F64       Banks to 384
      085 | 001 | 001 - 064 | User Bank Program (G) | G01 - G64       Banks to 448
      085 | 001 | 065 - 128 | User Bank Program (H) | H01 - H64       Banks to 512
      -----+-----------+-----------+----------------------------+-----------
      085 | 096 | 001 - 064 | Extra Bank Program (S) | S01 - S64      Banks to 576
      | : | : | : | :
      085 | 103 | 001 - 064 | Extra Bank Program (Z) | Z01 - Z64      Banks to 1024



   .. py:method:: _emit_program_name_signal(area: str, tone_name: str) -> None

      Emits the appropriate Qt signal for a given tone name

      :param area: str
      :param tone_name: str
      :return: None



   .. py:method:: _emit_tone_name_signal(area: str, tone_name: str) -> None

      Emits the appropriate Qt signal for a given tone name

      :param area: str
      :param tone_name: str
      :return: None



