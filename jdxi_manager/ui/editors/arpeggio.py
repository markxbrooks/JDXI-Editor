from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QCheckBox, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
import logging

from jdxi_manager.data.arp import ARP
from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets import Slider
from jdxi_manager.midi.constants import (
    START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
    MODEL_ID, JD_XI_ID, DT1_COMMAND_12, END_OF_SYSEX,
    DIGITAL_SYNTH_AREA, PART_1, SUBGROUP_ZERO,
    ArpeggioGrid, ArpeggioDuration, ArpeggioMotif, ArpeggioKey,
    SyncNote
)
from jdxi_manager.midi.messages import (
    create_parameter_message,
    create_sysex_message,
    create_patch_load_message,
    create_patch_save_message
)
from jdxi_manager.ui.editors.base_editor import BaseEditor

class ArpeggioEditor(BaseEditor):
    """Editor for JD-Xi arpeggiator settings"""

    # Arpeggiator constants
    MAX_OCTAVE_RANGE = 3
    MAX_ACCENT_RATE = 100
    MAX_SHUFFLE = 100
    
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        
        # Initialize arpeggiator state
        self.is_active = False
        self.current_pattern = 0
        self.current_grid = 0
        self.current_key = ArpeggioKey.C
        
        # Set window properties
        self.setStyleSheet(Style.MAIN_STYLESHEET)
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        self.setWindowTitle("Arpeggiator")
        
        # Create UI
        self._create_ui()
        
        # Request current patch data
        self._request_patch_data()

    def toggle_arpeggiator(self, enabled: bool):
        """Toggle arpeggiator on/off"""
        try:
            self._send_parameter(0x00, 127 if enabled else 0)
            self.is_active = enabled
            self._update_status_display()
        except Exception as e:
            logging.error(f"Error toggling arpeggiator: {str(e)}")

    def set_key(self, key: ArpeggioKey):
        """Set arpeggiator key"""
        try:
            self._send_parameter(0x20, key)
            self.current_key = key
            self._update_status_display()
        except Exception as e:
            logging.error(f"Error setting key: {str(e)}")

    def set_pattern(self, pattern_type: ArpeggioMotif):
        """Set arpeggio pattern type"""
        try:
            self._send_parameter(0x01, pattern_type)
            self.current_pattern = pattern_type
            self._update_pattern_display()
        except Exception as e:
            logging.error(f"Error setting pattern: {str(e)}")

    def set_grid(self, grid: ArpeggioGrid):
        """Set arpeggio grid/timing"""
        try:
            self._send_parameter(0x12, grid)
            self.current_grid = grid
            self._update_timing_display()
        except Exception as e:
            logging.error(f"Error setting grid: {str(e)}")

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
        """Send parameter change with validation"""
        if self._validate_parameters(parameter, value):
            super()._send_parameter(DIGITAL_SYNTH_AREA, parameter, value)
        else:
            logging.warning(f"Invalid parameter value: param={parameter} value={value}")
            
    def _request_patch_data(self):
        """Request current patch data from device"""
        try:
            self._send_sysex(
                bytes([0x15, 0x00, 0x00, 0x00]),  # Arpeggio area
                bytes([0x00])  # Request all parameters
            )
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

    def _update_ui_from_sysex(self, addr: bytes, data: bytes):
        """Update UI based on received SysEx data"""
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
        """Update pattern visualization"""
        # Get pattern info
        pattern_type = self.pattern_type.currentIndex()
        octave_range = self.octave_range.value()
        accent_rate = self.accent_rate.value()
        
        # Update pattern display widget
        self.pattern_display.set_pattern(pattern_type, octave_range, accent_rate)
        
        # Update info display
        pattern_name = self.pattern_type.currentText()
        self.pattern_info.setText(
            f"Pattern: {pattern_name}\n"
            f"Octave Range: {octave_range}\n"
            f"Accent Rate: {accent_rate}%"
        )

    def _update_timing_display(self):
        """Update timing display"""
        # Get timing info
        is_sync = self.sync.isChecked()
        rate = self.note.currentText() if is_sync else f"{self.rate.value()} BPM"
        duration = self.duration.value()
        shuffle = self.shuffle.value()
        
        # Update timing display
        self.timing_info.setText(
            f"Sync: {'ON' if is_sync else 'OFF'}\n"
            f"Rate: {rate}\n"
            f"Duration: {duration}%\n"
            f"Shuffle: {shuffle}%"
        )

    def _validate_parameters(self, param: int, value: int) -> bool:
        """Validate parameter values"""
        if param == 0x02:  # Octave Range
            return 0 <= value <= self.MAX_OCTAVE_RANGE
        elif param == 0x03:  # Accent Rate
            return 0 <= value <= self.MAX_ACCENT_RATE
        elif param == 0x14:  # Shuffle
            return 0 <= value <= self.MAX_SHUFFLE
        return True  # Other parameters use standard MIDI range (0-127)

    def _create_status_section(self):
        """Create arpeggiator status section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        header = QLabel("Status")
        header.setStyleSheet(f"background-color: {Style.HEADER_BG}; color: white; padding: 5px;")
        layout.addWidget(header)
        
        # Create status display
        self.status_display = QLabel()
        self.status_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_display)
        
        # Create enable button
        self.enable_button = QPushButton("Enable")
        self.enable_button.setCheckable(True)
        self.enable_button.toggled.connect(self.toggle_arpeggiator)
        layout.addWidget(self.enable_button)
        
        return frame

    def _update_status_display(self):
        """Update status display"""
        status = "ON" if self.is_active else "OFF"
        key = self.current_key.name if hasattr(self.current_key, 'name') else str(self.current_key)
        self.status_display.setText(f"Status: {status}\nKey: {key}")

    def _init_pattern_section(self):
        """Initialize pattern section controls"""
        # Add motif types
        motif_types = [
            "Up (L)", "Up (L&H)", "Up (_)",
            "Down (L)", "Down (L&H)", "Down (_)",
            "Up/Down (L)", "Up/Down (L&H)", "Up/Down (_)",
            "Random (L)", "Random (_)", "Phrase"
        ]
        self.pattern_type.addItems(motif_types)
        self.pattern_type.currentIndexChanged.connect(
            lambda v: self._send_parameter(ArpeggioMotif.UP_L + v)
        )

        # Add grid values
        grid_values = [
            "1/4", "1/8", "1/8 L", "1/8 H", "1/12",
            "1/16", "1/16 L", "1/16 H", "1/24"
        ]
        self.grid_combo.addItems(grid_values)
        self.grid_combo.currentIndexChanged.connect(
            lambda v: self._send_parameter(ArpeggioGrid.QUARTER + v)
        )

        # Add duration values
        duration_values = [
            "30%", "40%", "50%", "60%", "70%",
            "80%", "90%", "100%", "120%", "Full"
        ]
        self.duration_combo.addItems(duration_values)
        self.duration_combo.currentIndexChanged.connect(
            lambda v: self._send_parameter(ArpeggioDuration.D_30 + v)
        ) 

    def _request_patch_name(self, preset_num: int):
        """Request patch name from device"""
        # Arpeggiator doesn't have patch names
        pass 