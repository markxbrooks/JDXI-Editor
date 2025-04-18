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
from typing import Any, Callable, List, Optional, Union
from PySide6.QtCore import Signal

from jdxi_editor.log.message import log_parameter
from jdxi_editor.midi.data.address.address import ModelID, RolandID
from jdxi_editor.midi.io.controller import MidiIOController
from jdxi_editor.midi.sysex.device import DeviceInfo
from jdxi_editor.midi.message.sysex import SysexParameter
from jdxi_editor.midi.utils.json import log_to_json
from jdxi_editor.midi.sysex.parsers import parse_sysex
from jdxi_editor.midi.sysex.utils import get_parameter_from_address
from jdxi_editor.midi.preset.data import Preset


def nibble_data(data):
    """Sanitize the data by splitting bytes greater than 127 into 4-bit nibbles."""
    sanitized_data = []
    for byte in data:
        if byte > 127:
            high_nibble = (byte >> 4) & 0x0F
            low_nibble = byte & 0x0F
            # Combine nibbles into valid data bytes (0-127)
            sanitized_data.append(high_nibble)
            sanitized_data.append(low_nibble)
        else:
            sanitized_data.append(byte)
    return sanitized_data


def extract_command_info(message: Any) -> None:
    """Extracts and logs command type and address offset."""
    try:
        command_type = message.data[6]
        address_offset = "".join(f"{byte:02X}" for byte in message.data[7:11])
        command_name = SysexParameter.get_command_name(command_type)

        logging.debug(
            "Command: %s (0x%02X), Address Offset: %s",
            command_name,
            command_type,
            address_offset,
        )
    except Exception as ex:
        logging.warning(f"Unable to extract command or parameter address due to {ex}")


def rtmidi_to_mido(rtmidi_message):
    """Convert an rtmidi message to address mido message."""
    try:
        return mido.Message.from_bytes(rtmidi_message)
    except ValueError as err:
        logging.error("Failed to convert rtmidi message: %s", err)
        return None


def convert_to_mido_message(message_content: List[int]) -> Optional[Union[mido.Message, List[mido.Message]]]:
    """Convert raw MIDI message content to a mido.Message object or a list of them."""
    if not message_content:
        return None

    status_byte = message_content[0]

    try:
        # SysEx
        if status_byte == 0xF0 and message_content[-1] == 0xF7:
            sys_ex_data = nibble_data(message_content[1:-1])
            if len(sys_ex_data) > 128:
                nibbles = [sys_ex_data[i:i + 4] for i in range(0, len(sys_ex_data), 4)]
                return [mido.Message("sysex", data=nibble) for nibble in nibbles]
            return mido.Message("sysex", data=sys_ex_data)
    except Exception as ex:
        logging.info(f"Error {ex} occurred")
    try:
        # Program Change
        if 0xC0 <= status_byte <= 0xCF and len(message_content) >= 2:
            channel = status_byte & 0x0F
            program = message_content[1]
            return mido.Message("program_change", channel=channel, program=program)
    except Exception as ex:
        logging.info(f"Error {ex} occurred")

    try:
        # Control Change
        if 0xB0 <= status_byte <= 0xBF and len(message_content) >= 3:
            channel = status_byte & 0x0F
            control = message_content[1]
            value = message_content[2]
            return mido.Message("control_change", channel=channel, control=control, value=value)
    except Exception as ex:
        logging.info(f"Error {ex} occurred")

    # Other (not yet implemented)
    logging.info(f"Unhandled MIDI message: {message_content}")
    return None


def mido_message_data_to_byte_list(message):
    """mido message data to byte list"""
    hex_string = " ".join(f"{byte:02X}" for byte in message.data)
    logging.debug("converting (%d bytes)", len(message.data))

    # Reconstruct SysEx message bytes
    message_byte_list = bytes(
        [0xF0] + [int(byte, 16) for byte in hex_string.split()] + [0xF7]
    )
    return message_byte_list


def handle_identity_request(message):
    """Handles an incoming Identity Request and sends an Identity Reply."""
    byte_list = mido_message_data_to_byte_list(message)
    device_info = DeviceInfo.from_identity_reply(byte_list)
    if device_info:
        logging.info(device_info.to_string)
    device_id = device_info.device_id
    manufacturer_id = device_info.manufacturer
    version = message.data[9:12]  # Extract firmware version bytes

    version_str = ".".join(str(byte) for byte in version)
    if device_id == ModelID.DEVICE_ID:
        device_name = "JD-XI"
    else:
        device_name = "Unknown"
    if manufacturer_id == RolandID.ROLAND_ID:
        manufacturer_name = "Roland"
    else:
        manufacturer_name = "Unknown"
    logging.info(f"🏭 Manufacturer ID: \t{manufacturer_id}  \t{manufacturer_name}")
    logging.info(f"🎹 Device ID: \t\t\t{hex(device_id)} \t{device_name}")
    logging.info(f"🔄 Firmware Version: \t{version_str}")
    return {
        "device_id": device_id,
        "manufacturer_id": manufacturer_id,
        "firmware_version": version_str,
    }


def listen_midi(port_name, callback):
    """
    Function to listen for MIDI messages and call address callback.
    """
    with mido.open_input(port_name) as inport:
        logging.info(f"Listening on port: {port_name}")
        for msg in inport:
            callback(msg)  # Call the provided callback function


class MidiInHandler(MidiIOController):
    """
    Helper class for MIDI communication with the JD-Xi.

    This class listens to incoming MIDI messages, processes them based on
    their preset_type, and emits corresponding signals. It handles SysEx, Control
    Change, Program Change, Note On/Off, and Clock messages.
    """

    update_program_name = Signal(str)
    update_digital1_tone_name = Signal(str)
    update_digital2_tone_name = Signal(str)
    update_analog_tone_name = Signal(str)
    update_drums_tone_name = Signal(str)
    midi_message_incoming = Signal(object)
    midi_program_changed = Signal(int, int)  # channel, program
    midi_parameter_changed = Signal(object, int)  # Emit parameter and value
    midi_parameter_received = Signal(list, int)  # address, value
    midi_control_changed = Signal(int, int, int)  # channel, control, value
    midi_sysex_json = Signal(str)  # Signal emitting SysEx data as address JSON string

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
        self.midi_in.set_callback(self.midi_callback)
        self.midi_in.ignore_types(sysex=False, timing=True, active_sense=True)

    def midi_callback(self, message, data):
        """callback for rtmidi
        mido doesn't have callbacks, so we convert
        """
        try:
            message_content, data = message
            log_parameter("message_content", message_content)
            log_parameter("data", data)
            p = mido.Parser()
            p.feed(message_content)
            for message in p:
                self._handle_midi_message(message)
        except Exception as ex:
            logging.info(ex)

    def register_callback(self, callback: Callable) -> None:
        """
        Register address callback function for MIDI messages.

        :param callback: A callable that handles MIDI messages.
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def set_callback(self, callback: Callable) -> None:
        """
        Set address callback for MIDI messages.

        :param callback: The callback function to be set.
        """
        try:
            self.midi_in.set_callback(callback)
        except Exception as ex:
            logging.info(
                f"Error {ex} occurred calling self.midi_in.set_callback(callback)"
            )

    def _handle_midi_message(self, message: Any) -> None:
        """Routes MIDI messages to appropriate handlers."""
        try:
            preset_data = Preset()
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
                logging.info("Unhandled MIDI message type: %s", message.type)
        except Exception as ex:
            logging.info(f"Error {ex} occurred")

    def _handle_note_change(self, message: Any, preset_data) -> None:
        """
        Handle Note On and Note Off MIDI messages.

        :param message: The MIDI message.
        :param preset_data: Dictionary for preset data modifications.
        """
        logging.info("MIDI message note change: %s as %s", message.type, message)

    def _handle_clock(self, message: Any, preset_data) -> None:
        """
        Handle MIDI Clock messages quietly.

        :param message: The MIDI message.
        :param preset_data: Dictionary for preset data modifications.
        """
        # Suppress clock message output
        if message.type == "clock":
            return

    def _emit_program_or_tone_name(self, parsed_data):
        """Emits the appropriate Qt signal for the extracted tone name."""
        valid_addresses = {
            "12180000",
            "12190100",
            "12192100",
            "12194200",
            "12197000",  # Drums Common
        }

        address = parsed_data.get("ADDRESS")
        tone_name = parsed_data.get("TONE_NAME")
        area = parsed_data.get("TEMPORARY_AREA")
        logging.info(
            f"ADDRESS: {address} TEMPORARY_AREA: {area} TONE_NAME: {tone_name}"
        )

        if address in valid_addresses and tone_name:
            self._emit_signal(area, tone_name)

    def _emit_signal(self, area: str, tone_name: str) -> None:
        """Emits the appropriate Qt signal for a given tone name."""
        emit_map = {
            "TEMPORARY_PROGRAM_AREA": self.update_program_name,
            "TEMPORARY_DIGITAL_SYNTH_1_AREA": self.update_digital1_tone_name,
            "TEMPORARY_DIGITAL_SYNTH_2_AREA": self.update_digital2_tone_name,
            "TEMPORARY_ANALOG_SYNTH_AREA": self.update_analog_tone_name,
            "TEMPORARY_DRUM_KIT_AREA": self.update_drums_tone_name,
        }
        if emitter := emit_map.get(area):
            logging.info(f"Emitting tone name: {tone_name} to {area}")
            emitter.emit(tone_name)

    def _handle_sysex_message(self, message: Any, preset_data) -> None:
        """
        Handle SysEx MIDI messages from the Roland JD-Xi.

        Processes SysEx data, attempts to parse tone data, and extracts command
        and parameter information for further processing.

        :param message: The MIDI SysEx message.
        :param preset_data: Dictionary for preset data modifications.
        """
        logging.debug(f"handling incoming midi message: {message}")
        try:
            if (
                message.type == "sysex"
                and len(message.data) > 6
                and message.data[3] == 0x02
            ):  # Identity request
                handle_identity_request(message)
            # Convert raw SysEx data to address hex string
            hex_string = " ".join(f"{byte:02X}" for byte in message.data)
            logging.debug("SysEx message received (%d bytes)", len(message.data))

            # Reconstruct SysEx message bytes
            sysex_message_bytes = bytes(
                [0xF0] + [int(byte, 16) for byte in hex_string.split()] + [0xF7]
            )

            # If the message contains tone data, attempt to parse it
            if len(message.data) > 20:
                try:
                    parsed_data_dict = parse_sysex(sysex_message_bytes)
                    self._emit_program_or_tone_name(parsed_data_dict)
                    self.midi_sysex_json.emit(json.dumps(parsed_data_dict))
                    log_to_json(parsed_data_dict)
                except Exception as parse_ex:
                    logging.info("Failed to parse JD-Xi tone data: %s", parse_ex)
            extract_command_info(message)

        except Exception as ex:
            logging.info(f"Unexpected error {ex} while handling SysEx message")

    def _handle_control_change(self, message: Any, preset_data) -> None:  # @@
        """
        Handle Control Change (CC) MIDI messages.

        :param message: The MIDI Control Change message.
        :param preset_data: Dictionary for preset data modifications.
        """
        channel = message.channel + 1
        control = message.control
        value = message.value
        logging.info(
            "Control Change - Channel: %d, Control: %d, Value: %d",
            channel,
            control,
            value,
        )
        self.midi_control_changed.emit(channel, control, value)
        if control == 99:  # NRPN MSB
            self.nrpn_msb = value
        elif control == 98:  # NRPN LSB
            self.nrpn_lsb = value
        elif control == 6 and self.nrpn_msb is not None and self.nrpn_lsb is not None:
            # We have both MSB and LSB; reconstruct NRPN address
            nrpn_address = (self.nrpn_msb << 7) | self.nrpn_lsb
            # self._handle_nrpn_message(nrpn_address, value, channel)

            # Reset NRPN state
            self.nrpn_msb = None
            self.nrpn_lsb = None
        if control == 0:
            self.cc_msb_value = value
        elif control == 32:
            self.cc_lsb_value = value

    def _handle_program_change(self, message: Any, preset_data) -> None:
        """
        Handle Program Change (PC) MIDI messages.

        Processes program changes and maps them to preset changes based on
        CC values.

        :param message: The MIDI Program Change message.
        :param preset_data: Dictionary for preset data modifications.
        """
        channel = message.channel + 1
        program_number = message.program
        logging.info(
            "Program Change - Channel: %d, Program: %d", channel, program_number
        )

        self.midi_program_changed.emit(channel, program_number)

    def _handle_dt1_message(self, data: List[int]) -> None:
        """
        Handle Data Set 1 (DT1) messages.

        Extracts the address and value from the data and emits address parameter change signal.

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
