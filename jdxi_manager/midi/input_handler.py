import json
import logging
from typing import List, Callable

from PySide6.QtCore import Signal
from pubsub import pub

from jdxi_manager.data.digital import get_digital_parameter_by_address
from jdxi_manager.data.preset_data import DIGITAL_PRESETS
from jdxi_manager.data.preset_type import PresetType
from jdxi_manager.midi.basenew import MIDIBaseNew
from jdxi_manager.midi.jsonutils import log_json
from jdxi_manager.midi.parsers import parse_sysex
from jdxi_manager.midi.sysex import SysexParameter


class MIDIInHandlerNew(MIDIBaseNew):
    """Helper class for MIDI communication with the JD-Xi"""

    # parameter_received = Signal(list, int)  # address, value
    # json_sysex = Signal(str)  # json string only
    # parameter_changed = Signal(object, int)  # Emit parameter and value
    # preset_changed = Signal(int, str, int)
    incoming_midi_message = Signal(object)
    program_changed = Signal(int, int)  # Add signal for program changes (channel, program)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.callbacks: List[Callable] = []
        self.channel = 1
        self.preset_number = 0
        self.cc_number = 0
        self.cc_msb_value = 0
        self.cc_lsb_value = 0
        pub.subscribe(self._handle_incoming_midi_message, "incoming_midi_message")

    def _handle_incoming_midi_message(self, message):
        """Handle incoming MIDI messages"""
        if not message.type == "clock":
            self.incoming_midi_message.emit(message)
            logging.info(f"MIDI message of type {message.type} incoming: {message}")
        preset_data = {"modified": 0}
        try:
            message_handlers = {
                "sysex": self._handle_sysex_message,
                "control_change": self._handle_control_change,
                "program_change": self._handle_program_change,
                "note_on": self._handle_note_change,
                "note_off": self._handle_note_change,
                "clock": self._handle_clock,
            }
            handler = message_handlers.get(message.type)
            if handler:
                handler(message, preset_data)
            else:
                logging.info(f"Unhandled MIDI message type: {message.type}")
        except Exception as e:
            logging.error(f"Error handling incoming MIDI message: {str(e)}")

    def _handle_note_change(self, message, preset_data):
        logging.info(f"MIDI message type: {message.type} as {message}")

    def _handle_clock(self, message, preset_data):
        # keep the midi clock quiet!
        if message.type == "clock":
            return

    def _handle_sysex_message(self, message, preset_data):
        """Handle SysEx MIDI messages from Roland JD-Xi."""
        try:
            # Print the raw SysEx message in hex format
            hex_string = " ".join(f"{byte:02X}" for byte in message.data)
            logging.info(f"Received SysEx Message: {hex_string}")
            sysex_message = (
                    [0xF0] + [int(byte, 16) for byte in hex_string.split()] + [0xF7]
            )
            sysex_message_bytes = bytes(sysex_message)
            if len(message.data) > 63:
                # Detect and process JD-Xi tone data
                try:
                    parsed_data = parse_sysex(sysex_message_bytes)
                    json_data = json.dumps(parsed_data)
                    self.json_sysex.emit(json_data)
                    log_json(parsed_data)
                except Exception as ex:
                    logging.info(f"Error parsing JD-Xi tone data: {ex}")

            # Extract command type and parameter address
            try:
                command_type_address, address_offset = (
                    message.data[6],
                    message.data[7:11],
                )
                command_name = SysexParameter.get_command_name(command_type_address)
                logging.info(f"Command: {command_name} ({command_type_address:#02X})")
                logging.info(
                    f"Parameter Offset: {''.join(f'{byte:02X}' for byte in address_offset)}"
                )
            except Exception as ex:
                logging.error(f"Error parsing JD-Xi tone data: {ex}", exc_info=True)

        except Exception as e:
            logging.error(f"Error handling SysEx message: {e}", exc_info=True)

    def _handle_control_change(self, message, preset_data):
        """Handle Control Change (CC) MIDI messages."""
        channel, control, value = message.channel + 1, message.control, message.value
        logging.info(
            f"Control Change - Channel: {channel}, Control: {control}, Value: {value}"
        )
        if control == 0:
            self.cc_msb_value = value
        elif control == 32:
            self.cc_lsb_value = value

    def _handle_program_change(self, message, preset_data):
        """Handle Program Change (PC) MIDI messages."""
        channel, program_number = message.channel + 1, message.program
        logging.info(f"Program Change - Channel: {channel}, Program: {program_number}")

        # Emit the program change signal
        self.program_changed.emit(channel, program_number)

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
            logging.info(f"Preset changed to: {self.preset_number}")

    @staticmethod
    def _extract_patch_name(patch_name_bytes):
        """Extract ASCII patch name from SysEx message data."""
        return "".join(chr(b) for b in patch_name_bytes if 32 <= b <= 127).strip()

    def register_callback(self, callback: Callable):
        """Register a callback for MIDI messages"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def midi_callback(self, message, timestamp=None):
        """Handle incoming MIDI messages"""
        try:
            if message.type == "program_change":
                logging.info(f"Program Change - Channel: {message.channel}, Program: {message.program}")
            if not message.type == "clock":
                self.incoming_midi_message.emit(message)
                logging.info(f"MIDI message of type {message.type} incoming: {message}")
            preset_data = {"modified": 0}
            message_handlers = {
                "sysex": self._handle_sysex_message,
                "control_change": self._handle_control_change,
                "program_change": self._handle_program_change,
                "note_on": self._handle_note_change,
                "note_off": self._handle_note_change,
                "clock": self._handle_clock,
            }
            handler = message_handlers.get(message.type)
            if handler:
                handler(message, preset_data)
            else:
                logging.info(f"Unhandled MIDI message type: {message.type}")
        except Exception as e:
            logging.error(f"Error handling incoming MIDI message: {str(e)}")

    def _handle_dt1_message(self, data):
        """Handle Data Set 1 (DT1) messages"""
        if len(data) < 4:  # Need at least address and one data byte
            return

        address = data[0:3]
        value = data[3]
        logging.debug(f"Received parameter update: Address={address}, Value={value}")

        # Determine the parameter based on the address
        param = self._get_parameter_from_address(address)
        if param:
            self.parameter_changed.emit(param, value)

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
