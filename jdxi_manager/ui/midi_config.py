from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
    QLabel, QPushButton, QFrame, QCheckBox, QGroupBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette, QColor
import logging

from ..midi import MIDIHelper
from .style import Style

class MidiConfigFrame(QDialog):
    portsChanged = Signal(object, object)  # (midi_in, midi_out)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MIDI Configuration")
        self.setFixedSize(400, 390)
        
        # Get available MIDI ports
        self.input_ports = MIDIHelper.get_input_ports()
        self.output_ports = MIDIHelper.get_output_ports()
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Input port selection
        input_group = QGroupBox("MIDI Input")
        input_layout = QVBoxLayout()
        self.input_combo = QComboBox()
        self.input_combo.addItems(self.input_ports)
        input_layout.addWidget(self.input_combo)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Output port selection
        output_group = QGroupBox("MIDI Output")
        output_layout = QVBoxLayout()
        self.output_combo = QComboBox()
        self.output_combo.addItems(self.output_ports)
        output_layout.addWidget(self.output_combo)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Status section
        status_frame = self._create_section("Status", Style.COM_BG)
        self.status_label = QLabel("Not connected")
        status_frame.layout().addWidget(self.status_label)
        layout.addWidget(status_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.refresh_btn = QPushButton("Refresh Ports")
        self.refresh_btn.clicked.connect(self._refresh_ports)
        button_layout.addWidget(self.refresh_btn)
        
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self._test_connection)
        button_layout.addWidget(self.test_btn)
        
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply_settings)
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
        
        logging.info("MIDI configuration dialog initialized")
        
    def _create_section(self, title, color):
        """Create a section frame with header"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        
        # Header
        header = QFrame()
        header.setFixedHeight(24)
        header.setAutoFillBackground(True)
        
        palette = header.palette()
        # Convert color string to QColor
        palette.setColor(QPalette.Window, QColor(color))
        header.setPalette(palette)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(6, 0, 6, 0)
        
        label = QLabel(title)
        label.setStyleSheet("color: white; font-weight: bold;")
        header_layout.addWidget(label)
        
        layout.addWidget(header)
        return frame
        
    def _refresh_ports(self):
        """Refresh the available MIDI ports"""
        try:
            logging.debug("Refreshing MIDI ports")
            current_in = self.input_combo.currentText()
            current_out = self.output_combo.currentText()
            
            self.input_combo.clear()
            self.output_combo.clear()
            
            in_ports = MIDIHelper.get_input_ports()
            out_ports = MIDIHelper.get_output_ports()
            
            self.input_combo.addItems(in_ports)
            self.output_combo.addItems(out_ports)
            
            # Restore previous selections if still available
            in_idx = self.input_combo.findText(current_in)
            out_idx = self.output_combo.findText(current_out)
            
            if in_idx >= 0:
                self.input_combo.setCurrentIndex(in_idx)
                logging.debug(f"Restored input port: {current_in}")
            else:
                logging.info(f"Previous input port {current_in} no longer available")
                
            if out_idx >= 0:
                self.output_combo.setCurrentIndex(out_idx)
                logging.debug(f"Restored output port: {current_out}")
            else:
                logging.info(f"Previous output port {current_out} no longer available")
                
            self.status_label.setText("Ports refreshed")
            logging.info(f"Found {len(in_ports)} input ports and {len(out_ports)} output ports")
            
        except Exception as e:
            msg = f"Error refreshing ports: {str(e)}"
            logging.error(msg)
            self.status_label.setText(msg)
            
    def _test_connection(self):
        """Test MIDI connection by sending identity request"""
        try:
            port_name = self.output_combo.currentText()
            logging.debug(f"Testing connection to {port_name}")
            
            midi_out = MIDIHelper.open_output(port_name)
            if midi_out:
                try:
                    # Send both standard and Roland-specific identity requests
                    midi_out.send_message(MIDIHelper.create_identity_request())
                    midi_out.send_message(MIDIHelper.create_roland_identity_request())
                    
                    status = "Test messages sent"
                    logging.info(f"Sent test messages to {port_name}")
                finally:
                    midi_out.delete()  # Use delete() instead of close()
            else:
                status = "Could not open output port"
                logging.error(f"Failed to open output port {port_name}")
                
            self.status_label.setText(status)
            
        except Exception as e:
            msg = f"Test failed: {str(e)}"
            logging.error(msg)
            self.status_label.setText(msg)
            
    def _apply_settings(self):
        """Apply the MIDI settings"""
        try:
            in_port = self.input_combo.currentText()
            out_port = self.output_combo.currentText()
            
            logging.debug(f"Opening MIDI ports - In: {in_port}, Out: {out_port}")
            
            midi_in = MIDIHelper.open_input(in_port)
            midi_out = MIDIHelper.open_output(out_port)
            
            if midi_in and midi_out:
                status = "Connected"
                logging.info(f"Successfully connected to {in_port} and {out_port}")
                self.portsChanged.emit(midi_in, midi_out)
                self.accept()
            else:
                status = "Connection failed"
                if not midi_in:
                    logging.error(f"Failed to open input port {in_port}")
                if not midi_out:
                    logging.error(f"Failed to open output port {out_port}")
                    
            self.status_label.setText(status)
            
        except Exception as e:
            msg = f"Connection error: {str(e)}"
            logging.error(msg)
            self.status_label.setText(msg)
            
    def get_settings(self):
        """Get current MIDI settings"""
        return {
            'input_port': self.input_combo.currentText(),
            'output_port': self.output_combo.currentText()
        }
        
    def set_settings(self, settings):
        """Apply saved MIDI settings"""
        if 'input_port' in settings:
            idx = self.input_combo.findText(settings['input_port'])
            if idx >= 0:
                self.input_combo.setCurrentIndex(idx)
                
        if 'output_port' in settings:
            idx = self.output_combo.findText(settings['output_port'])
            if idx >= 0:
                self.output_combo.setCurrentIndex(idx) 

class MIDIConfigDialog(QDialog):
    def __init__(self, input_ports, output_ports, current_in=None, current_out=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MIDI Configuration")
        
        self.input_ports = input_ports
        self.output_ports = output_ports
        self.current_in = current_in
        self.current_out = current_out
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Input port selection
        input_group = QGroupBox("MIDI Input")
        input_layout = QVBoxLayout(input_group)
        
        self.input_combo = QComboBox()
        self.input_combo.addItems(self.input_ports)
        if self.current_in and self.current_in in self.input_ports:
            self.input_combo.setCurrentText(self.current_in)
            
        input_layout.addWidget(self.input_combo)
        layout.addWidget(input_group)
        
        # Output port selection
        output_group = QGroupBox("MIDI Output")
        output_layout = QVBoxLayout(output_group)
        
        self.output_combo = QComboBox()
        self.output_combo.addItems(self.output_ports)
        if self.current_out and self.current_out in self.output_ports:
            self.output_combo.setCurrentText(self.current_out)
            
        output_layout.addWidget(self.output_combo)
        layout.addWidget(output_group)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_input_port(self) -> str:
        """Get selected input port name
        
        Returns:
            Selected input port name or empty string if none selected
        """
        return self.input_combo.currentText()

    def get_output_port(self) -> str:
        """Get selected output port name
        
        Returns:
            Selected output port name or empty string if none selected
        """
        return self.output_combo.currentText()

    def get_settings(self) -> dict:
        """Get all selected settings
        
        Returns:
            Dictionary containing input_port and output_port selections
        """
        return {
            'input_port': self.get_input_port(),
            'output_port': self.get_output_port()
        } 