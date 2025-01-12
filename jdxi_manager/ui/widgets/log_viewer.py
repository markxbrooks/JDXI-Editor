from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QWidget, QTabWidget
)
from PySide6.QtCore import Qt, QTimer
import logging
import os

from jdxi_manager.ui.editors.base_editor import BaseEditor

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
        # self.detailed_text = QTextEdit()
        # self.detailed_text.setReadOnly(True)
        # self.tab_widget.addTab(self.detailed_text, "Detailed Logs")
        
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
        
        # Refresh button for detailed logs
        refresh_btn = QPushButton("Refresh Logs")
        refresh_btn.clicked.connect(self._refresh_detailed_logs)
        controls.addWidget(refresh_btn)
        
        controls.addStretch()
        
        # Set up refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._check_log_file)
        self.refresh_timer.start(100)  # Check every 100ms
        
        # Get log file path
        self.log_file = parent.log_file

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
            
    def append_message(self, message: str, decoded: bool = False):
        """Add message to log
        
        Args:
            message: Message to add
            decoded: If True, add to decoded tab instead of log tab
        """
        if decoded:
            self.decoded_text.append(message)
            # Scroll to bottom
            scrollbar = self.decoded_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        else:
            self.log_text.append(message)
            # Scroll to bottom
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
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
            
    def closeEvent(self, event):
        """Stop timer when window closes"""
        self.refresh_timer.stop()
        super().closeEvent(event) 