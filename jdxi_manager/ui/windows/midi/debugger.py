import logging
from tabulate import tabulate
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QTextEdit, QLabel, QPlainTextEdit
)
from PySide6.QtCore import Qt

from jdxi_manager.midi.data.constants import (
    START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
    MODEL_ID, JD_XI_HEADER, DT1_COMMAND_12, END_OF_SYSEX,
    DIGITAL_SYNTH_1_AREA, ANALOG_SYNTH_AREA,
    EFFECTS_AREA
)
from jdxi_manager.ui.style import Style
from jdxi_manager.midi.sysex.parsers import parse_sysex


class MIDIDebugger(QMainWindow):
    # SysEx message structure constants
    SYSEX_AREAS = {
        DIGITAL_SYNTH_1_AREA: "Digital Synth Area",
        EFFECTS_AREA: "System Area",
        0x20: "Pattern Area"
    }
    
    COMMANDS = {
        0x11: "RQ1 (Data Request)",
        DT1_COMMAND_12: "DT1 (Data Transfer)"
    }
    
    SECTIONS = {
        0x20: "OSC",
        0x21: "FILTER",
        0x22: "AMP",
        0x23: "LFO",
        0x24: "EFFECTS"
    }
    
    PARAMETERS = {
        0x00: "Wave Type",
        0x01: "Range",
        0x02: "Fine Tune",
        0x03: "Wave Type (OSC2)",
        0x04: "Range (OSC2)",
        0x05: "Fine Tune (OSC2)",
        0x06: "Cutoff",
        0x07: "Resonance",
        0x08: "Key Follow",
        0x13: "Volume",
        0x14: "Key Hold",
        0x15: "Portamento"
    }

    def __init__(self, midi_helper, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        
        # Set window properties
        self.setWindowTitle("MIDI Debugger")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(Style.JDXI_DEBUGGER)
        
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
            synth_str = f"Digital Synth {synth}" if synth in [1, 2] else f"Unknown Synth ({hex(synth)})"

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
                decoded = self._decode_sysex(message)
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
                    self.midi_helper.send_message(message)
                    
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