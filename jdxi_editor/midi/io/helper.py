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