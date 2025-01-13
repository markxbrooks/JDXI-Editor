from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QWidget, QTabWidget
)
from PySide6.QtCore import Qt, QTimer
import logging
import os
from pathlib import Path
from PySide6.QtCore import QThread

from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.midi.constants import (
    START_OF_SYSEX, END_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID,
    DT1_COMMAND, DIGITAL_SYNTH_AREA, OSC_PARAM_GROUP, WAVE_SAW,
    WAVE_SQUARE, WAVE_PULSE, WAVE_TRIANGLE, WAVE_SINE, WAVE_NOISE,
    WAVE_SUPER_SAW, WAVE_PCM
)

class LogViewer(BaseEditor):
    """Widget for viewing log messages"""
    
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        
        # Add debug logging
        logging.debug("Initializing LogViewer")
        logging.debug(f"MIDI helper: {midi_helper}")
        
        self.setWindowTitle("MIDI Log")
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        self.setCentralWidget(main_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create log file tab
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.tab_widget.addTab(self.log_text, "Log File")
        
        # Create decoded message tab
        self.decoded_text = QTextEdit()
        self.decoded_text.setReadOnly(True)
        self.tab_widget.addTab(self.decoded_text, "Last Message")
        
        # Create detailed logs tab
        self.detailed_text = QTextEdit()
        self.detailed_text.setReadOnly(True)
        self.tab_widget.addTab(self.detailed_text, "Detailed Logs")
        
        # Create controls layout
        controls = QHBoxLayout()
        main_layout.addLayout(controls)
        
        # Clear button
        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.clicked.connect(self._clear_log)
        controls.addWidget(self.clear_btn)
        
        # Test message button
        test_button = QPushButton("Test MIDI")
        test_button.clicked.connect(self._send_test_message)
        controls.addWidget(test_button)
        
        # Test Preset 1 button
        preset1_button = QPushButton("Test Preset 1")
        preset1_button.clicked.connect(self._send_preset1_messages)
        controls.addWidget(preset1_button)
        
        # Refresh button for detailed logs
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh_detailed_logs)
        controls.addWidget(self.refresh_btn)
        
        controls.addStretch()
        
        # Set up refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._check_log_file)
        self.refresh_timer.start(100)  # Check every 100ms
        
        # Get log file path
        self.log_file = Path.home() / ".jdxi_manager/logs/jdxi_manager.log"
        
        self.last_position = 0
        
        # Load initial detailed logs
        self._refresh_detailed_logs()
        
        # Set window properties
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # Add initial status message
        if self.midi_helper:
            self.append_message("MIDI helper initialized")
        else:
            self.append_message("No MIDI helper available")
            
        logging.debug("LogViewer initialization complete")
        
    def _check_log_file(self):
        """Check for new log messages"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    # Seek to last position
                    f.seek(self.last_position)
                    
                    # Read new lines
                    new_lines = f.readlines()
                    
                    if new_lines:
                        # Update position
                        self.last_position = f.tell()
                        
                        # Add new lines to display
                        for line in new_lines:
                            self.append_message(line.strip())
                            
        except Exception as e:
            logging.error(f"Error reading log file: {str(e)}")
            
    def _refresh_detailed_logs(self):
        """Refresh the detailed logs tab with full log file contents"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    log_contents = f.read()
                    self.log_text.setText(log_contents)
                    
                    # Scroll to bottom
                    scrollbar = self.log_text.verticalScrollBar()
                    scrollbar.setValue(scrollbar.maximum())
                    
        except Exception as e:
            logging.error(f"Error reading detailed logs: {str(e)}")
            self.log_text.setText(f"Error reading log file: {str(e)}")
            
    def append_message(self, message: str):
        """Add message to log with decoded SysEx if applicable"""
        try:
            # Convert hex string to bytes if needed
            if isinstance(message, str) and all(c in '0123456789ABCDEFabcdef ' for c in message.strip()):
                hex_bytes = bytes.fromhex(message.replace(' ', ''))
                if hex_bytes and hex_bytes[0] == START_OF_SYSEX:
                    decoded = self.decode_sysex(hex_bytes)
                    message = f"{message}\n\nDecoded:\n{decoded}"
                    
            self.log_text.append(message)
            
        except Exception as e:
            logging.error(f"Error appending message: {str(e)}")
            self.log_text.append(f"Error processing message: {str(e)}")
            
    def _clear_log(self):
        """Clear log contents"""
        self.log_text.clear()
        self.decoded_text.clear()
        # Don't clear detailed logs as they come from file
        
    def _send_test_message(self):
        """Send test MIDI message"""
        if self.midi_helper:
            # Check MIDI output status
            if not self.midi_helper.midi_out:
                self.append_message("No MIDI output port configured")
                return
            
            if not self.midi_helper.midi_out.is_port_open():
                self.append_message("MIDI output port is not open")
                return
            
            # Try to send test message
            if self.midi_helper.send_test_message():
                self.append_message("Test MIDI message sent successfully")
                self.append_message(f"Using output port: {self.midi_helper.current_out_port}")
            else:
                self.append_message("Failed to send test MIDI message")
                self.append_message("Check MIDI connections and try again")
        else:
            self.append_message("No MIDI helper available")
            self.append_message("Open MIDI Config to set up MIDI ports")
            
    def _send_preset1_messages(self):
        """Send messages to load Preset 1"""
        if not self.midi_helper:
            self.log_text.append("Error: No MIDI helper available")
            return
            
        # Bank/Program setup messages
        messages = [
            # Bank MSB = 95 (SuperNATURAL)
            [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x18, 0x00, 0x20, 0x06, 0x5F, 0x63, 0xF7],
            # Bank LSB = 64 (Preset bank)
            [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x18, 0x00, 0x20, 0x07, 0x40, 0x01, 0xF7],
            # Program number = 0
            [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x18, 0x00, 0x20, 0x08, 0x00, 0x40, 0xF7],
            # Request Common data
            [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x11, 0x19, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x26, 0xF7],
            # Request OSC data
            [0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x11, 0x19, 0x01, 0x20, 0x00, 0x00, 0x00, 0x00, 0x3D, 0x09, 0xF7]
        ]
        
        # Send each message with a small delay
        for msg in messages:
            self.midi_helper.send_message(msg)
            QThread.msleep(20)  # 20ms delay between messages
            
        self.log_text.append("Sent Preset 1 test messages")
        
    def decode_sysex(self, message: bytes) -> str:
        """Decode SysEx message into human-readable format"""
        try:
            if not message or message[0] != START_OF_SYSEX:
                return "Not a SysEx message"

            # Basic message validation
            if len(message) < 8:
                return "Invalid SysEx (too short)"
                
            if message[1] != ROLAND_ID:
                return f"Not a Roland message (ID: {message[1]:02X})"
                
            # Get command type
            command = message[7]
            command_name = {
                0x11: "RQ1 (Request)",
                0x12: "DT1 (Data)",
            }.get(command, f"Unknown ({command:02X})")
            
            # Get area and decode based on type
            area = message[8]
            area_name = {
                0x18: "Program",
                0x19: "Digital Synth 1",
                0x1A: "Digital Synth 2",
            }.get(area, f"Unknown ({area:02X})")
            
            # For Digital Synth parameters
            if area in [0x19, 0x1A]:
                part = message[9]
                group = message[10]
                param = message[11]
                value = message[12]
                
                group_name = {
                    0x20: "OSC",
                    0x21: "FILTER",
                    0x22: "AMP",
                    0x50: "MODIFY"
                }.get(group, f"Unknown ({group:02X})")
                
                # Decode parameter values based on group
                if group == OSC_PARAM_GROUP:
                    wave_name = {
                        WAVE_SAW: "SAW",
                        WAVE_SQUARE: "SQUARE",
                        WAVE_PULSE: "PULSE", 
                        WAVE_TRIANGLE: "TRIANGLE",
                        WAVE_SINE: "SINE",
                        WAVE_NOISE: "NOISE",
                        WAVE_SUPER_SAW: "SUPER SAW",
                        WAVE_PCM: "PCM"
                    }.get(value, f"Unknown ({value:02X})")
                    
                    return (f"Area: {area_name}\n"
                           f"Command: {command_name}\n"
                           f"Part: {part}\n"
                           f"Group: {group_name}\n"
                           f"Parameter: {param:02X}\n"
                           f"Value: {wave_name}")
                else:
                    return (f"Area: {area_name}\n"
                           f"Command: {command_name}\n"
                           f"Part: {part}\n" 
                           f"Group: {group_name}\n"
                           f"Parameter: {param:02X}\n"
                           f"Value: {value:02X}")
                           
            # For Program changes
            elif area == 0x18:
                param = message[11]
                value = message[12]
                param_name = {
                    0x06: "Bank MSB",
                    0x07: "Bank LSB",
                    0x08: "Program Number"
                }.get(param, f"Unknown ({param:02X})")
                
                return (f"Area: {area_name}\n"
                       f"Command: {command_name}\n"
                       f"Parameter: {param_name}\n"
                       f"Value: {value:02X}")
                       
            return f"Unknown message format for area {area:02X}"
            
        except Exception as e:
            logging.error(f"Error decoding SysEx: {str(e)}")
            return f"Error decoding message: {str(e)}"
        
    def closeEvent(self, event):
        """Stop timer when window closes"""
        self.refresh_timer.stop()
        super().closeEvent(event) 