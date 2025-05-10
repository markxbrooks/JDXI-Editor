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
from typing import Any, Callable, List, Optional
from PySide6.QtCore import Signal

from jdxi_editor.jdxi.sysex.offset import JDXISysExOffset, JDXIIdentityOffset
from jdxi_editor.log.error import log_error
from jdxi_editor.log.message import log_message
from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.midi.data.address.sysex import SUB_ID_2_IDENTITY_REPLY, START_OF_SYSEX, \
    END_OF_SYSEX
from jdxi_editor.midi.io.controller import MidiIOController
from jdxi_editor.midi.io.utils import handle_identity_request
from jdxi_editor.log.json import log_json
from jdxi_editor.midi.sysex.parse_utils import SYNTH_TYPE_MAP
from jdxi_editor.midi.sysex.parsers.sysex import JDXiSysExParser
from jdxi_editor.midi.sysex.utils import get_parameter_from_address
from jdxi_editor.jdxi.preset.button import JDXIPresetButton

from jdxi_editor.midi.data.address.address import AddressMemoryAreaMSB as AreaMSB


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
    midi_control_changed = Signal(int, int, int)  # channel, control, value
    midi_sysex_json = Signal(str)  # Signal emitting SysEx data as address JSON string

    def __init__(self, parent: Optional[Any] = None) -> None:
        """
        Initialize the MIDIInHandler.

        :param parent: Optional[Any] parent widget or object.
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
        self.sysex_parser = JDXiSysExParser()

    def midi_callback(self, message: list[Any], data: Any) -> None:
        """callback for rtmidi
        mido doesn't have callbacks, so we convert
        :param message: list[Any]
        :param data: Any
        """
        try:
            message_content, data = message
            p = mido.Parser()
            p.feed(message_content)
            for message in p:
                self._handle_midi_message(message)
        except Exception as ex:
            log_error(f"Error {ex} occurred")

    def reopen_input_port_name(self, in_port: str) -> bool:
        """Reopen the current MIDI input port and reattach the callback.
        :param in_port: str
        :return: bool
        """
        try:
            if self.input_port_number is None:
                log_message("No MIDI input port to reopen", level=logging.WARNING)
                return False

            # Close current input port if it's open
            if self.midi_in.is_port_open():
                self.midi_in.close_port()

            # Reopen input port
            self.open_input_port(in_port)

            # Reset callback
            if hasattr(self, "midi_callback"):
                self.midi_in.set_callback(self.midi_callback)
                log_message(f"Callback reattached to MIDI input port {in_port}")
            else:
                log_message(
                    "No handle_midi_input() method found for callback.",
                    level=logging.WARNING,
                )
            return True

        except Exception as ex:
            log_error(f"Failed to reopen MIDI input port: {ex}")
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
            log_message(
                f"Error {ex} occurred calling self.midi_in.set_callback(callback)"
            )

    def _handle_midi_message(self, message: Any) -> None:
        """Routes MIDI messages to appropriate handlers."""
        try:
            preset_data = JDXIPresetButton()
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
                log_message(f"Unhandled MIDI message type: {message.type}")
            self.midi_message_incoming.emit(message)
        except Exception as ex:
            log_error(f"Error {ex} occurred")

    def _handle_note_change(self, message: Any, preset_data: dict) -> None:
        """
        Handle Note On and Note Off MIDI messages.

        :param message: The MIDI message.
        :param preset_data: Dictionary for preset data modifications.
        """
        log_message(f"MIDI message note change: {message.type} as {message}")

    def _handle_clock(self, message: Any, preset_data: dict) -> None:
        """
        Handle MIDI Clock messages quietly.

        :param message: The MIDI message.
        :param preset_data: Dictionary for preset data modifications.
        """
        # Suppress clock message output
        if message.type == "clock":
            return

    def _emit_program_or_tone_name(self, parsed_data: dict) -> None:
        """Emits the appropriate Qt signal for the extracted tone name.
        :param parsed_data: dict
        """
        valid_addresses = {
            "12180000",
            "12190100",
            "12192100",
            "12194200",
            "12197000",  # Drums Common
        }

        address = parsed_data.get("ADDRESS")
        tone_name = parsed_data.get("TONE_NAME")
        temporary_area = parsed_data.get("TEMPORARY_AREA")
        log_parameter("ADDRESS", address, silent=True)
        log_parameter("TEMPORARY_AREA", temporary_area, silent=True)
        log_parameter("TONE_NAME", tone_name, silent=True)
        log_parameter("SYNTH_TONE", parsed_data.get("SYNTH_TONE"), silent=True)

        if address in valid_addresses and tone_name:
            if address == "12180000":
                self._emit_program_name_signal(temporary_area, tone_name)
            else:
                self._emit_tone_name_signal(temporary_area, tone_name)

    def _emit_program_name_signal(self, area: str, tone_name: str) -> None:
        """Emits the appropriate Qt signal for a given tone name."""
        if area == AreaMSB.TEMPORARY_PROGRAM.name:
            log_message(f"Emitting tone name: {tone_name} to {area}")
            self.update_program_name.emit(tone_name)

    def _emit_tone_name_signal(self, area: str, tone_name: str) -> None:
        """Emits the appropriate Qt signal for a given tone name."""
        synth_type = SYNTH_TYPE_MAP.get(area)
        if synth_type:
            log_message(
                f"Emitting tone name: {tone_name} to {area} (synth type: {synth_type})"
            )
            self.update_tone_name.emit(tone_name, synth_type)
        else:
            logging.warning(f"Unknown area: {area}. Cannot emit tone name.")

    def _handle_sysex_message(self, message: Any, preset_data: dict) -> None:
        """
        Handle SysEx MIDI messages from the Roland JD-Xi.

        Processes SysEx data, attempts to parse tone data, and extracts command
        and parameter information for further processing.

        :param message: The MIDI SysEx message.
        :param preset_data: Dictionary for preset data modifications.
        """
        try:
            if not (message.type == "sysex" and len(message.data) > 6):
                return
            mido_sub_id_byte_offset = JDXIIdentityOffset.SUB_ID_2 - 1 # account for lack of status byte
            if message.data[mido_sub_id_byte_offset] == SUB_ID_2_IDENTITY_REPLY:
                handle_identity_request(message)
                return

            hex_string = " ".join(f"{byte:02X}" for byte in message.data)
            log_parameter(f"SysEx message of length {len(message.data)} received:", hex_string)

            sysex_message_bytes = bytes([START_OF_SYSEX]) + bytes(message.data) + bytes([END_OF_SYSEX])
            try:
                parsed_data = self.sysex_parser.parse_bytes(sysex_message_bytes)
                log_parameter("Parsed data", parsed_data, silent=True)
                self._emit_program_or_tone_name(parsed_data)
                self.midi_sysex_json.emit(json.dumps(parsed_data))
                log_json(parsed_data, silent=True)
            except Exception as parse_ex:
                log_error(f"Failed to parse JD-Xi tone data: {parse_ex}")

        except Exception as ex:
            log_error(f"Unexpected error {ex} while handling SysEx message")

    def _handle_control_change(self, message: Any, preset_data: dict) -> None:  # @@
        """
        Handle Control Change (CC) MIDI messages.

        :param message: The MIDI Control Change message.
        :param preset_data: Dictionary for preset data modifications.
        """
        channel = message.channel + 1
        control = message.control
        value = message.value
        log_message(
            f"Control Change - Channel: {channel}, Control: {control}, Value: {value}"
        )
        self.midi_control_changed.emit(channel, control, value)
        if control == 99:  # NRPN MSB
            self.nrpn_msb = value
        elif control == 98:  # NRPN LSB
            self.nrpn_lsb = value
        elif control == 6 and self.nrpn_msb is not None and self.nrpn_lsb is not None:
            # We have both MSB and LSB; reconstruct NRPN address
            (self.nrpn_msb << 7) | self.nrpn_lsb
            # self._handle_nrpn_message(nrpn_address, value, channel)

            # Reset NRPN state
            self.nrpn_msb = None
            self.nrpn_lsb = None
        if control == 0:
            self.cc_msb_value = value
        elif control == 32:
            self.cc_lsb_value = value

    def _handle_program_change(self, message: Any, preset_data: dict) -> None:
        """
        Handle Program Change (PC) MIDI messages.

        Processes program changes and maps them to preset changes based on
        CC values.

        :param message: The MIDI Program Change message.
        :param preset_data: Dictionary for preset data modifications.
        """
        channel = message.channel + 1
        program_number = message.program
        log_message(f"Program Change - Channel: {channel}, Program: {program_number}")

        self.midi_program_changed.emit(channel, program_number)
