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

from PySide6.QtCore import Signal
from jdxi_manager.midi.io.input_handler import MIDIInHandler
from jdxi_manager.midi.io.output_handler import MIDIOutHandler
import logging


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
        self.parent = parent

    def send_parameter_old(self, area, part, group, param, value, size=1):
        """
        Send address parameter change to the JD-Xi.

        Args:
            area (int): Target memory area (e.g., TEMPORARY_DRUM_KIT_AREA)
            part (int): Target part (e.g., DRUM_KIT_AREA)
            group (int): Parameter group address
            param (int): Parameter address
            value (int): Parameter value
            size (int): Size of the value in bytes (1 or 4)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if size == 1:
                # Standard 1-byte parameter
                return super().send_parameter(area, part, group, param, value)
            elif size == 4:
                # 4-byte parameter format
                command = 0x12  # Command for 4-byte parameter
                address_msb = 0x19  # MSB for drum parameters
                
                # Construct 4-byte value
                value_bytes = [
                    (value >> 24) & 0xFF,
                    (value >> 16) & 0xFF,
                    (value >> 8) & 0xFF,
                    value & 0xFF
                ]
                
                # Construct SysEx message
                sysex_message = [
                    0xF0,  # Start of SysEx
                    0x41,  # Roland ID
                    0x10,  # Device ID
                    0x00, 0x00, 0x00,  # Model ID
                    0x0E,  # Command ID
                    command,  # Command
                    address_msb,  # Address MSB
                    0x70,  # Fixed address byte
                    group & 0xFF,  # Group address
                    param & 0xFF,  # Parameter address
                ] + value_bytes + [0xF7]  # End of SysEx
                
                logging.debug(f"Sending 4-byte parameter: {' '.join([hex(b)[2:].upper().zfill(2) for b in sysex_message])}")
                return self.send_sysex(sysex_message)
            else:
                logging.error(f"Unsupported parameter size: {size}")
                return False

        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")
            return False

    def send_sysex(self, message):
        """
        Send address raw SysEx message.

        Args:
            message (list): List of bytes forming the SysEx message

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.output_port:
                logging.error("No MIDI output port available")
                return False
                
            self.output_port.send_message(message)
            return True
            
        except Exception as e:
            logging.error(f"Error sending SysEx message: {str(e)}")
            return False



