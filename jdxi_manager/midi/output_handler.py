import logging
import time
from typing import List, Callable, Optional

from rtmidi.midiconstants import NOTE_ON, NOTE_OFF

from jdxi_manager.data.digital import get_digital_parameter_by_address
from jdxi_manager.midi.basenew import MIDIBaseNew


class MIDIOutHandlerNew(MIDIBaseNew):
    """Helper class for MIDI communication with the JD-Xi"""

    # parameter_received = Signal(list, int)  # address, value
    # json_sysex = Signal(str)  # json string only
    # parameter_changed = Signal(object, int)  # Emit parameter and value
    # preset_changed = Signal(int, str, int)
    # incoming_midi_message = Signal(object)
    # program_changed = Signal(int, int)  # Add signal for program changes (channel, program)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.callbacks: List[Callable] = []
        self.channel = 1
        self.preset_number = 0
        self.cc_number = 0
        self.cc_msb_value = 0
        self.cc_lsb_value = 0

    @staticmethod
    def _extract_patch_name(patch_name_bytes):
        """Extract ASCII patch name from SysEx message data."""
        return "".join(chr(b) for b in patch_name_bytes if 32 <= b <= 127).strip()

    def _get_parameter_from_address(self, address):
        """Map address to a DigitalParameter"""
        # Ensure the address is at least two elements
        if len(address) < 2:
            raise ValueError(
                f"Address must contain at least 2 elements, got {len(address)}"
            )

        # Extract the relevant part of the address (group, address pair)
        parameter_address = tuple(
            address[1:2]
        )  # Assuming address structure [group, address, ...]

        # Retrieve the corresponding DigitalParameter
        param = get_digital_parameter_by_address(parameter_address)

        if param:
            return param
        else:
            raise ValueError(
                f"Invalid address {parameter_address} - no corresponding DigitalParameter found."
            )

    def send_message(self, message: List[int]) -> bool:
        """Send raw MIDI message with validation"""
        logging.debug(
            f"Sending MIDI message: {' '.join([hex(x)[2:].upper().zfill(2) for x in message])}"
        )
        if not self.midi_out.is_port_open():
            logging.error("MIDI output port not open")
            return False

        try:
            # Validate SysEx messages
            # if message[0] == 0xF0:
            #    if not validate_sysex_message(message):
            #        logging.debug(f"Validation failed for message: {' '.join([hex(x)[2:].upper().zfill(2) for x in message])}")
            #        return False

            logging.debug(
                f"Validation passed, sending MIDI message: {' '.join([hex(x)[2:].upper().zfill(2) for x in message])}"
            )
            self.midi_out.send_message(message)
            return True
        except Exception as e:
            logging.error(f"Error sending MIDI message: {str(e)}")
            return False

    def send_note_on(self, note=60, velocity=127, channel=1):
        """Send a 'Note On' message."""
        self.send_channel_message(NOTE_ON, note, velocity, channel)

    def send_note_off(self, note=60, velocity=0, channel=1):
        """Send a 'Note Off' message."""
        self.send_channel_message(NOTE_OFF, note, velocity, channel)

    def send_channel_message(self, status, data1=None, data2=None, channel=1):
        """Send a MIDI channel mode message."""
        msg = [(status & 0xF0) | ((channel - 1) & 0xF)]

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
        """Send bank select messages

        Args:
            msb: Bank Select MSB value (0-127)
            lsb: Bank Select LSB value (0-127)
            channel: MIDI channel (0-15)
        """
        logging.debug(f"Sending bank select: {msb} {lsb} {channel}")
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
            logging.error(f"Error sending bank select: {str(e)}")
            return False

    def send_identity_request(self) -> bool:
        """Send identity request message (Universal System Exclusive)"""
        logging.debug(f"Sending identity request")
        try:
            # F0 7E 7F 06 01 F7
            return self.send_message([0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7])
        except Exception as e:
            logging.error(f"Error sending identity request: {str(e)}")
            return False

    def send_parameter(
            self, area: int, part: int, group: int, param: int, value: int
    ) -> bool:
        """Send parameter change message

        Args:
            area: Parameter area (e.g., Program, Digital Synth)
            part: Part number
            group: Parameter group
            param: Parameter number
            value: Parameter value (0-127)

        Returns:
            True if successful, False otherwise
        """
        logging.debug(
            f"Sending parameter: area={area}, part={part}, group={group}, param={param}, value={value}"
        )
        try:
            if not self.is_output_open:
                logging.warning("MIDI output not open")
                return False

            # Ensure all values are integers and within valid ranges
            area = int(area) & 0x7F
            part = int(part) & 0x7F
            group = int(group) & 0x7F
            param = int(param) & 0x7F
            value = int(value) & 0x7F

            # Create parameter message
            message = [
                0xF0,  # Start of SysEx
                0x41,
                0x10,  # Roland ID
                0x00,
                0x00,  # Device ID
                0x00,
                0x0E,  # Model ID
                0x12,  # DT1 Command
                area,  # Parameter area
                part,  # Part number
                group,  # Parameter group
                param,  # Parameter number
                value,  # Parameter value
                0x00,  # Checksum (placeholder)
                0xF7,  # End of SysEx
            ]

            # Calculate checksum
            checksum = (128 - (sum(message[8:-2]) & 0x7F)) & 0x7F
            message[-2] = checksum

            logging.debug(
                f"Sending parameter message: {' '.join([hex(x)[2:].upper().zfill(2) for x in message])}"
            )
            # Send message directly instead of using output_port
            return self.send_message(message)

        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")
            return False

    def send_program_change(self, program: int, channel: int = 0) -> bool:
        """Send program change message

        Args:
            program: Program number (0-127)
            channel: MIDI channel (0-15)
        """
        logging.debug(f"Sending program change: program={program}, channel={channel}")
        if not self.midi_out.is_port_open():
            logging.error("MIDI output port not open")
            return False

        try:
            # Program Change status byte: 0xC0 + channel
            logging.debug(
                f"Sending program change message: {' '.join([hex(x)[2:].upper().zfill(2) for x in [0xC0 + channel, program & 0x7F]])}"
            )
            return self.send_message([0xC0 + channel, program & 0x7F])
        except Exception as e:
            logging.error(f"Error sending program change: {str(e)}")
            return False

    def send_control_change(
            self, controller: int, value: int, channel: int = 0
    ) -> bool:
        """Send control change message

        Args:
            controller: Controller number (0-127)
            value: Controller value (0-127)
            channel: MIDI channel (0-15)
        """
        if not self.midi_out.is_port_open():
            logging.error("MIDI output port not open")
            return False

        try:
            # Control Change status byte: 0xB0 + channel
            logging.debug(
                f"Sending control change message: {' '.join([hex(x)[2:].upper().zfill(2) for x in [0xB0 + channel, controller & 0x7F, value & 0x7F]])}"
            )
            return self.send_message([0xB0 + channel, controller & 0x7F, value & 0x7F])
        except Exception as e:
            logging.error(f"Error sending control change: {str(e)}")
            return False

    def send_bank_and_program_change(self, channel, bank_msb, bank_lsb, program):
        """Sends Bank Select and Program Change messages."""
        self.send_control_change(channel, 0, bank_msb)  # Bank Select MSB
        self.send_control_change(channel, 32, bank_lsb)  # Bank Select LSB
        self.send_program_change(channel, program)  # Program Change

    def select_synth_tone(
            self, patch_number: int, bank: str = "preset", channel: int = 0
    ) -> bool:
        """
        Select a Synth Tone on the JD-Xi using a Program Change.

        Args:
            patch_number: Patch number (1-128) as listed in JD-Xi documentation.
            bank: "preset" (default) or "user" to select the correct bank.
            channel: MIDI channel (0-15)

        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        if not (1 <= patch_number <= 128):
            logging.error("Patch number must be between 1 and 128.")
            return False

        # JD-Xi uses 0-based program numbers
        program_number = patch_number - 1

        # Select correct bank
        if bank.lower() == "preset":
            bank_msb = 92  # Preset Bank
        elif bank.lower() == "user":
            bank_msb = 93  # User Bank
        else:
            logging.error("Invalid bank type. Use 'preset' or 'user'.")
            return False

        bank_lsb = 0  # Always 0 for JD-Xi

        # Send Bank Select and Program Change
        if not self.send_control_change(0, bank_msb, channel):  # CC#0 (Bank MSB)
            return False
        if not self.send_control_change(32, bank_lsb, channel):  # CC#32 (Bank LSB)
            return False
        if not self.send_program_change(program_number, channel):  # Send Program Change
            return False

        logging.info(
            f"Selected {bank.capitalize()} Synth Tone #{patch_number} (PC {program_number}) on channel {channel}."
        )
        return True

    def get_parameter(
            self, area: int, part: int, group: int, param: int
    ) -> Optional[int]:
        """Get parameter value via MIDI System Exclusive message

        Args:
            area: Parameter area (e.g., Digital Synth 1)
            part: Part number
            group: Parameter group
            param: Parameter number

        Returns:
            Parameter value (0-127) or None if error
        """
        logging.debug(
            f"Requesting parameter: area={area}, part={part}, group={group}, param={param}"
        )
        if not self.midi_out.is_port_open() or not self.midi_in.is_port_open():
            logging.error("MIDI ports not open")
            return None

        try:
            # Format: F0 41 10 00 00 3B {area} {part} {group} {param} F7
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

            # Send parameter request
            self.midi_out.send_message(request)

            # Wait for response (with timeout)
            start_time = time.time()
            while time.time() - start_time < 0.1:  # 100ms timeout
                if self.midi_in.get_message():
                    msg, _ = self.midi_in.get_message()
                    if len(msg) >= 11 and msg[0] == 0xF0 and msg[-1] == 0xF7:
                        # Response format: F0 41 10 00 00 3B {area} {part} {group} {param} {value} F7
                        return msg[10]  # Value is at index 10
                time.sleep(0.001)

            logging.warning("Timeout waiting for parameter response")
            return None

        except Exception as e:
            logging.error(f"Error getting parameter: {str(e)}")
            return None

    def request_parameter(self, area: int, part: int, group: int, param: int) -> bool:
        """Send parameter request message

        This is a non-blocking version that just sends the request without waiting for response.
        The response will be handled by the callback if registered.
        """
        if not self.midi_out.is_port_open():
            logging.error("MIDI output port not open")
            return False

        try:
            # Format: F0 41 10 00 00 3B {area} {part} {group} {param} F7
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
            logging.error(f"Error requesting parameter: {str(e)}")
            return False

    def send_cc(self, cc: int, value: int, channel: int = 0):
        """Send Control Change message

        Args:
            cc: Control Change number (0-127)
            value: Control Change value (0-127)
            channel: MIDI channel (0-15)

        Returns:
            True if successful, False otherwise
        """
        logging.debug(f"Sending CC: cc={cc}, value={value}, channel={channel}")
        try:
            if not self.is_output_open:
                logging.warning("MIDI output not open")
                return False

            # Create Control Change message (Status byte: 0xB0 + channel)
            message = [0xB0 + channel, cc & 0x7F, value & 0x7F]
            logging.debug(
                f"Sending CC message: {' '.join([hex(x)[2:].upper().zfill(2) for x in message])}"
            )
            # Send message using midi_out instead of output_port
            self.midi_out.send_message(message)
            logging.debug(f"Sent CC {cc}={value} on ch{channel}")
            return True

        except Exception as e:
            logging.error(f"Error sending CC message: {str(e)}")
            return False

    def send_sysex_rq1(self, device_id, address, size):
        """
        This message requests the other device to transmit data. The address
        and size indicate the type and amount of data that is requested.

        Parameters
        ----------
        device_id : list
            List of data for a specific device - [0x41, 0x10, 0x00, 0x00, 0x00, 0x0e] for Roland JD-Xi.
        address : list
            Base address where to save data (the last byte is defined in the instrument).
        size : list
            List of four bytes - [MSB, 2nd, 3rd, LSB].
        timeout : int, optional
            Maximum number of attempts to wait for a response (default is 100).

        Returns
        -------
        list or str
            If a valid SysEx response is received, returns the data (excluding header).
            Otherwise, returns 'unknown'.
        """
        # Create the SysEx message
        sysex_data = device_id + [0x11] + address + size + [0]
        logging.debug(f"Sending SysEx message: {sysex_data}")
        self.midi_out.send_message(sysex_data)
        return

    def send_note_on(self, note=60, velocity=127, channel=1):
        """Send a 'Note On' message."""
        self.send_channel_message(NOTE_ON, note, velocity, channel)

    def send_note_off(self, note=60, velocity=0, channel=1):
        """Send a 'Note Off' message."""
        self.send_channel_message(NOTE_OFF, note, velocity, channel)

    def send_channel_message(self, status, data1=None, data2=None, channel=1):
        """Send a MIDI channel mode message."""
        msg = [(status & 0xF0) | ((channel - 1) & 0xF)]

        if data1 is not None:
            msg.append(data1 & 0x7F)

            if data2 is not None:
                msg.append(data2 & 0x7F)

        if self.midi_out.is_port_open():
            self.midi_out.send_message(msg)
            logging.debug(f"Sent MIDI message: {msg}")
        else:
            logging.error("MIDI output port not open")
