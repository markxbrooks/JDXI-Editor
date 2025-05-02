"""
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
    - jdxi_manager.midi.input_handler.MIDIInHandler for handling incoming MIDI messages.
    - jdxi_manager.midi.output_handler.MIDIOutHandler for handling outgoing MIDI messages.

"""

import logging

from jdxi_editor.log.error import log_error
from jdxi_editor.log.message import log_message
from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.midi.io.input_handler import MidiInHandler
from jdxi_editor.midi.io.output_handler import MidiOutHandler
from jdxi_editor.ui.windows.jdxi.helpers.port import find_jdxi_port


class MidiIOHelper(MidiInHandler, MidiOutHandler):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MidiIOHelper, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, parent=None):
        self._current_out_port = None
        self._current_in_port = None
        self.in_port_name = ""  # Store input port name
        self.out_port_name = ""  # Store output port name
        if not hasattr(self, "initialized"):  # To avoid reinitialization
            super().__init__()
            self.midi_messages = []
            self.current_in = None
            self.current_out = None
            if parent:
                self.parent = parent
            self.initialized = True

    def load_patch(self, file_path: str):
        """
        Load the JSON patch as a string and emit it.

        :param file_path: str
        :return: None
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file_handle:
                json_string = file_handle.read()
                self.midi_sysex_json.emit(json_string)
        except Exception as ex:
            log_error(f"Error reading or emitting sysex JSON: {ex}", level=logging.ERROR)

    def load_sysx_patch(self, file_path: str):
        """
        Load the SysEx patch from a file and emit it.

        :param file_path: str
        :return: None
        """
        try:
            with open(file_path, "rb") as file:
                sysex_data = file.read()

            if not sysex_data.startswith(b"\xF0") or not sysex_data.endswith(b"\xF7"):
                log_message("Invalid SysEx file format")
                return
        except Exception as ex:
            log_error(f"Error {ex} occurred opening file", level=logging.ERROR)

        self.midi_messages.append(sysex_data)
        try:
            log_message(f"attempting to send message: {sysex_data}")
            sysex_list = list(sysex_data)
            self.send_raw_message(sysex_list)
        except Exception as ex:
            log_error(f"Error {ex} sending sysex list", level=logging.ERROR)

    def set_midi_ports(self, in_port: str, out_port: str) -> bool:
        """
        Set MIDI input and output ports

        :param in_port: str
        :param out_port: str
        :return: bool
        """
        try:
            if not self.open_input_port(in_port):
                return False
            if not self.open_output_port(out_port):
                return False
            return True

        except Exception as ex:
            log_error(f"Error setting MIDI ports: {str(ex)}", level=logging.ERROR)
            return False

    def connect_port_names(self, in_port: str, out_port: str):
        """
        Attempt to automatically connect to JD-Xi MIDI ports.

        :param in_port: str
        :param out_port: str
        :return: bool
        """
        try:
            # Ensure both ports are found
            if not in_port or not out_port:
                log_message("JD-Xi MIDI auto-connect failed", level=logging.WARNING)
                log_parameter("MIDI in_port", in_port)
                log_parameter("MIDI out_port", out_port)
                return False
            self.set_midi_ports(in_port, out_port)

            # Verify connection
            if self.identify_device():
                log_parameter("Successfully connected to JD-Xi MIDI:", in_port)
                log_message("Successfully connected to JD-Xi MIDI", out_port)
                return True
            else:
                log_message("JD-Xi identity verification failed.", level=logging.WARNING)
                return False

        except Exception as ex:
            log_error(f"Error auto-connecting to JD-Xi: {str(ex)}", level=logging.ERROR)
            return False

    def reconnect_port_names(self, in_port: str, out_port: str):
        """
        Reconnect ports

        :param in_port: str
        :param out_port: str
        :return: None
        """
        try:
            self.close_ports()
            self.connect_port_names(in_port, out_port)
            self.open_output_port(out_port)
            self.reopen_input_port_name(in_port)
        except Exception as ex:
            print(f"Error {ex} occurred reconnecting ports")

    def auto_connect_jdxi(self):
        """
        Attempt to automatically connect to JD-Xi MIDI ports.

        :return: bool
        """
        try:
            # Find JD-Xi ports
            jdxi_in_port = find_jdxi_port(self.get_input_ports())
            jdxi_out_port = find_jdxi_port(self.get_output_ports())
            self.connect_port_names(jdxi_in_port, jdxi_out_port)
            self.identify_device()
            return True
        except Exception as ex:
            log_error(f"Error auto-connecting to JD-Xi: {str(ex)}", level=logging.ERROR)
            return False
