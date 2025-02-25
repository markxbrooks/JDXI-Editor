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
import mido
from typing import Any, Callable, Dict, List, Optional, Tuple
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, PROGRAM_CHANGE, CONTROL_CHANGE, SYSTEM_EXCLUSIVE, TIMING_CLOCK
from PySide6.QtCore import Signal
from pubsub import pub

from jdxi_manager.data.digital import get_digital_parameter_by_address
from jdxi_manager.data.presets.data import DIGITAL_PRESETS_ENUMERATED
from jdxi_manager.data.presets.type import PresetType
from jdxi_manager.midi.io.controller import MidiIOController
from jdxi_manager.midi.utils.json import log_json
from jdxi_manager.midi.utils.parsers import parse_sysex
from jdxi_manager.midi.sysex.sysex import SysexParameter
from jdxi_manager.midi.sysex.utils import get_parameter_from_address


class MIDIInHandler(MidiIOController):
    """
    Helper class for MIDI communication with the JD-Xi.

    This class listens to incoming MIDI messages, processes them based on
    their type, and emits corresponding signals. It handles SysEx, Control
    Change, Program Change, Note On/Off, and Clock messages.
    """

    midi_incoming_message = Signal(object)
    midi_program_changed = Signal(int, int)  # channel, program
    midi_parameter_changed = Signal(object, int)  # Emit parameter and value
    midi_parameter_received = Signal(list, int)  # address, value
    midi_sysex_json = Signal(str)  # Signal emitting SysEx data as a JSON string

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
        self.cc_msb_value: int = 0
        self.cc_lsb_value: int = 0
        self.register_callback(self.midi_callback)
        pub.subscribe(self.handle_incoming_midi_message, "midi_incoming_message")

    def rtmidi_to_mido(self, rtmidi_message):
        """Convert an rtmidi message to a mido message."""
        return mido.Message.from_bytes(rtmidi_message)

    def register_callback(self, callback: Callable) -> None:
        """
        Register a callback function for MIDI messages.

        :param callback: A callable that handles MIDI messages.
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def midi_callback(self, event: Any, timestamp: Optional[float] = None) -> None:
        """
        Handle incoming MIDI messages and route them to appropriate handlers.

        This method provides an alternative entry point for processing messages.

        :param message: The MIDI message.
        :param timestamp: Optional timestamp for the message.
        """
        try:
            logging.info(f"message type: {type(event)}")
            if type(event) == tuple:
                message_data , _ = event
                message = self.rtmidi_to_mido(message_data)
                if message.type == "program_change":
                    logging.info("Program Change - Channel: %d, Program: %d", message.channel, message.program)
                if message.type != "clock":
                    self.midi_incoming_message.emit(message)
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

    def set_callback(self, callback: Callable) -> None:
        """
        Set a callback for MIDI messages.

        :param callback: The callback function to be set.
        """
        self.midi_in.set_callback(callback)

    def handle_incoming_midi_message(self, message: Any) -> None:
        """
        Process incoming MIDI messages.

        This method routes the message to the appropriate handler based on its type.

        :param message: The incoming MIDI message.
        """
        # Do not process clock messages for logging/emission
        if message.type != "clock":
            self.midi_incoming_message.emit(message)
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

        Processes SysEx data, attempts to parse tone data, and extracts command
        and parameter information for further processing.

        :param message: The MIDI SysEx message.
        :param preset_data: Dictionary for preset data modifications.
        """
        try:
            # Convert raw SysEx data to a hex string
            hex_string = " ".join(f"{byte:02X}" for byte in message.data)
            logging.debug("SysEx message received (%d bytes)", len(message.data))

            # Reconstruct SysEx message bytes
            sysex_message_bytes = bytes([0xF0] + [int(byte, 16) for byte in hex_string.split()] + [0xF7])

            # If the message contains tone data, attempt to parse it
            if len(message.data) > 63:
                try:
                    parsed_data = parse_sysex(sysex_message_bytes)
                    self.midi_sysex_json.emit(json.dumps(parsed_data))
                    log_json(parsed_data)
                except Exception as parse_ex:
                    logging.warning("Failed to parse JD-Xi tone data: %s", parse_ex)

            # Extract command type and parameter address
            try:
                command_type = message.data[6]
                address_offset = "".join(f"{byte:02X}" for byte in message.data[7:11])
                command_name = SysexParameter.get_command_name(command_type)
                logging.debug("Command: %s (0x%02X), Address Offset: %s", command_name, command_type, address_offset)
            except Exception:
                logging.warning("Unable to extract command or parameter address", exc_info=True)

        except Exception:
            logging.error("Unexpected error while handling SysEx message", exc_info=True)

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

        self.midi_program_changed.emit(channel, program_number)

        preset_mapping: Dict[int, PresetType] = {
            95: PresetType.DIGITAL_1,
            94: PresetType.ANALOG,
            86: PresetType.DRUMS,
        }

        if self.cc_msb_value in preset_mapping:
            preset_data["type"] = preset_mapping[self.cc_msb_value]
            # Adjust preset number based on LSB value
            self.preset_number = program_number + (128 if self.cc_lsb_value == 65 else 0)
            preset_name = DIGITAL_PRESETS_ENUMERATED[self.preset_number] if self.preset_number < len(DIGITAL_PRESETS_ENUMERATED) else "Unknown Preset"
            pub.sendMessage(
                "update_display_preset",
                preset_number=self.preset_number,
                preset_name=preset_name,
                channel=channel,
            )
            logging.info("Preset changed to: %d", self.preset_number)

    def _handle_dt1_message(self, data: List[int]) -> None:
        """
        Handle Data Set 1 (DT1) messages.

        Extracts the address and value from the data and emits a parameter change signal.

        :param data: List of integers representing the DT1 message data.
        """
        if len(data) < 4:
            return

        # Extract address (first three bytes) and value (fourth byte)
        address = data[:3]
        value = data[3]
        logging.debug("Parameter update received: Address=%s, Value=%d", address, value)

        # Retrieve the parameter using the address and emit the change signal if found
        param = get_parameter_from_address(address)
        if param:
            self.midi_parameter_changed.emit(param, value)
