from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QTextEdit, QLabel, QPlainTextEdit
)
from PySide6.QtCore import Qt
import logging
from jdxi_manager.midi.constants import (
    START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
    MODEL_ID, JD_XI_ID, DT1_COMMAND_12, END_OF_SYSEX,
    DIGITAL_SYNTH_AREA, ANALOG_SYNTH_AREA, TEMPORARY_DRUM_KIT_AREA,
    EFFECTS_AREA
)
from jdxi_manager.ui.style import Style


class MIDIDebugger(QMainWindow):
    # SysEx message structure constants
    SYSEX_AREAS = {
        DIGITAL_SYNTH_AREA: "Digital Synth Area",
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
        # self.setStyleSheet(Style.EDITOR_STYLE)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E2E2E;
            }
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-family: 'Myriad Pro';
            }
            QPlainTextEdit {
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Consolas';
            }
            QTextEdit {
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Consolas';
            }
            QPushButton {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: 1px solid #FF0000;
                border-radius: 3px;
                padding: 5px 15px;
                font-family: 'Myriad Pro';
            }
            QPushButton:hover {
                background-color: #4D4D4D;
                border: 1px solid #FF3333;
            }
            QPushButton:pressed {
                background-color: #2D2D2D;
            }
        """)
        
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
        
        # Add widgets to splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        
        # Add splitter to main layout
        layout.addWidget(splitter)
        
    def _decode_sysex(self, message):
        """Decode a SysEx message"""
        if len(message) < 8:
            return "Invalid SysEx message (too short)"
            
        if message[0] != 0xF0 or message[1] != 0x41:
            return "Not a Roland SysEx message"
            
        try:
            # Get command type
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
                "| Byte | Description                | Value  | Notes                        |\n"
                "|------|----------------------------|--------|------------------------------|\n"
                f"| 0    | Start of SysEx             | {hex(message[0])}     |                              |\n"
                f"| 1    | Manufacturer ID            | {hex(message[1])}     | Roland                       |\n"
                f"| 2    | Device ID                  | {hex(message[2])}     |                              |\n"
                f"| 3-6  | Model ID                   | {' '.join(hex(x) for x in message[3:7])} |                          |\n"
                f"| 7    | Command ID                 | {hex(command)}     | {command_str}           |\n"
                f"| 8    | Area                       | {hex(area)}     | {area_str}           |\n"
                f"| 9    | Synth                      | {hex(synth)}     | {synth_str}              |\n"
                f"| 10-13| Section                    | {' '.join(hex(x) for x in message[10:14])} | {section_str}          |\n"
                f"| 14-15| Parameter                  | {' '.join(hex(x) for x in message[14:16])}  | {param_str}                    |\n"
                f"| 16   | Value                      | {hex(value)}     | {value} ({hex(value)})                         |\n"
                f"| 17   | End of SysEx               | {hex(message[-1])}     |                              |\n"
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