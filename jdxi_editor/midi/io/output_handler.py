"""
MIDI Output Handler
===================

This module provides the `MIDIOutHandler` class for managing MIDI output, allowing users to send
note-on, note-off, and control change messages through address specified MIDI output port.

Dependencies:
    - rtmidi: A library for working with MIDI messages and ports.

Example usage:
    handler = MIDIOutHandler("MIDI Output Port")
    handler.send_note_on(60, velocity=100)
    handler.send_note_off(60)
    handler.send_control_change(7, 127)
    handler.close()

"""

import logging
import time
from typing import List, Optional

from rtmidi.midiconstants import NOTE_ON, NOTE_OFF

from jdxi_editor.midi.data.constants.sysex import (
    ROLAND_ID,
    DEVICE_ID,
    RQ1_COMMAND_11,
    END_OF_SYSEX,
)
from jdxi_editor.midi.io.controller import MidiIOController
from jdxi_editor.midi.message.identity_request import IdentityRequestMessage
from jdxi_editor.midi.message.midi import MidiMessage
from jdxi_editor.midi.message.program_change import ProgramChangeMessage
from jdxi_editor.midi.message.control_change import ControlChangeMessage
from jdxi_editor.midi.message.channel import ChannelMessage
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.message.sysex import SysExMessage
from jdxi_editor.midi.utils.byte import split_value_to_nibbles


def format_midi_message_to_hex_string(message):
    """hexlify message"""
    formatted_message = " ".join([hex(x)[2:].upper().zfill(2) for x in message])
    return formatted_message


def construct_address(area, group, param, part):
    """Address construction"""
    address = [area, part, group & 0xFF, param & 0xFF]
    return address


def increment_group(group, param):
    """Adjust group if param exceeds 127"""
    if param > 127:
        group += 1
    return group


class MIDIOutHandler(MidiIOController):
    """Helper class for MIDI communication with the JD-Xi."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.channel = 1

    def send_raw_message(self, message: List[int]) -> bool:
        """
        Send a raw MIDI message with validation.

        Args:
            message: List of integer values representing the MIDI message.

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        logging.info(f"attempting to send message: {type(message)} {message}")
        try:
            if not message:
                logging.info("MIDI message is empty.")
                raise ValueError

            if any(not (0 <= x <= 255) for x in message):
                logging.info(f"Invalid MIDI value detected: {message}")
                raise ValueError
        except Exception as ex:
            logging.info(f"Error {ex} occurred processing midi message")

        formatted_message = format_midi_message_to_hex_string(message)
        logging.info(f"Sending MIDI message: {formatted_message}")

        if not self.midi_out.is_port_open():
            logging.info("MIDI output port is not open.")
            return False

        try:
            logging.info(
                f"Validation passed, sending MIDI message: "
                f"{type(formatted_message)} {formatted_message}"
            )
            self.midi_out.send_message(message)
            return True
        except (ValueError, TypeError, OSError, IOError) as ex:
            logging.info(f"Error sending MIDI message: {ex}")
            return False

    def send_note_on(self, note: int = 60, velocity: int = 127, channel: int = 1):
        """Send address 'Note On' message."""
        self.send_channel_message(NOTE_ON, note, velocity, channel)

    def send_note_off(self, note: int = 60, velocity: int = 0, channel: int = 1):
        """Send address 'Note Off' message."""
        self.send_channel_message(NOTE_OFF, note, velocity, channel)

    def send_channel_message(
        self,
        status: int,
        data1: Optional[int] = None,
        data2: Optional[int] = None,
        channel: int = 1,
    ) -> None:
        """
        Send a MIDI Channel Message.

        Args:
            status (int): Status byte (e.g., NOTE_ON, NOTE_OFF, CONTROL_CHANGE).
            data1 (Optional[int]): First data byte, typically a note or controller number.
            data2 (Optional[int]): Second data byte, typically velocity or value.
            channel (int): MIDI channel (1-based, range 1-16).

        Raises:
            ValueError: If the channel is out of range (1-16).
        """
        if not 1 <= channel <= 16:
            raise ValueError(f"Invalid MIDI channel: {channel}. Must be 1-16.")
        channel_message = ChannelMessage(
            status, data1, data2, channel - 1
        )  # convert to 0-based
        message_bytes_list = channel_message.to_list()
        self.send_raw_message(message_bytes_list)

    def send_bank_select(self, msb: int, lsb: int, channel: int = 0) -> bool:
        """
        Send bank select messages.

        Args:
            msb: Bank Select MSB value (0-127).
            lsb: Bank Select LSB value (0-127).
            channel: MIDI channel (0-15).
        Returns:
            True if successful, False otherwise.
        """
        logging.debug(f"Sending bank select: MSB={msb}, LSB={lsb}, channel={channel}")
        try:
            # Bank Select MSB (CC#0)
            self.send_raw_message([0xB0 + channel, 0x00, msb])
            # Bank Select LSB (CC#32)
            self.send_raw_message([0xB0 + channel, 0x20, lsb])
            return True
        except (ValueError, TypeError, OSError, IOError) as ex:
            logging.error(f"Error sending bank select: {ex}")
            return False

    def send_identity_request(self) -> bool:
        """
        Send identity request message (Universal System Exclusive).

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        logging.debug("Sending identity request")
        try:
            identity_request_message = IdentityRequestMessage()
            identity_request_bytes_list = identity_request_message.to_list()
            logging.info(
                f"sending identity request message: "
                f"{type(identity_request_bytes_list)} {identity_request_bytes_list}"
            )
            self.send_raw_message(identity_request_bytes_list)
            return True
        except (ValueError, TypeError, OSError, IOError) as ex:
            logging.error(f"Error sending identity request: {ex}")
            return False

    def send_midi_message(
        self, sysex_message: MidiMessage
    ) -> bool:
        """
        Send address parameter change message using MidiMessage.

        Args:
            sysex_message: of type MidiMessage.
        Returns:
            True if successful, False otherwise.
        """
        try:
            message = sysex_message.to_list()
            return self.send_raw_message(message)

        except (ValueError, TypeError, OSError, IOError) as ex:
            logging.error(f"Error sending parameter: {ex}")
            return False

    def send_parameter(
        self, area: int, part: int, group: int, param: int, value: int, size: int = 1
    ) -> bool:
        """
        Send address parameter change message using RolandSysEx.

        Args:
            area: Parameter area (e.g., Program, Digital Synth).
            part: Part number.
            group: Parameter area.
            param: Parameter number.
            value: Parameter value.
            size: Size of the value in bytes (1, 4, or 5).
        Returns:
            True if successful, False otherwise.
        """
        logging.info(
            f"send_parameter: \tarea={hex(area)}, \tpart={hex(part)}, \tgroup={hex(group)}, "
            f"\tparam={hex(param)}, \tvalue={value}, \tsize={size}"
        )
        try:
            group = increment_group(group, param)
            address = construct_address(area, group, param, part)
            if size == 1:
                data_bytes = [value & 0x7F]  # Single byte format (0-127)
            elif size in [4, 5]:
                data_bytes = split_value_to_nibbles(value, size)  # Convert to nibbles
            else:
                logging.error(f"Unsupported parameter size: {size}")
                return False
            sysex_message = RolandSysEx()
            message = sysex_message.construct_sysex(address, *data_bytes)
            return self.send_raw_message(message)

        except (ValueError, TypeError, OSError, IOError) as ex:
            logging.error(f"Error sending parameter: {ex}")
            return False

    def send_program_change(self, program: int, channel: int = 0) -> bool:
        """
        Send address program change message.

        Args:
            program: Program number (0-127).
            channel: MIDI channel (0-15).
        Returns:
            True if successful, False otherwise.
        """
        logging.debug(f"Sending program change: program={program}, channel={channel}")
        try:
            program_change_message = ProgramChangeMessage(
                channel=channel, program=program
            )
            message = program_change_message.to_list()
            return self.send_raw_message(message)
        except (ValueError, TypeError, OSError, IOError) as ex:
            logging.error(f"Error sending program change: {ex}")
            return False

    def send_control_change(
        self, controller: int, value: int, channel: int = 0
    ) -> bool:
        """
        Send address control change message.

        Args:
            controller: Controller number (0-127).
            value: Controller value (0-127).
            channel: MIDI channel (0-15).
        Returns:
            True if successful, False otherwise.
        """
        logging.info(
            f"attempting to send - controller {controller} "
            f"value {value} channel {channel}"
        )
        if not 0 <= channel <= 15:
            logging.error(f"Invalid MIDI channel: {channel}. Must be 0-15.")
            return False
        if not 0 <= controller <= 127:
            logging.error(f"Invalid controller number: {controller}. Must be 0-127.")
            return False
        if not 0 <= value <= 127:
            logging.error(f"Invalid controller value: {value}. Must be 0-127.")
            return False
        try:
            control_change_message = ControlChangeMessage(channel, controller, value)
            message = control_change_message.to_list()
            return self.send_raw_message(message)
        except (ValueError, TypeError, OSError, IOError) as ex:
            logging.error(f"send_control_change: Error sending control change: {ex}")
            return False

    def send_bank_select_and_program_change(
        self, channel: int, bank_msb: int, bank_lsb: int, program: int
    ) -> bool:
        """
        Sends Bank Select and Program Change messages.

        Args:
            channel: MIDI channel (0-15).
            bank_msb: Bank MSB value.
            bank_lsb: Bank LSB value.
            program: Program number.
        Returns:
            True if all messages are sent successfully, False otherwise.
        """
        try:
            logging.info(f"send_bank_select_and_program_change "
                         f"channel: {channel} "
                         f" bank_msb: {bank_msb} "
                         f" bank_lsb: {bank_lsb} "
                         f"program: {program} ")
            logging.info(f"1) sending send_control_change "
                     f"controller: 0 "
                     f" bank_msb: {bank_msb} "
                     f" program: {channel} ")
            self.send_control_change(0, bank_msb, channel)

            logging.info(f"2) sending send_control_change "
                     f"controller: 32"
                     f" bank_lsb: {bank_lsb} "
                     f" program: {channel} ")
            self.send_control_change(32, bank_lsb, channel)

            logging.info(f"3) sending send_program_change "
                     f" program: {program} "
                     f" program: {channel} ")
            self.send_program_change(program, channel)
            return True
        except Exception as ex:
            logging.info(f"Error {ex} occurred sending bank and program change message")

    def get_parameter(
        self, area: int, part: int, group: int, param: int
    ) -> Optional[int]:
        """
        Get parameter value via MIDI System Exclusive message.

        Args:
            area: Parameter area (e.g., Digital Synth 1).
            part: Part number.
            group: Parameter area.
            param: Parameter number.
        Returns:
            Parameter value (0-127) or None if an error occurs.
        """
        logging.info(
            f"Requesting parameter: area={area}, part={part}, "
            f"group={group}, param={param}"
        )

        if not self.midi_out.is_port_open() or not self.midi_in.is_port_open():
            logging.error("MIDI ports not open")
            return None

        try:
            # Construct SysEx request using SysExMessage
            request = SysExMessage(
                manufacturer_id=[ROLAND_ID],
                device_id=DEVICE_ID,
                model_id=[0x00, 0x00, 0x3B, 0x00],  # Example model ID
                command=RQ1_COMMAND_11,  # RQ1 (Request Data) command for Roland
                address=[area, part, group, param],  # Address of parameter
                data=[],  # No payload for request
            )

            self.midi_out.send_raw_message(request.to_bytes())

            # Wait for response with a timeout of 100ms.
            start_time = time.time()
            while time.time() - start_time < 0.1:
                message = self.midi_in.get_message()
                if message:
                    msg, _ = message
                    if len(msg) >= 11 and msg[0] == 0xF0 and msg[-1] == END_OF_SYSEX:
                        # Parse response
                        response = SysExMessage.from_bytes(bytes(msg))
                        # Extract parameter value
                        return response.data[0] if response.data else None

                time.sleep(0.001)

            logging.warning("Timeout waiting for parameter response")
            raise TimeoutError

        except (TimeoutError, OSError, IOError) as ex:
            logging.error(f"Error getting parameter: {ex}")
            return None
