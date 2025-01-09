import logging

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

from ...data.arp import ARP  # Import ARP class directly
from ...midi import MIDIHelper, MIDIConnection
from ..style import Style
from ..widgets import Slider

class ArpeggioEditor(QMainWindow):
    def __init__(self, midi_out=None, parent=None):
        super().__init__(parent)
        self.main_window = parent
        
        # Set window properties
        self.setStyleSheet(Style.DARK_THEME)
        self.setFixedWidth(400)
        self.setMinimumHeight(500)
        
        # Create UI
        self._create_ui()
        
        # Set up parameter bindings
        self._setup_parameter_bindings()
        
        # Request current patch data
        self._request_patch_data()

    def _create_ui(self):
        """Create the user interface"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        
        # Pattern section
        pattern = self._create_pattern_section()
        layout.addWidget(pattern)
        
        # Timing section
        timing = self._create_timing_section()
        layout.addWidget(timing)
        
        # Add MIDI parameter bindings
        self._setup_parameter_bindings()
        
    def _create_section_header(self, title, color):
        """Create a colored header for a section"""
        header = QFrame()
        header.setFixedHeight(24)
        header.setAutoFillBackground(True)
        
        palette = header.palette()
        palette.setColor(QPalette.Window, QColor(color))
        header.setPalette(palette)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(6, 0, 6, 0)
        
        label = QLabel(title)
        label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(label)
        
        return header
        
    def _create_pattern_section(self):
        """Create pattern controls section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # Add header
        layout.addWidget(self._create_section_header("Pattern", Style.ARP_BG))
        
        # Pattern type dropdown
        pattern_row = QHBoxLayout()
        pattern_label = QLabel("Pattern")
        self.pattern_type = QComboBox()
        self.pattern_type.addItems(ARP.PATTERNS)  # Use patterns from ARP class
        pattern_row.addWidget(pattern_label)
        pattern_row.addWidget(self.pattern_type)
        layout.addLayout(pattern_row)
        
        # Octave range slider
        self.octave_range = Slider("Octave Range", 0, 3)
        layout.addWidget(self.octave_range)
        
        # Accent rate slider
        self.accent_rate = Slider("Accent Rate", 0, 100)
        layout.addWidget(self.accent_rate)
        
        return section
        
    def _create_timing_section(self):
        """Create timing controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        
        # Add header
        layout.addWidget(self._create_section_header("Timing", Style.ARP_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Sync controls
        sync_frame = QFrame()
        sync_layout = QVBoxLayout(sync_frame)
        
        self.sync = QCheckBox("Sync to Tempo")
        self.sync.toggled.connect(self._handle_sync)
        sync_layout.addWidget(self.sync)
        
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.sync)
        
        self.rate = Slider("Rate", 0, 127,
            display_format=lambda v: f"{v:3d}")
        time_layout.addWidget(self.rate)
        
        self.note = QComboBox()
        self.note.addItems(ARP.NOTE_VALUES)
        self.note.hide()  # Hidden until sync enabled
        time_layout.addWidget(self.note)
        
        sync_layout.addLayout(time_layout)
        controls.addWidget(sync_frame)
        
        # Parameters
        params_frame = QFrame()
        params_layout = QVBoxLayout(params_frame)
        
        self.duration = Slider("Duration", 0, 100,
            display_format=lambda v: f"{v:d}%")
        self.shuffle = Slider("Shuffle", 0, 100,
            display_format=lambda v: f"{v:d}%")
        
        params_layout.addWidget(self.duration)
        params_layout.addWidget(self.shuffle)
        
        controls.addWidget(params_frame)
        layout.addLayout(controls)
        
        return frame
        
    def _handle_sync(self, sync_enabled):
        """Handle sync button toggle"""
        self.rate.setVisible(not sync_enabled)
        self.note.setVisible(sync_enabled)
        
    def _setup_parameter_bindings(self):
        """Set up MIDI parameter bindings"""
        # Pattern parameters
        self.pattern_type.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x01, v))
        self.octave_range.valueChanged.connect(
            lambda v: self._send_parameter(0x02, v))
        self.accent_rate.valueChanged.connect(
            lambda v: self._send_parameter(0x03, v))
            
        # Timing parameters
        self.sync.toggled.connect(
            lambda v: self._send_parameter(0x10, int(v)))
        self.rate.valueChanged.connect(
            lambda v: self._send_parameter(0x11, v))
        self.note.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x12, v))
        self.duration.valueChanged.connect(
            lambda v: self._send_parameter(0x13, v))
        self.shuffle.valueChanged.connect(
            lambda v: self._send_parameter(0x14, v))
            
    def _send_parameter(self, parameter, value):
        """Send parameter change to JD-Xi"""
        try:
            msg = MIDIHelper.create_parameter_message(
                0x15,        # Arpeggio address
                0x00,        # No part number needed
                parameter,   # Parameter number
                value       # Parameter value (0-127)
            )
            if self.main_window and self.main_window.midi_out:
                self.main_window.midi_out.send_message(msg)
                if hasattr(self.main_window, 'midi_out_indicator'):
                    self.main_window.midi_out_indicator.blink()
                logging.debug(f"Sent MIDI message: {' '.join([hex(b)[2:].upper().zfill(2) for b in msg])}")
            
        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")
            
    def _request_patch_data(self):
        """Request current patch data from synth"""
        try:
            msg = MIDIHelper.create_sysex_message(
                bytes([0x15, 0x00, 0x00, 0x00]),  # Arpeggio address
                bytes([0x00])  # Data
            )
            if self.main_window and self.main_window.midi_out:
                self.main_window.midi_out.send_message(msg)
                if hasattr(self.main_window, 'midi_out_indicator'):
                    self.main_window.midi_out_indicator.blink()
                logging.debug(f"Sent MIDI message: {' '.join([hex(b)[2:].upper().zfill(2) for b in msg])}")
            
        except Exception as e:
            logging.error(f"Error requesting patch data: {str(e)}")

    def _handle_midi_input(self, message, timestamp):
        """Handle incoming MIDI message"""
        try:
            # Validate message is for arpeggiator
            if not self._validate_sysex_message(message):
                return
                
            # Parse parameter values and update UI
            self._update_parameters(message)
            
        except Exception as e:
            logging.error(f"Error handling MIDI input: {str(e)}")

    def _update_ui_from_sysex(self, addr, data):
        """Update UI controls based on received SysEx data"""
        # Check if it's for arpeggio (0x15)
        if addr[0] != 0x15:
            return
            
        param = addr[3]
        value = data[0]
        
        # Pattern parameters
        if param == 0x01:  # Pattern Type
            self.pattern_type.setCurrentIndex(value)
        elif param == 0x02:  # Octave Range
            self.octave_range.setValue(value)
        elif param == 0x03:  # Accent Rate
            self.accent_rate.setValue(value)
            
        # Timing parameters
        elif param == 0x10:  # Sync
            self.sync.setChecked(bool(value))
            self._handle_sync(bool(value))
        elif param == 0x11:  # Rate
            self.rate.setValue(value)
        elif param == 0x12:  # Note
            self.note.setCurrentIndex(value)
        elif param == 0x13:  # Duration
            self.duration.setValue(value)
        elif param == 0x14:  # Shuffle
            self.shuffle.setValue(value) 
            
        # Update pattern display after parameter changes
        if param in (0x01, 0x02, 0x03):
            self._update_pattern_display()
            
    def _update_pattern_display(self):
        """Update the pattern visualization"""
        self.pattern_display.set_pattern(
            self.pattern_type.currentIndex(),
            self.octave_range.value(),
            self.accent_rate.value()
        ) 