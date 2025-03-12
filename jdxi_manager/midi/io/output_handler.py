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

from jdxi_manager.midi.data.constants import START_OF_SYSEX, DEVICE_ID, MODEL_ID_1, END_OF_SYSEX
from jdxi_manager.midi.data.constants.sysex import ROLAND_ID, MODEL_ID_2, MODEL_ID_3, MODEL_ID_4
from jdxi_manager.midi.io.controller import MidiIOController
from jdxi_manager.midi.sysex.messages import IdentityRequest
from jdxi_manager.midi.sysex.roland import RolandSysEx
from jdxi_manager.midi.sysex.sysex import SysExMessage
from jdxi_manager.midi.sysex.utils import calculate_checksum
from jdxi_manager.midi.utils.byte import split_value_to_nibbles


def format_midi_message_to_hex_string(message):
    formatted_message = " ".join([hex(x)[2:].upper().zfill(2) for x in message])
    return formatted_message


def construct_address(area, group, param, part):
    # Address construction
    address = [area, part, group & 0xFF, param & 0xFF]
    return address


def increment_group(group, param):
    # Adjust group if param exceeds 127
    if param > 127:
        group += 1
    return group


class MIDIOutHandler(MidiIOController):
    """Helper class for MIDI communication with the JD-Xi."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.channel = 1

    def send_message(self, message: List[int]) -> bool:
        """
        Send a raw MIDI message with validation.

        Args:
            message: List of integer values representing the MIDI message.

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        logging.info(f"attempting to send message: {type(message)} {message}")
        if not message:
            logging.info("MIDI message is empty.")
            return False

        if any(not (0 <= x <= 255) for x in message):
            logging.info(f"Invalid MIDI value detected: {message}")
            return False

        formatted_message = format_midi_message_to_hex_string(message)
        logging.info(f"Sending MIDI message: {formatted_message}")

        if not self.midi_out.is_port_open():
            logging.info("MIDI output port is not open.")
            return False

        try:
            logging.info(
                f"Validation passed, sending MIDI message: {type(formatted_message)} {formatted_message}"
            )
            self.midi_out.send_message(message)
            return True
        except Exception as ex:
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
    ):
        """
        Send address MIDI channel mode message.

        Args:
            status: Status byte (e.g., NOTE_ON, NOTE_OFF).
            data1: First data byte (optional).
            data2: Second data byte (optional).
            channel: MIDI channel (1-based).
        """
        msg = [(status & 0xF0) | ((channel - 1) & 0x0F)]
        if data1 is not None:
            msg.append(data1 & 0x7F)
            if data2 is not None:
                msg.append(data2 & 0x7F)

        if self.midi_out.is_port_open():
            self.midi_out.send_message(msg)
            logging.debug(f"Sent MIDI message: {msg}")
        else:
            logging.error("MIDI output port not open")

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
        if not self.midi_out.is_port_open():
            logging.error("MIDI output port not open")
            return False

        try:
            # Bank Select MSB (CC#0)
            self.send_message([0xB0 + channel, 0x00, msb])
            # Bank Select LSB (CC#32)
            self.send_message([0xB0 + channel, 0x20, lsb])
            return True
        except Exception as e:
            logging.error(f"Error sending bank select: {e}")
            return False

    def send_identity_request(self) -> bool:
        """
        Send identity request message (Universal System Exclusive).

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        logging.debug("Sending identity request")
        try:
            request = IdentityRequest()
            request_bytes_list = request.to_list()
            logging.info(f"sending identity request message: {type(request_bytes_list)} {request_bytes_list}")
            self.send_message(request_bytes_list)
        except Exception as e:
            logging.error(f"Error sending identity request: {e}")
            return False

    def send_parameter(self, area: int, part: int, group: int, param: int, value: int, size: int = 1) -> bool:
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

            # Determine the value format
            if size == 1:
                data_bytes = [value & 0x7F]  # Single byte (0-127)
            elif size in [4, 5]:
                data_bytes = split_value_to_nibbles(value, size)  # Convert to nibbles
            else:
                logging.error(f"Unsupported parameter size: {size}")
                return False

            # Create a RolandSysEx message
            sysex_message = RolandSysEx()
            message = sysex_message.construct_sysex(address, *data_bytes)

            # Convert to a readable format for logging
            formatted_message = format_midi_message_to_hex_string(message)
            logging.info(f"Sending SysEx message: {formatted_message}")

            return self.send_message(message)

        except Exception as ex:
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
        if not self.midi_out.is_port_open():
            logging.error("MIDI output port not open")
            return False

        try:
            msg = [0xC0 + channel, program & 0x7F]
            formatted_msg = format_midi_message_to_hex_string(msg)
            logging.debug(f"Sending program change message: {formatted_msg}")
            return self.send_message(msg)
        except Exception as e:
            logging.error(f"Error sending program change: {e}")
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
            f"Attempting to send control change: controller {controller} value {value} channel {channel}"
        )
        try:
            message = [0xB0 + channel, controller & 0x7F, value & 0x7F]
            formatted_msg = format_midi_message_to_hex_string(message)
            logging.debug(f"Sending control change message: {formatted_msg}")
            return self.send_message(message)
        except Exception as e:
            logging.error(f"Error sending control change: {e}")
            return False

    def send_bank_and_program_change(
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
        if not (
            self.send_control_change(0, bank_msb, channel)
            and self.send_control_change(32, bank_lsb, channel)
            and self.send_program_change(program, channel)
        ):
            return False
        return True

    def select_synth_tone(
        self, patch_number: int, bank: str = "preset", channel: int = 0
    ) -> bool:
        """
        Select address Synth Tone on the JD-Xi using address Program Change.

        Args:
            patch_number: Patch number (1-128) as listed in JD-Xi documentation.
            bank: "preset" (default) or "user" to select the correct bank.
            channel: MIDI channel (0-15).
        Returns:
            True if the message was sent successfully, False otherwise.
        """
        if not (1 <= patch_number <= 128):
            logging.error("Patch number must be between 1 and 128.")
            return False

        # JD-Xi uses 0-based program numbers
        program_number = patch_number - 1
        bank = bank.lower()

        if bank == "preset":
            bank_msb = 92  # Preset Bank
        elif bank == "user":
            bank_msb = 93  # User Bank
        else:
            logging.error("Invalid bank preset_type. Use 'preset' or 'user'.")
            return False

        bank_lsb = 0  # Always 0 for JD-Xi

        if (
            self.send_control_change(0, bank_msb, channel)
            and self.send_control_change(32, bank_lsb, channel)
            and self.send_program_change(program_number, channel)
        ):
            logging.info(
                f"Selected {bank.capitalize()} Synth Tone #{patch_number} (PC {program_number}) on channel {channel}."
            )
            return True
        return False

    def get_parameter(self, area: int, part: int, group: int, param: int) -> Optional[int]:
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
        logging.info(f"Requesting parameter: area={area}, part={part}, group={group}, param={param}")

        if not self.midi_out.is_port_open() or not self.midi_in.is_port_open():
            logging.error("MIDI ports not open")
            return None

        try:
            # Construct SysEx request using SysExMessage
            request = SysExMessage(
                manufacturer_id=[ROLAND_ID],
                device_id=DEVICE_ID,
                model_id=[0x00, 0x00, 0x3B, 0x00],  # Example model ID
                command=0x11,  # RQ1 (Request Data) command for Roland
                address=[area, part, group, param],  # Address of parameter
                data=[]  # No payload for request
            )

            self.midi_out.send_message(request.to_bytes())

            # Wait for response with a timeout of 100ms.
            start_time = time.time()
            while time.time() - start_time < 0.1:
                message = self.midi_in.get_message()
                if message:
                    msg, _ = message
                    if len(msg) >= 11 and msg[0] == 0xF0 and msg[-1] == 0xF7:
                        response = SysExMessage.from_bytes(bytes(msg))  # Parse response
                        return response.data[0] if response.data else None  # Extract parameter value

                time.sleep(0.001)

            logging.warning("Timeout waiting for parameter response")
            raise TimeoutError

        except Exception as ex:
            logging.error(f"Error getting parameter: {ex}")
            return None

    def request_parameter(self, area: int, part: int, group: int, param: int) -> bool:
        """
        Send address non-blocking parameter request message.

        Args:
            area: Parameter area.
            part: Part number.
            group: Parameter area.
            param: Parameter number.
        Returns:
            True if the message was sent successfully, False otherwise.
        """
        if not self.midi_out.is_port_open():
            logging.error("MIDI output port not open")
            return False

        try:
            request = [
                0xF0,
                0x41,
                0x10,
                0x00,
                0x00,
                0x3B,
                area,
                part,
                group,
                param,
                0xF7,
            ]
            return self.send_message(request)
        except Exception as e:
            logging.error(f"Error requesting parameter: {e}")
            return False

    def send_cc(self, cc: int, value: int, channel: int = 0) -> bool:
        """
        Send address Control Change (CC) message.

        Args:
            cc: Control Change number (0-127).
            value: Control Change value (0-127).
            channel: MIDI channel (0-15).
        Returns:
            True if the message was sent successfully, False otherwise.
        """
        logging.debug(f"Sending CC: cc={cc}, value={value}, channel={channel}")
        try:
            if not self.is_output_open:
                logging.warning("MIDI output not open")
                return False

            msg = [0xB0 + channel, cc & 0x7F, value & 0x7F]
            formatted_msg = format_midi_message_to_hex_string(msg)
            logging.debug(f"Sending CC message: {formatted_msg}")
            self.midi_out.send_message(msg)
            logging.debug(f"Sent CC {cc}={value} on ch{channel}")
            return True
        except Exception as e:
            logging.error(f"Error sending CC message: {e}")
            return False

    def send_sysex_rq1(self, device_id: List[int], address: List[int], size: List[int]):
        """
        Send address SysEx Request (RQ1) message.

        The address and size indicate the preset_type and amount of data that is requested.

        Args:
            device_id: List of device-specific data (e.g., [0x41, 0x10, 0x00, 0x00, 0x00, 0x0E] for Roland JD-Xi).
            address: Base address where to save data.
            size: List of four bytes representing the size (e.g., [MSB, second, third, LSB]).
        """
        sysex_data = device_id + [0x11] + address + size + [0]
        logging.debug(f"Sending SysEx message: {type(sysex_data)} {sysex_data}")
        self.midi_out.send_message(sysex_data)
