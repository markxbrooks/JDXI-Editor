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
from typing import Optional, Protocol, Tuple, Type, TypeVar, runtime_checkable

from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.midi.data.address.address import CommandID, SysExOffsetByte
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.message import MidiMessage
from jdxi_editor.midi.message.sysex.offset import JDXiSysExMessageLayout
from jdxi_editor.midi.sysex.parser.sysex import JDXiSysExParser
from jdxi_editor.midi.sysex.sections import SysExSection
from jdxi_editor.ui.common import JDXi, QVBoxLayout, QWidget
from jdxi_editor.ui.windows.midi.helpers.debugger import validate_checksum

T = TypeVar("T", bound="EnumWithAddress")


@runtime_checkable
class SysExEnumProtocol(Protocol):
    @classmethod
    def message_position(cls) -> int: ...

    def __call__(self, value: int): ...


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


def parse_sysex_byte(byte_value: int, enum_cls: Type[SysExEnumProtocol]) -> str:
    """
    Get the name of a SysEx byte value using a given enum class.

    Supports both:
    - address-aware enums (get_parameter_by_address)
    - value-based enums (IntEnum / Enum)

    :param byte_value: SysEx byte value
    :param enum_cls: Enum class
    :return: name or "COMMON (0x??)" if not found
    """
    enum_member = None

    if hasattr(enum_cls, "get_parameter_by_address"):
        enum_member = enum_cls.get_parameter_by_address(byte_value)
    else:
        try:
            enum_member = enum_cls(byte_value)
        except (ValueError, TypeError):
            enum_member = None

    return enum_member.name if enum_member else f"COMMON (0x{byte_value:02X})"


def parse_sysex_message(
    message: bytes, enum_cls: Type[SysExEnumProtocol]
) -> Tuple[str, int]:
    """
    Parse a SysEx message and return the name and byte value of the specified parameter.

    :param message: bytes
    :param enum_cls: Enum class (EnumWithAddress or IntEnum with message_position)
    :return: Tuple containing the name and byte value
    """
    byte_value = int(message[enum_cls.message_position()])
    name = parse_sysex_byte(byte_value, enum_cls)
    if name.startswith("COMMON ("):
        name = f"Unknown ({hex(byte_value)})"
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

        JDXi.UI.Theme.apply_debugger_window(self)

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Tab widget: SysEx and CC/PC
        self.tab_widget = QTabWidget()

        # --- SysEx tab ---
        sysex_tab = QWidget()
        sysex_layout = QVBoxLayout(sysex_tab)

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
        sysex_layout.addWidget(splitter)

        self.tab_widget.addTab(sysex_tab, "SysEx")

        # --- CC/PC tab ---
        cc_pc_tab = self._build_cc_pc_panel()
        self.tab_widget.addTab(cc_pc_tab, "CC / PC")

        layout.addWidget(self.tab_widget)
        self.sysex_parser = JDXiSysExParser()

    def _build_cc_pc_panel(self) -> QWidget:
        """Build the CC/PC tab with channel, CC, PC, and Bank+PC controls."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Channel (1–16)
        channel_group = QGroupBox("Channel")
        channel_form = QFormLayout()
        self.cc_pc_channel = QSpinBox()
        self.cc_pc_channel.setRange(1, 16)
        self.cc_pc_channel.setValue(1)
        channel_form.addRow("Channel:", self.cc_pc_channel)
        channel_group.setLayout(channel_form)
        layout.addWidget(channel_group)

        # Control Change
        cc_group = QGroupBox("Control Change")
        cc_layout = QVBoxLayout()
        cc_form = QFormLayout()
        self.cc_controller = QSpinBox()
        self.cc_controller.setRange(0, 127)
        self.cc_controller.setValue(7)
        self.cc_value = QSpinBox()
        self.cc_value.setRange(0, 127)
        self.cc_value.setValue(100)
        cc_form.addRow("Controller:", self.cc_controller)
        cc_form.addRow("Value:", self.cc_value)
        send_cc_btn = QPushButton("Send CC")
        send_cc_btn.clicked.connect(self._send_cc)
        cc_form.addRow("", send_cc_btn)
        cc_layout.addLayout(cc_form)
        cc_ref = QPlainTextEdit()
        cc_ref.setReadOnly(True)
        cc_ref.setMaximumHeight(140)
        cc_ref.setStyleSheet("font-family: monospace; font-size: 10px;")
        cc_ref.setPlainText(
            "CC#  | Name\n"
            "-----+----------------------\n"
            "  1  | Modulation Wheel\n"
            "  7  | Volume\n"
            " 10  | Pan\n"
            " 64  | Sustain Pedal\n"
            " 91  | Reverb\n"
            " 93  | Chorus\n"
            "123  | All Notes Off / All Sound Off"
        )
        cc_layout.addWidget(QLabel("Reference:"))
        cc_layout.addWidget(cc_ref)
        cc_group.setLayout(cc_layout)
        layout.addWidget(cc_group)

        # Program Change
        pc_group = QGroupBox("Program Change")
        pc_form = QFormLayout()
        self.pc_program = QSpinBox()
        self.pc_program.setRange(0, 127)
        self.pc_program.setValue(0)
        pc_form.addRow("Program:", self.pc_program)
        send_pc_btn = QPushButton("Send PC")
        send_pc_btn.clicked.connect(self._send_pc)
        pc_form.addRow("", send_pc_btn)
        pc_group.setLayout(pc_form)
        layout.addWidget(pc_group)

        # Bank Select + Program Change
        bank_group = QGroupBox("Bank Select + Program Change")
        bank_layout = QVBoxLayout()
        bank_form = QFormLayout()
        self.bank_msb = QSpinBox()
        self.bank_msb.setRange(0, 127)
        self.bank_msb.setValue(0)
        self.bank_lsb = QSpinBox()
        self.bank_lsb.setRange(0, 127)
        self.bank_lsb.setValue(0)
        self.bank_program = QSpinBox()
        self.bank_program.setRange(0, 127)
        self.bank_program.setValue(0)
        bank_form.addRow("Bank MSB:", self.bank_msb)
        bank_form.addRow("Bank LSB:", self.bank_lsb)
        bank_form.addRow("Program:", self.bank_program)
        send_bank_btn = QPushButton("Send Bank+PC")
        send_bank_btn.clicked.connect(self._send_bank_pc)
        bank_form.addRow("", send_bank_btn)
        bank_layout.addLayout(bank_form)

        # Quick reference: Bank Select (CC#0, CC#32) + JD-Xi bank mapping
        bank_ref = QPlainTextEdit()
        bank_ref.setReadOnly(True)
        bank_ref.setMaximumHeight(240)
        bank_ref.setStyleSheet("font-family: monospace; font-size: 10px;")
        bank_ref.setPlainText(
            "Bank Select (CC#0, CC#32)\n"
            "Status  2nd byte  3rd byte\n"
            "BnH     00H       mmH     (Bank MSB)\n"
            "BnH     20H       llH     (Bank LSB)\n"
            "n = channel 0-F (ch.1-16), mm/ll = 00-7F (bank 1-16384)\n"
            "* Not received when Receive Bank Select (SysEx) is OFF.\n\n"
            "JD-Xi Bank → Program mapping:\n"
            "MSB LSB   PC       GROUP                    NUMBER\n"
            "----+-----+--------+-------------------------+------\n"
            " 85   0   0-63     User Bank (E)             E01-E64\n"
            " 85   0   64-127   User Bank (F)              F01-F64\n"
            " 85   1   0-63     User Bank (G)              G01-G64\n"
            " 85   1   64-127   User Bank (H)              H01-H64\n"
            "----+-----+--------+-------------------------+------\n"
            " 85  64   0-63     Preset Bank (A)           A01-A64\n"
            " 85  64   64-127   Preset Bank (B)           B01-B64\n"
            " 85  65   0-63     Preset Bank (C)           C01-C64\n"
            " 85  65   64-127   Preset Bank (D)           D01-D64\n"
            "----+-----+--------+-------------------------+------\n"
            " 85  96   0-63    Extra Bank (S)            S01-S64\n"
            " 85  97-103 ...   Extra Banks T-Z            T01-Z64"
        )
        bank_layout.addWidget(QLabel("Reference:"))
        bank_layout.addWidget(bank_ref)
        bank_group.setLayout(bank_layout)
        layout.addWidget(bank_group)

        layout.addStretch()
        return tab

    def _send_cc(self) -> None:
        """Send Control Change from CC/PC tab."""
        if not self.midi_helper or not self.midi_helper.midi_out:
            return
        channel = self.cc_pc_channel.value() - 1  # 1–16 → 0–15
        controller = self.cc_controller.value()
        value = self.cc_value.value()
        success = self.midi_helper.send_control_change(controller, value, channel)
        self._log_cc_pc_result("CC", success, f"ch={channel + 1} cc#{controller}={value}")

    def _send_pc(self) -> None:
        """Send Program Change from CC/PC tab."""
        if not self.midi_helper or not self.midi_helper.midi_out:
            return
        channel = self.cc_pc_channel.value() - 1  # 1–16 → 0–15
        program = self.pc_program.value()
        success = self.midi_helper.send_program_change(program, channel)
        self._log_cc_pc_result("PC", success, f"ch={channel + 1} prog={program}")

    def _send_bank_pc(self) -> None:
        """Send Bank Select + Program Change from CC/PC tab."""
        if not self.midi_helper or not self.midi_helper.midi_out:
            return
        channel = self.cc_pc_channel.value() - 1  # 1–16 → 0–15
        msb = self.bank_msb.value()
        lsb = self.bank_lsb.value()
        program = self.bank_program.value()
        success = self.midi_helper.send_bank_select_and_program_change(channel, msb, lsb, program)
        self._log_cc_pc_result("Bank+PC", success, f"ch={channel + 1} bank={msb}/{lsb} prog={program}")

    def _log_cc_pc_result(self, label: str, success: bool, detail: str) -> None:
        """Log CC/PC send result to the SysEx tab's response log."""
        msg = f"{label} {'OK' if success else 'Failed'}: {detail}"
        self.log_response(msg)

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
        if message[0] != MidiMessage.MIDI_STATUS_MASK or message[1] != 0x41:
            return "Not a Roland address SysEx message"

        def fmt_row(byte, desc, val, notes=""):
            return f"| {byte:<5} | {desc:<28} | {val:<17} | {notes:<30} |\n"

        try:
            sysex_dict = self.sysex_parser.parse_bytes(bytes(message))
            log.parameter("sysex_dict", sysex_dict)

            command_id, command_byte = parse_sysex_message(message, CommandID)
            temporary_area = sysex_dict.get(SysExSection.TEMPORARY_AREA, "Unknown")
            synth_tone = sysex_dict.get(SysExSection.SYNTH_TONE, "Unknown")
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
