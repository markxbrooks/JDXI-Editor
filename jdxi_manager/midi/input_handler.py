"""
MIDIInHandler Module
====================

This module provides the MIDIInHandler class for handling MIDI communication with the Roland JD-Xi.
It supports processing of SysEx, Control Change, Program Change, Note On/Off, and Clock messages.
The handler decodes incoming MIDI messages, routes them to appropriate sub-handlers, and emits Qt signals
for integration with PySide6-based applications.

Classes:
    MIDIInHandler: Processes incoming MIDI messages, handles SysEx tone data parsing, and emits signals
                   for further processing in the application.

Usage:
    Instantiate MIDIInHandler and connect to its signals to integrate MIDI data handling with your application.

Dependencies:
    - PySide6.QtCore.Signal for signal emission.
    - pubsub for publish/subscribe messaging.
    - jdxi_manager modules for data handling, parsing, and MIDI processing.
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional

from PySide6.QtCore import Signal
from pubsub import pub

from jdxi_manager.data.digital import get_digital_parameter_by_address
from jdxi_manager.data.preset_data import DIGITAL_PRESETS
from jdxi_manager.data.preset_type import PresetType
from jdxi_manager.midi.basenew import MIDIBase
from jdxi_manager.midi.jsonutils import log_json
from jdxi_manager.midi.parsers import parse_sysex
from jdxi_manager.midi.sysex import SysexParameter


class MIDIInHandler(MIDIBase):
    """
    Helper class for MIDI communication with the JD-Xi.

    This class listens to incoming MIDI messages, processes them based on
    their type, and emits corresponding signals. It handles SysEx, Control
    Change, Program Change, Note On/Off, and Clock messages.
    """

    incoming_midi_message = Signal(object)
    program_changed = Signal(int, int)  # channel, program

    def __init__(self, parent: Optional[Any] = None) -> None:
        """
        Initialize the MIDIInHandler.

        :param parent: Optional parent widget or object.
        """
        super().__init__(parent)
        self.parent = parent
        self.callbacks: List[Callable] = []
        self.channel: int = 1
        self.preset_number: int = 0
        self.cc_number: int = 0
        self.cc_msb_value: int = 0
        self.cc_lsb_value: int = 0
        pub.subscribe(self._handle_incoming_midi_message, "incoming_midi_message")

    def _handle_incoming_midi_message(self, message: Any) -> None:
        """
        Process incoming MIDI messages.

        This method routes the message to the appropriate handler based on its type.

        :param message: The incoming MIDI message.
        """
        # Do not process clock messages for logging/emission
        if message.type != "clock":
            self.incoming_midi_message.emit(message)
            logging.info("MIDI message of type %s incoming: %s", message.type, message)

        preset_data: Dict[str, Any] = {"modified": 0}
        message_handlers: Dict[str, Callable[[Any, Dict[str, Any]], None]] = {
            "sysex": self._handle_sysex_message,
            "control_change": self._handle_control_change,
            "program_change": self._handle_program_change,
            "note_on": self._handle_note_change,
            "note_off": self._handle_note_change,
            "clock": self._handle_clock,
        }
        handler = message_handlers.get(message.type)
        try:
            if handler:
                handler(message, preset_data)
            else:
                logging.info("Unhandled MIDI message type: %s", message.type)
        except Exception as exc:
            logging.error("Error handling incoming MIDI message: %s", str(exc))

    def _handle_note_change(self, message: Any, preset_data: Dict[str, Any]) -> None:
        """
        Handle Note On and Note Off MIDI messages.

        :param message: The MIDI message.
        :param preset_data: Dictionary for preset data modifications.
        """
        logging.info("MIDI message type: %s as %s", message.type, message)

    def _handle_clock(self, message: Any, preset_data: Dict[str, Any]) -> None:
        """
        Handle MIDI Clock messages quietly.

        :param message: The MIDI message.
        :param preset_data: Dictionary for preset data modifications.
        """
        # Suppress clock message output
        if message.type == "clock":
            return

    def _handle_sysex_message(self, message: Any, preset_data: Dict[str, Any]) -> None:
        """
        Handle SysEx MIDI messages from the Roland JD-Xi.

        The method processes SysEx data, attempting to parse tone data and
        extract command and parameter information.

        :param message: The MIDI SysEx message.
        :param preset_data: Dictionary for preset data modifications.
        """
        try:
            # Log raw SysEx message as hex
            hex_string = " ".join(f"{byte:02X}" for byte in message.data)
            logging.info("Received SysEx Message: %s", hex_string)
            # Reconstruct the SysEx message bytes
            sysex_message = [0xF0] + [int(byte, 16) for byte in hex_string.split()] + [0xF7]
            sysex_message_bytes = bytes(sysex_message)
            if len(message.data) > 63:
                try:
                    parsed_data = parse_sysex(sysex_message_bytes)
                    json_data = json.dumps(parsed_data)
                    # Emit JSON string for further processing
                    self.json_sysex.emit(json_data)
                    log_json(parsed_data)
                except Exception as ex:
                    logging.info("Error parsing JD-Xi tone data: %s", ex)

            try:
                command_type_address = message.data[6]
                address_offset = message.data[7:11]
                command_name = SysexParameter.get_command_name(command_type_address)
                logging.info("Command: %s (%#02X)", command_name, command_type_address)
                logging.info("Parameter Offset: %s", "".join(f"{byte:02X}" for byte in address_offset))
            except Exception as ex:
                logging.error("Error parsing JD-Xi tone data: %s", ex, exc_info=True)
        except Exception as exc:
            logging.error("Error handling SysEx message: %s", exc, exc_info=True)

    def _handle_control_change(self, message: Any, preset_data: Dict[str, Any]) -> None:
        """
        Handle Control Change (CC) MIDI messages.

        :param message: The MIDI Control Change message.
        :param preset_data: Dictionary for preset data modifications.
        """
        channel = message.channel + 1
        control = message.control
        value = message.value
        logging.info("Control Change - Channel: %d, Control: %d, Value: %d", channel, control, value)
        if control == 0:
            self.cc_msb_value = value
        elif control == 32:
            self.cc_lsb_value = value

    def _handle_program_change(self, message: Any, preset_data: Dict[str, Any]) -> None:
        """
        Handle Program Change (PC) MIDI messages.

        Processes program changes and maps them to preset changes based on
        CC values.

        :param message: The MIDI Program Change message.
        :param preset_data: Dictionary for preset data modifications.
        """
        channel = message.channel + 1
        program_number = message.program
        logging.info("Program Change - Channel: %d, Program: %d", channel, program_number)

        self.program_changed.emit(channel, program_number)

        preset_mapping: Dict[int, PresetType] = {
            95: PresetType.DIGITAL_1,
            94: PresetType.ANALOG,
            86: PresetType.DRUMS,
        }

        if self.cc_msb_value in preset_mapping:
            preset_data["type"] = preset_mapping[self.cc_msb_value]
            # Adjust preset number based on LSB value
            self.preset_number = program_number + (128 if self.cc_lsb_value == 65 else 0)
            preset_name = DIGITAL_PRESETS[self.preset_number] if self.preset_number < len(DIGITAL_PRESETS) else "Unknown Preset"
            pub.sendMessage(
                "update_display_preset",
                preset_number=self.preset_number,
                preset_name=preset_name,
                channel=channel,
            )
            logging.info("Preset changed to: %d", self.preset_number)

    @staticmethod
    def _extract_patch_name(patch_name_bytes: List[int]) -> str:
        """
        Extract an ASCII patch name from SysEx message bytes.

        Only bytes corresponding to printable ASCII characters are used.

        :param patch_name_bytes: List of byte values representing the patch name.
        :return: The extracted and cleaned patch name string.
        """
        return "".join(chr(b) for b in patch_name_bytes if 32 <= b <= 127).strip()

    def register_callback(self, callback: Callable) -> None:
        """
        Register a callback function for MIDI messages.

        :param callback: A callable that handles MIDI messages.
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def midi_callback(self, message: Any, timestamp: Optional[float] = None) -> None:
        """
        Handle incoming MIDI messages and route them to appropriate handlers.

        This method provides an alternative entry point for processing messages.

        :param message: The MIDI message.
        :param timestamp: Optional timestamp for the message.
        """
        try:
            if message.type == "program_change":
                logging.info("Program Change - Channel: %d, Program: %d", message.channel, message.program)
            if message.type != "clock":
                self.incoming_midi_message.emit(message)
                logging.info("MIDI message of type %s incoming: %s", message.type, message)
            preset_data: Dict[str, Any] = {"modified": 0}
            message_handlers: Dict[str, Callable[[Any, Dict[str, Any]], None]] = {
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
                logging.info("Unhandled MIDI message type: %s", message.type)
        except Exception as exc:
            logging.error("Error handling incoming MIDI message: %s", str(exc))

    def _handle_dt1_message(self, data: List[int]) -> None:
        """
        Handle Data Set 1 (DT1) messages.

        Extracts the address and value, then emits a parameter change signal.

        :param data: List of integers representing the DT1 message data.
        """
        if len(data) < 4:
            return

        address = data[0:3]
        value = data[3]
        logging.debug("Received parameter update: Address=%s, Value=%d", address, value)

        param = self._get_parameter_from_address(address)
        if param:
            self.parameter_changed.emit(param, value)

    def _get_parameter_from_address(self, address: List[int]) -> Any:
        """
        Map an address to a DigitalParameter.

        :param address: List of integers representing the address.
        :return: The corresponding DigitalParameter.
        :raises ValueError: If the address is invalid or not found.
        """
        if len(address) < 2:
            raise ValueError(f"Address must contain at least 2 elements, got {len(address)}")

        # Assuming address structure [group, address, ...]
        parameter_address = tuple(address[1:2])
        param = get_digital_parameter_by_address(parameter_address)

        if param:
            return param
        else:
            raise ValueError(f"Invalid address {parameter_address} - no corresponding DigitalParameter found.")

    def handle_sysex_message(self, message: List[int]) -> None:
        """
        Handle an incoming SysEx message.

        This method checks if the message is long enough and then processes
        Data Set 1 messages.

        :param message: List of integers representing the SysEx message.
        """
        try:
            if len(message) < 8:
                return

            # Check if this is a DT1 command (0x12)
            if message[7] == 0x12:
                self._handle_dt1_message(message[8:])
        except Exception as exc:
            logging.error("Error handling SysEx message: %s", str(exc))

    def set_callback(self, callback: Callable) -> None:
        """
        Set a callback for MIDI messages.

        :param callback: The callback function to be set.
        """
        self.midi_in.set_callback(callback)
