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
from pathlib import Path

import mido
from typing import Any, Callable, List, Optional
from PySide6.QtCore import Signal

from jdxi_editor.log.message import log_parameter
from jdxi_editor.midi.io.controller import MidiIOController
from jdxi_editor.midi.io.utils import extract_command_info, handle_identity_request
from jdxi_editor.midi.preset.type import JDXISynth
from jdxi_editor.midi.utils.json import log_to_json
from jdxi_editor.midi.sysex.parsers import parse_sysex
from jdxi_editor.midi.sysex.utils import get_parameter_from_address
from jdxi_editor.midi.preset.data import ButtonPreset


class MidiInHandler(MidiIOController):
    """
    Helper class for MIDI communication with the JD-Xi.

    This class listens to incoming MIDI messages, processes them based on
    their preset_type, and emits corresponding signals. It handles SysEx, Control
    Change, Program Change, Note On/Off, and Clock messages.
    """

    update_tone_name = Signal(str, str)
    update_program_name = Signal(str)
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

    def reopen_input_port_name(self, in_port) -> bool:
        """Reopen the current MIDI input port and reattach the callback."""
        try:
            if self.input_port_number is None:
                logging.warning("No MIDI input port to reopen.")
                return False

            # Close current input port if it's open
            if self.midi_in.is_port_open():
                self.midi_in.close_port()

            # Reopen input port
            self.open_input_port(in_port)

            # Reset callback
            if hasattr(self, "midi_callback"):
                self.midi_in.set_callback(self.midi_callback)
                logging.info(f"Callback reattached to MIDI input port {in_port}")
            else:
                logging.warning("No handle_midi_input() method found for callback.")
            return True

        except Exception as ex:
            logging.error(f"Failed to reopen MIDI input port: {ex}")
            return False

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
            preset_data = ButtonPreset()
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
            self.midi_message_incoming.emit(message)
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
            self._emit_program_name_signal(area, tone_name)
            self._emit_tone_name_signal(area, tone_name)

    def _emit_program_name_signal(self, area: str, tone_name: str) -> None:
        """Emits the appropriate Qt signal for a given tone name."""
        if area == "TEMPORARY_PROGRAM_AREA":
            logging.info(f"Emitting tone name: {tone_name} to {area}")
            self.update_program_name.emit(tone_name)

    def _emit_tone_name_signal(self, area: str, tone_name: str) -> None:
        """Emits the appropriate Qt signal for a given tone name."""
        synth_type_map = {
            "TEMPORARY_PROGRAM_AREA": JDXISynth.PROGRAM,
            "TEMPORARY_DIGITAL_SYNTH_1_AREA": JDXISynth.DIGITAL_1,
            "TEMPORARY_DIGITAL_SYNTH_2_AREA": JDXISynth.DIGITAL_2,
            "TEMPORARY_ANALOG_SYNTH_AREA": JDXISynth.ANALOG,
            "TEMPORARY_DRUM_KIT_AREA": JDXISynth.DRUMS,
        }

        synth_type = synth_type_map.get(area)
        if synth_type:
            logging.info(f"Emitting tone name: {tone_name} to {area} (synth type: {synth_type})")
            self.update_tone_name.emit(tone_name, synth_type)
        else:
            logging.warning(f"Unknown area: {area}. Cannot emit tone name.")

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
                    print(f"Parsed data: {parsed_data_dict}")
                    self._emit_program_or_tone_name(parsed_data_dict)
                    json_log_folder = Path.home() / ".jdxi_editor" / "logs"
                    json_log_folder.mkdir(parents=True, exist_ok=True)
                    json_log_file = json_log_folder / f"jdxi_tone_data_{parsed_data_dict['ADDRESS']}.json"
                    with open(json_log_file, "w", encoding="utf-8") as f:
                        json.dump(parsed_data_dict, f, ensure_ascii=False, indent=2)
                    # Emit the parsed data as a JSON string
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
