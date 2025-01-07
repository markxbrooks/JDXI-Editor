import logging
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

class DrumValidator:
    """Validator for JD-Xi Drum parameters"""
    
    # Parameter ranges for each section
    RANGES = {
        # Common parameters
        'level': (0, 127),
        'pan': (-64, 63),
        'velocity': (0, 127),
        'pitch': (-24, 24),
        'decay': (0, 127),
        'tune': (-50, 50),
        'reverb_send': (0, 127),
        'delay_send': (0, 127),
        'fx_send': (0, 127),
        'attack': (0, 127),
        'release': (0, 127),
        'filter': (0, 127)
    }
    
    # Section offsets
    SECTION_OFFSETS = {
        'kick': 0x00,
        'snare': 0x10,
        'hihat': 0x20,
        'tom': 0x30,
        'cymbal': 0x40,
        'perc': 0x50
    }
    
    @classmethod
    def validate_parameter(cls, section, parameter, value):
        """Validate a parameter value"""
        try:
            # Check section is valid
            if section not in cls.SECTION_OFFSETS:
                raise ValueError(f"Invalid section: {section}")
            
            # Check parameter is valid
            if parameter not in cls.RANGES:
                raise ValueError(f"Invalid parameter: {parameter}")
            
            # Get parameter range
            min_val, max_val = cls.RANGES[parameter]
            
            # Check value is within range
            if not min_val <= value <= max_val:
                raise ValueError(f"Value {value} out of range ({min_val}-{max_val}) for {parameter}")
            
            return True
            
        except Exception as e:
            logging.error(f"Parameter validation failed: {str(e)}")
            return False

class DrumEditor(QMainWindow):
    def __init__(self, midi_out=None):
        super().__init__()
        self.setStyleSheet(Style.DARK_THEME)
        self.midi_out = midi_out
        
        # Set window properties
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        
        # Parameter addresses within each section
        self.param_addresses = {
            'level': 0x00,
            'pan': 0x01,
            'velocity': 0x02,
            'pitch': 0x03,
            'decay': 0x04,
            'tune': 0x05,
            'reverb_send': 0x06,
            'delay_send': 0x07,
            'fx_send': 0x08,
            'attack': 0x09,
            'release': 0x0A,
            'filter': 0x0B
        }
        
        # Initialize control dictionaries for each section
        self.controls = {
            'kick': {},
            'snare': {},
            'hihat': {},
            'tom': {},
            'cymbal': {},
            'percussion': {}
        }
        
        # Create UI
        self._create_ui()
        
        # Setup parameter bindings
        self._setup_parameter_bindings()
        
        # Request current patch data
        self._request_patch_data()
        
    def _create_ui(self):
        """Create the user interface"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(scroll)
        
        # Create main widget
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSpacing(25)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Create drum sections
        kick = self._create_drum_section("Kick", Style.RED)
        snare = self._create_drum_section("Snare", Style.RED)
        hihat = self._create_drum_section("Hi-Hat", Style.RED)
        tom = self._create_drum_section("Tom", Style.RED)
        cymbal = self._create_drum_section("Cymbal", Style.RED)
        percussion = self._create_drum_section("Percussion", Style.RED)
        
        # Add sections with separators
        layout.addWidget(kick)
        layout.addWidget(self._create_separator())
        layout.addWidget(snare)
        layout.addWidget(self._create_separator())
        layout.addWidget(hihat)
        layout.addWidget(self._create_separator())
        layout.addWidget(tom)
        layout.addWidget(self._create_separator())
        layout.addWidget(cymbal)
        layout.addWidget(self._create_separator())
        layout.addWidget(percussion)
        
        # Add stretch at the bottom
        layout.addStretch()
        
        # Set the widget to scroll area
        scroll.setWidget(central)
        
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
        """Set up MIDI parameter bindings for all drum sections"""
        # MIDI parameter offsets for each section
        section_offsets = {
            'kick': 0x00,
            'snare': 0x10,
            'hihat': 0x20,
            'tom': 0x30,
            'cymbal': 0x40,
            'percussion': 0x50
        }
        
        # Parameter addresses within each section
        param_addresses = {
            'level': 0x00,
            'pan': 0x01,
            'velocity': 0x02,
            'pitch': 0x03,
            'decay': 0x04,
            'tune': 0x05,
            'reverb_send': 0x06,
            'delay_send': 0x07,
            'fx_send': 0x08,
            'attack': 0x09,
            'release': 0x0A,
            'filter': 0x0B
        }
        
        # Set up bindings for each section
        for section, controls in self.controls.items():
            section_offset = section_offsets[section]
            
            for param, control in controls.items():
                param_addr = param_addresses[param]
                
                # Create closure for parameter values
                def make_callback(section_offset, param_addr, needs_offset=False):
                    def callback(value):
                        if needs_offset:
                            value += 64  # Center around 64 for bipolar parameters
                        self._send_parameter(section_offset, param_addr, value)
                    return callback
                
                # Connect with appropriate value conversion
                if param in ['pan', 'pitch', 'tune']:
                    control.valueChanged.connect(
                        make_callback(section_offset, param_addr, True)
                    )
                else:
                    control.valueChanged.connect(
                        make_callback(section_offset, param_addr)
                    )

    def _send_parameter(self, section_offset, parameter, value):
        """Send a drum parameter change via MIDI"""
        if self.midi_out:
            try:
                # Get section name from offset
                section = next(
                    (name for name, offset in DrumValidator.SECTION_OFFSETS.items() 
                     if offset == section_offset),
                    None
                )
                
                if not section:
                    raise ValueError(f"Invalid section offset: {hex(section_offset)}")
                
                # Get parameter name from address
                param_name = next(
                    (name for name, addr in self.param_addresses.items() 
                     if addr == parameter),
                    None
                )
                
                if not param_name:
                    raise ValueError(f"Invalid parameter address: {hex(parameter)}")
                
                # Validate parameter
                if DrumValidator.validate_parameter(section, param_name, value):
                    msg = MIDIHelper.create_parameter_message(
                        0x19,  # Drums address
                        section_offset,  # Section offset
                        parameter,  # Parameter address
                        value & 0x7F  # Ensure 7-bit value
                    )
                    self.midi_out.send_message(msg)
                    logging.debug(f"Sent drum parameter - Section: {section}, "
                                f"Parameter: {param_name}, Value: {value}")
                else:
                    logging.error(f"Parameter validation failed - Section: {section}, "
                                f"Parameter: {param_name}, Value: {value}")
                    
            except Exception as e:
                logging.error(f"Error sending drum parameter: {str(e)}")
            
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
        # Check if it's for drums (0x18)
        if addr[0] != 0x18:
            return
            
        part = addr[1]    # Drum part number
        param = addr[3]    # Parameter number
        value = data[0]    # Parameter value
        
        try:
            # Update the appropriate control based on part/parameter
            if part < len(self.drum_parts):
                drum_part = self.drum_parts[part]
                if param == 0x00:
                    drum_part.level.setValue(value)
                elif param == 0x01:
                    drum_part.pan.setValue(value - 64)  # Convert 0-127 to -64-+63
                elif param == 0x02:
                    drum_part.tune.setValue(value - 64)  # Convert 0-127 to -64-+63
                # ... etc for other parameters
                
        except Exception as e:
            logging.error(f"Error updating UI from SysEx: {str(e)}") 

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

    def _create_drum_section(self, title, color):
        """Create a section for a drum type"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)  # Match other editors' margins
        
        # Add header
        layout.addWidget(self._create_section_header(title, color))
        layout.addSpacing(10)
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(30)
        
        # Level and Pan
        level_frame = QFrame()
        level_layout = QVBoxLayout(level_frame)
        
        self.level = Slider("Level", 0, 127)
        self.pan = Slider("Pan", -64, 63, center=True)
        self.velocity = Slider("Velocity", 0, 127)
        
        level_layout.addWidget(self.level)
        level_layout.addWidget(self.pan)
        level_layout.addWidget(self.velocity)
        controls.addWidget(level_frame)
        
        # Pitch and Decay
        pitch_frame = QFrame()
        pitch_layout = QVBoxLayout(pitch_frame)
        
        self.pitch = Slider("Pitch", -24, 24, center=True)
        self.decay = Slider("Decay", 0, 127)
        self.tune = Slider("Fine Tune", -50, 50, center=True)
        
        pitch_layout.addWidget(self.pitch)
        pitch_layout.addWidget(self.decay)
        pitch_layout.addWidget(self.tune)
        controls.addWidget(pitch_frame)
        
        # Effects
        fx_frame = QFrame()
        fx_layout = QVBoxLayout(fx_frame)
        
        self.reverb_send = Slider("Reverb Send", 0, 127)
        self.delay_send = Slider("Delay Send", 0, 127)
        self.fx_send = Slider("FX Send", 0, 127)
        
        fx_layout.addWidget(self.reverb_send)
        fx_layout.addWidget(self.delay_send)
        fx_layout.addWidget(self.fx_send)
        controls.addWidget(fx_frame)
        
        # Additional Controls
        extra_frame = QFrame()
        extra_layout = QVBoxLayout(extra_frame)
        
        self.attack = Slider("Attack", 0, 127)
        self.release = Slider("Release", 0, 127)
        self.filter = Slider("Filter", 0, 127)
        
        extra_layout.addWidget(self.attack)
        extra_layout.addWidget(self.release)
        extra_layout.addWidget(self.filter)
        controls.addWidget(extra_frame)
        
        # Store controls in dictionary for this section
        section_key = title.lower().replace('-', '')
        self.controls[section_key] = {
            'level': self.level,
            'pan': self.pan,
            'velocity': self.velocity,
            'pitch': self.pitch,
            'decay': self.decay,
            'tune': self.tune,
            'reverb_send': self.reverb_send,
            'delay_send': self.delay_send,
            'fx_send': self.fx_send,
            'attack': self.attack,
            'release': self.release,
            'filter': self.filter
        }
        
        layout.addLayout(controls)
        return frame 