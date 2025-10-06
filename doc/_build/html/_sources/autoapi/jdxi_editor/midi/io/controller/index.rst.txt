jdxi_editor.midi.io.controller
==============================

.. py:module:: jdxi_editor.midi.io.controller

.. autoapi-nested-parse::

   MIDI I/O Controller for JD-Xi

   This module provides the `MidiIOController` class, which facilitates MIDI communication
   with the Roland JD-Xi synthesizer. It allows users to list, open, and manage MIDI input
   and output ports, automatically detect JD-Xi ports, and handle MIDI message reception.

   Features:
   - Retrieve available MIDI input and output ports.
   - Automatically detect JD-Xi MIDI ports.
   - Open and close MIDI input and output ports by name or index.
   - Check the status of open MIDI ports.
   - Set a callback for incoming MIDI messages.

   Dependencies:
   - `rtmidi` for MIDI communication.
   - `PyQt6.QtCore` for QObject-based structure.

   Example Usage:
       controller = MidiIOController()
       controller.open_ports("JD-Xi MIDI IN", "JD-Xi MIDI OUT")
       print(controller.current_in_port, controller.current_out_port)



Classes
-------

.. autoapisummary::

   jdxi_editor.midi.io.controller.MidiIOController


Module Contents
---------------

.. py:class:: MidiIOController(parent: PySide6.QtCore.QObject)

   Bases: :py:obj:`PySide6.QtCore.QObject`


   Helper class for MIDI communication with the JD-Xi


   .. py:attribute:: midi_in


   .. py:attribute:: midi_out


   .. py:attribute:: input_port_number
      :type:  Optional[int]
      :value: None



   .. py:attribute:: output_port_number
      :type:  Optional[int]
      :value: None



   .. py:property:: current_in_port
      :type: Optional[str]


      Get current input port name

      :return: Optional[str], MIDI input port name


   .. py:property:: current_out_port
      :type: Optional[str]


      Get current output port name

      :return: Optional[str], MIDI output port name


   .. py:method:: get_input_ports() -> List[str]

      Get available MIDI input ports

      :return: List[str], MIDI input ports



   .. py:method:: get_output_ports() -> List[str]

      Get available MIDI output ports

      :return: List[str], MIDI output ports



   .. py:method:: find_jdxi_ports() -> Tuple[Optional[str], Optional[str]]

      Find JD-Xi input and output ports

      :return: Tuple[Optional[str], Optional[str]], JD-Xi input and output ports



   .. py:method:: open_input(port_name_or_index: str) -> bool

      Open MIDI input port by name or index

      :param port_name_or_index: str, MIDI input port name or index
      :return: bool True if successful, False otherwise



   .. py:method:: open_output(port_name_or_index: str) -> bool

      Open MIDI output port by name or index

      :param port_name_or_index: str
      :return: bool True if successful, False otherwise



   .. py:method:: open_input_port(port_name_or_index: str) -> bool

      Open MIDI input port by name or index

      :param port_name_or_index: str
      :return: bool



   .. py:method:: open_output_port(port_name_or_index: str) -> bool

      Open MIDI output port by name or index

      :param port_name_or_index: str, MIDI output port name or index
      :return: bool True if successful, False otherwise



   .. py:method:: close_ports() -> None

      Close MIDI ports

      :return: None



   .. py:property:: is_input_open
      :type: bool


      Check if MIDI input port is open

      :return: bool


   .. py:property:: is_output_open
      :type: bool


      Check if MIDI output port is open

      :return: bool


   .. py:method:: open_ports(in_port: str, out_port: str) -> bool

      Open both input and output ports by name

      :param in_port: str, Input port name or None
      :param out_port: str, Output port name or None
      :return: bool



