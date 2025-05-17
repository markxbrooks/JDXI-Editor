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
from typing import Optional, Iterable

from PySide6.QtCore import Signal
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF

from jdxi_editor.jdxi.midi.constant import JDXiMidiConstant
from jdxi_editor.jdxi.sysex.bitmask import JDXiBitMask
from jdxi_editor.jdxi.sysex.offset import JDXiSysExOffset
from jdxi_editor.log.error import log_error
from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.log.message import log_message
from jdxi_editor.midi.data.address.address import (
    CommandID, AddressStartMSB, ModelID,
)
from jdxi_editor.midi.data.address.sysex import END_OF_SYSEX, RolandID, START_OF_SYSEX
from jdxi_editor.midi.data.parsers.util import OUTBOUND_MESSAGE_IGNORED_KEYS
from jdxi_editor.midi.io.controller import MidiIOController
from jdxi_editor.midi.io.utils import format_midi_message_to_hex_string
from jdxi_editor.midi.message.identity_request import IdentityRequestMessage
from jdxi_editor.midi.message.midi import MidiMessage
from jdxi_editor.midi.message.program_change import ProgramChangeMessage
from jdxi_editor.midi.message.control_change import ControlChangeMessage
from jdxi_editor.midi.message.channel import ChannelMessage
from jdxi_editor.midi.message.sysex import SysExMessage
from jdxi_editor.midi.data.sysex.length import ONE_BYTE_SYSEX_DATA_LENGTH
from jdxi_editor.midi.sysex.parsers.sysex import JDXiSysExParser


def validate_midi_message(message: Iterable[int]) -> bool:
    """
    Validate a raw MIDI message.

    This function checks that the message is non-empty and all values are
    within the valid MIDI byte range (0–255).

    :param message: A MIDI message represented as a list of integers or a bytes object.
    :type message: Iterable[int], can be a list, bytes, tuple, set
    :return: True if the message is valid, False otherwise.
    :rtype: bool
    """
    if not message:
        log_message("MIDI message is empty.")
        return False

    for byte in message:
        if not isinstance(byte, int) or not (0 <= byte <= 255):
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
        self.sysex_parser = JDXiSysExParser()

    def send_raw_message(self, message: Iterable[int]) -> bool:
        """
        Send a validated raw MIDI message through the output port.

        This method logs the message, checks the validity using `validate_midi_message`,
        and attempts to send it via the MIDI output port.

        :param message: A MIDI message represented as a list of integers or a bytes object.
        :type message: Union[bytes, List[int]]
        :return: True if the message was successfully sent, False otherwise.
        :rtype: bool
        """

        if not validate_midi_message(message):
            log_message("MIDI message validation failed.")
            return False

        formatted_message = format_midi_message_to_hex_string(message)

        if not self.midi_out.is_port_open():
            log_message("MIDI output port is not open.")
            return False
        try:
            parsed_data = self.sysex_parser.parse_bytes(bytes(message))
            filtered_data = {
                k: v for k, v in parsed_data.items() if k not in OUTBOUND_MESSAGE_IGNORED_KEYS
            }
        except Exception as ex:
            filtered_data = {}
        try:
            log_message(
                f"[MIDI QC passed] — [ Sending message: {formatted_message} ] {filtered_data}",
                level=logging.INFO,
                silent=False
            )
            self.midi_out.send_message(message)
            self.midi_message_outgoing.emit(message)
            return True
        except (ValueError, TypeError, OSError, IOError) as ex:
            log_error(f"Error sending message: {ex}")
            return False

    def send_note_on(
        self, note: int = 60, velocity: int = 127, channel: int = 1
    ) -> None:
        """
        Send 'Note On' message to the specified MIDI channel.

        :param note: int MIDI note number (0–127), default is 60 (Middle C).
        :param velocity: int Note velocity (0–127), default is 127.
        :param channel: int MIDI channel (1–16), default is 1.
        """
        self.send_channel_message(NOTE_ON, note, velocity, channel)

    def send_note_off(
        self, note: int = 60, velocity: int = 0, channel: int = 1
    ) -> None:
        """
        Send address 'Note Off' message
        :param note: int MIDI note number (0–127), default is 60 (Middle C).
        :param velocity: int Note velocity (0–127), default is 127.
        :param channel: int MIDI channel (1–16), default is 1.
        """
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
        Send address bank select message.
        :param msb: int Upper byte of the bank.
        :param lsb: int Lower byte of the bank.
        :param channel: int midi channel (0-15).
        :return: bool True if successful, False otherwise.
        """
        log_message("========Sending bank select==========")
        log_parameter("MSB", msb)
        log_parameter("LSB", lsb)
        log_parameter("channel", channel)
        try:
            # Bank Select MSB (CC#0)
            self.send_raw_message([0xB0 + channel, 0x00, msb])
            # Bank Select LSB (CC#32)
            self.send_raw_message([0xB0 + channel, 0x20, lsb])
            return True
        except (ValueError, TypeError, OSError, IOError) as ex:
            log_error(f"Error sending bank select: {ex}")
            return False

    def send_identity_request(self) -> bool:
        """
        Send identity request message (Universal System Exclusive).

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        log_message("=========Sending identity request========")
        try:
            identity_request_message = IdentityRequestMessage()
            identity_request_bytes_list = identity_request_message.to_message_list()
            log_message(
                f"sending identity request message: "
                f"{type(identity_request_bytes_list)} {identity_request_bytes_list}"
            )
            self.send_raw_message(identity_request_bytes_list)
            return True
        except (ValueError, TypeError, OSError, IOError) as ex:
            log_error(f"Error sending identity request: {ex}")
            return False

    def send_midi_message(self, sysex_message: MidiMessage) -> bool:
        """
        Send SysEx parameter change message using a MidiMessage.

        :param sysex_message: MidiMessage instance to be converted and sent.
        :return: True if the message was successfully sent, False otherwise.
        """
        try:
            message = sysex_message.to_message_list()
            return self.send_raw_message(message)

        except (ValueError, TypeError, OSError, IOError) as ex:
            log_error(f"Error sending message: {ex}")
            return False

    def send_program_change(self, program: int, channel: int = 0) -> bool:
        """
        Send address program change message.
        :param program: int Program number (0-127).
        :param channel: int MIDI channel (0-15).
        :return: True if successful, False otherwise.
        """
        log_message("=====Sending program change====")
        log_parameter("program", program)
        log_parameter("channel", channel)
        try:
            program_change_message = ProgramChangeMessage(
                channel=channel, program=program
            )
            message = program_change_message.to_message_list()
            return self.send_raw_message(message)
        except (ValueError, TypeError, OSError, IOError) as ex:
            log_error(f"Error sending program change: {ex}")
            return False

    def send_control_change(
        self, controller: int, value: int, channel: int = 0
    ) -> bool:
        """
        Send address control change message.

        :param controller: int Controller number (0–127).
        :param value: int Controller value (0–127).
        :param channel: int MIDI channel (0–15).
        :return: True if successful, False otherwise.
        """
        log_message("=====Sending control change====")
        log_parameter("controller", controller)
        log_parameter("value", value)
        log_parameter("channel", channel)
        if not 0 <= channel <= 15:
            log_message(f"Invalid MIDI channel: {channel}. Must be 0-15.")
            return False
        if not 0 <= controller <= 127:
            log_message(f"Invalid controller number: {controller}. Must be 0-127.")
            return False
        if not 0 <= value <= 127:
            log_message(f"Invalid controller value: {value}. Must be 0-127.")
            return False
        try:
            control_change_message = ControlChangeMessage(channel, controller, value)
            message = control_change_message.to_message_list()
            return self.send_raw_message(message)
        except (ValueError, TypeError, OSError, IOError) as ex:
            log_message(f"send_control_change: Error sending control change: {ex}")
            return False

    def send_rpn(self, parameter: int, value: int, channel: int = 0) -> bool:
        """
        Send a Registered Parameter Number (RPN) message via MIDI Control Change.

        :param parameter: int RPN parameter number (0–16383).
        :param value: int Parameter value (0–16383).
        :param channel: int MIDI channel (0–15).
        :return: True if messages sent successfully, False otherwise.
        """
        log_message("========sending rpn=========")
        if not 0 <= parameter <= 16383:
            log_message(f"Invalid RPN parameter: {parameter}. Must be 0–16383.")
            return False
        if not 0 <= value <= 16383:
            log_message(f"Invalid RPN value: {value}. Must be 0–16383.")
            return False

        # Split into MSB/LSB
        rpn_msb = (parameter >> 7) & JDXiBitMask.LOW_7_BITS
        rpn_lsb = parameter & JDXiBitMask.LOW_7_BITS
        value_msb = (value >> 7) & JDXiBitMask.LOW_7_BITS
        value_lsb = value & JDXiBitMask.LOW_7_BITS

        success = (
            self.send_control_change(101, rpn_msb, channel)
            and self.send_control_change(100, rpn_lsb, channel)  # RPN MSB
            and self.send_control_change(6, value_msb, channel)  # RPN LSB
            and self.send_control_change(  # Data Entry MSB
                38, value_lsb, channel
            )  # Data Entry LSB
        )

        if success:
            log_message("Success: Sent RPN")
            log_parameter("Param", parameter)
            log_parameter("Value", value)
            log_parameter("Channel", channel)
        else:
            log_message("Failed to send RPN messages.")

        return success

    def send_nrpn(
        self, parameter: int, value: int, channel: int = 0, use_14bit: bool = False
    ) -> bool:
        """
        Send a Non-Registered Parameter Number (NRPN) message via MIDI Control Change.

        :param parameter: int NRPN parameter number (0–16383).
        :param value: int Parameter value (0–16383 for 14-bit, 0–127 for 7-bit).
        :param channel: int MIDI channel (0–15).
        :param use_14bit: bool If True, send both MSB and LSB for value (14-bit). If False, send only MSB (7-bit).
        :return: True if all messages were sent successfully, False otherwise.
        """
        log_message("========sending nrpn=========")
        log_parameter("parameter", parameter)
        log_parameter("value", value)
        log_parameter("channel", channel)
        log_parameter("use_14bit", use_14bit)
        if not 0 <= parameter <= 16383:
            log_message(f"Invalid NRPN parameter: {parameter}. Must be 0–16383.")
            return False
        if not 0 <= value <= (16383 if use_14bit else 127):
            log_message(
                f"Invalid NRPN value: {value}. Must be 0–{16383 if use_14bit else 127}."
            )
            return False

        nrpn_msb = (parameter >> 7) & JDXiBitMask.LOW_7_BITS
        nrpn_lsb = parameter & JDXiBitMask.LOW_7_BITS
        if use_14bit:
            value_msb = (value >> 7) & JDXiBitMask.LOW_7_BITS
            value_lsb = value & JDXiBitMask.LOW_7_BITS
        else:
            value_msb = value & JDXiBitMask.LOW_7_BITS
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
            log_message("Sent NRPN:")
            log_parameter("parameter", parameter)
            log_parameter("value", value)
            log_parameter("channel", channel)
        else:
            log_message("Failed to send NRPN messages.")
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
            log_message("========send_bank_select_and_program_change=========")
            log_parameter("channel", channel)
            log_parameter("bank_msb", bank_msb)
            log_parameter("bank_lsb", bank_lsb)
            log_parameter("program", program)
            log_message(
                f"-------#1 send_control_change controller=0, bank_msb={bank_msb}, channel: {channel} --------"
            )
            self.send_control_change(0, bank_msb, channel)
            log_message(
                f"-------#2 send_control_change controller=32, bank_lsb={bank_lsb}, channel: {channel} --------"
            )
            self.send_control_change(32, bank_lsb, channel)
            log_message(
                f"-------#3 send_program_change program: {program} channel: {channel} --------"
            )
            self.send_program_change(program, channel)
            return True
        except Exception as ex:
            log_error(f"Error {ex} occurred sending bank and program change message")
            return False

    def identify_device(self) -> bool:
        """Send Identity Request and verify response"""
        request = IdentityRequestMessage()
        self.send_message(request)
        log_parameter("sending identity request message:", request)

    def send_message(self, message: MidiMessage):
        """unpack the message list and send it"""
        try:
            raw_message = message.to_message_list()
            self.send_raw_message(raw_message)
            log_parameter("Sent MIDI message:", raw_message)

        except Exception as ex:
            log_error(f"Error sending identity request: {str(ex)}")

    def get_parameter(self, msb: int, umb: int, lmb: int, param: int) -> Optional[int]:
        """
        Request a parameter value from the JD-Xi.
        :param msb: Most significant byte of the address.
        :param umb: Upper middle byte of the address.
        :param lmb: Lower middle byte of the address.
        :param param: Address parameter to request.
        :return: Nonne
        """
        log_message("Requesting parameter")
        log_parameter("msb", msb)
        log_parameter("umb", umb)
        log_parameter("lmb", lmb)
        log_parameter("param", param)

        if not self.midi_out.is_port_open() or not self.midi_in.is_port_open():
            log_message("MIDI ports not open")
            return None

        try:
            # Construct SysEx request using SysExMessage
            request = SysExMessage(
                manufacturer_id=[RolandID.ROLAND_ID],
                device_id=RolandID.DEVICE_ID,
                model_id=[ModelID.MODEL_ID_1, ModelID.MODEL_ID_2, ModelID.MODEL_ID_3, ModelID.MODEL_ID_4],  # Example model ID
                command=CommandID.RQ1,  # RQ1 (Request Data) command for Roland
                address=[msb, umb, lmb, param],  # Address of parameter
                data=[],  # No payload for request
            )

            self.midi_out.send_message(request.to_bytes())

            # Wait for response with a timeout of 100ms.
            start_time = time.time()
            while time.time() - start_time < 0.1:
                message = self.midi_in.get_message()
                if message:
                    msg, _ = message
                    if len(msg) >= ONE_BYTE_SYSEX_DATA_LENGTH and msg[JDXiSysExOffset.SYSEX_START] == JDXiMidiConstant.START_OF_SYSEX and msg[JDXiSysExOffset.SYSEX_END] == END_OF_SYSEX:
                        # Parse response
                        response = SysExMessage.from_bytes(bytes(msg))
                        # Extract parameter value
                        return response.data[0] if response.data else None

                time.sleep(0.001)

            logging.warning("Timeout waiting for parameter response")
            raise TimeoutError

        except (TimeoutError, OSError, IOError) as ex:
            log_error(f"Error getting parameter: {ex}")
            return None

    def save_patch(self, file_path: str) -> bool:
        """
        Save the current patch to a file in JD-Xi format.
        :param file_path: str Path to the file where the patch will be saved.
        :return: bool True if successful, False otherwise.
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

            log_message(f"Patch saved to {file_path}")
            return True
        except Exception as ex:
            log_error(f"Error saving patch: {str(ex)}")
            return False

    def _get_digital_parameters(self):
        """Get digital parameters"""
        parameters = {}
        for area in AddressStartMSB.DIGITAL_L:
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
