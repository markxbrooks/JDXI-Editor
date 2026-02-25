"""
MIDI Helper Module
==================

This module provides address unified helper class for MIDI communication with the Roland JD-Xi.
It integrates both MIDI input and output functionalities by combining the features of
the MIDIInHandler and MIDIOutHandler classes.

Classes:
    MIDIHelper: A helper class that inherits from both MIDIInHandler and MIDIOutHandler,
                offering address consolidated interface for handling MIDI messages (including
                SysEx messages in JSON format) for the JD-Xi synthesizer.

Dependencies:
    - PySide6.QtCore.Signal for Qt signal support.
    - jdxi_editor.midi.input_handler.MIDIInHandler for handling incoming MIDI messages.
    - jdxi_editor.midi.output_handler.MIDIOutHandler for handling outgoing MIDI messages.

"""

import json
import logging
import zipfile

import mido
from decologr import Decologr as log

from jdxi_editor.midi.data.address.address import (
    JDXiSysExAddress,
    JDXiSysExOffsetTemporaryToneUMB,
)
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.digital.common import DigitalCommonParam
from jdxi_editor.midi.data.parameter.digital.partial import DigitalPartialParam
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParam
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.data.parameter.program.common import ProgramCommonParam
from jdxi_editor.midi.io.input_handler import MidiInHandler
from jdxi_editor.midi.io.output_handler import MidiOutHandler
from jdxi_editor.midi.sysex.composer import JDXiSysExComposer
from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.ui.windows.jdxi.helpers.port import find_jdxi_port


class MidiIOHelper(MidiInHandler, MidiOutHandler):
    """
    MidiIOHelper

    Class to handle midi input/output
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MidiIOHelper, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, parent=None):
        """constructor"""
        # Check if QObject has already been initialized (singleton pattern)
        # QObject sets _parent attribute when initialized
        if hasattr(self, "_parent") or hasattr(self, "initialized"):
            # Already initialized, just update parent if provided
            if parent and hasattr(self, "setParent"):
                self.setParent(parent)
            return

        self._current_out_port = None
        self._current_in_port = None
        self.in_port_name = ""  # Store input port name
        self.out_port_name = ""  # Store output port name

        # Initialize parent classes - this will initialize QObject once through MRO
        # Since both MidiInHandler and MidiOutHandler inherit from MidiIOController (QObject),
        # Python's MRO ensures QObject.__init__ is only called once
        super().__init__(parent)

        # Set additional attributes
        self.midi_messages = []
        self.current_in = None
        self.current_out = None
        self.initialized = True

    def send_mido_message(self, msg: mido.Message):
        """
        send_mido_message

        :param msg: mido.Message
        :return:
        """
        self.send_raw_message(msg.bytes())

    def send_json_patch_to_instrument(self, json_string: str) -> None:
        """
        Send all parameters from a JSON patch to the instrument as SysEx messages.

        :param json_string: str JSON string containing patch data
        :return: None
        """
        try:
            # Use the JSON parser for consistency
            from jdxi_editor.midi.sysex.parser.json_parser import JDXiJsonSysexParser

            parser = JDXiJsonSysexParser(json_string)
            patch_data = parser.parse()

            if not patch_data:
                log.error("Failed to parse JSON patch data", scope="MidiIOHelper")
                return

            # Skip metadata fields
            metadata_fields = {
                SysExSection.JD_XI_HEADER,
                SysExSection.ADDRESS,
                SysExSection.TEMPORARY_AREA,
                SysExSection.SYNTH_TONE,
            }

            # Parse address from hex string
            address_hex = patch_data.get(SysExSection.ADDRESS, "")
            if not address_hex or len(address_hex) < 8:
                log.warning(f"Invalid ADDRESS in patch data: {address_hex}")
                return

            # Convert hex address to bytes and create RolandSysExAddress
            address_bytes = bytes(
                int(address_hex[i : i + 2], 16) for i in range(0, len(address_hex), 2)
            )
            if len(address_bytes) < 4:
                log.warning(f"Address too short: {address_bytes}")
                return

            address = JDXiSysExAddress(
                msb=address_bytes[0],
                umb=address_bytes[1],
                lmb=address_bytes[2],
                lsb=address_bytes[3],
            )

            # Determine parameter class based on TEMPORARY_AREA and SYNTH_TONE
            temporary_area = patch_data.get(SysExSection.TEMPORARY_AREA, "")
            synth_tone = patch_data.get(SysExSection.SYNTH_TONE, "")

            # Map to parameter class
            param_class = None
            if temporary_area == "TEMPORARY_PROGRAM":
                # Program common parameters
                if synth_tone == "COMMON":
                    param_class = ProgramCommonParam
                else:
                    log.warning(
                        f"Unsupported synth_tone for TEMPORARY_PROGRAM: {synth_tone}"
                    )
                    return
            elif temporary_area == JDXiSysExOffsetTemporaryToneUMB.ANALOG_SYNTH.name:
                param_class = AnalogParam
            elif (
                temporary_area == JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_1.name
                or temporary_area
                == JDXiSysExOffsetTemporaryToneUMB.DIGITAL_SYNTH_2.name
            ):
                if synth_tone in [
                    "PARTIAL_1",
                    "PARTIAL_2",
                    "PARTIAL_3",
                    "PARTIAL_1.name",
                    "PARTIAL_2.name",
                    "PARTIAL_3.name",
                ]:
                    param_class = DigitalPartialParam
                else:
                    param_class = DigitalCommonParam
            elif temporary_area == JDXiSysExOffsetTemporaryToneUMB.DRUM_KIT.name:
                # Drum common has lmb=0x00, partials have lmb >= 0x2E
                if address.lmb == 0x00 or synth_tone == "COMMON":
                    param_class = DrumCommonParam
                else:
                    param_class = DrumPartialParam

            if not param_class:
                log.warning(
                    f"Could not determine parameter class for {temporary_area}/{synth_tone}"
                )
                return

            # Create composer
            composer = JDXiSysExComposer()

            # Send each parameter
            sent_count = 0
            skipped_count = 0
            for param_name, param_value in patch_data.items():
                if param_name in metadata_fields:
                    continue

                # Get parameter enum
                param = (
                    param_class.get_by_name(param_name)
                    if hasattr(param_class, "get_by_name")
                    else None
                )
                if not param:
                    skipped_count += 1
                    continue

                # Convert value to int if needed
                try:
                    raw_value = (
                        int(param_value)
                        if not isinstance(param_value, int)
                        else param_value
                    )
                except (ValueError, TypeError):
                    log.warning(f"Invalid value type for {param_name}: {param_value}")
                    skipped_count += 1
                    continue

                # Check if this is a raw MIDI value (> 127) that needs conversion to digital value
                # Parsed SysEx JSON contains raw MIDI values (0-255), but compose_message expects digital values
                value = raw_value

                # Get parameter max value (for 1-byte parameters, this should be <= 127)
                param_max = getattr(param, "max_val", None)
                if param_max is None:
                    # If max_val is not set, try to infer from the parameter definition
                    # Most parameters have max_val, but if not, assume 127 for safety
                    param_max = 127

                # If value is > 127, it's likely a raw MIDI byte that needs handling
                if raw_value > 127:
                    # Try to convert from MIDI to digital value if the parameter supports it
                    if hasattr(param, "convert_from_midi"):
                        try:
                            value = param.convert_from_midi(raw_value)
                            log.message(
                                f"Converted {param_name} from MIDI value {raw_value} to display value {value}",
                                silent=True,
                            )
                        except Exception as conv_ex:
                            log.warning(
                                f"Failed to convert {param_name} from MIDI {raw_value}: {conv_ex}"
                            )
                            # If conversion fails and value is still out of range, skip it
                            if param_max <= 127:
                                log.warning(
                                    f"Skipping {param_name}: MIDI value {raw_value} out of range (max: {param_max})"
                                )
                                skipped_count += 1
                                continue
                            # If param_max > 127, it might be a 4-nibble parameter, so use value as-is
                            value = raw_value
                    elif param_max <= 127:
                        # Parameter doesn't support conversion and max is <= 127, so value > 127 is invalid
                        # In Roland SysEx, 0x80 (128) often means "no change" - skip these
                        log.warning(
                            f"Skipping {param_name}: MIDI value {raw_value} out of range for 1-byte parameter (max: {param_max})",
                            silent=True,
                        )
                        skipped_count += 1
                        continue
                    # If param_max > 127, it's likely a 4-nibble parameter, so value > 127 might be valid
                    # But still check - if it's way too large, skip it
                    if raw_value > 65535:
                        log.warning(
                            f"Skipping {param_name}: MIDI value {raw_value} exceeds 16-bit range"
                        )
                        skipped_count += 1
                        continue
                    # Use value as-is and let compose_message handle it

                # Note: compose_message expects digital values and will convert them to MIDI internally
                # We've now ensured value is a digital value (either it was already one, or we converted it)

                # Final validation: if value is still > 127 and param is 1-byte, skip it
                # This catches cases where conversion didn't work or wasn't available
                get_nibbled_size = getattr(param, "get_nibbled_size", None)
                param_size = get_nibbled_size() if callable(get_nibbled_size) else 1
                if param_size == 1 and value > 127:
                    log.warning(
                        f"Skipping {param_name}: final value {value} still out of range for 1-byte parameter",
                        silent=True,
                    )
                    skipped_count += 1
                    continue

                # Compose and send SysEx message
                try:
                    sysex_message = composer.compose_message(
                        address=address,
                        param=param,
                        value=value,  # Pass digital value as-is
                    )
                    if sysex_message:
                        result = self.send_midi_message(sysex_message)
                        if result:
                            sent_count += 1
                        else:
                            log.warning(f"Failed to send {param_name}")
                            skipped_count += 1
                    else:
                        skipped_count += 1
                except ValueError as ve:
                    # Catch validation errors from compose_message
                    if (
                        "range" in str(ve).lower()
                        or "256" in str(ve)
                        or "out of range" in str(ve).lower()
                    ):
                        # Silently skip out-of-range values - these are expected for invalid parsed data
                        log.warning(f"Skipping {param_name}: {ve}", silent=True)
                    else:
                        log.warning(f"Error composing message for {param_name}: {ve}")
                    skipped_count += 1
                except Exception as ex:
                    log.warning(f"Error sending {param_name}: {ex}")
                    skipped_count += 1

            log.message(
                f"Sent {sent_count} parameters to instrument (skipped {skipped_count})"
            )

        except json.JSONDecodeError as ex:
            log.error(f"Invalid JSON in patch: {ex}", scope="MidiIOHelper")
        except Exception as ex:
            log.error(f"Error sending patch to instrument: {ex}", scope="MidiIOHelper")

    def load_patch(self, file_path: str):
        """
        Load the JSON patch as a string and emit it.
        Also handles .msz bundles which may contain MIDI files.
        Automatically sends all loaded parameters to the instrument.

        :param file_path: str
        :return: None
        """
        if file_path.endswith((".jsz", ".msz")):
            log.message(
                f"Loading {'MSZ' if file_path.endswith('.msz') else 'JSZ'} file"
            )
            try:
                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    # Extract and load MIDI files first (if any)
                    midi_files = [f for f in zip_ref.namelist() if f.endswith(".mid")]
                    if midi_files:
                        log.message(
                            f"Found {len(midi_files)} MIDI file(s) in bundle",
                            scope="MidiIOHelper",
                        )
                        # Emit signal for MIDI file loading (will be handled by PatchManager)
                        for midi_file in midi_files:
                            log.message(
                                f"MIDI file in bundle: {midi_file}",
                                scope="MidiIOHelper",
                            )

                    # Load JSON files and send to instrument
                    for json_file in zip_ref.namelist():
                        log.message(f"File in zip: {json_file}", scope="MidiIOHelper")
                        if json_file.endswith(".json"):
                            log.message(
                                f"Loading JSON file: {json_file}", scope="MidiIOHelper"
                            )
                            # Read the JSON file from the zip archive
                            with zip_ref.open(json_file) as json_file_handle:
                                json_string = json_file_handle.read().decode("utf-8")
                                # Emit for UI update
                                self.midi_sysex_json.emit(json_string)
                                # Send to instrument
                                self.send_json_patch_to_instrument(json_string)
            except Exception as ex:
                log.error(
                    f"Error reading or emitting sysex JSON: {ex}", scope="MidiIOHelper"
                )
            return
        try:
            with open(file_path, "r", encoding="utf-8") as file_handle:
                json_string = file_handle.read()
                # Emit for UI update
                self.midi_sysex_json.emit(json_string)
                # Send to instrument
                self.send_json_patch_to_instrument(json_string)
        except Exception as ex:
            log.error(f"Error reading or emitting sysex JSON: {ex}")

    def __str__(self):
        """
        __str__

        :return: str String representation
        """
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def load_sysx_patch(self, file_path: str):
        """
        Load the SysEx patch from a file and emit it.

        :param file_path: str File path as a string
        :return: None
        """
        try:
            with open(file_path, "rb") as file:
                sysex_data = file.read()

            if not sysex_data.startswith(b"\xf0") or not sysex_data.endswith(b"\xf7"):
                log.message("Invalid SysEx file format", scope="MidiIOHelper")
                return
        except Exception as ex:
            log.error(f"Error {ex} occurred opening file", scope="MidiIOHelper")

        self.midi_messages.append(sysex_data)
        try:
            log.message(
                f"attempting to send message: {sysex_data}", scope="MidiIOHelper"
            )
            sysex_list = list(sysex_data)
            self.send_raw_message(sysex_list)
        except Exception as ex:
            log.error(f"Error {ex} sending sysex list", scope="MidiIOHelper")

    def set_midi_ports(self, in_port: str, out_port: str) -> bool:
        """
        Set MIDI input and output ports

        :param in_port: str
        :param out_port: str
        :return: bool True on success, False otherwise
        """
        try:
            if not self.open_input_port(in_port):
                return False
            if not self.open_output_port(out_port):
                return False
            return True

        except Exception as ex:
            log.error(f"Error setting MIDI ports: {str(ex)}", scope="MidiIOHelper")
            return False

    def connect_port_names(self, in_port: str, out_port: str) -> bool:
        """
        Attempt to automatically connect to JD-Xi MIDI ports.

        :param in_port: str
        :param out_port: str
        :return: bool True on success, False otherwise
        """
        try:
            # Ensure both ports are found
            if not in_port or not out_port:
                log.message(
                    "JD-Xi MIDI auto-connect failed",
                    level=logging.WARNING,
                    scope="MidiIOHelper",
                )
                log.parameter("MIDI in_port", in_port, scope="MidiIOHelper")
                log.parameter("MIDI out_port", out_port, scope="MidiIOHelper")
                return False
            self.set_midi_ports(in_port, out_port)
            # Verify connection
            log.parameter(
                "Successfully connected to JD-Xi MIDI:", in_port, scope="MidiIOHelper"
            )
            log.parameter(
                "Successfully connected to JD-Xi MIDI", out_port, scope="MidiIOHelper"
            )
            self.identify_device()
            return True

        except Exception as ex:
            log.error(
                f"Error auto-connecting to JD-Xi: {str(ex)}", scope="MidiIOHelper"
            )
            return False

    def reconnect_port_names(self, in_port: str, out_port: str) -> bool:
        """
        Reconnect ports

        :param in_port: str
        :param out_port: str
        :return: None
        """
        try:
            self.close_ports()
            self.connect_port_names(in_port, out_port)
            self.open_output_port(out_port)
            self.reopen_input_port_name(in_port)
            return True
        except Exception as ex:
            log.error(f"Error {ex} occurred reconnecting ports", scope="MidiIOHelper")
            return False

    def auto_connect_jdxi(self) -> bool:
        """
        Attempt to automatically connect to JD-Xi MIDI ports.

        :return: bool True on success, False otherwise
        """
        try:
            # Find JD-Xi ports
            jdxi_in_port = find_jdxi_port(self.get_input_ports())
            jdxi_out_port = find_jdxi_port(self.get_output_ports())
            self.connect_port_names(jdxi_in_port, jdxi_out_port)
            # self.identify_device()
            return True
        except Exception as ex:
            log.error(
                f"Error auto-connecting to JD-Xi: {str(ex)}", scope="MidiIOHelper"
            )
            return False
