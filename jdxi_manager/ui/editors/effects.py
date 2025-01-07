from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QGridLayout, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor
import logging

from ...data import FX
from ...midi import MIDIHelper
from ..style import Style
from ..widgets import Slider

class EffectsValidator:
    """Validator for JD-Xi effects parameters"""
    
    # Parameter ranges
    RANGES = {
        # Effect 1 & 2
        (0x50, 0x00): (0, 9),    # Effect type (10 types)
        (0x50, 0x01): (0, 127),  # Level
        (0x50, 0x02): (0, 127),  # Param 1
        (0x50, 0x03): (0, 127),  # Param 2
        (0x60, 0x00): (0, 9),    # Effect type
        (0x60, 0x01): (0, 127),  # Level
        (0x60, 0x02): (0, 127),  # Param 1
        (0x60, 0x03): (0, 127),  # Param 2
        
        # Reverb
        (0x10, 0x00): (0, 5),    # Type (6 types)
        (0x10, 0x01): (0, 127),  # Level
        (0x10, 0x02): (0, 127),  # Time
        (0x10, 0x03): (0, 127),  # Pre-delay
        
        # Delay
        (0x20, 0x00): (0, 1),    # Sync (bool)
        (0x20, 0x01): (0, 127),  # Time
        (0x20, 0x02): (0, 10),   # Note (11 values)
        (0x20, 0x03): (0, 127),  # Feedback
        (0x20, 0x04): (0, 127),  # HF Damp
        (0x20, 0x05): (0, 127),  # Level
        
        # Chorus
        (0x30, 0x00): (0, 127),  # Rate
        (0x30, 0x01): (0, 127),  # Depth
        (0x30, 0x02): (0, 127),  # Level
        
        # Master EQ
        (0x40, 0x00): (0, 24),   # Low (-12 to +12)
        (0x40, 0x01): (0, 24),   # Mid (-12 to +12)
        (0x40, 0x02): (0, 24),   # High (-12 to +12)
        (0x40, 0x03): (0, 127),  # Master Level
    }
    
    @classmethod
    def validate_parameter(cls, section, parameter, value):
        """Validate a parameter value"""
        # Check section range
        if section not in [0x50, 0x60, 0x10, 0x20, 0x30, 0x40]:
            raise ValueError(f"Invalid section: {hex(section)}")
            
        # Get parameter range
        param_range = cls.RANGES.get((section, parameter))
        if param_range is None:
            raise ValueError(f"Invalid parameter {hex(parameter)} for section {hex(section)}")
            
        # Check value range
        min_val, max_val = param_range
        if not min_val <= value <= max_val:
            raise ValueError(f"Value {value} out of range ({min_val}-{max_val})")
            
        return True

    @classmethod
    def validate_power_message(cls, section, value):
        """Validate effect power message"""
        # Check section is valid effect
        if section not in [0x08, 0x09, 0x0A]:  # Reverb, Delay, Chorus
            raise ValueError(f"Invalid effect section: {hex(section)}")
            
        # Check value is boolean
        if value not in [0, 1]:
            raise ValueError(f"Invalid power value: {value} (must be 0 or 1)")
            
        return True

class EffectsEditor(QMainWindow):
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
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create sections
        effect1 = self._create_effect_section(1)
        effect2 = self._create_effect_section(2)
        reverb = self._create_reverb_section()
        delay = self._create_delay_section()
        chorus = self._create_chorus_section()
        master = self._create_master_section()
        
        # Create container for sections with separators
        sections_layout = QVBoxLayout()
        
        # Top row: Effect 1, Effect 2
        effects_row = QHBoxLayout()
        effects_row.addWidget(effect1)
        effects_row.addWidget(effect2)
        sections_layout.addLayout(effects_row)
        
        # Add separator
        sections_layout.addWidget(self._create_separator())
        
        # Middle row: Reverb, Delay
        middle_row = QHBoxLayout()
        middle_row.addWidget(reverb)
        middle_row.addWidget(delay)
        sections_layout.addLayout(middle_row)
        
        # Add separator
        sections_layout.addWidget(self._create_separator())
        
        # Bottom row: Chorus, Master
        bottom_row = QHBoxLayout()
        bottom_row.addWidget(chorus)
        bottom_row.addWidget(master)
        sections_layout.addLayout(bottom_row)
        
        # Add sections layout to main layout
        layout.addLayout(sections_layout)
        
        # Add MIDI parameter bindings
        self._setup_parameter_bindings()
        
    def _create_section_header(self, title, color):
        """Create a colored header for a section"""
        header = QFrame()
        header.setFixedHeight(30)
        header.setAutoFillBackground(True)
        
        palette = header.palette()
        palette.setColor(QPalette.Window, QColor(color))
        header.setPalette(palette)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 0, 10, 0)
        
        label = QLabel(title)
        label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        layout.addWidget(label)
        
        return header
        
    def _create_reverb_section(self):
        """Create reverb controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setMinimumHeight(200)
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with on/off button
        header_layout = QHBoxLayout()
        header = self._create_section_header("Reverb", Style.REVERB_BG)
        header.setFixedWidth(120)  # Make room for button
        header_layout.addWidget(header)
        
        self.reverb_on = QCheckBox("On/Off")
        self.reverb_on.setStyleSheet("QCheckBox { color: white; }")
        header_layout.addWidget(self.reverb_on)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Type selection
        type_frame = QFrame()
        type_layout = QVBoxLayout(type_frame)
        
        type_label = QLabel("Type")
        type_layout.addWidget(type_label)
        
        self.reverb_type = QComboBox()
        self.reverb_type.addItems(FX.REVERB_TYPES)
        type_layout.addWidget(self.reverb_type)
        
        controls.addWidget(type_frame)
        
        # Parameters
        params_frame = QFrame()
        params_layout = QVBoxLayout(params_frame)
        
        self.reverb_level = Slider("Level", 0, 127, 
            display_format=lambda v: f"{v:3d}")
        self.reverb_time = Slider("Time", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.reverb_pre_delay = Slider("Pre-Delay", 0, 127,
            display_format=lambda v: f"{v:3d} ms")
        
        params_layout.addWidget(self.reverb_level)
        params_layout.addWidget(self.reverb_time)
        params_layout.addWidget(self.reverb_pre_delay)
        
        controls.addWidget(params_frame)
        layout.addLayout(controls)
        
        return frame
        
    def _create_delay_section(self):
        """Create delay controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setMinimumHeight(200)
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with on/off button
        header_layout = QHBoxLayout()
        header = self._create_section_header("Delay", Style.DELAY_BG)
        header.setFixedWidth(120)  # Make room for button
        header_layout.addWidget(header)
        
        self.delay_on = QCheckBox("On/Off")
        self.delay_on.setStyleSheet("QCheckBox { color: white; }")
        header_layout.addWidget(self.delay_on)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Sync controls
        sync_frame = QFrame()
        sync_layout = QVBoxLayout(sync_frame)
        
        time_layout = QHBoxLayout()
        
        self.delay_sync = QCheckBox("Sync to Tempo")
        self.delay_sync.toggled.connect(self._handle_delay_sync)
        time_layout.addWidget(self.delay_sync)
        
        self.delay_time = Slider("Time", 0, 127,
            display_format=lambda v: f"{v:3d} ms")
        time_layout.addWidget(self.delay_time)
        
        self.delay_note = QComboBox()
        self.delay_note.addItems(FX.DELAY_NOTES)
        self.delay_note.hide()  # Hidden until sync enabled
        time_layout.addWidget(self.delay_note)
        
        sync_layout.addLayout(time_layout)
        controls.addWidget(sync_frame)
        
        # Parameters
        params_frame = QFrame()
        params_layout = QVBoxLayout(params_frame)
        
        self.delay_feedback = Slider("Feedback", 0, 127,
            display_format=lambda v: f"{v:3d}%")
        self.delay_hf_damp = Slider("HF Damp", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.delay_level = Slider("Level", 0, 127,
            display_format=lambda v: f"{v:3d}")
        
        params_layout.addWidget(self.delay_feedback)
        params_layout.addWidget(self.delay_hf_damp)
        params_layout.addWidget(self.delay_level)
        
        controls.addWidget(params_frame)
        layout.addLayout(controls)
        
        return frame

    def _create_chorus_section(self):
        """Create chorus controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setMinimumHeight(200)
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with on/off button
        header_layout = QHBoxLayout()
        header = self._create_section_header("Chorus", Style.CHORUS_BG)
        header.setFixedWidth(120)  # Make room for button
        header_layout.addWidget(header)
        
        self.chorus_on = QCheckBox("On/Off")
        self.chorus_on.setStyleSheet("QCheckBox { color: white; }")
        header_layout.addWidget(self.chorus_on)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Parameters
        params_frame = QFrame()
        params_layout = QVBoxLayout(params_frame)
        
        self.chorus_rate = Slider("Rate", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.chorus_depth = Slider("Depth", 0, 127,
            display_format=lambda v: f"{v:3d}%")
        self.chorus_level = Slider("Level", 0, 127,
            display_format=lambda v: f"{v:3d}")
        
        params_layout.addWidget(self.chorus_rate)
        params_layout.addWidget(self.chorus_depth)
        params_layout.addWidget(self.chorus_level)
        
        controls.addWidget(params_frame)
        layout.addLayout(controls)
        
        return frame
        
    def _create_master_section(self):
        """Create master controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setMinimumHeight(200)  # Set minimum height for uniformity
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Add header
        layout.addWidget(self._create_section_header("Master", Style.MASTER_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # EQ controls
        eq_frame = QFrame()
        eq_layout = QVBoxLayout(eq_frame)
        
        self.eq_low = Slider("Low", -12, 12, center=True,
            display_format=lambda v: f"{v:+3d} dB")
        self.eq_mid = Slider("Mid", -12, 12, center=True,
            display_format=lambda v: f"{v:+3d} dB")
        self.eq_high = Slider("High", -12, 12, center=True,
            display_format=lambda v: f"{v:+3d} dB")
        
        eq_layout.addWidget(self.eq_low)
        eq_layout.addWidget(self.eq_mid)
        eq_layout.addWidget(self.eq_high)
        
        controls.addWidget(eq_frame)
        
        # Master level
        level_frame = QFrame()
        level_layout = QVBoxLayout(level_frame)
        
        self.master_level = Slider("Master Level", 0, 127,
            display_format=lambda v: f"{v:3d}")
        level_layout.addWidget(self.master_level)
        
        controls.addWidget(level_frame)
        layout.addLayout(controls)
        
        return frame
        
    def _handle_delay_sync(self, sync_enabled):
        """Handle delay sync button toggle"""
        self.delay_time.setVisible(not sync_enabled)
        self.delay_note.setVisible(sync_enabled)
        
    def _create_effect_section(self, number):
        """Create effect controls section"""
        # Use different orange for each effect
        color = Style.FX1_BG if number == 1 else Style.FX2_BG
        
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        frame.setMinimumHeight(200)
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Add header with specific color
        layout.addWidget(self._create_section_header(f"Effect {number}", color))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(30)
        
        # Type selection
        type_frame = QFrame()
        type_layout = QVBoxLayout(type_frame)
        type_layout.setSpacing(10)
        
        type_label = QLabel("Type")
        type_layout.addWidget(type_label)
        
        effect_type = QComboBox()
        effect_type.addItems(FX.EFFECT_TYPES)
        effect_type.setMinimumWidth(150)
        type_layout.addWidget(effect_type)
        setattr(self, f"effect{number}_type", effect_type)
        
        controls.addWidget(type_frame)
        
        # Parameters
        params_frame = QFrame()
        params_layout = QVBoxLayout(params_frame)
        params_layout.setSpacing(15)
        
        # Common parameters for all effect types
        level = Slider("Level", 0, 127,
            display_format=lambda v: f"{v:3d}")
        level.setMinimumWidth(200)
        setattr(self, f"effect{number}_level", level)
        
        param1 = Slider("Parameter 1", 0, 127,
            display_format=lambda v: f"{v:3d}")
        param1.setMinimumWidth(200)
        setattr(self, f"effect{number}_param1", param1)
        
        param2 = Slider("Parameter 2", 0, 127,
            display_format=lambda v: f"{v:3d}")
        param2.setMinimumWidth(200)
        setattr(self, f"effect{number}_param2", param2)
        
        params_layout.addWidget(level)
        params_layout.addWidget(param1)
        params_layout.addWidget(param2)
        
        controls.addWidget(params_frame)
        layout.addLayout(controls)
        
        return frame
        
    def _setup_parameter_bindings(self):
        """Set up MIDI parameter bindings"""
        if not self.midi_out:
            return
            
        # Reverb on/off
        self.reverb_on.toggled.connect(self._send_reverb_power)
            
        # Delay on/off
        self.delay_on.toggled.connect(self._send_delay_power)
        
        # Chorus on/off
        self.chorus_on.toggled.connect(self._send_chorus_power)
        
        # Effect 1 parameters
        self.effect1_type.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x50, 0x00, v))
        self.effect1_level.valueChanged.connect(
            lambda v: self._send_parameter(0x50, 0x01, v))
        self.effect1_param1.valueChanged.connect(
            lambda v: self._send_parameter(0x50, 0x02, v))
        self.effect1_param2.valueChanged.connect(
            lambda v: self._send_parameter(0x50, 0x03, v))
            
        # Effect 2 parameters
        self.effect2_type.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x60, 0x00, v))
        self.effect2_level.valueChanged.connect(
            lambda v: self._send_parameter(0x60, 0x01, v))
        self.effect2_param1.valueChanged.connect(
            lambda v: self._send_parameter(0x60, 0x02, v))
        self.effect2_param2.valueChanged.connect(
            lambda v: self._send_parameter(0x60, 0x03, v))
            
        # Reverb parameters
        self.reverb_type.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x10, 0x00, v))
        self.reverb_level.valueChanged.connect(
            lambda v: self._send_parameter(0x10, 0x01, v))
        self.reverb_time.valueChanged.connect(
            lambda v: self._send_parameter(0x10, 0x02, v))
        self.reverb_pre_delay.valueChanged.connect(
            lambda v: self._send_parameter(0x10, 0x03, v))
            
        # Delay parameters
        self.delay_sync.toggled.connect(
            lambda v: self._send_parameter(0x20, 0x00, int(v)))
        self.delay_time.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x01, v))
        self.delay_note.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x20, 0x02, v))
        self.delay_feedback.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x03, v))
        self.delay_hf_damp.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x04, v))
        self.delay_level.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x05, v))
            
        # Chorus parameters
        self.chorus_rate.valueChanged.connect(
            lambda v: self._send_parameter(0x30, 0x00, v))
        self.chorus_depth.valueChanged.connect(
            lambda v: self._send_parameter(0x30, 0x01, v))
        self.chorus_level.valueChanged.connect(
            lambda v: self._send_parameter(0x30, 0x02, v))
            
        # Master parameters
        self.eq_low.valueChanged.connect(
            lambda v: self._send_parameter(0x40, 0x00, v + 12))  # Convert -12-+12 to 0-24
        self.eq_mid.valueChanged.connect(
            lambda v: self._send_parameter(0x40, 0x01, v + 12))
        self.eq_high.valueChanged.connect(
            lambda v: self._send_parameter(0x40, 0x02, v + 12))
        self.master_level.valueChanged.connect(
            lambda v: self._send_parameter(0x40, 0x03, v))
            
    def _send_parameter(self, section, parameter, value):
        """Send parameter change to synth"""
        if not self.midi_out:
            return
            
        try:
            # Validate parameter
            EffectsValidator.validate_parameter(section, parameter, value)
            
            msg = MIDIHelper.create_parameter_message(0x16, section, parameter, value)
            self.midi_out.send_message(msg)
            
            # Log the MIDI message
            section_names = {
                0x50: "Effect 1",
                0x60: "Effect 2",
                0x10: "Reverb",
                0x20: "Delay",
                0x30: "Chorus",
                0x40: "Master"
            }
            
            param_names = {
                0x00: "Type/Sync",
                0x01: "Level/Time",
                0x02: "Parameter 1/Note",
                0x03: "Parameter 2/Feedback",
                0x04: "HF Damp",
                0x05: "Level"
            }
            
            section_name = section_names.get(section, hex(section))
            param_name = param_names.get(parameter, hex(parameter))
            
            logging.info(f"MIDI: {section_name} - {param_name} = {value}")
            logging.debug(f"Raw MIDI: hex = {' '.join([hex(b) for b in msg])}")
            logging.debug(f"Raw MIDI: dec = {' '.join([str(b) for b in msg])}")
            
        except ValueError as e:
            logging.error(f"Parameter validation failed: {str(e)}")
        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")

    def _request_patch_data(self):
        """Request current patch data from synth"""
        if self.midi_out:
            # Request all effects parameters
            addr = bytes([0x16, 0x00, 0x00, 0x00])
            msg = MIDIHelper.create_sysex_message(addr, bytes([0x00]))
            self.midi_out.send_message(msg)
            
            # Log request message
            logging.debug(f"Request MIDI: hex = {' '.join([hex(b) for b in msg])}")
            logging.debug(f"Request MIDI: dec = {' '.join([str(b) for b in msg])}")
            
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
                
                # Log received MIDI data
                logging.debug(f"MIDI IN: hex = {' '.join([hex(b) for b in data])}")
                logging.debug(f"MIDI IN: dec = {' '.join([str(b) for b in data])}")
                
                # Queue UI update on main thread
                QTimer.singleShot(0, lambda: self._update_ui_from_sysex(addr, param_data))
                
    def _update_ui_from_sysex(self, addr, data):
        """Update UI controls based on received SysEx data"""
        try:
            # Check for reverb power message
            if (addr[0] == 0x18 and addr[1] == 0x00 and 
                addr[2] == 0x08 and addr[3] == 0x00):
                self.reverb_on.setChecked(bool(data[0]))
                return
                
            # Check for delay power message
            if (addr[0] == 0x18 and addr[1] == 0x00 and 
                addr[2] == 0x09 and addr[3] == 0x00):
                self.delay_on.setChecked(bool(data[0]))
                return
                
            # Check for chorus power message
            if (addr[0] == 0x18 and addr[1] == 0x00 and 
                addr[2] == 0x0A and addr[3] == 0x00):
                self.chorus_on.setChecked(bool(data[0]))
                return
                
            # Effect 1 parameters (0x50)
            if addr[0] == 0x50:
                if addr[1] == 0x00:
                    self.effect1_type.setCurrentIndex(data[0])
                elif addr[1] == 0x01:
                    self.effect1_level.setValue(data[0])
                elif addr[1] == 0x02:
                    self.effect1_param1.setValue(data[0])
                elif addr[1] == 0x03:
                    self.effect1_param2.setValue(data[0])
                    
            # Effect 2 parameters (0x60)
            elif addr[0] == 0x60:
                if addr[1] == 0x00:
                    self.effect2_type.setCurrentIndex(data[0])
                elif addr[1] == 0x01:
                    self.effect2_level.setValue(data[0])
                elif addr[1] == 0x02:
                    self.effect2_param1.setValue(data[0])
                elif addr[1] == 0x03:
                    self.effect2_param2.setValue(data[0])
                    
            # Reverb parameters (0x10)
            elif addr[0] == 0x10:
                if addr[1] == 0x00:
                    self.reverb_type.setCurrentIndex(data[0])
                elif addr[1] == 0x01:
                    self.reverb_level.setValue(data[0])
                elif addr[1] == 0x02:
                    self.reverb_time.setValue(data[0])
                elif addr[1] == 0x03:
                    self.reverb_pre_delay.setValue(data[0])
                    
            # Delay parameters (0x20)
            elif addr[0] == 0x20:
                if addr[1] == 0x00:
                    self.delay_sync.setChecked(bool(data[0]))
                elif addr[1] == 0x01:
                    self.delay_time.setValue(data[0])
                elif addr[1] == 0x02:
                    self.delay_note.setCurrentIndex(data[0])
                elif addr[1] == 0x03:
                    self.delay_feedback.setValue(data[0])
                elif addr[1] == 0x04:
                    self.delay_hf_damp.setValue(data[0])
                elif addr[1] == 0x05:
                    self.delay_level.setValue(data[0])
                    
            # Chorus parameters (0x30)
            elif addr[0] == 0x30:
                if addr[1] == 0x00:
                    self.chorus_rate.setValue(data[0])
                elif addr[1] == 0x01:
                    self.chorus_depth.setValue(data[0])
                elif addr[1] == 0x02:
                    self.chorus_level.setValue(data[0])
                    
            # Master parameters (0x40)
            elif addr[0] == 0x40:
                if addr[1] == 0x00:
                    self.eq_low.setValue(data[0] - 12)  # Convert 0-24 to -12-+12
                elif addr[1] == 0x01:
                    self.eq_mid.setValue(data[0] - 12)
                elif addr[1] == 0x02:
                    self.eq_high.setValue(data[0] - 12)
                elif addr[1] == 0x03:
                    self.master_level.setValue(data[0])
                    
        except Exception as e:
            logging.error(f"Error updating UI from SysEx: {str(e)}") 

    def _send_reverb_power(self, on):
        """Send reverb power on/off command"""
        try:
            # Validate power message
            EffectsValidator.validate_power_message(0x08, int(on))
            
            if not self.midi_out:
                return
            
            # Build message with correct format for reverb power
            msg = bytes([
                0xF0, 0x41, 0x10,             # SysEx header
                0x00, 0x00, 0x00,             # Model ID
                0x0E,                         # JD-Xi ID
                0x12,                         # DT1 Command
                0x18, 0x00, 0x08, 0x00,       # Address
                0x01 if on else 0x00,         # Value (1=on, 0=off)
                0x5F if on else 0x60,         # Checksum
                0xF7                          # End of SysEx
            ])
            
            self.midi_out.send_message(msg)
            logging.debug(f"Reverb power {'on' if on else 'off'}")
            logging.debug(f"Raw MIDI: hex = {' '.join([hex(b) for b in msg])}")
            logging.debug(f"Raw MIDI: dec = {' '.join([str(b) for b in msg])}")
            
        except Exception as e:
            logging.error(f"Error sending reverb power: {str(e)}") 

    def _send_delay_power(self, on):
        """Send delay power on/off command"""
        if not self.midi_out:
            return
            
        try:
            # Build message with correct format for delay power
            msg = bytes([
                0xF0, 0x41, 0x10,             # SysEx header
                0x00, 0x00, 0x00,             # Model ID
                0x0E,                         # JD-Xi ID
                0x12,                         # DT1 Command
                0x18, 0x00, 0x09, 0x00,       # Address (0x09 for delay)
                0x01 if on else 0x00,         # Value (1=on, 0=off)
                0x5E if on else 0x5F,         # Checksum
                0xF7                          # End of SysEx
            ])
            
            self.midi_out.send_message(msg)
            logging.debug(f"Delay power {'on' if on else 'off'}")
            logging.debug(f"Raw MIDI: hex = {' '.join([hex(b) for b in msg])}")
            logging.debug(f"Raw MIDI: dec = {' '.join([str(b) for b in msg])}")
            
        except Exception as e:
            logging.error(f"Error sending delay power: {str(e)}") 

    def _send_chorus_power(self, on):
        """Send chorus power on/off command"""
        if not self.midi_out:
            return
            
        try:
            # Build message with correct format for chorus power
            msg = bytes([
                0xF0, 0x41, 0x10,             # SysEx header
                0x00, 0x00, 0x00,             # Model ID
                0x0E,                         # JD-Xi ID
                0x12,                         # DT1 Command
                0x18, 0x00, 0x0A, 0x00,       # Address (0x0A for chorus)
                0x01 if on else 0x00,         # Value (1=on, 0=off)
                0x5D if on else 0x5E,         # Checksum
                0xF7                          # End of SysEx
            ])
            
            self.midi_out.send_message(msg)
            logging.debug(f"Chorus power {'on' if on else 'off'}")
            logging.debug(f"Raw MIDI: hex = {' '.join([hex(b) for b in msg])}")
            logging.debug(f"Raw MIDI: dec = {' '.join([str(b) for b in msg])}")
            
        except Exception as e:
            logging.error(f"Error sending chorus power: {str(e)}") 

    def _create_separator(self):
        """Create a red separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(2)
        separator.setStyleSheet(f"""
            QFrame {{
                background-color: {Style.RED};
                margin: 10px 0px;
            }}
        """)
        return separator 