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
from dataclasses import asdict

import mido
from typing import Any, Callable, List, Optional, Dict
from PySide6.QtCore import Signal

from jdxi_editor.jdxi.midi.constant import JDXiConstant, MidiConstant
from jdxi_editor.jdxi.preset.data import JDXiPresetData
from jdxi_editor.jdxi.preset.incoming_data import IncomingPresetData
from jdxi_editor.jdxi.program.program import JDXiProgram
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.jdxi.sysex.offset import JDXIIdentityOffset
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.programs import JDXiProgramList
from jdxi_editor.midi.io.controller import MidiIOController
from jdxi_editor.midi.io.utils import handle_identity_request
from jdxi_editor.midi.map.synth_type import JDXiMapSynthType
from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser
from jdxi_editor.midi.sysex.request.data import IGNORED_KEYS
from jdxi_editor.jdxi.preset.button import JDXiPresetButtonData

from jdxi_editor.midi.data.address.address import AddressStartMSB as AreaMSB
# from jdxi_editor.ui.editors.helpers.program import add_program_and_save


def add_program_and_save(new_program: JDXiProgram) -> bool:
    """
    add_program_and_save

    :param new_program:
    :return:
    """
    try:
        program_list = load_programs()
        log.parameter("program_list", program_list)
        existing_ids = {p["id"] for p in program_list}
        existing_pcs = {p["pc"] for p in program_list}

        if new_program.id in existing_ids or new_program.pc in existing_pcs:
            print(f"Program '{new_program.id}' already exists.")
            return False

        log.message(f"Adding new program {new_program}: {new_program.id} with PC {new_program.pc}")

        program_list.append(new_program.to_dict())

        log.message(f"Program list after addition: {program_list}")

        save_programs(program_list)
        log.message(f"Added and saved program: {new_program.id} with PC {new_program.pc}")
        return True
    except Exception as e:
        log.error(f"Failed to add and save program: {e}")
        return False


def load_programs() -> List[Dict[str, str]]:
    try:
        with open(JDXiProgramList.PROGRAMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_programs(program_list: List[Dict[str, str]]) -> None:
    """
    save_programs

    :param program_list: List[Dict[str, str]]
    :return: None
    """
    with open(JDXiProgramList.PROGRAMS_FILE, "w", encoding="utf-8") as f:
        json.dump(program_list, f, indent=4, ensure_ascii=False)


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
        self._incoming_preset_data = IncomingPresetData()

    def midi_callback(self, message: list[Any], data: Any) -> None:
        """
        callback for rtmidi
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
            log.error(f"Error {ex} occurred")

    def reopen_input_port_name(self, in_port: str) -> bool:
        """
        Reopen the current MIDI input port and reattach the callback.

        :param in_port: str
        :return: bool
        """
        try:
            if self.input_port_number is None:
                log.warning("No MIDI input port to reopen")
                return False

            # Close current input port if it's open
            if self.midi_in.is_port_open():
                self.midi_in.close_port()

            # Reopen input port
            self.open_input_port(in_port)

            # Reset callback
            if hasattr(self, "midi_callback"):
                self.midi_in.set_callback(self.midi_callback)
                log.message(f"Callback reattached to MIDI input port {in_port}")
            else:
                log.warning("No handle_midi_input() method found for callback.")
            return True

        except Exception as ex:
            log.error(f"Failed to reopen MIDI input port: {ex}")
            return False

    def set_callback(self, callback: Callable) -> None:
        """
        Set address callback for MIDI messages.

        :param callback: The callback function to be set.
        """
        try:
            self.midi_in.set_callback(callback)
        except Exception as ex:
            log.message(
                f"Error {ex} occurred calling self.midi_in.set_callback(callback)"
            )

    def _handle_midi_message(self, message: Any) -> None:
        """
        Routes MIDI messages to appropriate handlers

        :param message: Any
        :return: None
        """
        try:
            preset_data = JDXiPresetButtonData()
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
                log.message(f"Unhandled MIDI message type: {message.type}")
            self.midi_message_incoming.emit(message)
        except Exception as ex:
            log.error(f"Error {ex} occurred")

    def _handle_note_change(self, message: mido.Message, preset_data: dict) -> None:
        """
        Handle Note On and Note Off MIDI messages.

        :param message: Any The MIDI message.
        :param preset_data: Dictionary for preset data modifications.
        """
        log.message(f"MIDI message note change: {message.type} as {message}")

    def _handle_clock(self, message: mido.Message, preset_data: dict) -> None:
        """
        Handle MIDI Clock messages quietly.

        :param message: mido.Message The MIDI message.
        :param preset_data: Dictionary for preset data modifications.
        """
        # Suppress clock message output
        if message.type == "clock":
            return

    def _handle_sysex_message(self, message: mido.Message, preset_data: dict) -> None:
        """
        Handle SysEx MIDI messages from the Roland JD-Xi.

        Processes SysEx data, attempts to parse tone data, and extracts command
        and parameter information for further processing.

        :param message: mido.Message The MIDI SysEx message.
        :param preset_data: Dictionary for preset data modifications.
        """
        try:
            if not (message.type == "sysex" and len(message.data) > 6):
                return
            mido_sub_id_byte_offset = JDXIIdentityOffset.SUB_ID_2_IDENTITY_REPLY - 1  # account for lack of status byte
            if message.data[mido_sub_id_byte_offset] == JDXiConstant.SUB_ID_2_IDENTITY_REPLY:
                handle_identity_request(message)
                return

            hex_string = " ".join(f"{byte:02X}" for byte in message.data)
            sysex_message_bytes = bytes([MidiConstant.START_OF_SYSEX]) + bytes(message.data) + bytes(
                [MidiConstant.END_OF_SYSEX])
            try:
                parsed_data = self.sysex_parser.parse_bytes(sysex_message_bytes)
                filtered_data = {
                    k: v for k, v in parsed_data.items() if k not in IGNORED_KEYS
                }
            except Exception as ex:
                log.error(f"Error {ex} occurred parsing data")
                filtered_data = {}
            log.message(
                f"[MIDI SysEx received]: {hex_string} {filtered_data}",
                silent=False
            )
            try:
                parsed_data = self.sysex_parser.parse_bytes(sysex_message_bytes)
                log.parameter("Parsed data", parsed_data, silent=True)
                self._emit_program_or_tone_name(parsed_data)
                self.midi_sysex_json.emit(json.dumps(parsed_data))
                log.json(parsed_data, silent=True)
            except Exception as parse_ex:
                log.error(f"Failed to parse JD-Xi tone data: {parse_ex}")

        except Exception as ex:
            log.error(f"Unexpected error {ex} while handling SysEx message")

    def _handle_control_change(self, message: mido.Message, preset_data: dict) -> None:  # @@
        """
        Handle Control Change (CC) MIDI messages.

        :param message: mido.Message The MIDI Control Change message.
        :param preset_data: Dictionary for preset data modifications.
        """
        channel = message.channel + 1
        control = message.control
        value = message.value
        log.message(
            f"Control Change - Channel: {channel}, Control: {control}, Value: {value}"
        )
        self.midi_control_changed.emit(channel, control, value)
        if control == MidiConstant.CONTROL_CHANGE_NRPN_MSB:  # NRPN MSB
            self.nrpn_msb = value
        elif control == MidiConstant.CONTROL_CHANGE_NRPN_LSB:  # NRPN LSB
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

    def _handle_program_change(self, message: mido.Message, preset_data: dict) -> None:
        """
        Handle Program Change (PC) MIDI messages.

        Processes program changes and maps them to preset changes based on
        CC values.

        :param message: mido.Message The MIDI Program Change message.
        :param preset_data: Dictionary for preset data modifications.
        """
        channel = message.channel + 1
        program_number = message.program
        log.message(f"Program Change - Channel: {channel}, Program: {program_number}")

        # Store for later use
        self._incoming_preset_data.channel = channel
        self._incoming_preset_data.program_number = program_number

        self.midi_program_changed.emit(channel, program_number)

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
        log.parameter("ADDRESS", address, silent=True)
        log.parameter("TEMPORARY_AREA", temporary_area, silent=True)
        log.parameter("TONE_NAME", tone_name, silent=True)
        log.parameter("SYNTH_TONE", parsed_data.get("SYNTH_TONE"), silent=True)

        # Map address to synth section
        section_map = {
            "12190100": "digital_1",
            "12192100": "digital_2",
            "12194200": "analog",
            "12197000": "drum",
        }

        section = section_map.get(address)
        if section:
            self._incoming_preset_data.set_tone_name(section, tone_name)

        if address in valid_addresses and tone_name:
            if address == "12180000":
                self._emit_program_name_signal(temporary_area, tone_name)
                self._incoming_preset_data.program_name = tone_name
            else:
                self._emit_tone_name_signal(temporary_area, tone_name)

        # All parts received? Then save program!

        if all(k in self._incoming_preset_data.tone_names for k in ("digital_1", "digital_2", "analog", "drum")):
            self._auto_add_current_program()

    def _auto_add_current_program(self):
        """
        _auto_add_current_program

        :return:
        """
        data = self._incoming_preset_data
        log.parameter("preset data", data)
        if data.program_number is None:
            log.message("No program number; cannot auto-add program")
            return

        def to_preset(name, synth_type, preset_number):
            preset = JDXiPresetData.get_preset_details(synth_type, preset_number)
            preset.name = name
            return preset

        try:
            """
            For reference:
            BANK SELECT|  PROGRAM | GROUP|                   NUMBER
            MSB | LSB | NUMBER    |                         |
            -----+-----------+-----------+----------------------------+-----------
            085 | 064 | 001 - 064 | Preset Bank Program (A) | A01 - A64     Banks to 64
            085 | 064 | 065 - 128 | Preset Bank Program (B) | B01 - B64     Banks to 128
            085 | 065 | 001 - 064 | Preset Bank Program (C) | C01 - C64     Banks to 192
            085 | 065 | 065 - 128 | Preset Bank Program (D) | D01 - D64     Banks to 256
            -----+-----------+-----------+----------------------------+-----------
            085 | 000 | 001 - 064 | User Bank Program (E) | E01 - E64       Banks to 320
            085 | 000 | 065 - 128 | User Bank Program (F) | F01 - F64       Banks to 384
            085 | 001 | 001 - 064 | User Bank Program (G) | G01 - G64       Banks to 448
            085 | 001 | 065 - 128 | User Bank Program (H) | H01 - H64       Banks to 512
            -----+-----------+-----------+----------------------------+-----------
            085 | 096 | 001 - 064 | Extra Bank Program (S) | S01 - S64      Banks to 576
            | : | : | : | :
            085 | 103 | 001 - 064 | Extra Bank Program (Z) | Z01 - Z64      Banks to 1024
            """
            program_number = data.program_number or 0
            prefix = "E"
            msb = 85
            lsb = 0
            """
            if 255 < data.program_number < 319:
                lsb = 0
                prefix = "E"
            elif 319 <= data.program_number < 383:
                lsb = 1
                prefix = "F"
            elif 383 <= data.program_number < 447:
                lsb = 0
                prefix = "G"
            elif 447 <= data.program_number < 511:
                lsb = 1
                prefix = "H"""
            if 256 <= program_number <= 320:
                lsb = 0
                prefix = "E"
                display_number = program_number - 256 + 1
            elif 321 <= program_number <= 384:
                lsb = 0
                prefix = "F"
                display_number = program_number - 320
            elif 385 <= program_number <= 448:
                lsb = 1
                prefix = "G"
                display_number = program_number - 384
            elif 449 <= program_number <= 512:
                lsb = 1
                prefix = "H"
                display_number = program_number - 448
            elif 513 <= program_number <= 1024:
                # Extra banks: S (LSB 96) to Z (LSB 103)
                bank_index = (program_number - 513) // 64
                lsb = 96 + bank_index
                prefix = chr(ord("S") + bank_index)
                display_number = (program_number - 513) % 64 + 1
            else:
                log.message(f"❌ Program number {program_number} is not valid (outside 256–1024)")
                return
            program = JDXiProgram(
                id=f"{prefix}{display_number + 1:02d}",
                name=f"{data.program_name}",
                genre="Unknown",
                pc=program_number,
                msb=msb,
                lsb=lsb,
                digital_1=data.tone_names.get("digital_1"),
                digital_2=data.tone_names.get("digital_2"),
                analog=data.tone_names.get("analog"),
                drums=data.tone_names.get("drum"),
            )
            log.parameter("program", program)
        except Exception as ex:
            log.message(f"Error {ex} creating JDXiProgram")
            return
        log.parameter("program", program)
        if add_program_and_save(program):
            log.message(f"✅ Auto-added program: {program.id}")
        else:
            log.message(f"⚠️ Duplicate or failed to add: {program.id}")

    def _emit_program_name_signal(self, area: str, tone_name: str) -> None:
        """
        Emits the appropriate Qt signal for a given tone name

        :param area: str
        :param tone_name: str
        :return: None
        """
        if area == AreaMSB.TEMPORARY_PROGRAM.name:
            log.message(f"Emitting program name: {tone_name} to {area}")
            self.update_program_name.emit(tone_name)

    def _emit_tone_name_signal(self, area: str, tone_name: str) -> None:
        """
        Emits the appropriate Qt signal for a given tone name

        :param area: str
        :param tone_name: str
        :return: None
        """
        synth_type = JDXiMapSynthType.MAP.get(area)
        if synth_type:
            log.message(
                f"Emitting tone name: {tone_name} to {area} (synth type: {synth_type})"
            )
            self.update_tone_name.emit(tone_name, synth_type)
        else:
            log.warning(f"Unknown area: {area}. Cannot emit tone name.")
