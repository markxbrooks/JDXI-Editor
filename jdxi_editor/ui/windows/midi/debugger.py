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

import logging
from tabulate import tabulate
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QTextEdit, QLabel, QPlainTextEdit
)
from PySide6.QtCore import Qt

from jdxi_editor.midi.data.address.address import CommandID, MemoryAreaAddress, TemporaryToneAddressOffset, \
    DrumKitAddressOffset
from jdxi_editor.ui.style import JDXIStyle
from jdxi_editor.midi.sysex.parsers import parse_sysex
from jdxi_editor.ui.windows.midi.helpers.debugger import validate_checksum


class MIDIDebugger(QMainWindow):
    # SysEx message structure constants
    SYSEX_AREAS = {
        MemoryAreaAddress.TEMPORARY_TONE: "Temporary Tone",
        MemoryAreaAddress.EFFECTS_AREA: "System Area",
    }

    SYNTHS = {
        TemporaryToneAddressOffset.DIGITAL_PART_1: "DIGITAL_PART_1",
        TemporaryToneAddressOffset.DIGITAL_PART_2: "DIGITAL_PART_2",
        TemporaryToneAddressOffset.ANALOG_PART: "ANALOG_PART",
        TemporaryToneAddressOffset.DRUM_KIT_PART: "DRUM_KIT_PART"
    }

    COMMANDS = {
        CommandID.RQ1: "RQ1 (Data Request)",
        CommandID.DT1: "DT1 (Data Transfer)"
    }

    SECTIONS = {
        DrumKitAddressOffset.COMMON: "COMMON",
        DrumKitAddressOffset.DRUM_KIT_PART_1: "BD1",
        DrumKitAddressOffset.DRUM_KIT_PART_2: "RIM",
        DrumKitAddressOffset.DRUM_KIT_PART_3: "BD2",
     }

    GROUPS = {
        0x20: "OSC_1_GROUP",
        0x21: "OSC_2_GROUP",
        0x22: "FILTER_GROUP",
        0x23: "AMP_GROUP",
        0x24: "LFO_1_GROUP",
        0x25: "LFO_2_GROUP",
        0x26: "EFFECTS_GROUP",
    }

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

    def _decode_sysex_new(self, message):
        """Decode address SysEx message"""
        if len(message) < 8:
            return "Invalid SysEx message (too short)"

        if message[0] != 0xF0 or message[1] != 0x41:
            return "Not a Roland SysEx message"

        try:
            # Use the parse_sysex function to decode the message
            decoded_parameters = parse_sysex(message)
            print(decoded_parameters)

            # Format the output using the decoded parameters
            table_data = [[key, value] for key, value in decoded_parameters.items()]
            decoded = tabulate(table_data, headers=["Parameter", "Value"], tablefmt="grid")
            return decoded

        except Exception as e:
            return f"Error decoding message: {str(e)}"

    def _decode_sysex_15(self, message):
        """Decode address SysEx message"""
        if len(message) != 15:
            return "Invalid SysEx message (must be 15 bytes)"

        if message[0] != 0xF0 or message[1] != 0x41:
            return "Not a Roland address SysEx message"

        try:
            # Get command
            command = message[7]
            command_str = self.COMMANDS.get(command, f"Unknown Command ({hex(command)})")

            # Get area
            area = message[8]
            area_str = self.SYSEX_AREAS.get(area, f"Unknown Area ({hex(area)})")

            # Get synth number
            synth = message[9]
            synth_str = self.SYNTHS.get(synth, f"Unknown Synth ({hex(synth)})")

            # Get parameter address (bytes 10 and 11 separately)
            group = message[10]
            param = message[11]
            group_address = hex(group)
            param_address = hex(param)
            # param_str = DigitalParameter.get_name_by_address(int(param))
            group_str = self.GROUPS.get(group, f"Common Group ({group_address})")
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
                f"| {7:<5} | {'Command ID':<28} | {hex(command):<17} | {command_str:<30} |\n"
                f"| {8:<5} | {'Area':<28} | {hex(area):<17} | {area_str:<30} |\n"
                f"| {9:<5} | {'Synth':<28} | {hex(synth):<17} | {synth_str:<30} |\n"
                f"| {10:<5} | {'Parameter Address High':<28} | {group_address:<17} | {group_str:<30} |\n"
                f"| {11:<5} | {'Parameter Address Low':<28} | {param_address:<17} | {param_str:<30} |\n"
                f"| {12:<5} | {'Parameter Value':<28} | {hex(value):<17} | {value} ({hex(value)}) {'':<22} |\n"
                f"| {13:<5} | {'Checksum':<28} | {hex(checksum):<17} | {'Valid' if checksum_valid else 'Invalid'} {'':<22} |\n"
                f"| {14:<5} | {'End of SysEx':<28} | {hex(message[-1]):<17} | {'':<30} |\n"
                f"|{'-' * 7}|{'-' * 30}|{'-' * 19}|{'-' * 32}|\n"
            )

            return decoded

        except Exception as e:
            return f"Error decoding message: {str(e)}"

    def _decode_sysex(self, message):
        """Decode address SysEx message"""
        if len(message) < 8:
            return "Invalid SysEx message (too short)"

        if message[0] != 0xF0 or message[1] != 0x41:
            return "Not address Roland SysEx message"

        try:
            # Get command preset_type
            command = message[7]
            command_str = self.COMMANDS.get(command, f"Unknown Command ({hex(command)})")

            # Get area
            area = message[8]
            area_str = self.SYSEX_AREAS.get(area, f"Unknown Area ({hex(area)})")

            # Get synth number
            synth = message[9]
            synth_str = self.SYNTHS.get(area, f"Unknown Synth ({hex(synth)})")

            # Get section
            section = message[10]
            section_str = self.SECTIONS.get(section, f"Unknown Section ({hex(section)})")

            # Get parameter
            param = message[11]
            param_str = self.PARAMETERS.get(param, f"Unknown Parameter ({hex(param)})")

            # Get value
            value = message[12]

            # Format the output
            decoded = (
                f"|{'-' * 7}|{'-' * 30}|{'-' * 19}|{'-' * 32}|\n"
                f"| {'Byte':<5} | {'Description':<28} | {'Value':<17} | {'Notes':<30} |\n"
                f"|{'-' * 7}|{'-' * 30}|{'-' * 19}|{'-' * 32}|\n"
                f"| {0:<5} | {'Start of SysEx':<28} | {hex(message[0]):<17} | {'':<30} |\n"
                f"| {1:<5} | {'Manufacturer ID':<28} | {hex(message[1]):<17} | {'Roland':<30} |\n"
                f"| {2:<5} | {'Device ID':<28} | {hex(message[2]):<17} | {'':<30} |\n"
                f"| {'3-6':<5} | {'Model ID':<28} | {' '.join(hex(x) for x in message[3:7]):<17} | {'':<30} |\n"
                f"| {7:<5} | {'Command ID':<28} | {hex(command):<17} | {command_str:<30} |\n"
                f"| {8:<5} | {'Area':<28} | {hex(area):<17} | {area_str:<30} |\n"
                f"| {9:<5} | {'Synth':<28} | {hex(synth):<17} | {synth_str:<30} |\n"
                f"| {'10-13':<5} | {'Section':<28} | {' '.join(hex(x) for x in message[10:14]):<17} | {section_str:<30} |\n"
                f"| {'14-15':<5} | {'Parameter':<28} | {' '.join(hex(x) for x in message[14:16]):<17} | {param_str:<30} |\n"
                f"| {16:<5} | {'Value':<28} | {hex(value):<17} | {value} ({hex(value)}) {'':<22} |\n"
                f"| {17:<5} | {'End of SysEx':<28} | {hex(message[-1]):<17} | {'':<30} |\n"
                f"|{'-' * 7}|{'-' * 30}|{'-' * 19}|{'-' * 32}|\n"
            )

            return decoded

        except Exception as e:
            return f"Error decoding message: {str(e)}"

    def _decode_current(self):
        """Decode the currently entered message"""
        text = self.command_input.toPlainText().strip()
        if not text:
            return
        for line in text.split('\n'):
            try:
                # Convert hex string to bytes
                hex_values = text.split()
                message = [int(x, 16) for x in hex_values]
                # message = bytes(int(byte, 16) for byte in text.split())
                # Decode and display
                decoded = self._decode_sysex_15(message)
                self.decoded_text.append(decoded)

            except ValueError as e:
                self.decoded_text.setText(f"Error parsing hex values: {str(e)}")
            except Exception as e:
                self.decoded_text.setText(f"Error decoding message: {str(e)}")

    def _send_commands(self):
        """Send entered MIDI commands"""
        if not self.midi_helper:
            self.log_response("Error: MIDI helper not initialized")
            return

        if not self.midi_helper.midi_out:
            self.log_response("Error: No MIDI output port available")
            return

        try:
            # Get commands from input
            text = self.command_input.toPlainText().strip()
            if not text:
                return

            # Process each line
            for line in text.split('\n'):
                try:
                    # Split the hex string and convert each value
                    hex_values = line.strip().split()
                    message = []

                    # Debug print
                    self.log_response(f"Converting hex values: {hex_values}")

                    for hex_str in hex_values:
                        # Remove any '0x' prefix if present
                        hex_str = hex_str.replace('0x', '').replace('0X', '')
                        value = int(hex_str, 16)
                        message.append(value)

                    # Debug print the converted message
                    self.log_response(f"Converted to bytes: {[hex(b) for b in message]}")

                    # Send message using MIDIHelper's send_message
                    self.midi_helper.send_raw_message(message)

                    # Log success
                    hex_str = ' '.join([f"{b:02X}" for b in message])
                    self.log_response(f"Successfully sent: {hex_str}")
                    logging.debug(f"Debug window sent MIDI message: {hex_str}")

                except ValueError as e:
                    self.log_response(f"Error parsing hex value in line: {line}\n{str(e)}")
                except Exception as e:
                    self.log_response(f"Error sending message: {line}\n{str(e)}")

        except Exception as e:
            self.log_response(f"Error sending commands: {str(e)}")

    def log_response(self, text):
        """Add text to response log"""
        self.response_log.append(text)

    def handle_midi_response(self, message):
        """Handle incoming MIDI message"""
        try:
            # Convert message to hex string
            hex_str = ' '.join([f"{b:02X}" for b in message])
            self.log_response(f"Received: {hex_str}")

        except Exception as e:
            self.log_response(f"Error handling response: {str(e)}")
