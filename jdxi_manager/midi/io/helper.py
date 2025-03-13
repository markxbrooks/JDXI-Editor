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
from jdxi_manager.midi.io.input_handler import MIDIInHandler
from jdxi_manager.midi.io.output_handler import MIDIOutHandler


class MIDIHelper(MIDIInHandler, MIDIOutHandler):
    """
    Helper class for MIDI communication with the JD-Xi.

    This class integrates both input and output MIDI functionalities by inheriting
    from MIDIInHandler and MIDIOutHandler. It also provides address JSON-formatted SysEx
    signal for convenient handling of SysEx messages.
    """

    def __init__(self, parent=None):
        """
        Initialize the MIDIHelper.

        :param parent: Optional parent widget or object.
        """
        super().__init__(parent)
        self.midi_messages = []
        self.parent = parent

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

    def midi_callback(self, event):
        self.midi_callback(event=event)
