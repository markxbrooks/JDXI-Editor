from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

from ...data import ARP
from ...midi import MIDIHelper
from ..style import Style
from ..widgets import Slider

class ArpeggioEditor(QMainWindow):
    def __init__(self, midi_out=None):
        super().__init__()
        self.setStyleSheet(Style.DARK_THEME)  # Add dark theme
        self.midi_out = midi_out
        
        # Set window properties to match other editors
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        
        # Create UI
        self._create_ui()
        
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
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        
        # Add header
        layout.addWidget(self._create_section_header("Pattern", Style.ARP_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Pattern selection
        pattern_frame = QFrame()
        pattern_layout = QVBoxLayout(pattern_frame)
        
        pattern_label = QLabel("Pattern Type")
        pattern_layout.addWidget(pattern_label)
        
        self.pattern_type = QComboBox()
        self.pattern_type.addItems(ARP.PATTERNS)
        pattern_layout.addWidget(self.pattern_type)
        
        controls.addWidget(pattern_frame)
        
        # Parameters
        params_frame = QFrame()
        params_layout = QVBoxLayout(params_frame)
        
        self.octave_range = Slider("Octave Range", 0, 3,
            display_format=lambda v: f"{v:d}")
        self.accent_rate = Slider("Accent Rate", 0, 100,
            display_format=lambda v: f"{v:d}%")
        
        params_layout.addWidget(self.octave_range)
        params_layout.addWidget(self.accent_rate)
        
        controls.addWidget(params_frame)
        layout.addLayout(controls)
        
        return frame
        
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
        if not self.midi_out:
            return
            
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
        """Send parameter change to synth"""
        if self.midi_out:
            msg = MIDIHelper.create_parameter_message(0x15, None, parameter, value)
            self.midi_out.send_message(msg)
            
    def _request_patch_data(self):
        """Request current patch data from synth"""
        if self.midi_out:
            # Request all arpeggio parameters
            addr = bytes([0x15, 0x00, 0x00, 0x00])
            msg = MIDIHelper.create_sysex_message(addr, bytes([0x00]))
            self.midi_out.send_message(msg)
            
    def set_midi_ports(self, midi_in, midi_out):
        """Update MIDI port connections"""
        self.midi_in = midi_in
        self.midi_out = midi_out
        
        if midi_in:
            midi_in.set_callback(self._handle_midi_input)
            
    def _handle_midi_input(self, message, timestamp):
        """Handle incoming MIDI messages"""
        data = message[0]  # Get the raw MIDI data
        
        # Check if it's a SysEx message
        if data[0] == 0xF0 and len(data) > 8:
            # Verify it's a Roland message for JD-Xi
            if (data[1] == 0x41 and  # Roland ID
                data[4:8] == bytes([0x00, 0x00, 0x00, 0x0E])):  # JD-Xi ID
                
                # Get address and parameter data
                addr = data[8:12]  # 4-byte address
                param_data = data[12:-1]  # Parameter data (excluding F7)
                
                # Queue UI update on main thread
                QTimer.singleShot(0, lambda: self._update_ui_from_sysex(addr, param_data))
                
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