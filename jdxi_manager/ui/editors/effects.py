from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFrame, QLabel, QPushButton, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor

from ...data import FX
from ...midi import MIDIHelper
from ..style import Style
from ..widgets import Slider

class EffectsEditor(QMainWindow):
    def __init__(self, midi_out=None):
        super().__init__()
        self.midi_out = midi_out
        
        # Create UI
        self._create_ui()
        
        # Request current patch data
        self._request_patch_data()
        
    def _create_ui(self):
        # Set window properties
        self.setFixedSize(740, 610)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        
        # Create sections
        reverb = self._create_reverb_section()
        delay = self._create_delay_section()
        chorus = self._create_chorus_section()
        master = self._create_master_section()
        
        # Add sections to layout
        layout.addWidget(reverb)
        layout.addWidget(delay)
        layout.addWidget(chorus)
        layout.addWidget(master)
        
        # Add MIDI parameter bindings
        self._setup_parameter_bindings()
        
    def _create_section_header(self, title, color):
        """Create a colored header for a section"""
        header = QFrame()
        header.setFixedHeight(24)
        header.setAutoFillBackground(True)
        
        # Set background color
        palette = header.palette()
        palette.setColor(QPalette.Window, QColor(color))
        header.setPalette(palette)
        
        # Add label
        layout = QHBoxLayout(header)
        layout.setContentsMargins(6, 0, 6, 0)
        label = QLabel(title)
        label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(label)
        
        return header
        
    def _create_reverb_section(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Reverb", Style.VCF_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Type selection
        type_frame = QFrame()
        type_frame.setFrameStyle(QFrame.StyledPanel)
        type_layout = QVBoxLayout(type_frame)
        type_layout.addWidget(QLabel("Type"))
        
        self.reverb_type = QComboBox()
        self.reverb_type.addItems([
            "Room 1", "Room 2", "Stage 1", "Stage 2", 
            "Hall 1", "Hall 2", "Plate"
        ])
        type_layout.addWidget(self.reverb_type)
        controls.addWidget(type_frame)
        
        # Parameters
        params_frame = QFrame()
        params_frame.setFrameStyle(QFrame.StyledPanel)
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
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Delay", Style.OSC_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Time controls
        time_frame = QFrame()
        time_frame.setFrameStyle(QFrame.StyledPanel)
        time_layout = QVBoxLayout(time_frame)
        
        self.delay_sync = QPushButton("Sync")
        self.delay_sync.setCheckable(True)
        time_layout.addWidget(self.delay_sync)
        
        self.delay_time = Slider("Time", 0, 127,
            display_format=lambda v: f"{v:3d} ms")
        time_layout.addWidget(self.delay_time)
        
        self.delay_note = QComboBox()
        self.delay_note.addItems([
            "1/32", "1/16T", "1/16", "1/8T", "1/8",
            "1/4T", "1/4", "1/2T", "1/2", "1/1T", "1/1"
        ])
        self.delay_note.setVisible(False)
        time_layout.addWidget(self.delay_note)
        controls.addWidget(time_frame)
        
        # Parameters
        params_frame = QFrame()
        params_frame.setFrameStyle(QFrame.StyledPanel)
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
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Chorus", Style.AMP_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Parameters
        params_frame = QFrame()
        params_frame.setFrameStyle(QFrame.StyledPanel)
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
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Master", Style.COM_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Master EQ
        eq_frame = QFrame()
        eq_frame.setFrameStyle(QFrame.StyledPanel)
        eq_layout = QVBoxLayout(eq_frame)
        eq_layout.addWidget(QLabel("Master EQ"))
        
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
        
        # Master Level
        level_frame = QFrame()
        level_frame.setFrameStyle(QFrame.StyledPanel)
        level_layout = QVBoxLayout(level_frame)
        level_layout.addWidget(QLabel("Master Level"))
        
        self.master_level = Slider("Level", 0, 127,
            display_format=lambda v: f"{v:3d}")
        level_layout.addWidget(self.master_level)
        controls.addWidget(level_frame)
        
        layout.addLayout(controls)
        return frame

    def _setup_parameter_bindings(self):
        """Set up MIDI parameter bindings for all controls"""
        # Reverb parameters
        self.reverb_type.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x10, v))  # Type
        self.reverb_level.valueChanged.connect(
            lambda v: self._send_parameter(0x11, v))  # Level
        self.reverb_time.valueChanged.connect(
            lambda v: self._send_parameter(0x12, v))  # Time
        self.reverb_pre_delay.valueChanged.connect(
            lambda v: self._send_parameter(0x13, v))  # Pre-Delay
            
        # Delay parameters
        self.delay_sync.toggled.connect(
            lambda v: self._send_parameter(0x20, 1 if v else 0))  # Sync
        self.delay_time.valueChanged.connect(
            lambda v: self._send_parameter(0x21, v))  # Time
        self.delay_note.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x22, v))  # Note
        self.delay_feedback.valueChanged.connect(
            lambda v: self._send_parameter(0x23, v))  # Feedback
        self.delay_hf_damp.valueChanged.connect(
            lambda v: self._send_parameter(0x24, v))  # HF Damp
        self.delay_level.valueChanged.connect(
            lambda v: self._send_parameter(0x25, v))  # Level
            
        # Chorus parameters
        self.chorus_rate.valueChanged.connect(
            lambda v: self._send_parameter(0x30, v))  # Rate
        self.chorus_depth.valueChanged.connect(
            lambda v: self._send_parameter(0x31, v))  # Depth
        self.chorus_level.valueChanged.connect(
            lambda v: self._send_parameter(0x32, v))  # Level
            
        # Master EQ parameters
        self.eq_low.valueChanged.connect(
            lambda v: self._send_parameter(0x40, v + 12))  # Low
        self.eq_mid.valueChanged.connect(
            lambda v: self._send_parameter(0x41, v + 12))  # Mid
        self.eq_high.valueChanged.connect(
            lambda v: self._send_parameter(0x42, v + 12))  # High
            
        # Master Level
        self.master_level.valueChanged.connect(
            lambda v: self._send_parameter(0x43, v))  # Level
            
        # Connect delay sync to note visibility
        self.delay_sync.toggled.connect(
            lambda v: self._handle_delay_sync(v))
            
    def _handle_delay_sync(self, sync_enabled):
        """Handle delay sync button toggle"""
        self.delay_time.setVisible(not sync_enabled)
        self.delay_note.setVisible(sync_enabled)
            
    def _send_parameter(self, parameter, value):
        """Send a parameter change via MIDI"""
        if self.midi_out:
            msg = MIDIHelper.create_parameter_message(
                0x16,  # Effects address
                None,  # No partial for effects
                parameter,
                value
            )
            self.midi_out.send_message(msg)
            
    def _request_patch_data(self):
        """Request current patch data from synth"""
        if self.midi_out:
            # Request reverb parameters
            addr = bytes([0x16, 0x00, 0x10, 0x00])
            msg = MIDIHelper.create_sysex_message(addr, bytes([0x00]))
            self.midi_out.send_message(msg)
            
            # Request delay parameters
            addr = bytes([0x16, 0x00, 0x20, 0x00])
            msg = MIDIHelper.create_sysex_message(addr, bytes([0x00]))
            self.midi_out.send_message(msg)
            
            # Request chorus parameters
            addr = bytes([0x16, 0x00, 0x30, 0x00])
            msg = MIDIHelper.create_sysex_message(addr, bytes([0x00]))
            self.midi_out.send_message(msg)
            
            # Request master parameters
            addr = bytes([0x16, 0x00, 0x40, 0x00])
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
        # Check if it's for effects (0x16)
        if addr[0] != 0x16:
            return
            
        # Get section and parameter
        section = addr[2]  # 0x10=reverb, 0x20=delay, 0x30=chorus, 0x40=master
        param = addr[3]
        value = data[0]
        
        # Reverb parameters (0x10)
        if section == 0x10:
            if param == 0x00:  # Type
                self.reverb_type.setCurrentIndex(value)
            elif param == 0x01:  # Level
                self.reverb_level.setValue(value)
            elif param == 0x02:  # Time
                self.reverb_time.setValue(value)
            elif param == 0x03:  # Pre-Delay
                self.reverb_pre_delay.setValue(value)
                
        # Delay parameters (0x20)
        elif section == 0x20:
            if param == 0x00:  # Sync
                self.delay_sync.setChecked(bool(value))
                self._handle_delay_sync(bool(value))
            elif param == 0x01:  # Time
                self.delay_time.setValue(value)
            elif param == 0x02:  # Note
                self.delay_note.setCurrentIndex(value)
            elif param == 0x03:  # Feedback
                self.delay_feedback.setValue(value)
            elif param == 0x04:  # HF Damp
                self.delay_hf_damp.setValue(value)
            elif param == 0x05:  # Level
                self.delay_level.setValue(value)
                
        # Chorus parameters (0x30)
        elif section == 0x30:
            if param == 0x00:  # Rate
                self.chorus_rate.setValue(value)
            elif param == 0x01:  # Depth
                self.chorus_depth.setValue(value)
            elif param == 0x02:  # Level
                self.chorus_level.setValue(value)
                
        # Master parameters (0x40)
        elif section == 0x40:
            if param == 0x00:  # EQ Low
                self.eq_low.setValue(value - 12)  # Convert 0-24 to -12-+12
            elif param == 0x01:  # EQ Mid
                self.eq_mid.setValue(value - 12)
            elif param == 0x02:  # EQ High
                self.eq_high.setValue(value - 12)
            elif param == 0x03:  # Master Level
                self.master_level.setValue(value) 