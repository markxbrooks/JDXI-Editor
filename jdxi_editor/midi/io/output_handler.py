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
import json
from typing import List, Optional, Union

from PySide6.QtCore import Signal
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF
from jdxi_editor.midi.data.address.helpers import apply_address_offset, construct_address
from jdxi_editor.globals import LOG_PADDING_WIDTH
from jdxi_editor.log.message import log_parameter
from jdxi_editor.midi.data.address.address import (
    CommandID,
    AddressMemoryAreaMSB,
)
from jdxi_editor.midi.data.address.sysex import END_OF_SYSEX, RolandID
from jdxi_editor.midi.io.controller import MidiIOController
from jdxi_editor.midi.io.utils import (
    format_midi_message_to_hex_string,
    construct_address,
    increment_group,
)
from jdxi_editor.midi.message.identity_request import IdentityRequestMessage
from jdxi_editor.midi.message.midi import MidiMessage
from jdxi_editor.midi.message.program_change import ProgramChangeMessage
from jdxi_editor.midi.message.control_change import ControlChangeMessage
from jdxi_editor.midi.message.channel import ChannelMessage
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.message.sysex import SysExMessage
from jdxi_editor.midi.utils.byte import split_value_to_nibbles


def validate_midi_message(message: Union[bytes, List[int]]) -> bool:
    """
    Validate a raw MIDI message.

    This function checks that the message is non-empty and all values are
    within the valid MIDI byte range (0–255).

    :param message: A MIDI message represented as a list of integers or a bytes object.
    :type message: Union[bytes, List[int]]
    :return: True if the message is valid, False otherwise.
    :rtype: bool
    """
    if not message:
        logging.info("MIDI message is empty.")
        return False

    if any(not (0 <= x <= 255) for x in message):
        log_parameter("Invalid MIDI value detected:", message)
        return False

    return True


class MidiOutHandler(MidiIOController):
    """Helper class for MIDI communication with the JD-Xi."""

    midi_message_outgoing = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.channel = 1

    def send_raw_message(self, message: Union[bytes, List[int]]) -> bool:
        """
        Send a validated raw MIDI message through the output port.

        This method logs the message, checks the validity using `validate_midi_message`,
        and attempts to send it via the MIDI output port.

        :param message: A MIDI message represented as a list of integers or a bytes object.
        :type message: Union[bytes, List[int]]
        :return: True if the message was successfully sent, False otherwise.
        :rtype: bool
        """
        log_parameter("Attempting to send message:", message)

        if not validate_midi_message(message):
            logging.info("MIDI message validation failed.")
            return False

        formatted_message = format_midi_message_to_hex_string(message)
        log_parameter("Sending MIDI message:", formatted_message)

        if not self.midi_out.is_port_open():
            logging.info("MIDI output port is not open.")
            return False

        try:
            log_parameter("QC passed, sending message:", formatted_message)
            self.midi_out.send_message(message)
            self.midi_message_outgoing.emit(message)
            return True
        except (ValueError, TypeError, OSError, IOError) as ex:
            logging.info(f"Error sending message: {ex}")
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
        message_bytes_list = channel_message.to_message_list()
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
            identity_request_bytes_list = identity_request_message.to_message_list()
            logging.info(
                f"sending identity request message: "
                f"{type(identity_request_bytes_list)} {identity_request_bytes_list}"
            )
            self.send_raw_message(identity_request_bytes_list)
            return True
        except (ValueError, TypeError, OSError, IOError) as ex:
            logging.error(f"Error sending identity request: {ex}")
            return False

    def send_midi_message(self, sysex_message: MidiMessage) -> bool:
        """
        Send address parameter change message using MidiMessage.

        Args:
            sysex_message: of type MidiMessage.
        Returns:
            True if successful, False otherwise.
        """
        #logging.info(
        #    f"send_midi_message: \t{type(sysex_message)} {sysex_message}"
        #)
        try:
            message = sysex_message.to_message_list()
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
            address = apply_address_offset(area, group, param, part)
            if size == 1:
                data_bytes = [value & 0x7F]  # Single byte format (0-127)
            elif size in [4, 5]:
                data_bytes = split_value_to_nibbles(value)  # Convert to nibbles
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
            message = program_change_message.to_message_list()
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
            message = control_change_message.to_message_list()
            return self.send_raw_message(message)
        except (ValueError, TypeError, OSError, IOError) as ex:
            logging.error(f"send_control_change: Error sending control change: {ex}")
            return False

    def send_rpn(self, parameter: int, value: int, channel: int = 0) -> bool:
        """
        Send a Registered Parameter Number (RPN) message via MIDI Control Change.

        Args:
            parameter: RPN parameter number (0–16383)
            value: Parameter value (0–16383)
            channel: MIDI channel (0–15)

        Returns:
            True if messages sent successfully, False otherwise
        """
        if not 0 <= parameter <= 16383:
            logging.error(f"Invalid RPN parameter: {parameter}. Must be 0–16383.")
            return False
        if not 0 <= value <= 16383:
            logging.error(f"Invalid RPN value: {value}. Must be 0–16383.")
            return False

        # Split into MSB/LSB
        rpn_msb = (parameter >> 7) & 0x7F
        rpn_lsb = parameter & 0x7F
        value_msb = (value >> 7) & 0x7F
        value_lsb = value & 0x7F

        success = (
            self.send_control_change(101, rpn_msb, channel)
            and self.send_control_change(100, rpn_lsb, channel)  # RPN MSB
            and self.send_control_change(6, value_msb, channel)  # RPN LSB
            and self.send_control_change(  # Data Entry MSB
                38, value_lsb, channel
            )  # Data Entry LSB
        )

        if success:
            logging.info(f"Sent RPN: Param {parameter}, Value {value}, Ch {channel}")
        else:
            logging.error("Failed to send RPN messages.")

        return success

    def send_nrpn(
        self, parameter: int, value: int, channel: int = 0, use_14bit: bool = False
    ) -> bool:
        """
        Send an NRPN (Non-Registered Parameter Number) message using MIDI Control Change.

        Args:
            parameter: The NRPN parameter number (0-16383).
            value: The value to set (0-16383 for 14-bit, 0-127 for 7-bit).
            channel: MIDI channel (0–15).
            use_14bit: If False, only send Data Entry MSB (7-bit).

        Returns:
            True if all messages were sent successfully, False otherwise.
        """
        logging.info(f"sending parameter {parameter} value {value} channel {channel}")
        if not 0 <= parameter <= 16383:
            logging.error(f"Invalid NRPN parameter: {parameter}. Must be 0–16383.")
            return False
        if not 0 <= value <= (16383 if use_14bit else 127):
            logging.error(
                f"Invalid NRPN value: {value}. Must be 0–{16383 if use_14bit else 127}."
            )
            return False

        nrpn_msb = (parameter >> 7) & 0x7F
        nrpn_lsb = parameter & 0x7F
        if use_14bit:
            value_msb = (value >> 7) & 0x7F
            value_lsb = value & 0x7F
        else:
            value_msb = value & 0x7F
            value_lsb = 0  # Optional; not sent anyway

        ok = True
        ok &= self.send_control_change(99, nrpn_msb, channel)  # NRPN MSB
        ok &= self.send_control_change(98, nrpn_lsb, channel)  # NRPN LSB
        ok &= self.send_control_change(6, value_msb, channel)  # Data Entry MSB
        if use_14bit:
            ok &= self.send_control_change(38, value_lsb, channel)  # Data Entry LSB

        # Optional cleanup (nulling NRPN, not required but can prevent stuck parameters)
        ok &= self.send_control_change(99, 127, channel)  # NRPN MSB null
        ok &= self.send_control_change(98, 127, channel)  # NRPN LSB null

        if ok:
            logging.info(
                f"Sent NRPN: Param {parameter}, Value {value}, Channel {channel}, 14-bit={use_14bit}"
            )
        else:
            logging.error("Failed to send NRPN messages.")

        return ok

    def send_bank_select_and_program_change(
        self, channel: int, bank_msb: int, bank_lsb: int, program: int
    ) -> bool:
        """
        Sends Bank Select and Program Change messages.

        Args:
            channel: MIDI channel (1-16).
            bank_msb: Bank MSB value.
            bank_lsb: Bank LSB value.
            program: Program number.
        Returns:
            True if all messages are sent successfully, False otherwise.
        """
        try:
            logging.info(
                f"send_bank_select_and_program_change "
                f"channel: {channel} "
                f" bank_msb: {bank_msb} "
                f" bank_lsb: {bank_lsb} "
                f"program: {program} "
            )
            logging.info(
                f"1) sending send_control_change "
                f"controller: 0 "
                f" bank_msb: {bank_msb} "
                f" channel: {channel} "
            )
            self.send_control_change(0, bank_msb, channel)

            logging.info(
                f"2) sending send_control_change "
                f"controller: 32"
                f" bank_lsb: {bank_lsb} "
                f" channel: {channel} "
            )
            self.send_control_change(32, bank_lsb, channel)

            logging.info(
                f"3) sending send_program_change "
                f" program: {program} "
                f" channel: {channel} "
            )
            self.send_program_change(program, channel)
            return True
        except Exception as ex:
            logging.info(f"Error {ex} occurred sending bank and program change message")
            return False

    def identify_device(self) -> bool:
        """Send Identity Request and verify response"""
        request = IdentityRequestMessage()
        self.send_message(request)
        logging.info(f"sending identity request message: {request}")

    def send_message(self, message: MidiMessage):
        """unpack the message list and send it"""
        try:
            raw_message = message.to_message_list()
            self.send_raw_message(raw_message)
            logging.debug(
                f"Sent MIDI message: {' '.join([hex(b)[2:].upper().zfill(2) for b in raw_message])}"
            )
        except Exception as ex:
            logging.error(f"Error sending identity request: {str(ex)}")

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
                manufacturer_id=[RolandID.ROLAND_ID],
                device_id=RolandID.DEVICE_ID,
                model_id=[0x00, 0x00, 0x3B, 0x00],  # Example model ID
                command=CommandID.RQ1,  # RQ1 (Request Data) command for Roland
                address=[area, part, group, param],  # Address of parameter
                data=[],  # No payload for request
            )

            self.midi_out.send_message(request.to_bytes())

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

    def save_patch(self, file_path: str) -> bool:
        """Save current patch state to JSON file

        Args:
            file_path: Path to save the .jdx file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure file has .jdx extension
            if not file_path.endswith(".jdx"):
                file_path += ".jdx"

            # Collect patch data
            patch_data = {
                "version": "1.0",
                "name": "Untitled Patch",  # TODO: Get actual patch name
                "type": "JD-Xi Patch",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "parameters": {
                    "digital": self._get_digital_parameters(),
                    "analog": self._get_analog_parameters(),
                    "drums": self._get_drum_parameters(),
                    "effects": self._get_effects_parameters(),
                },
            }

            # Save to file
            with open(file_path, "w") as f:
                json.dump(patch_data, f, indent=2)

            logging.info(f"Patch saved to {file_path}")
            return True
        except Exception as e:
            logging.error(f"Error saving patch: {str(e)}")
            return False

    def _get_digital_parameters(self):
        """Get digital parameters"""
        parameters = {}
        for area in AddressMemoryAreaMSB.DIGITAL_L:
            for part in range(0x00, 0x03):
                for group in range(0x00, 0x03):
                    for param in range(0x00, 0x03):
                        value = self.get_parameter(area, part, group, param)
                        parameters[
                            f"{area:02X}{part:02X}{group:02X}{param:02X}"
                        ] = value
        return parameters

    def _get_analog_parameters(self):
        """Get analog parameters"""
        parameters = {}
        for area in range(0x00, 0x03):
            for part in range(0x00, 0x03):
                for group in range(0x00, 0x03):
                    for param in range(0x00, 0x03):
                        value = self.get_parameter(area, part, group, param)
                        parameters[
                            f"{area:02X}{part:02X}{group:02X}{param:02X}"
                        ] = value
        return parameters

    def _get_drum_parameters(self):
        """Get drum parameters"""
        parameters = {}
        for area in range(0x00, 0x03):
            for part in range(0x00, 0x03):
                for group in range(0x00, 0x03):
                    for param in range(0x00, 0x03):
                        value = self.get_parameter(area, part, group, param)
                        parameters[
                            f"{area:02X}{part:02X}{group:02X}{param:02X}"
                        ] = value
        return parameters

    def _get_effects_parameters(self):
        """Get effects parameters"""
        parameters = {}
        for area in range(0x00, 0x03):
            for part in range(0x00, 0x03):
                for group in range(0x00, 0x03):
                    for param in range(0x00, 0x03):
                        value = self.get_parameter(area, part, group, param)
                        parameters[
                            f"{area:02X}{part:02X}{group:02X}{param:02X}"
                        ] = value
        return parameters
