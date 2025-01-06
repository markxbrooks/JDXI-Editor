from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QPushButton,
    QMessageBox
)
from PySide6.QtCore import Signal, Qt, QTimer
import rtmidi
import time

class MidiConfigFrame(QFrame):
    midi_connected = Signal(object, object)  # in_port, out_port
    
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        
        # Initialize MIDI
        self._midi_in = rtmidi.MidiIn()
        self._midi_out = rtmidi.MidiOut()
        self._current_in_port = None
        self._current_out_port = None
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # MIDI Input selection
        in_layout = QHBoxLayout()
        in_label = QLabel("MIDI In:")
        in_label.setFixedWidth(60)
        self.in_combo = QComboBox()
        self.in_combo.currentIndexChanged.connect(self._on_port_changed)
        in_layout.addWidget(in_label)
        in_layout.addWidget(self.in_combo, 1)
        layout.addLayout(in_layout)
        
        # MIDI Output selection
        out_layout = QHBoxLayout()
        out_label = QLabel("MIDI Out:")
        out_label.setFixedWidth(60)
        self.out_combo = QComboBox()
        self.out_combo.currentIndexChanged.connect(self._on_port_changed)
        out_layout.addWidget(out_label)
        out_layout.addWidget(self.out_combo, 1)
        layout.addLayout(out_layout)
        
        # Test and Panic buttons
        btn_layout = QHBoxLayout()
        self.test_btn = QPushButton("Test")
        self.test_btn.clicked.connect(self._test_connection)
        self.test_btn.setEnabled(False)
        
        self.panic_btn = QPushButton("Panic")
        self.panic_btn.clicked.connect(self._send_panic)
        self.panic_btn.setEnabled(False)
        
        btn_layout.addWidget(self.test_btn)
        btn_layout.addWidget(self.panic_btn)
        layout.addLayout(btn_layout)
        
        # Refresh ports initially
        self._refresh_ports()
        
        # Set up periodic port refresh
        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(self._refresh_ports)
        self._refresh_timer.start(1000)  # Refresh every second
        
    def _refresh_ports(self):
        """Refresh the list of available MIDI ports"""
        # Store current selections
        current_in = self.in_combo.currentText()
        current_out = self.out_combo.currentText()
        
        # Input ports
        self.in_combo.clear()
        self.in_combo.addItem("Select MIDI Input...")
        for port in self._midi_in.get_ports():
            self.in_combo.addItem(port)
            
        # Output ports
        self.out_combo.clear()
        self.out_combo.addItem("Select MIDI Output...")
        for port in self._midi_out.get_ports():
            self.out_combo.addItem(port)
            
        # Restore selections if still available
        in_idx = self.in_combo.findText(current_in)
        if in_idx > 0:
            self.in_combo.setCurrentIndex(in_idx)
            
        out_idx = self.out_combo.findText(current_out)
        if out_idx > 0:
            self.out_combo.setCurrentIndex(out_idx)
            
    def _on_port_changed(self):
        """Handle MIDI port selection changes"""
        # Close existing ports
        if self._current_in_port is not None:
            self._current_in_port.close_port()
            self._current_in_port = None
            
        if self._current_out_port is not None:
            self._current_out_port.close_port()
            self._current_out_port = None
        
        # Get selected port indices
        in_idx = self.in_combo.currentIndex() - 1  # -1 to account for "Select" item
        out_idx = self.out_combo.currentIndex() - 1
        
        if in_idx >= 0 and out_idx >= 0:
            try:
                # Open new input port
                self._current_in_port = rtmidi.MidiIn()
                self._current_in_port.open_port(in_idx)
                self._current_in_port.ignore_types(sysex=False)
                
                # Open new output port
                self._current_out_port = rtmidi.MidiOut()
                self._current_out_port.open_port(out_idx)
                
                # Enable buttons
                self.test_btn.setEnabled(True)
                self.panic_btn.setEnabled(True)
                
                # Emit connection signal
                self.midi_connected.emit(self._current_in_port, self._current_out_port)
                
            except rtmidi.InvalidPortError as e:
                QMessageBox.warning(self, "MIDI Error", 
                    f"Failed to open MIDI ports: {str(e)}")
                self._refresh_ports()
        else:
            # Disable buttons if no ports selected
            self.test_btn.setEnabled(False)
            self.panic_btn.setEnabled(False)
            
    def _test_connection(self):
        """Test MIDI connection by sending a note on/off message"""
        if self._current_out_port:
            try:
                # Send note on
                self._current_out_port.send_message([0x90, 60, 100])  # Channel 1, middle C, velocity 100
                time.sleep(0.1)  # Short delay
                # Send note off
                self._current_out_port.send_message([0x80, 60, 0])    # Channel 1, middle C, velocity 0
                
                QMessageBox.information(self, "MIDI Test", 
                    "MIDI test message sent successfully.")
                    
            except Exception as e:
                QMessageBox.warning(self, "MIDI Error",
                    f"Failed to send test message: {str(e)}")
                
    def _send_panic(self):
        """Send MIDI panic (all notes off) message"""
        if self._current_out_port:
            try:
                # Send all notes off on all channels
                for channel in range(16):
                    # Controller 123 = All Notes Off
                    self._current_out_port.send_message([0xB0 + channel, 123, 0])
                    
                QMessageBox.information(self, "MIDI Panic",
                    "All notes off message sent successfully.")
                    
            except Exception as e:
                QMessageBox.warning(self, "MIDI Error",
                    f"Failed to send panic message: {str(e)}")
                
    def closeEvent(self, event):
        """Clean up MIDI ports when closing"""
        if self._current_in_port:
            self._current_in_port.close_port()
        if self._current_out_port:
            self._current_out_port.close_port()
        event.accept() 