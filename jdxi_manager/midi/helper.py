import logging
import re

from pubsub import pub
import rtmidi
from typing import Optional, List, Tuple, Callable
import time
from jdxi_manager.data.preset_data import DIGITAL_PRESETS, DRUM_PRESETS, ANALOG_PRESETS
from PySide6.QtCore import Signal, QObject

from jdxi_manager.data.preset_type import PresetType
from jdxi_manager.midi.constants.sysex import (
    DIGITAL_SYNTH_1_AREA,
    DIGITAL_SYNTH_2_AREA,
    ANALOG_SYNTH_AREA,
    DRUM_KIT_AREA,
)


def find_preset_number(preset_name, presets):
    """
    Find the 1-based index of a preset name in a list of presets, ignoring numerical prefixes.

    Args:
        preset_name (str): The name of the preset to find.
        presets (list of str): The list of preset names with numerical prefixes.

    Returns:
        int or None: The 1-based index of the preset, or None if not found.
    """
    if not isinstance(presets, list) or not isinstance(preset_name, str):
        raise ValueError(
            "Invalid input: 'presets' must be a list and 'preset_name' must be a string."
        )

    # Strip and lower the incoming preset name for comparison
    preset_name_clean = preset_name.strip().lower()

    for index, preset in enumerate(presets):
        # Split the numerical prefix from the preset name
        _, name = preset.split(": ", 1)

        # Compare the stripped and lowercased names
        if name.strip().lower() == preset_name_clean:
            return index + 1  # Convert to 1-based index

    # Return None if no match is found
    return None


class MIDIHelper(QObject):
    """Helper class for MIDI communication with the JD-Xi"""

    parameter_received = Signal(list, int)  # address, value
    preset_changed = Signal(int, str, int)
    midi_note_received = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()
        self.input_port_number: Optional[int] = None
        self.output_port_number: Optional[int] = None
        self.parent = parent
        self.callbacks: List[Callable] = []
        self.channel = 1
        self.preset_number = 0
        self.cc_number = 0
        self.cc_msb_value = 0
        self.cc_lsb_value = 0
        pub.subscribe(self._handle_incoming_midi_message, "incoming_midi_message")

    @property
    def current_in_port(self) -> Optional[str]:
        """Get current input port name"""
        if self.input_port_number is not None and self.is_input_open:
            ports = self.midi_in.get_ports()
            if 0 <= self.input_port_number < len(ports):
                return ports[self.input_port_number]
        return None

    @property
    def current_out_port(self) -> Optional[str]:
        """Get current output port name"""
        if self.output_port_number is not None and self.is_output_open:
            ports = self.midi_out.get_ports()
            if 0 <= self.output_port_number < len(ports):
                return ports[self.output_port_number]
        return None

    def _handle_incoming_midi_message(self, message):
        """Handle incoming MIDI message from pubsub."""
        preset_data = {"modified": 0}
        try:
            print(f"Received MIDI message: {message}")

            message_handlers = {
                "sysex": self._handle_sysex_message,
                "control_change": self._handle_control_change,
                "program_change": self._handle_program_change,
                "note_on": self._handle_note_change,
                "note_off": self._handle_note_change,
            }

            handler = message_handlers[message.type]
            if handler:
                handler(message, preset_data)
            else:
                print(f"Unhandled MIDI message type: {message.type}")

        except Exception as e:
            logging.error(f"Error handling incoming MIDI message: {str(e)}")

    def _handle_note_change(self, message, preset_data):
        print(f"MIDI message type: {message.type} as {message}")

    def _handle_sysex_message(self, message, preset_data):
        """Handle SysEx MIDI messages."""
        try:
            manufacturer_id, device_family_id = message.data[0], message.data[2:6]
            if manufacturer_id != 0x41 or device_family_id != [0x10, 0x00, 0x00, 0x0E]:
                print("Received SysEx message is not from a Roland JD-Xi.")
                return

            print("Valid Roland JD-Xi SysEx message detected.")
            command_type, address_offset = message.data[6], message.data[7:11]
            print(f"Command Type: {command_type:#02X}")
            print(
                f"Address/Parameter Offset: {''.join(f'{byte:02X}' for byte in address_offset)}"
            )

            # Determine which editor to send the message to based on the address
            area_code = address_offset[0]
            if area_code == DIGITAL_SYNTH_1_AREA:
                self.parameter_received.emit(address_offset, message.data[11])
            elif area_code == DIGITAL_SYNTH_2_AREA:
                self.parameter_received.emit(address_offset, message.data[11])
            elif area_code == ANALOG_SYNTH_AREA:
                self.parameter_received.emit(address_offset, message.data[11])
            elif area_code == DRUM_KIT_AREA:
                self.parameter_received.emit(address_offset, message.data[11])

        except Exception as e:
            logging.error(f"Error handling SysEx message: {str(e)}")

    def _handle_control_change(self, message, preset_data):
        """Handle Control Change (CC) MIDI messages."""
        channel, control, value = message.channel + 1, message.control, message.value
        print(
            f"Control Change - Channel: {channel}, Control: {control}, Value: {value}"
        )

        if control == 0:
            self.cc_msb_value = value
        elif control == 32:
            self.cc_lsb_value = value

    def _handle_program_change(self, message, preset_data):
        """Handle Program Change (PC) MIDI messages."""
        channel, program_number = message.channel + 1, message.program
        print(f"Program Change - Channel: {channel}, Program: {program_number}")

        preset_mapping = {
            95: PresetType.DIGITAL_1,
            94: PresetType.ANALOG,
            86: PresetType.DRUMS,
        }

        if self.cc_msb_value in preset_mapping:
            preset_data["type"] = preset_mapping[self.cc_msb_value]
            self.preset_number = program_number + (
                128 if self.cc_lsb_value == 65 else 0
            )

            pub.sendMessage(
                "update_display_preset",
                preset_number=self.preset_number,
                preset_name=(
                    DIGITAL_PRESETS[self.preset_number]
                    if self.preset_number < len(DIGITAL_PRESETS)
                    else "Unknown Preset"
                ),
                channel=channel,
            )
            print(f"Preset changed to: {self.preset_number}")

    @staticmethod
    def _extract_patch_name(patch_name_bytes):
        """Extract ASCII patch name from SysEx message data."""
        return "".join(chr(b) for b in patch_name_bytes if 32 <= b <= 127).strip()

    def register_callback(self, callback: Callable):
        """Register a callback for MIDI messages"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def _midi_callback(self, message, timestamp=None):
        """Internal callback for MIDI messages"""
        try:
            print(f"MIDI message: {message}")
            # Invoke all registered callbacks
            for callback in self.callbacks:
                callback(message, timestamp)

            # Handle SysEx messages separately if needed
            if message[0] == 0xF0:  # SysEx start
                self.handle_sysex_message(message)

        except Exception as e:
            logging.error(f"Error in MIDI callback: {str(e)}")

    def _handle_dt1_message(self, data):
        """Handle Data Set 1 (DT1) messages

        Format: aa bb cc dd ... where:
        aa bb cc = Address
        dd ... = Data
        """
        if len(data) < 4:  # Need at least address and one data byte
            return

        address = data[0:3]
        print(f"Address: {address}")
        value = data[3]
        print(f"Value: {value}")
        # Emit signal with parameter data
        self.parameter_received.emit(address, value)

    def get_input_ports(self) -> List[str]:
        """Get available MIDI input ports"""
        return self.midi_in.get_ports()

    def get_output_ports(self) -> List[str]:
        """Get available MIDI output ports"""
        return self.midi_out.get_ports()

    def get_ports(self) -> Tuple[List[str], List[str]]:
        """Get available MIDI input and output ports"""
        return (self.get_input_ports(), self.get_output_ports())

    def find_jdxi_ports(self) -> Tuple[Optional[str], Optional[str]]:
        """Find JD-Xi input and output ports"""
        in_ports = self.get_input_ports()
        out_ports = self.get_output_ports()

        jdxi_in = next((p for p in in_ports if "jd-xi" in p.lower()), None)
        jdxi_out = next((p for p in out_ports if "jd-xi" in p.lower()), None)

        return (jdxi_in, jdxi_out)

    def validate_sysex_message(self, message: List[int]) -> bool:
        """Validate JD-Xi SysEx message format"""
        try:
            # Check length
            if len(message) not in [15, 18]:
                logging.error(f"Invalid SysEx length: {len(message)}")
                return False

            # Check header
            if message[:7] != [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E]:
                logging.error("Invalid SysEx header")
                return False

            # Check DT1 command
            if message[7] not in [0x12, 0x11]:
                logging.error("Invalid command byte")
                return False

            # Check end marker
            if message[-1] != 0xF7:
                logging.error("Invalid SysEx end marker")
                return False

            # Verify checksum
            data_sum = sum(message[8:-2]) & 0x7F  # Sum from area to value
            checksum = (128 - data_sum) & 0x7F
            if message[-2] != checksum:
                logging.error(
                    f"Invalid checksum: expected {checksum}, got {message[-2]}"
                )
                return False

            return True

        except Exception as e:
            logging.error(f"Error validating SysEx message: {str(e)}")
            return False

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
            #    if not self.validate_sysex_message(message):
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

    def send_bank_select(self, msb: int, lsb: int, channel: int = 0) -> bool:
        """Send bank select messages

        Args:
            msb: Bank Select MSB value (0-127)
            lsb: Bank Select LSB value (0-127)
            channel: MIDI channel (0-15)
        """
        logging.debug(
            f"Sending bank select: {msb} {lsb} {channel}"
        )
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
        logging.debug(
            f"Sending identity request"
        )
        try:
            # F0 7E 7F 06 01 F7
            return self.send_message([0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7])
        except Exception as e:
            logging.error(f"Error sending identity request: {str(e)}")
            return False

    def open_input(self, port_name_or_index) -> bool:
        """Open MIDI input port by name or index"""
        return self.open_input_port(port_name_or_index)

    def open_output(self, port_name_or_index) -> bool:
        """Open MIDI output port by name or index"""
        return self.open_output_port(port_name_or_index)

    def open_input_port(self, port_name_or_index) -> bool:
        """Open MIDI input port by name or index"""
        try:
            ports = self.get_input_ports()
            port_index = port_name_or_index

            if isinstance(port_name_or_index, str):
                for i, name in enumerate(ports):
                    if port_name_or_index.lower() in name.lower():
                        port_index = i
                        break
                else:
                    logging.error(f"MIDI input port not found: {port_name_or_index}")
                    return False

            if not isinstance(port_index, int) or not (0 <= port_index < len(ports)):
                logging.error(f"Invalid MIDI input port index: {port_index}")
                return False

            self.midi_in.open_port(port_index)
            self.input_port_number = port_index
            self.midi_in.set_callback(self._midi_callback)
            logging.info(f"Opened MIDI input port: {ports[port_index]}")
            return True

        except Exception as e:
            logging.error(f"Error opening MIDI input port: {str(e)}")
            return False

    def open_output_port(self, port_name_or_index) -> bool:
        """Open MIDI output port by name or index"""
        try:
            ports = self.get_output_ports()
            port_index = port_name_or_index

            if isinstance(port_name_or_index, str):
                # Find port index by name
                for i, name in enumerate(ports):
                    if port_name_or_index.lower() in name.lower():
                        port_index = i
                        break
                else:
                    logging.error(f"MIDI output port not found: {port_name_or_index}")
                    return False

            # Validate port index
            if not isinstance(port_index, int) or not (0 <= port_index < len(ports)):
                logging.error(f"Invalid MIDI output port index: {port_index}")
                return False

            self.midi_out.open_port(port_index)
            self.output_port_number = port_index
            logging.info(f"Opened MIDI output port: {ports[port_index]}")
            return True

        except Exception as e:
            logging.error(f"Error opening MIDI output port: {str(e)}")
            return False

    def close_ports(self):
        """Close MIDI ports"""
        if self.midi_in.is_port_open():
            self.midi_in.close_port()
        if self.midi_out.is_port_open():
            self.midi_out.close_port()
        self.input_port_number = None
        self.output_port_number = None

    @property
    def is_input_open(self) -> bool:
        """Check if MIDI input port is open"""
        return self.midi_in.is_port_open()

    @property
    def is_output_open(self) -> bool:
        """Check if MIDI output port is open"""
        return self.midi_out.is_port_open()

    def open_ports(self, in_port: str, out_port: str) -> bool:
        """Open both input and output ports by name

        Args:
            in_port: Input port name or None
            out_port: Output port name or None
        """
        try:
            input_success = True
            output_success = True

            if in_port:
                input_success = self.open_input_port(in_port)
            if out_port:
                output_success = self.open_output_port(out_port)

            return input_success and output_success

        except Exception as e:
            logging.error(f"Error opening MIDI ports: {str(e)}")
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

    def handle_sysex_message(self, message):
        """Handle incoming SysEx messages"""
        try:
            if len(message) < 8:  # Minimum length for JD-Xi SysEx
                return

            # Check if this is a data set message (DT1)
            if message[7] == 0x12:  # DT1 command
                self._handle_dt1_message(message[8:])

        except Exception as e:
            logging.error(f"Error handling SysEx message: {str(e)}")

    def set_callback(self, callback):
        self.midi_in.set_callback(callback)
