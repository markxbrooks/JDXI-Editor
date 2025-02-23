
"""
MIDI Helper Module
==================

This module provides a unified helper class for MIDI communication with the Roland JD-Xi.
It integrates both MIDI input and output functionalities by combining the features of
the MIDIInHandler and MIDIOutHandler classes.

Classes:
    MIDIHelper: A helper class that inherits from both MIDIInHandler and MIDIOutHandler,
                offering a consolidated interface for handling MIDI messages (including
                SysEx messages in JSON format) for the JD-Xi synthesizer.

Dependencies:
    - PySide6.QtCore.Signal for Qt signal support.
    - jdxi_manager.midi.input_handler.MIDIInHandler for handling incoming MIDI messages.
    - jdxi_manager.midi.output_handler.MIDIOutHandler for handling outgoing MIDI messages.
"""

from PySide6.QtCore import Signal

from jdxi_manager.midi.io.input_handler import MIDIInHandler
from jdxi_manager.midi.io.output_handler import MIDIOutHandler


class MIDIHelper(MIDIInHandler, MIDIOutHandler):
    """
    Helper class for MIDI communication with the JD-Xi.

    This class integrates both input and output MIDI functionalities by inheriting
    from MIDIInHandler and MIDIOutHandler. It also provides a JSON-formatted SysEx
    signal for convenient handling of SysEx messages.
    """

    def __init__(self, parent=None):
        """
        Initialize the MIDIHelper.

        :param parent: Optional parent widget or object.
        """
        super().__init__(parent)
        self.parent = parent



