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

from jdxi_editor.midi.io.input_handler import MidiInHandler
from jdxi_editor.midi.io.output_handler import MidiOutHandler
from jdxi_editor.midi.message.identity_request import IdentityRequestMessage


class MidiIOHelper(MidiInHandler, MidiOutHandler):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MidiIOHelper, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, parent=None):
        if not hasattr(self, "initialized"):  # To avoid reinitialization
            super().__init__()
            self.midi_messages = []
            self.current_in = None
            self.current_out = None
            if parent:
                self.parent = parent
            self.initialized = True

    def load_patch(self, file_path):
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

    def reconnect_ports(self, midi_in_name, midi_out_name):
        if self.midi_in:
            self.midi_in.delete()  # Use delete() instead of close()
        if self.midi_out:
            self.midi_out.delete()  # Use delete() instead of close()

    def connect_jdxi_midi_ports(self):
        """Connect to MIDI ports"""
        try:
            # Find JD-Xi ports
            in_port, out_port = self.find_jdxi_ports()

            if in_port and out_port:
                # Open ports
                if self.open_ports(in_port, out_port):
                    logging.info(f"Connected to JD-Xi ({in_port}, {out_port})")
                    return True
            logging.warning("JD-Xi not found")
            return False
        except Exception as ex:
            logging.info(f"Error connecting to jdxi ports")

    def set_midi_ports(self, in_port: str, out_port: str) -> bool:
        """Set MIDI input and output ports

        Args:
            in_port: Input port name
            out_port: Output port name

        Returns:
            True if successful, False otherwise
        """
        try:
            # Open ports
            if not self.midi_helper.open_input_port(in_port):
                return False

            if not self.midi_helper.open_output_port(out_port):
                return False

            # Update indicators
            self.midi_in_indicator.set_state(self.midi_helper.is_input_open)
            self.midi_out_indicator.set_state(self.midi_helper.is_output_open)

            return True

        except Exception as ex:
            logging.error(f"Error setting MIDI ports: {str(ex)}")
            return False

    def _auto_connect_jdxi(self):
        """Attempt to automatically connect to JD-Xi MIDI ports."""
        try:
            # Get available ports
            input_ports = self.midi_helper.get_input_ports()
            output_ports = self.midi_helper.get_output_ports()

            # Find JD-Xi ports
            selected_in_port = _find_jdxi_port(input_ports, "input")
            selected_out_port = _find_jdxi_port(output_ports, "output")

            # Ensure both ports are found
            if not selected_in_port or not selected_out_port:
                logging.warning(
                    f"JD-Xi MIDI auto-connect failed. Found input: {selected_in_port}, output: {selected_out_port}"
                )
                return False

            # Open the found ports
            self.midi_helper.open_input_port(selected_in_port)
            self.midi_helper.open_output_port(selected_out_port)

            # Explicitly store the selected ports # FIXME: this looks incorrect
            self.midi_helper.current_in_port = selected_in_port
            self.midi_helper.current_out_port = selected_out_port

            # Verify connection
            if self._verify_jdxi_connection():
                logging.info(
                    f"Successfully connected to JD-Xi MIDI: {selected_in_port} / {selected_out_port}"
                )
                return True
            else:
                logging.warning("JD-Xi identity verification failed.")
                return False

        except Exception as ex:
            logging.error(f"Error auto-connecting to JD-Xi: {str(ex)}")
            return False

    def _verify_jdxi_connection(self):
        """Verify connected device is address JD-Xi by sending identity request"""
        try:
            # Create identity request message using dataclass
            identity_request = IdentityRequestMessage()
            self.send_raw_message(identity_request.to_message_list())
            logging.debug("Sent JD-Xi identity request")

        except Exception as ex:
            logging.error(f"Error sending identity request: {str(ex)}")
