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
import os
from typing import Any, Callable, Dict, List, Optional

import mido
from decologr import Decologr as log
from picomidi.constant import Midi
from PySide6.QtCore import Signal

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import AddressStartMSB as AreaMSB
from jdxi_editor.midi.io.controller import MidiIOController

# handle_identity_request moved to JDXiSysExParser.parse_identity_request
from jdxi_editor.midi.map.synth_type import JDXiMapSynthType
from jdxi_editor.midi.message.sysex.offset import JDXiSysExIdentityLayout
from jdxi_editor.midi.program.program import JDXiProgram
from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser
from jdxi_editor.midi.sysex.request.data import IGNORED_KEYS
from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.ui.preset.button import JDXiPresetButtonData
from jdxi_editor.ui.preset.incoming_data import IncomingPresetData
from jdxi_editor.ui.programs import JDXiUIProgramList


def add_or_replace_program_and_save(new_program: JDXiProgram) -> bool:
    """
    Add a new program to the list, replacing any with matching ID or PC.
    Uses SQLite database for reliable storage.

    :param new_program: JDXiProgram to add or replace.
    :return: True if successfully added/replaced and saved, False otherwise.
    """
    try:
        # Use SQLite database instead of JSON
        from jdxi_editor.ui.programs.database import get_database

        db = get_database()
        return db.add_or_replace_program(new_program)
    except Exception as e:
        log.error(f"❌ Failed to add or replace program: {e}")
        return False


def add_or_replace_program_and_save_old(new_program: JDXiProgram) -> bool:
    """
    add_or_replace_program_and_save

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

        log.message(
            f"Adding new program {new_program}: {new_program.id} with PC {new_program.pc}"
        )

        program_list.append(new_program.to_dict())

        log.message(f"Program list after addition: {program_list}")

        save_programs(program_list)
        log.message(
            f"Added and saved program: {new_program.id} with PC {new_program.pc}"
        )
        return True
    except Exception as e:
        log.error(f"Failed to add and save program: {e}")
        return False


def load_programs() -> List[Dict[str, str]]:
    try:
        with open(JDXiUIProgramList.USER_PROGRAMS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_programs(program_list: List[Dict[str, str]]) -> None:
    """
    Save the program list to USER_PROGRAMS_FILE, creating the file and directory if needed.

    :param program_list: List of program dictionaries.
    """
    try:
        file_path = JDXiUIProgramList.USER_PROGRAMS_FILE
        os.makedirs(
            os.path.dirname(file_path), exist_ok=True
        )  # ensure directory exists
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(program_list, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving programs: {e}")


def save_programs_old(program_list: List[Dict[str, str]]) -> None:
    """
    save_programs

    :param program_list: List[Dict[str, str]]
    :return: None
    """
    with open(JDXiUIProgramList.USER_PROGRAMS_FILE, "w", encoding="utf-8") as f:
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
        self._incoming_preset_data.msb = 85  # default to Preset Bank

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
            mido_sub_id_byte_offset = (
                JDXiSysExIdentityLayout.ID.SUB2 - 1
            )  # account for lack of status byte
            if (
                message.data[mido_sub_id_byte_offset]
                == JDXi.Midi.SYSEX.IDENTITY.CONST.SUB2_IDENTITY_REPLY
            ):
                self.sysex_parser.parse_identity_request(message)
                return

            hex_string = " ".join(f"{byte:02X}" for byte in message.data)
            sysex_message_bytes = (
                bytes([Midi.SYSEX.START])
                + bytes(message.data)
                + bytes([Midi.SYSEX.END])
            )
            try:
                parsed_data = self.sysex_parser.parse_bytes(sysex_message_bytes)
                filtered_data = {
                    k: v for k, v in parsed_data.items() if k not in IGNORED_KEYS
                }
            except ValueError as ex:
                # Skip logging for non-JD-Xi messages (e.g., universal identity_request requests)
                error_msg = str(ex)
                if "Not a JD-Xi SysEx message" in error_msg:
                    # This is a universal MIDI message, not a JD-Xi message - skip silently
                    filtered_data = {}
                    return
                else:
                    # Log error for actual JD-Xi parsing errors
                    log.error(f"Error {ex} occurred parsing data")
                    filtered_data = {}
            except Exception as ex:
                log.error(f"Error {ex} occurred parsing data")
                filtered_data = {}
            log.message(
                f"[MIDI SysEx received]: {hex_string} {filtered_data}", silent=False
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

    def _handle_control_change(
        self, message: mido.Message, preset_data: dict
    ) -> None:  # @@
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
        if value in [
            JDXi.Midi.CC.BANK_SELECT.LSB.BANK_E_AND_F,
            JDXi.Midi.CC.BANK_SELECT.LSB.BANK_G_AND_H,
        ]:
            log.parameter("control", control)  # Bank Select LSB 00 or 01
            log.parameter("value", value)  # Bank Select LSB 00 or 01
            self._incoming_preset_data.lsb = value

        self.midi_control_changed.emit(channel, control, value)
        if control == Midi.CC.NRPN.MSB:  # NRPN MSB
            self.nrpn_msb = value
        elif control == Midi.CC.NRPN.LSB:  # NRPN LSB
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

        address = parsed_data.get(SysExSection.ADDRESS)

        tone_name = parsed_data.get(SysExSection.TONE_NAME)
        temporary_area = parsed_data.get(SysExSection.TEMPORARY_AREA)
        log.parameter(SysExSection.ADDRESS, address, silent=True)
        log.parameter(SysExSection.TEMPORARY_AREA, temporary_area, silent=True)
        log.parameter(SysExSection.TONE_NAME, tone_name, silent=True)
        log.parameter(
            SysExSection.SYNTH_TONE,
            parsed_data.get(SysExSection.SYNTH_TONE),
            silent=True,
        )

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
        # Only auto-add if enabled (disabled during manual database updates)
        auto_add_enabled = getattr(self, "_auto_add_enabled", True)
        if auto_add_enabled and all(
            k in self._incoming_preset_data.tone_names
            for k in ("digital_1", "digital_2", "analog", "drum")
        ):
            self._auto_add_current_program()

    def _auto_add_current_program(self):
        """
        _auto_add_current_program

        :return: None

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
        data = self._incoming_preset_data
        log.parameter("preset data", data)

        if data.program_number is None:
            log.message("No program number; cannot auto-add program")
            return

        try:
            program_number = data.program_number
            # Default MSB to 85 (standard for JD-Xi programs) if not set
            msb = data.msb if data.msb is not None else 85
            # Default LSB to 0 (User Bank E/F) if not set
            # This is the most common case for user programs
            lsb = data.lsb if data.lsb is not None else 0
            prefix = None

            # Guard against None values (should not happen after defaults, but keep as safety check)
            if msb is None:
                log.message(f"❌ Missing MSB (msb={msb}); cannot auto-add program")
                return

            index_in_bank = program_number % 64

            # === User Banks ===
            if msb == 85:
                if lsb == 0:
                    prefix = "E" if program_number < 64 else "F"
                elif lsb == 1:
                    prefix = "G" if program_number < 64 else "H"
                elif 96 <= lsb <= 103:
                    prefix = chr(ord("S") + (lsb - 96))
                else:
                    log.message(f"❌ Unsupported LSB {lsb} for user/extra banks")
                    return
            else:
                log.message(f"❌ Unsupported MSB {msb} (expected 85)")
                return

            program = JDXiProgram(
                id=f"{prefix}{index_in_bank + 1:02d}",
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

        if add_or_replace_program_and_save(program):
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
