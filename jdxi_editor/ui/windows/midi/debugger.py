"""
debugger module
====================
MIDI Debugger for monitoring and interacting with MIDI commands and SysEx messages.

This class provides a graphical user interface (GUI) for sending, decoding, and logging MIDI messages, including SysEx messages. It allows the user to input MIDI commands in hexadecimal format, send them to a connected MIDI device, and view the decoded output for further analysis. The debugger supports both standard MIDI messages and Roland-specific address-based SysEx messages, including their parameters, values, and checksums.

Key Features:
- Send MIDI messages in hexadecimal format to a MIDI device.
- Decode Roland SysEx messages with detailed information, including areas, commands, and parameters.
- Display decoded message data in a readable table format.
- Log responses from MIDI devices, including message sending success and failure information.
- Validate checksum for SysEx messages to ensure message integrity.
- Provides an easy-to-use interface with instructions, buttons, and output areas for effective debugging.

Attributes:
    SYSEX_AREAS (dict): Mappings for SysEx area IDs to their human-readable names.
    COMMANDS (dict): Mappings for SysEx command IDs to their human-readable names.
    SECTIONS (dict): Mappings for SysEx section IDs to their human-readable names.
    GROUPS (dict): Mappings for SysEx group IDs to their human-readable names.
    PARAMETERS (dict): Mappings for SysEx parameter IDs to their human-readable names.

Methods:
    __init__(self, midi_helper, parent=None): Initializes the MIDI debugger with a MIDI helper.
    _decode_sysex_new(self, message): Decodes a SysEx message in the new format.
    _decode_sysex_15(self, message): Decodes a 15-byte SysEx address message.
    _decode_sysex(self, message): Decodes a general SysEx message.
    _decode_current(self): Decodes the currently entered MIDI message from the input field.
    _send_commands(self): Sends the entered MIDI commands to the connected MIDI device.
    log_response(self, text): Logs a response message to the response log.
    handle_midi_response(self, message): Handles incoming MIDI messages and logs them.

This class is useful for MIDI developers, musicians, and anyone working with MIDI devices, providing both real-time MIDI debugging and SysEx message analysis capabilities.

"""

import re
from typing import Tuple

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QPushButton,
    QTextEdit,
    QLabel,
    QPlainTextEdit,
)
from PySide6.QtCore import Qt

from jdxi_editor.log.error import log_error
from jdxi_editor.log.message import log_message
from jdxi_editor.midi.data.parameter.analog import AddressParameterAnalog
from jdxi_editor.midi.data.address.address import (
    CommandID,
    AddressMemoryAreaMSB,
    AddressOffsetTemporaryToneUMB,
    AddressOffsetProgramLMB,
)
from jdxi_editor.midi.data.parameter.digital.common import AddressParameterDigitalCommon
from jdxi_editor.midi.data.parameter.digital.partial import AddressParameterDigitalPartial
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.jdxi.style import JDXIStyle
from jdxi_editor.ui.windows.midi.helpers.debugger import validate_checksum

from typing import Protocol, TypeVar, Optional

T = TypeVar("T", bound="EnumWithAddress")

PARAMETER_PART_MAP = {
    "TEMPORARY_DIGITAL_SYNTH_1_AREA": AddressParameterDigitalPartial,
    "TEMPORARY_DIGITAL_SYNTH_2_AREA": AddressParameterDigitalPartial,
    "ANALOG_PART": AddressParameterAnalog,
    "DRUM_KIT_PART": AddressParameterDrumPartial,  # Fixed key name
    "COMMON": AddressParameterDigitalCommon
}


class EnumWithAddress(Protocol):
    @classmethod
    def message_position(cls) -> int: ...

    @classmethod
    def get_parameter_by_address(cls, address: int) -> Optional[T]: ...


def parse_sysex_byte(byte_value: int, enum_cls: EnumWithAddress) -> str:
    """
    Get the name of a SysEx byte value using a given enum class.
    :param byte_value:
    :param enum_cls:
    :return: name of the parameter or "Unknown" if not found
    """
    enum_member = enum_cls.get_parameter_by_address(byte_value)
    name = enum_member.name if enum_member else f"Unknown ({hex(byte_value)})"
    return name


def parse_sysex_message(message: bytes, enum_cls: EnumWithAddress) -> Tuple[str, int]:
    """
    Parse a SysEx message and return the name and byte value of the specified parameter.
    :param message:
    :param enum_cls:
    :return: Tuple containing the name and byte value
    """
    byte_value = int(message[enum_cls.message_position()])
    enum_member = enum_cls.get_parameter_by_address(byte_value)
    name = enum_member.name if enum_member else f"Unknown ({hex(byte_value)})"
    return name, byte_value


class MIDIDebugger(QMainWindow):
    # SysEx message structure constants

    PARAMETERS = {
        0x00: "OSC_WAVE",
        0x01: "OSC_VARIATION",
        0x03: "OSC_PITCH",
        0x04: "OSC_DETUNE",
        0x05: "OSC_PWM_DEPTH",
        0x06: "OSC_PW",
        0x07: "OSC_PITCH_ENV_A",
        0x08: "OSC_PITCH_ENV_D",
        0x09: "OSC_PITCH_ENV_DEPTH",
        0x0A: "FILTER_MODE",
        0x0B: "FILTER_SLOPE",
        0x0C: "FILTER_CUTOFF",
        0x0D: "FILTER_KEYFOLLOW",
        0x0E: "FILTER_ENV_VELO",
        0x0F: "FILTER_RESONANCE",
        0x10: "FILTER_ENV_A",
        0x11: "FILTER_ENV_D",
        0x12: "FILTER_ENV_S",
        0x13: "FILTER_ENV_R",
        0x14: "FILTER_ENV_DEPTH",
        0x15: "AMP_LEVEL",
        0x16: "AMP_VELO_SENS",
        0x17: "AMP_ENV_A",
        0x18: "AMP_ENV_D",
        0x19: "AMP_ENV_S",
        0x1A: "AMP_ENV_R",
        0x1B: "AMP_PAN",
    }

    def __init__(self, midi_helper, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper

        # Set window properties
        self.setWindowTitle("MIDI Debugger")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(JDXIStyle.DEBUGGER)

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Create splitter for hex and decoded views
        splitter = QSplitter(Qt.Vertical)

        # Top section - Hex input and buttons
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)

        # Instructions
        instructions = QLabel(
            "Enter MIDI commands (one per line) in hex format:\n"
            "Example: F0 41 10 00 00 00 0E 12 19 01 20 00 01 F7"
        )
        instructions.setWordWrap(True)
        top_layout.addWidget(instructions)

        # Command input
        self.command_input = QPlainTextEdit()
        self.command_input.setPlaceholderText("Enter MIDI commands here...")
        top_layout.addWidget(self.command_input)

        # Buttons
        button_layout = QHBoxLayout()

        self.send_button = QPushButton("Send Commands")
        self.send_button.clicked.connect(self._send_commands)
        button_layout.addWidget(self.send_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.command_input.clear)
        button_layout.addWidget(self.clear_button)

        self.decode_button = QPushButton("Decode")
        self.decode_button.clicked.connect(self._decode_current)
        button_layout.addWidget(self.decode_button)

        top_layout.addLayout(button_layout)

        # Bottom section - Decoded view
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)

        # Decoded output
        bottom_layout.addWidget(QLabel("Decoded Message:"))
        self.decoded_text = QTextEdit()
        self.decoded_text.setReadOnly(True)
        bottom_layout.addWidget(self.decoded_text)

        # Response log
        bottom_layout.addWidget(QLabel("Response Log:"))
        self.response_log = QTextEdit()
        self.response_log.setReadOnly(True)
        bottom_layout.addWidget(self.response_log)

        self.clear_button.clicked.connect(self.decoded_text.clear)
        self.clear_button.clicked.connect(self.response_log.clear)

        # Add widgets to splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)

        # Add splitter to main layout
        layout.addWidget(splitter)

    def _decode_sysex_15(self, message):
        """Decode address SysEx message."""
        if len(message) != 15:
            return "Invalid SysEx message (must be 15 bytes)"
        if message[0] != 0xF0 or message[1] != 0x41:
            return "Not a Roland address SysEx message"

        try:
            # Parse top-level SysEx components
            command_str, command_byte = parse_sysex_message(message, CommandID)
            area_str, area_byte = parse_sysex_message(message, AddressMemoryAreaMSB)
            synth_str, synth_byte = parse_sysex_message(message, AddressOffsetTemporaryToneUMB)
            part_str, part_byte = parse_sysex_message(message, AddressOffsetProgramLMB)
            part_address = hex(part_byte)

            try:
                parameter_enum = PARAMETER_PART_MAP.get(synth_str)
                if parameter_enum is not None:
                    param_str, param = parse_sysex_message(message, parameter_enum)
                else:
                    raise ValueError(f"No parameter enum defined for synth type: {synth_str}")
                param_address = hex(param)
            except Exception as ex:
                log_error(f"Error {ex} parsing sysex bytes")
                param = message[11]
                param_address = hex(param)
                param_str = self.PARAMETERS.get(param, f"Unknown Parameter ({param_address})")

            # Get value
            value = message[12]

            # Get checksum
            checksum = message[13]
            checksum_valid = validate_checksum(message[7:13], checksum)

            # Format the output
            decoded = (
                f"|{'-' * 7}|{'-' * 30}|{'-' * 19}|{'-' * 32}|\n"
                f"| {'Byte':<5} | {'Description':<28} | {'Value':<17} | {'Notes':<30} |\n"
                f"|{'-' * 7}|{'-' * 30}|{'-' * 19}|{'-' * 32}|\n"
                f"| {0:<5} | {'Start of SysEx':<28} | {hex(message[0]):<17} | {'':<30} |\n"
                f"| {1:<5} | {'Manufacturer ID':<28} | {hex(message[1]):<17} | {'Roland':<30} |\n"
                f"| {2:<5} | {'Device ID':<28} | {hex(message[2]):<17} | {'':<30} |\n"
                f"| {'3-6':<5} | {'Model ID':<28} | {' '.join(hex(x) for x in message[3:7]):<17} | {'':<30} |\n"
                f"| {7:<5} | {'Command ID':<28} | {hex(command_byte):<17} | {command_str:<30} |\n"
                f"| {8:<5} | {'Area':<28} | {hex(area_byte):<17} | {area_str:<30} |\n"
                f"| {9:<5} | {'Synth':<28} | {hex(synth_byte):<17} | {synth_str:<30} |\n"
                f"| {10:<5} | {'Parameter Address High':<28} | {part_address:<17} | {part_str:<30} |\n"
                f"| {11:<5} | {'Parameter Address Low':<28} | {param_address:<17} | {param_str:<30} |\n"
                f"| {12:<5} | {'Parameter Value':<28} | {hex(value):<17} | {value} ({hex(value)}) {'':<22} |\n"
                f"| {13:<5} | {'Checksum':<28} | {hex(checksum):<17} | {'Valid' if checksum_valid else 'Invalid'} {'':<22} |\n"
                f"| {14:<5} | {'End of SysEx':<28} | {hex(message[-1]):<17} | {'':<30} |\n"
                f"|{'-' * 7}|{'-' * 30}|{'-' * 19}|{'-' * 32}|\n"
            )

            return decoded

        except Exception as ex:
            return f"Error decoding message: {str(ex)}"

    def _decode_sysex_15_old(self, message):
        """Decode address SysEx message"""
        if len(message) != 15:
            return "Invalid SysEx message (must be 15 bytes)"
        if message[0] != 0xF0 or message[1] != 0x41:
            return "Not a Roland address SysEx message"
        PARAMETER_PART_MAP = {
            "TEMPORARY_DIGITAL_SYNTH_1_AREA": AddressParameterDigitalPartial,
            "TEMPORARY_DIGITAL_SYNTH_2_AREA": AddressParameterDigitalPartial,
            "ANALOG_PART": AddressParameterAnalog,
            "DRUM_KIT_PART": AddressParameterDrumPartial,
            "COMMON": AddressParameterDigitalCommon
        }
        try:
            # Parse top-level SysEx components
            command_str, command_byte = parse_sysex_message(message, CommandID)
            area_str, area_byte = parse_sysex_message(message, AddressMemoryAreaMSB)
            synth_str, synth_byte = parse_sysex_message(message, AddressOffsetTemporaryToneUMB)
            part_str, part_byte = parse_sysex_message(message, AddressOffsetProgramLMB)
            part_address = hex(part_byte)
            try:
                parameter = PARAMETER_PART_MAP.get(synth_str)
                param_str, param = parse_sysex_message(message, parameter)
                param_address = hex(param)
            except Exception as ex:
                log_error(f"Error {ex} parsing sysex bytes")
                param = message[11]
                param_address = hex(param)
                param_str = self.PARAMETERS.get(param, f"Unknown Parameter ({param_address})")
            # Get value
            value = message[12]

            # Get checksum
            checksum = message[13]
            checksum_valid = validate_checksum(message[7:13], checksum)

            # Format the output
            decoded = (
                f"|{'-' * 7}|{'-' * 30}|{'-' * 19}|{'-' * 32}|\n"
                f"| {'Byte':<5} | {'Description':<28} | {'Value':<17} | {'Notes':<30} |\n"
                f"|{'-' * 7}|{'-' * 30}|{'-' * 19}|{'-' * 32}|\n"
                f"| {0:<5} | {'Start of SysEx':<28} | {hex(message[0]):<17} | {'':<30} |\n"
                f"| {1:<5} | {'Manufacturer ID':<28} | {hex(message[1]):<17} | {'Roland':<30} |\n"
                f"| {2:<5} | {'Device ID':<28} | {hex(message[2]):<17} | {'':<30} |\n"
                f"| {'3-6':<5} | {'Model ID':<28} | {' '.join(hex(x) for x in message[3:7]):<17} | {'':<30} |\n"
                f"| {7:<5} | {'Command ID':<28} | {hex(command_byte):<17} | {command_str:<30} |\n"
                f"| {8:<5} | {'Area':<28} | {hex(area_byte):<17} | {area_str:<30} |\n"
                f"| {9:<5} | {'Synth':<28} | {hex(synth_byte):<17} | {synth_str:<30} |\n"
                f"| {10:<5} | {'Parameter Address High':<28} | {part_address:<17} | {part_str:<30} |\n"
                f"| {11:<5} | {'Parameter Address Low':<28} | {param_address:<17} | {param_str:<30} |\n"
                f"| {12:<5} | {'Parameter Value':<28} | {hex(value):<17} | {value} ({hex(value)}) {'':<22} |\n"
                f"| {13:<5} | {'Checksum':<28} | {hex(checksum):<17} | {'Valid' if checksum_valid else 'Invalid'} {'':<22} |\n"
                f"| {14:<5} | {'End of SysEx':<28} | {hex(message[-1]):<17} | {'':<30} |\n"
                f"|{'-' * 7}|{'-' * 30}|{'-' * 19}|{'-' * 32}|\n"
            )

            return decoded

        except Exception as ex:
            return f"Error decoding message: {str(ex)}"

    def _decode_current(self):
        """Decode the currently entered message"""
        text = self.command_input.toPlainText().strip()
        if not text:
            return
        for line in text.split("\n"):
            try:
                # Convert hex string to bytes
                hex_values = text.split()
                message = [int(x, 16) for x in hex_values]
                # message = bytes(int(byte, 16) for byte in text.split())
                # Decode and display
                decoded = self._decode_sysex_15(message)
                self.decoded_text.append(decoded)

            except ValueError as ex:
                self.decoded_text.setText(f"Error parsing hex values: {str(ex)}")
            except Exception as ex:
                self.decoded_text.setText(f"Error decoding message: {str(ex)}")

    def _send_commands(self):
        """Send all valid SysEx MIDI messages from user-entered text input."""
        if not self.midi_helper:
            self.log_response("Error: MIDI helper not initialized")
            return

        if not self.midi_helper.midi_out:
            self.log_response("Error: No MIDI output port available")
            return

        try:
            # Get all input text
            text = self.command_input.toPlainText().strip()
            if not text:
                return

            # Normalize line breaks and whitespace
            normalized = re.sub(r'\s+', ' ', text)

            # Regex pattern to match all SysEx messages (F0 ... F7)
            sysex_pattern = r'F0(?:\s[0-9A-Fa-f]{2})+?\sF7'
            matches = re.findall(sysex_pattern, normalized)

            if not matches:
                self.log_response("No valid SysEx messages found.")
                return

            for match in matches:
                self.send_message(match)

        except Exception as ex:
            self.log_response(f"Unhandled error in _send_commands: {str(ex)}")

    def send_message(self, match):
        try:
            # Convert hex string to list of ints
            hex_values = match.strip().split()
            self.log_response(f"Converting hex values: {hex_values}")

            message = [int(h, 16) for h in hex_values]

            # Send the message
            success = self.midi_helper.send_raw_message(message)

            hex_str = " ".join([f"{b:02X}" for b in message])
            if success:
                self.log_response(f"Successfully sent: {hex_str}")
            else:
                self.log_response(f"Failed to send: {hex_str}")

            log_message(f"Sent SysEx: {hex_str}")

        except ValueError as ex:
            self.log_response(f"Error parsing message: {match}\n{str(ex)}")
        except Exception as ex:
            self.log_response(f"Unexpected error: {match}\n{str(ex)}")

    def log_response(self, text):
        """Add text to response log"""
        self.response_log.append(text)

    def handle_midi_response(self, message):
        """Handle incoming MIDI message"""
        try:
            # Convert message to hex string
            hex_str = " ".join([f"{b:02X}" for b in message])
            self.log_response(f"Received: {hex_str}")

        except Exception as ex:
            self.log_response(f"Error handling response: {str(ex)}")
