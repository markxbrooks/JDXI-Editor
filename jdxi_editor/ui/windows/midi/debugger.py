"""
debugger module
====================
MIDI Debugger for monitoring and interacting with MIDI commands and SysEx messages.

This class provides a graphical user interface (GUI) for sending, decoding,
and logging MIDI messages, including SysEx messages. It allows the user to input
MIDI commands in hexadecimal format, send them to a connected MIDI device,
and view the decoded output for further analysis. The debugger supports both
standard MIDI messages and Roland-specific address-based SysEx messages,
including their parameters, values, and checksums.

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
from typing import Optional, Protocol, Tuple, TypeVar

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import CommandID
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.message.sysex.offset import JDXiSysExMessageLayout
from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser
from jdxi_editor.ui.windows.midi.helpers.debugger import validate_checksum
from picomidi.sysex.parameter.address import AddressParameter

T = TypeVar("T", bound="EnumWithAddress")


class EnumWithAddress(Protocol):
    @classmethod
    def message_position(cls) -> int:
        """Get the position of the message in the SysEx message.
        :return: int - the position of the message
        """
        ...

    @classmethod
    def get_parameter_by_address(cls, address: int) -> Optional[T]:
        """Get the enum member by address.
        :param address: int
        :return: Optional[T] - the enum member or None if not found
        """
        ...


def parse_sysex_byte(byte_value: int, enum_cls: EnumWithAddress) -> str:
    """
    Get the name of a SysEx byte value using a given enum class.

    :param byte_value: int
    :param enum_cls: EnumWithAddress
    :return: name of the parameter or "Unknown" if not found
    """
    enum_member = enum_cls.get_parameter_by_address(byte_value)
    name = enum_member.name if enum_member else f"COMMON ({hex(byte_value)})"
    return name


def parse_sysex_message(message: bytes, enum_cls: EnumWithAddress) -> Tuple[str, int]:
    """
    Parse a SysEx message and return the name and byte value of the specified parameter.

    :param message: str
    :param enum_cls: EnumWithAddress
    :return: Tuple containing the name and byte value
    """
    byte_value = int(message[enum_cls.message_position()])
    enum_member = enum_cls.get_parameter_by_address(byte_value)
    name = enum_member.name if enum_member else f"Unknown ({hex(byte_value)})"
    return name, byte_value


def parse_parameter(offset: int, parameter_type: AddressParameter) -> str:
    """
    Parses JD-Xi tone parameters from SysEx data for Digital, Analog, and Digital Common types.

    :param offset: int - The offset in the SysEx message where the parameter starts.
    :param parameter_type: AddressParameter - The parameter type to parse.
    :return: str name
    """
    return parameter_type.get_name_by_address(offset)


class MIDIDebugger(QMainWindow):
    # SysEx message structure constants

    def __init__(self, midi_helper: MidiIOHelper, parent: QWidget = None):
        """
        init method

        :param midi_helper: MidiIOHelper
        :param parent: QWidget main window
        """
        super().__init__(parent)
        self.midi_helper = midi_helper

        # Set window properties
        self.setWindowTitle("MIDI Debugger")
        self.setMinimumSize(800, 600)

        JDXi.UI.ThemeManager.apply_debugger_window(self)

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
        self.sysex_parser = JDXiSysExParser()

    def _decode_current(self):
        """Decode the currently entered SysEx message(s)"""
        text = self.command_input.toPlainText().strip()
        if not text:
            return

        self.decoded_text.clear()
        lines = text.splitlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                hex_values = line.split()
                message = [int(x, 16) for x in hex_values]
                decoded = self._decode_sysex_15(message)
                self.decoded_text.append(decoded)
            except ValueError as ex:
                self.decoded_text.append(f"Error parsing line: '{line}' -> {str(ex)}")
            except Exception as ex:
                self.decoded_text.append(f"Error decoding line: '{line}' -> {str(ex)}")

    def _decode_sysex_15(self, message):
        """Decode a 15-byte Roland address SysEx message."""
        if len(message) != 15:
            return "Invalid SysEx message (must be 15 bytes)"
        if message[0] != 0xF0 or message[1] != 0x41:
            return "Not a Roland address SysEx message"

        def fmt_row(byte, desc, val, notes=""):
            return f"| {byte:<5} | {desc:<28} | {val:<17} | {notes:<30} |\n"

        try:
            sysex_dict = self.sysex_parser.parse_bytes(bytes(message))
            log.parameter("sysex_dict", sysex_dict)

            command_id, command_byte = parse_sysex_message(message, CommandID)
            temporary_area = sysex_dict.get("TEMPORARY_AREA", "Unknown")
            synth_tone = sysex_dict.get("SYNTH_TONE", "Unknown")
            param_name = sysex_dict.get("PARAM", "Unknown")

            address_msb = message[JDXiSysExMessageLayout.ADDRESS.MSB]
            address_umb = message[JDXiSysExMessageLayout.ADDRESS.UMB]
            address_lsb = message[JDXiSysExMessageLayout.ADDRESS.LSB]
            value = message[JDXiSysExMessageLayout.VALUE]
            checksum = message[JDXiSysExMessageLayout.CHECKSUM]
            checksum_valid = validate_checksum(
                message[
                    JDXiSysExMessageLayout.ADDRESS.MSB : JDXiSysExMessageLayout.CHECKSUM
                ],
                checksum,
            )

            lines = [
                f"|{'-' * 7}|{'-' * 30}|{'-' * 19}|{'-' * 32}|\n",
                fmt_row("Byte", "Description", "Value", "Notes"),
                f"|{'-' * 7}|{'-' * 30}|{'-' * 19}|{'-' * 32}|\n",
                fmt_row(
                    0, "Start of SysEx", hex(message[JDXiSysExMessageLayout.START])
                ),
                fmt_row(
                    1,
                    "Manufacturer ID",
                    hex(message[JDXiSysExMessageLayout.ROLAND_ID]),
                    "Roland",
                ),
                fmt_row(2, "Device ID", hex(message[JDXiSysExMessageLayout.DEVICE_ID])),
                fmt_row(
                    "3-6",
                    "Model ID",
                    " ".join(
                        hex(x)
                        for x in message[
                            JDXiSysExMessageLayout.MODEL_ID.POS1 : JDXiSysExMessageLayout.COMMAND_ID
                        ]
                    ),
                ),
                fmt_row(7, "Command ID", hex(command_byte), command_id),
                fmt_row("8-9", "Synth Area", hex(address_msb), temporary_area),
                fmt_row(10, "Synth Part", hex(address_umb), synth_tone),
                fmt_row(11, "Parameter Address Low", address_lsb, param_name),
                fmt_row(12, "Parameter Value", hex(value), f"{value} ({hex(value)})"),
                fmt_row(
                    13,
                    "Checksum",
                    hex(checksum),
                    "Valid" if checksum_valid else "Invalid",
                ),
                fmt_row(14, "End of SysEx", hex(message[JDXiSysExMessageLayout.END])),
                f"|{'-' * 7}|{'-' * 30}|{'-' * 19}|{'-' * 32}|\n",
            ]

            return "".join(lines)

        except Exception as ex:
            return f"Error decoding message: {str(ex)}"

    def _send_commands(self) -> None:
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
            normalized = re.sub(r"\s+", " ", text)

            # Regex pattern to match all SysEx messages (F0 ... F7)
            sysex_pattern = r"F0(?:\s[0-9A-Fa-f]{2})+?\sF7"
            matches = re.findall(sysex_pattern, normalized)

            if not matches:
                self.log_response("No valid SysEx messages found.")
                return

            for match in matches:
                self.send_message(match)

        except Exception as ex:
            self.log_response(f"Unhandled error in _send_commands: {str(ex)}")

    def send_message(self, match: str) -> None:
        """
        Send a SysEx message based on the provided hex string.

        :param match: str - Hex string representing the SysEx message
        :return: None
        """

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

            log.message(f"Sent SysEx: {hex_str}")

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
