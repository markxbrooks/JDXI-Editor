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
import json
import logging

from jdxi_editor.midi.io.input_handler import MidiInHandler
from jdxi_editor.midi.io.output_handler import MidiOutHandler
from jdxi_editor.midi.message.identity_request import IdentityRequestMessage
from jdxi_editor.midi.message.midi import MidiMessage
from jdxi_editor.midi.message.roland import JDXiSysEx
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

    def load_patch(self, file_path):
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
            logging.error(f"Error reading or emitting sysex JSON: {ex}")

    def load_sysx_patch(self, file_path):
        try:
            with open(file_path, "rb") as file:
                sysex_data = file.read()

            if not sysex_data.startswith(b"\xF0") or not sysex_data.endswith(b"\xF7"):
                logging.error("Invalid SysEx file format")
                return
        except Exception as ex:
            logging.info(f"Error {ex} occurred opening file")

        self.midi_messages.append(sysex_data)
        try:
            logging.info(f"attempting to send message: {sysex_data}")
            sysex_list = list(sysex_data)
            self.send_raw_message(sysex_list)
        except Exception as ex:
            logging.info(f"Error {ex} sending sysex list")

    def set_midi_ports(self, in_port: str, out_port: str) -> bool:
        """Set MIDI input and output ports

        Args:
            in_port: Input port name
            out_port: Output port name

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.open_input_port(in_port):
                return False
            if not self.open_output_port(out_port):
                return False
            return True

        except Exception as ex:
            logging.error(f"Error setting MIDI ports: {str(ex)}")
            return False

    def connect_port_names(self, in_port: str, out_port: str):
        """Attempt to automatically connect to JD-Xi MIDI ports."""
        try:
            # Ensure both ports are found
            if not in_port or not out_port:
                logging.warning(
                    f"JD-Xi MIDI auto-connect failed. Found input: {in_port}, output: {out_port}"
                )
                return False
            self.set_midi_ports(in_port, out_port)

            # Verify connection
            if self.identify_device():
                logging.info(
                    f"Successfully connected to JD-Xi MIDI: {in_port} / {out_port}"
                )
                return True
            else:
                logging.warning("JD-Xi identity verification failed.")
                return False

        except Exception as ex:
            logging.error(f"Error auto-connecting to JD-Xi: {str(ex)}")
            return False

    def reconnect_port_names(self, in_port: str, out_port: str):
        """ reconnect ports """
        try:
            self.close_ports()
            self.connect_port_names(in_port, out_port)
            self.open_output_port(out_port)
            self.reopen_input_port_name(in_port)
        except Exception as ex:
            print(f"Error {ex} occurred reconnecting ports")

    def auto_connect_jdxi(self):
        """Attempt to automatically connect to JD-Xi MIDI ports."""
        try:
            # Find JD-Xi ports
            jdxi_in_port = find_jdxi_port(self.get_input_ports())
            jdxi_out_port = find_jdxi_port(self.get_output_ports())
            self.connect_port_names(jdxi_in_port, jdxi_out_port)
            self.identify_device()
        except Exception as ex:
            logging.error(f"Error auto-connecting to JD-Xi: {str(ex)}")
            return False
