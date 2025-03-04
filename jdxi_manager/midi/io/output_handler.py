"""
MIDI Output Handler

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

from jdxi_manager.midi.io.controller import MidiIOController
from jdxi_manager.midi.utils.byte import split_value_to_nibbles


class MIDIOutHandler(MidiIOController):
    """Helper class for MIDI communication with the JD-Xi."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.channel = 1

    def send_message(self, message: List[int]) -> bool:
        """
        Send address raw MIDI message with validation.

        Args:
            message: List of integer values representing the MIDI message.
        Returns:
            True if the message was sent successfully, False otherwise.
        """
        formatted_message = " ".join([hex(x)[2:].upper().zfill(2) for x in message])
        logging.debug(f"Sending MIDI message: {formatted_message}")

        if not self.midi_out.is_port_open():
            logging.error("MIDI output port not open")
            return False

        try:
            logging.debug(f"Validation passed, sending MIDI message: {formatted_message}")
            self.midi_out.send_message(message)
            return True
        except Exception as e:
            logging.error(f"Error sending MIDI message: {e}")
            return False

    def send_note_on(self, note: int = 60, velocity: int = 127, channel: int = 1):
        """Send address 'Note On' message."""
        self.send_channel_message(NOTE_ON, note, velocity, channel)

    def send_note_off(self, note: int = 60, velocity: int = 0, channel: int = 1):
        """Send address 'Note Off' message."""
        self.send_channel_message(NOTE_OFF, note, velocity, channel)

    def send_channel_message(self, status: int, data1: Optional[int] = None,
                             data2: Optional[int] = None, channel: int = 1):
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
            # Identity Request: F0 7E 7F 06 01 F7
            return self.send_message([0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7])
        except Exception as e:
            logging.error(f"Error sending identity request: {e}")
            return False

    def send_parameter_experimental(self, area: int, part: int, group: int, param: int, value: int, size: int = 1) -> bool:
        """
        Send address parameter change message.

        Args:
            area: Parameter area (e.g., Program, Digital Synth).
            part: Part number.
            group: Parameter group.
            param: Parameter number.
            value: Parameter value.
            size: Size of the value in bytes (1, 4, or 5).
        Returns:
            True if successful, False otherwise.
        """
        logging.info(
            f"Sending parameter: area={hex(area)}, part={hex(part)}, group={hex(group)}, param={hex(param)}, value={value}, size={size}")

        if not self.is_output_open:
            logging.warning("MIDI output not open")
            return False

        try:
            # Construct the address portion of the message
            if param > 127:
                group = group + 1
            address = [area, part, group & 0xFF, param & 0xFF]

            def increment_byte_list(parameter_value: int, size: int):
                """
                Given an integer and size (4 or 5), split it into the corresponding number of bytes.
                """
                bytes_list = []
                for i in range(size):
                    # Each byte is 7 bits, so we extract the appropriate 7 bits for the current byte
                    byte = (parameter_value >> (7 * (size - i - 1))) & 0x7F
                    bytes_list.append(byte)
                return bytes_list

            if size == 1:
                message = [
                              0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12,  # SysEx header
                          ] + address + [
                              value & 0x7F,  # Parameter value (0-127)
                              0x00,  # Placeholder for checksum
                              0xF7  # End of SysEx
                          ]

            elif size == 4 or size == 5:
                byte_list = increment_byte_list(value, size)
                message = [
                              0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12,
                          ] + address + byte_list + [0x00, 0xF7]  # Add checksum placeholder

            else:
                logging.error(f"Unsupported parameter size: {size}")
                return False

            # Calculate checksum (for message[8:-2])
            checksum = (128 - (sum(message[8:-2]) & 0x7F)) & 0x7F
            message[-2] = checksum

            formatted_message = " ".join([hex(x)[2:].upper().zfill(2) for x in message])
            logging.info(f"Sending parameter message: {formatted_message}")
            return self.send_message(message)

        except Exception as e:
            logging.error(f"Error sending parameter: {e}")
            return False

    def send_parameter(self, area: int, part: int, group: int, param: int, value: int, size: int = 1) -> bool:
        """
        Send address parameter change message.

        Args:
            area: Parameter area (e.g., Program, Digital Synth).
            part: Part number.
            group: Parameter group.
            param: Parameter number.
            value: Parameter value.
            size: Size of the value in bytes (1, 4, or 5).
        Returns:
            True if successful, False otherwise.
        """
        logging.info(
            f"Sending parameter: area={hex(area)}, part={hex(part)}, group={hex(group)}, param={hex(param)}, value={value}, size={size}")

        if not self.is_output_open:
            logging.warning("MIDI output not open")
            return False

        try:
            # Construct the address portion of the message
            if param > 127:
                group = group + 1
            address = [area, part, group & 0xFF, param & 0xFF]

            def increment_byte_list(parameter_value: int):
                # Handle the 0x00 to 0x0F cycle for the last byte
                last_byte = parameter_value % 16

                # Handle the increment of the second byte after every 16 steps
                second_byte = (parameter_value // 16) % 16

                # Handle the increment of the first byte after every 256 steps
                first_byte = (parameter_value // 256)

                # Return the three incrementing bytes
                increment_bytes = [0x00, first_byte, second_byte, last_byte]

                return increment_bytes

            if size == 1:
                message = [
                              0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12,  # SysEx header
                          ] + address + [
                              value & 0x7F,  # Parameter value (0-127)
                              0x00,  # Placeholder for checksum
                              0xF7  # End of SysEx
                          ]

            elif size in [4, 5]:
                # byte_list = increment_byte_list(value)
                value_byte_list = split_value_to_nibbles(value, size)
                message = [
                              0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12,
                          ] + address + value_byte_list + [0x00, 0xF7]  # Add checksum placeholder
            else:
                logging.error(f"Unsupported parameter size: {size}")
                return False
            """ 
            elif size == 5:
                value_byte_list = [
                    (value >> 28) & 0x7F,  # First 7 bits of MSB
                    (value >> 21) & 0x7F,  # Second 7 bits
                    (value >> 14) & 0x7F,  # Third 7 bits
                    (value >> 7) & 0x7F,   # Fourth 7 bits
                    value & 0x7F + 1       # Least significant 7 bits (adjusted)
                ]

                message = [
                              0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12,
                          ] + address + value_byte_list + [0x00, 0xF7]  # Add checksum placeholder
            """
            # Calculate checksum (for message[8:-2])
            checksum = (128 - (sum(message[8:-2]) & 0x7F)) & 0x7F
            message[-2] = checksum

            formatted_message = " ".join([hex(x)[2:].upper().zfill(2) for x in message])
            logging.info(f"Sending parameter message: {formatted_message}")
            return self.send_message(message)

        except Exception as e:
            logging.error(f"Error sending parameter: {e}")
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
            formatted_msg = " ".join([hex(x)[2:].upper().zfill(2) for x in msg])
            logging.debug(f"Sending program change message: {formatted_msg}")
            return self.send_message(msg)
        except Exception as e:
            logging.error(f"Error sending program change: {e}")
            return False

    def send_control_change(self, controller: int, value: int, channel: int = 0) -> bool:
        """
        Send address control change message.

        Args:
            controller: Controller number (0-127).
            value: Controller value (0-127).
            channel: MIDI channel (0-15).
        Returns:
            True if successful, False otherwise.
        """
        if not self.midi_out.is_port_open():
            logging.error("MIDI output port not open")
            return False

        try:
            msg = [0xB0 + channel, controller & 0x7F, value & 0x7F]
            formatted_msg = " ".join([hex(x)[2:].upper().zfill(2) for x in msg])
            logging.debug(f"Sending control change message: {formatted_msg}")
            return self.send_message(msg)
        except Exception as e:
            logging.error(f"Error sending control change: {e}")
            return False

    def send_bank_and_program_change(self, channel: int, bank_msb: int, bank_lsb: int, program: int) -> bool:
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
        if not (self.send_control_change(0, bank_msb, channel) and
                self.send_control_change(32, bank_lsb, channel) and
                self.send_program_change(program, channel)):
            return False
        return True

    def select_synth_tone(self, patch_number: int, bank: str = "preset", channel: int = 0) -> bool:
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

        if (self.send_control_change(0, bank_msb, channel) and
            self.send_control_change(32, bank_lsb, channel) and
            self.send_program_change(program_number, channel)):
            logging.info(f"Selected {bank.capitalize()} Synth Tone #{patch_number} (PC {program_number}) on channel {channel}.")
            return True
        return False

    def get_parameter(self, area: int, part: int, group: int, param: int) -> Optional[int]:
        """
        Get parameter value via MIDI System Exclusive message.

        Args:
            area: Parameter area (e.g., Digital Synth 1).
            part: Part number.
            group: Parameter group.
            param: Parameter number.
        Returns:
            Parameter value (0-127) or None if an error occurs.
        """
        logging.info(f"Requesting parameter: area={area}, address={part}, group={group}, param={param}")
        if not self.midi_out.is_port_open() or not self.midi_in.is_port_open():
            logging.error("MIDI ports not open")
            return None

        try:
            request = [
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x3B,
                area, part, group, param,
                0xF7
            ]
            self.midi_out.send_message(request)

            # Wait for response with address timeout of 100ms.
            start_time = time.time()
            while time.time() - start_time < 0.1:
                message = self.midi_in.get_message()
                if message:
                    msg, _ = message
                    if len(msg) >= 11 and msg[0] == 0xF0 and msg[-1] == 0xF7:
                        return msg[10]  # Value is at index 10
                time.sleep(0.001)

            logging.warning("Timeout waiting for parameter response")
            return None

        except Exception as e:
            logging.error(f"Error getting parameter: {e}")
            return None

    def request_parameter(self, area: int, part: int, group: int, param: int) -> bool:
        """
        Send address non-blocking parameter request message.

        Args:
            area: Parameter area.
            part: Part number.
            group: Parameter group.
            param: Parameter number.
        Returns:
            True if the message was sent successfully, False otherwise.
        """
        if not self.midi_out.is_port_open():
            logging.error("MIDI output port not open")
            return False

        try:
            request = [
                0xF0, 0x41, 0x10, 0x00, 0x00, 0x3B,
                area, part, group, param,
                0xF7
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
            formatted_msg = " ".join([hex(x)[2:].upper().zfill(2) for x in msg])
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
        logging.debug(f"Sending SysEx message: {sysex_data}")
        self.midi_out.send_message(sysex_data)
