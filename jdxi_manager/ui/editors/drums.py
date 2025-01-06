from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFrame, QLabel, QPushButton, QComboBox,
    QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor

from ...data import DR
from ...midi import MIDIHelper
from ..style import Style
from ..widgets import Slider

class DrumEditor(QMainWindow):
    def __init__(self, midi_out=None):
        super().__init__()
        self.midi_out = midi_out
        
        # Initialize control lists
        self.level_sliders = []
        self.pan_sliders = []
        self.pitch_sliders = []
        self.decay_sliders = []
        self.drum_buttons = []
        
        # Create UI
        self._create_ui()
        
        # Request current patch data
        self._request_patch_data()
        
    def _create_ui(self):
        # Set window properties
        self.setFixedSize(1246, 710)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        
        # Create sections
        common = self._create_common_section()
        drums = self._create_drums_section()
        fx = self._create_fx_section()
        
        # Add sections to layout
        layout.addWidget(common)
        layout.addWidget(drums)
        layout.addWidget(fx)
        
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
        
    def _create_common_section(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Common", Style.COM_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Volume and Pan
        vol_frame = QFrame()
        vol_frame.setFrameStyle(QFrame.StyledPanel)
        vol_layout = QHBoxLayout(vol_frame)
        self.volume = Slider("Volume", 0, 127)
        self.pan = Slider("Pan", -64, 63, center=True)
        vol_layout.addWidget(self.volume)
        vol_layout.addWidget(self.pan)
        controls.addWidget(vol_frame)
        
        layout.addLayout(controls)
        return frame
        
    def _create_drums_section(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Drums", Style.OSC_BG))
        
        # Create scrollable area for drum pads
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create drum grid
        drum_widget = QWidget()
        grid = QGridLayout(drum_widget)
        grid.setSpacing(10)
        
        # Create drum pads (4x8 grid)
        for row in range(4):
            for col in range(8):
                pad_num = row * 8 + col
                pad = self._create_drum_pad(pad_num)
                grid.addWidget(pad, row, col)
                
        scroll.setWidget(drum_widget)
        layout.addWidget(scroll)
        
        return frame
        
    def _create_drum_pad(self, pad_num):
        """Create a single drum pad with its controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(5)
        
        # Drum name and button
        name_layout = QHBoxLayout()
        name = QLabel(f"Drum {pad_num + 1}")
        button = QPushButton("●")
        button.setCheckable(True)
        button.setFixedSize(30, 30)
        self.drum_buttons.append(button)
        name_layout.addWidget(name)
        name_layout.addWidget(button)
        layout.addLayout(name_layout)
        
        # Controls
        level = Slider("Level", 0, 127)
        pan = Slider("Pan", -64, 63, center=True)
        pitch = Slider("Pitch", -24, 24, center=True)
        decay = Slider("Decay", 0, 127)
        
        self.level_sliders.append(level)
        self.pan_sliders.append(pan)
        self.pitch_sliders.append(pitch)
        self.decay_sliders.append(decay)
        
        layout.addWidget(level)
        layout.addWidget(pan)
        layout.addWidget(pitch)
        layout.addWidget(decay)
        
        return frame
        
    def _create_fx_section(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Effects", Style.VCF_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Reverb
        reverb_frame = QFrame()
        reverb_frame.setFrameStyle(QFrame.StyledPanel)
        reverb_layout = QVBoxLayout(reverb_frame)
        reverb_layout.addWidget(QLabel("Reverb"))
        
        self.reverb_type = QComboBox()
        self.reverb_type.addItems(["Room 1", "Room 2", "Stage 1", "Stage 2", "Hall 1", "Hall 2"])
        self.reverb_level = Slider("Level", 0, 127)
        self.reverb_time = Slider("Time", 0, 127)
        
        reverb_layout.addWidget(self.reverb_type)
        reverb_layout.addWidget(self.reverb_level)
        reverb_layout.addWidget(self.reverb_time)
        controls.addWidget(reverb_frame)
        
        # Delay
        delay_frame = QFrame()
        delay_frame.setFrameStyle(QFrame.StyledPanel)
        delay_layout = QVBoxLayout(delay_frame)
        delay_layout.addWidget(QLabel("Delay"))
        
        self.delay_sync = QPushButton("Sync")
        self.delay_sync.setCheckable(True)
        self.delay_time = Slider("Time", 0, 127)
        self.delay_feedback = Slider("Feedback", 0, 127)
        self.delay_level = Slider("Level", 0, 127)
        
        delay_layout.addWidget(self.delay_sync)
        delay_layout.addWidget(self.delay_time)
        delay_layout.addWidget(self.delay_feedback)
        delay_layout.addWidget(self.delay_level)
        controls.addWidget(delay_frame)
        
        layout.addLayout(controls)
        return frame

    def _setup_parameter_bindings(self):
        """Set up MIDI parameter bindings for all controls"""
        # Common parameters
        self.volume.valueChanged.connect(
            lambda v: self._send_parameter(0x01, v))  # Volume
        self.pan.valueChanged.connect(
            lambda v: self._send_parameter(0x02, v + 64))  # Pan
            
        # Drum parameters (for each drum pad)
        for pad_num in range(32):  # 32 drum pads total
            # Level
            self.level_sliders[pad_num].valueChanged.connect(
                lambda v, p=pad_num: self._send_drum_parameter(p, 0x01, v))
                
            # Pan
            self.pan_sliders[pad_num].valueChanged.connect(
                lambda v, p=pad_num: self._send_drum_parameter(p, 0x02, v + 64))
                
            # Pitch
            self.pitch_sliders[pad_num].valueChanged.connect(
                lambda v, p=pad_num: self._send_drum_parameter(p, 0x03, v + 64))
                
            # Decay
            self.decay_sliders[pad_num].valueChanged.connect(
                lambda v, p=pad_num: self._send_drum_parameter(p, 0x04, v))
                
            # Mute button
            self.drum_buttons[pad_num].toggled.connect(
                lambda v, p=pad_num: self._send_drum_parameter(p, 0x05, 1 if v else 0))
                
        # Effects parameters
        # Reverb
        self.reverb_type.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x30, v))
        self.reverb_level.valueChanged.connect(
            lambda v: self._send_parameter(0x31, v))
        self.reverb_time.valueChanged.connect(
            lambda v: self._send_parameter(0x32, v))
            
        # Delay
        self.delay_sync.toggled.connect(
            lambda v: self._send_parameter(0x40, 1 if v else 0))
        self.delay_time.valueChanged.connect(
            lambda v: self._send_parameter(0x41, v))
        self.delay_feedback.valueChanged.connect(
            lambda v: self._send_parameter(0x42, v))
        self.delay_level.valueChanged.connect(
            lambda v: self._send_parameter(0x43, v))
            
    def _send_parameter(self, parameter, value):
        """Send a common parameter change via MIDI"""
        if self.midi_out:
            msg = MIDIHelper.create_parameter_message(
                0x17,  # Drums address
                None,  # No partial for drums
                parameter,
                value
            )
            self.midi_out.send_message(msg)
            
    def _send_drum_parameter(self, pad_num, parameter, value):
        """Send a drum-specific parameter change via MIDI"""
        if self.midi_out:
            # Calculate drum parameter address
            drum_offset = 0x10 + pad_num  # 0x10-0x2F for drums 1-32
            msg = MIDIHelper.create_parameter_message(
                0x17,  # Drums address
                drum_offset,
                parameter,
                value
            )
            self.midi_out.send_message(msg)
            
    def _request_patch_data(self):
        """Request current patch data from synth"""
        if self.midi_out:
            # Request common parameters
            addr = bytes([0x17, 0x00, 0x00, 0x00])
            msg = MIDIHelper.create_sysex_message(addr, bytes([0x00]))
            self.midi_out.send_message(msg)
            
            # Request drum parameters
            for pad_num in range(32):
                addr = bytes([0x17, 0x00, 0x10 + pad_num, 0x00])
                msg = MIDIHelper.create_sysex_message(addr, bytes([0x00]))
                self.midi_out.send_message(msg)
                
            # Request effects parameters
            addr = bytes([0x17, 0x00, 0x30, 0x00])  # Reverb
            msg = MIDIHelper.create_sysex_message(addr, bytes([0x00]))
            self.midi_out.send_message(msg)
            
            addr = bytes([0x17, 0x00, 0x40, 0x00])  # Delay
            msg = MIDIHelper.create_sysex_message(addr, bytes([0x00]))
            self.midi_out.send_message(msg)
            
    def set_midi_ports(self, midi_in, midi_out):
        """Update MIDI port connections"""
        self.midi_in = midi_in
        self.midi_out = midi_out
        
        if midi_in:
            midi_in.set_callback(self._handle_midi_input) 