from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QCheckBox, QPushButton,
    QFileDialog, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor
import logging
from pathlib import Path

from ...data import SN1, SN2, DigitalSynth
from ...midi import MIDIHelper
from ..style import Style
from ..widgets import Slider, WaveformButton

class DigitalSynthValidator:
    """Validator for JD-Xi Digital Synth parameters"""
    
    # Parameter ranges
    RANGES = {
        # OSC 1 (0x20)
        (0x20, 0x00): (0, 13),    # Wave Type (0=Saw, 1=Square, 2=Triangle, 3=Noise, 4=Sine, 5=Super Saw, 6-13=PCM)
        (0x20, 0x01): (0, 48),    # Range (-24 to +24, stored as 0-48)
        (0x20, 0x02): (0, 127),   # Color
        
        # OSC 2 (0x20)
        (0x20, 0x10): (0, 13),    # Wave Type (same as OSC 1)
        (0x20, 0x11): (0, 48),    # Range
        (0x20, 0x12): (0, 127),   # Color
        (0x20, 0x13): (0, 100),   # Fine Tune (-50 to +50, stored as 0-100)
        (0x20, 0x20): (0, 127),   # OSC Mix
        
        # Filter (0x21)
        (0x21, 0x00): (0, 127),   # Cutoff
        (0x21, 0x01): (0, 127),   # Resonance
        (0x21, 0x02): (0, 127),   # Key Follow
        (0x21, 0x03): (0, 127),   # Env Depth
        (0x21, 0x10): (0, 127),   # Attack
        (0x21, 0x11): (0, 127),   # Decay
        (0x21, 0x12): (0, 127),   # Sustain
        (0x21, 0x13): (0, 127),   # Release
        
        # Amplifier (0x22)
        (0x22, 0x00): (0, 127),   # Level
        (0x22, 0x01): (0, 127),   # Pan
        (0x22, 0x02): (0, 127),   # Velocity
        (0x22, 0x10): (0, 127),   # Attack
        (0x22, 0x11): (0, 127),   # Decay
        (0x22, 0x12): (0, 127),   # Sustain
        (0x22, 0x13): (0, 127),   # Release
        
        # LFO (0x26)
        (0x26, 0x00): (0, 3),     # LFO1 Wave
        (0x26, 0x01): (0, 127),   # LFO1 Rate
        (0x26, 0x10): (0, 3),     # LFO2 Wave
        (0x26, 0x11): (0, 127),   # LFO2 Rate
        (0x26, 0x20): (0, 127),   # LFO Mix
    }
    
    @classmethod
    def validate_parameter(cls, section, parameter, value):
        """Validate a parameter value"""
        # Check section range
        if section not in [0x20, 0x21, 0x22, 0x26]:
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

class DigitalSynthEditor(QMainWindow):
    def __init__(self, midi_out=None, synth_num=1):
        super().__init__()
        self.setStyleSheet(Style.DARK_THEME)
        self.midi_out = midi_out
        self.synth_num = synth_num
        self.data = SN1 if synth_num == 1 else SN2
        
        # Set window properties - taller with fixed width
        self.setFixedWidth(1000)  # Wider than before
        self.setMinimumHeight(600)  # Minimum height
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create UI
        self._create_ui()
        
        # Request current patch data
        self._request_patch_data()
        
    def _create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        load_action = file_menu.addAction("&Load Patch...")
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self._load_patch)
        
        save_action = file_menu.addAction("&Save Patch...")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_patch)
        
        file_menu.addSeparator()
        
        close_action = file_menu.addAction("&Close")
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close)

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
        layout.setSpacing(25)  # Increased from 15
        layout.setContentsMargins(25, 25, 25, 25)  # Increased from 15
        
        # Create sections
        osc = self._create_oscillator_section()
        vcf = self._create_filter_section()
        amp = self._create_amplifier_section()
        lfo = self._create_lfo_section()
        
        # Add sections to layout with spacing and separators
        layout.addWidget(osc)
        layout.addWidget(self._create_separator())
        layout.addWidget(vcf)
        layout.addWidget(self._create_separator())
        layout.addWidget(amp)
        layout.addWidget(self._create_separator())
        layout.addWidget(lfo)
        
        # Add stretch at the bottom
        layout.addStretch()
        
        # Set the widget to scroll area
        scroll.setWidget(central)
        
        # Add MIDI parameter bindings
        self._setup_parameter_bindings()
        
    def _create_section_header(self, title, color):
        """Create a colored header for a section"""
        header = QFrame()
        header.setFixedHeight(30)  # Increased height
        header.setAutoFillBackground(True)
        
        palette = header.palette()
        palette.setColor(QPalette.Window, QColor(color))
        header.setPalette(palette)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 0, 10, 0)  # Increased margins
        
        label = QLabel(title)
        label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")  # Larger font
        layout.addWidget(label)
        
        return header
        
    def _create_oscillator_section(self):
        """Create oscillator controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)  # Increased from 15
        layout.setContentsMargins(30, 25, 30, 25)  # Increased from 20
        
        # Add header
        layout.addWidget(self._create_section_header("Oscillator", Style.OSC_BG))
        layout.addSpacing(10)  # Add space after header
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(30)  # Increased from 20
        
        # OSC 1
        osc1_frame = QFrame()
        osc1_layout = QVBoxLayout(osc1_frame)
        
        osc1_label = QLabel("OSC 1")
        osc1_layout.addWidget(osc1_label)
        
        self.osc1_wave = WaveformButton()
        osc1_layout.addWidget(self.osc1_wave)
        
        self.osc1_range = Slider("Range", -24, 24, center=True,
            display_format=lambda v: f"{v:+d}")
        self.osc1_color = Slider("Color", 0, 127,
            display_format=lambda v: f"{v:3d}")
        
        osc1_layout.addWidget(self.osc1_range)
        osc1_layout.addWidget(self.osc1_color)
        
        controls.addWidget(osc1_frame)
        
        # OSC 2
        osc2_frame = QFrame()
        osc2_layout = QVBoxLayout(osc2_frame)
        
        osc2_label = QLabel("OSC 2")
        osc2_layout.addWidget(osc2_label)
        
        self.osc2_wave = WaveformButton()
        osc2_layout.addWidget(self.osc2_wave)
        
        self.osc2_range = Slider("Range", -24, 24, center=True,
            display_format=lambda v: f"{v:+d}")
        self.osc2_color = Slider("Color", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.osc2_tune = Slider("Tune", -50, 50, center=True,
            display_format=lambda v: f"{v:+d}")
        
        osc2_layout.addWidget(self.osc2_range)
        osc2_layout.addWidget(self.osc2_color)
        osc2_layout.addWidget(self.osc2_tune)
        
        controls.addWidget(osc2_frame)
        
        # Mix
        mix_frame = QFrame()
        mix_layout = QVBoxLayout(mix_frame)
        
        mix_label = QLabel("Mix")
        mix_layout.addWidget(mix_label)
        
        self.osc_mix = Slider("OSC Mix", 0, 127,
            display_format=lambda v: f"{v:3d}")
        mix_layout.addWidget(self.osc_mix)
        
        controls.addWidget(mix_frame)
        
        layout.addLayout(controls)
        return frame

    def _create_filter_section(self):
        """Create filter controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Add header
        layout.addWidget(self._create_section_header("Filter", Style.VCF_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(30)
        
        # Filter parameters
        params_frame = QFrame()
        params_layout = QVBoxLayout(params_frame)
        params_layout.setSpacing(15)
        
        self.filter_cutoff = Slider("Cutoff", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.filter_resonance = Slider("Resonance", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.filter_env_depth = Slider("Env Depth", -63, 63, center=True,
            display_format=lambda v: f"{v:+3d}")
        self.filter_key_follow = Slider("Key Follow", 0, 127,
            display_format=lambda v: f"{v:3d}")
        
        params_layout.addWidget(self.filter_cutoff)
        params_layout.addWidget(self.filter_resonance)
        params_layout.addWidget(self.filter_env_depth)
        params_layout.addWidget(self.filter_key_follow)
        
        controls.addWidget(params_frame)
        
        # Filter envelope
        env_frame = QFrame()
        env_layout = QVBoxLayout(env_frame)
        env_layout.setSpacing(15)
        
        self.filter_attack = Slider("Attack", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.filter_decay = Slider("Decay", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.filter_sustain = Slider("Sustain", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.filter_release = Slider("Release", 0, 127,
            display_format=lambda v: f"{v:3d}")
        
        env_layout.addWidget(self.filter_attack)
        env_layout.addWidget(self.filter_decay)
        env_layout.addWidget(self.filter_sustain)
        env_layout.addWidget(self.filter_release)
        
        controls.addWidget(env_frame)
        layout.addLayout(controls)
        
        return frame

    def _create_amplifier_section(self):
        """Create amplifier controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Add header
        layout.addWidget(self._create_section_header("Amplifier", Style.AMP_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(30)
        
        # Level parameters
        level_frame = QFrame()
        level_layout = QVBoxLayout(level_frame)
        level_layout.setSpacing(15)
        
        self.amp_level = Slider("Level", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.amp_pan = Slider("Pan", -64, 63, center=True,
            display_format=lambda v: f"{v:+3d}")
        self.amp_velocity = Slider("Velocity", 0, 127,
            display_format=lambda v: f"{v:3d}")
        
        level_layout.addWidget(self.amp_level)
        level_layout.addWidget(self.amp_pan)
        level_layout.addWidget(self.amp_velocity)
        
        controls.addWidget(level_frame)
        
        # Envelope
        env_frame = QFrame()
        env_layout = QVBoxLayout(env_frame)
        env_layout.setSpacing(15)
        
        self.amp_attack = Slider("Attack", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.amp_decay = Slider("Decay", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.amp_sustain = Slider("Sustain", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.amp_release = Slider("Release", 0, 127,
            display_format=lambda v: f"{v:3d}")
        
        env_layout.addWidget(self.amp_attack)
        env_layout.addWidget(self.amp_decay)
        env_layout.addWidget(self.amp_sustain)
        env_layout.addWidget(self.amp_release)
        
        controls.addWidget(env_frame)
        layout.addLayout(controls)
        
        return frame

    def _create_lfo_section(self):
        """Create LFO controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Add header
        layout.addWidget(self._create_section_header("LFO", Style.LFO_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(30)
        
        # LFO 1
        lfo1_frame = QFrame()
        lfo1_layout = QVBoxLayout(lfo1_frame)
        
        lfo1_label = QLabel("LFO 1")
        lfo1_layout.addWidget(lfo1_label)
        
        self.lfo1_wave = WaveformButton()
        lfo1_layout.addWidget(self.lfo1_wave)
        
        self.lfo1_rate = Slider("Rate", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.lfo1_depth = Slider("Depth", 0, 127,
            display_format=lambda v: f"{v:3d}")
        
        lfo1_layout.addWidget(self.lfo1_rate)
        lfo1_layout.addWidget(self.lfo1_depth)
        
        controls.addWidget(lfo1_frame)
        
        # LFO 2
        lfo2_frame = QFrame()
        lfo2_layout = QVBoxLayout(lfo2_frame)
        
        lfo2_label = QLabel("LFO 2")
        lfo2_layout.addWidget(lfo2_label)
        
        self.lfo2_wave = WaveformButton()
        lfo2_layout.addWidget(self.lfo2_wave)
        
        self.lfo2_rate = Slider("Rate", 0, 127,
            display_format=lambda v: f"{v:3d}")
        self.lfo2_depth = Slider("Depth", 0, 127,
            display_format=lambda v: f"{v:3d}")
        
        lfo2_layout.addWidget(self.lfo2_rate)
        lfo2_layout.addWidget(self.lfo2_depth)
        
        controls.addWidget(lfo2_frame)
        
        # Mix
        mix_frame = QFrame()
        mix_layout = QVBoxLayout(mix_frame)
        
        mix_label = QLabel("Mix")
        mix_layout.addWidget(mix_label)
        
        self.lfo_mix = Slider("LFO Mix", 0, 127,
            display_format=lambda v: f"{v:3d}")
        mix_layout.addWidget(self.lfo_mix)
        
        controls.addWidget(mix_frame)
        
        layout.addLayout(controls)
        return frame

    def _setup_parameter_bindings(self):
        """Set up MIDI parameter bindings for all controls"""
        # OSC 1 parameters
        self.osc1_wave.waveformChanged.connect(
            lambda v: self._send_parameter(0x20, 0x00, v))  # Wave Type
        self.osc1_range.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x01, v + 24))  # Range (-24-+24)
        self.osc1_color.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x02, v))  # Color
        
        # OSC 2 parameters
        self.osc2_wave.waveformChanged.connect(
            lambda v: self._send_parameter(0x20, 0x10, v))  # Wave Type
        self.osc2_range.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x11, v + 24))  # Range (-24-+24)
        self.osc2_color.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x12, v))  # Color
        self.osc2_tune.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x13, v + 50))  # Fine Tune (-50-+50)
            
        # OSC Mix parameters
        self.osc_mix.valueChanged.connect(
            lambda v: self._send_parameter(0x20, 0x20, v))  # OSC Mix
            
        # Filter parameters
        self.filter_cutoff.valueChanged.connect(
            lambda v: self._send_parameter(0x21, 0x00, v))  # Cutoff
        self.filter_resonance.valueChanged.connect(
            lambda v: self._send_parameter(0x21, 0x01, v))  # Resonance
        self.filter_key_follow.valueChanged.connect(
            lambda v: self._send_parameter(0x21, 0x02, v + 64))  # Key Follow (-64-+63)
        self.filter_env_depth.valueChanged.connect(
            lambda v: self._send_parameter(0x21, 0x03, v + 64))  # Convert -64-+63 to 0-127
            
        # Filter envelope
        self.filter_attack.valueChanged.connect(
            lambda v: self._send_parameter(0x21, 0x10, v))
        self.filter_decay.valueChanged.connect(
            lambda v: self._send_parameter(0x21, 0x11, v))
        self.filter_sustain.valueChanged.connect(
            lambda v: self._send_parameter(0x21, 0x12, v))
        self.filter_release.valueChanged.connect(
            lambda v: self._send_parameter(0x21, 0x13, v))
            
        # Amplifier parameters
        self.amp_level.valueChanged.connect(
            lambda v: self._send_parameter(0x22, 0x00, v))
        self.amp_pan.valueChanged.connect(
            lambda v: self._send_parameter(0x22, 0x01, v + 64))  # Convert -64-+63 to 0-127
        self.amp_velocity.valueChanged.connect(
            lambda v: self._send_parameter(0x22, 0x02, v))
            
        # Amp envelope
        self.amp_attack.valueChanged.connect(
            lambda v: self._send_parameter(0x22, 0x10, v))
        self.amp_decay.valueChanged.connect(
            lambda v: self._send_parameter(0x22, 0x11, v))
        self.amp_sustain.valueChanged.connect(
            lambda v: self._send_parameter(0x22, 0x12, v))
        self.amp_release.valueChanged.connect(
            lambda v: self._send_parameter(0x22, 0x13, v))
            
        # LFO parameters - Updated addresses to match Perl version
        self.lfo1_wave.waveformChanged.connect(
            lambda v: self._send_parameter(0x26, 0x00, v))  # Changed from 0x23 to 0x26
        self.lfo1_rate.valueChanged.connect(
            lambda v: self._send_parameter(0x26, 0x01, v))
        self.lfo2_wave.waveformChanged.connect(
            lambda v: self._send_parameter(0x26, 0x10, v))  # Second LFO offset
        self.lfo2_rate.valueChanged.connect(
            lambda v: self._send_parameter(0x26, 0x11, v))
        self.lfo_mix.valueChanged.connect(
            lambda v: self._send_parameter(0x26, 0x20, v))  # Mix parameter

    def _request_patch_data(self):
        """Request current patch data from synth"""
        if not self.midi_out:
            return
            
        try:
            # Use 0x01/0x02 for synth number instead of 0x20/0x21
            synth_num = 0x01 if self.synth_num == 1 else 0x02
            
            # Build request message
            msg = bytes([
                0xF0, 0x41, 0x10,             # SysEx header
                0x00, 0x00, 0x00,             # Model ID
                0x0E,                         # JD-Xi ID
                0x11,                         # RQ1 Command (request data)
                0x19,                         # Digital Synth area
                synth_num,                    # Synth number (0x01/0x02)
                0x00, 0x00,                   # Address
                0x00, 0x00, 0x00, 0x40,       # Size (64 bytes)
                0x00,                         # Placeholder for checksum
                0xF7                          # End of SysEx
            ])
            
            # Calculate and update checksum
            checksum = 0
            for byte in msg[8:-2]:  # Sum from address to size
                checksum += byte
            checksum = (-checksum) & 0x7F
            msg_list = list(msg)
            msg_list[-2] = checksum
            msg = bytes(msg_list)
            
            self.midi_out.send_message(msg)
            
            # Log the request
            logging.debug(f"Requesting patch data for Digital Synth {self.synth_num}")
            logging.debug(f"Raw MIDI: hex = {' '.join([hex(b) for b in msg])}")
            logging.debug(f"Raw MIDI: dec = {' '.join([str(b) for b in msg])}")
            
        except Exception as e:
            logging.error(f"Error requesting patch data: {str(e)}")

    def _validate_sysex_message(self, data):
        """Validate a SysEx message"""
        try:
            # Check basic SysEx structure
            if not data or len(data) < 14:  # Updated minimum length to include checksum
                raise ValueError("Message too short")
                
            # Check SysEx frame
            if data[0] != 0xF0 or data[-1] != 0xF7:
                raise ValueError("Invalid SysEx frame")
                
            # Check Roland ID and Device ID
            if data[1] != 0x41:  # Roland ID
                raise ValueError("Not a Roland message")
                
            # Check JD-Xi ID
            if data[6] != 0x0E:  # JD-Xi ID
                raise ValueError("Not a JD-Xi message")
                
            # Check DT1 Command
            if data[7] != 0x12:  # Added DT1 check
                raise ValueError("Not a DT1 message")
                
            # Check Digital Synth area
            if data[8] != 0x19:  # Updated index due to DT1
                raise ValueError("Not a Digital Synth message")
                
            # Check correct synth number
            expected_synth = 0x20 if self.synth_num == 1 else 0x21
            if data[9] != expected_synth:  # Updated index
                raise ValueError(f"Wrong synth number (got {hex(data[9])}, expected {hex(expected_synth)})")
                
            # Verify checksum
            expected_checksum = self._calculate_checksum(data)
            if data[-2] != expected_checksum:  # Checksum is second-to-last byte
                raise ValueError(f"Invalid checksum (got {hex(data[-2])}, expected {hex(expected_checksum)})")
                
            return True
            
        except Exception as e:
            logging.error(f"SysEx validation failed: {str(e)}")
            return False

    def _calculate_checksum(self, data):
        """Calculate Roland checksum for address and data bytes"""
        # Sum address and data bytes (after DT1 command)
        checksum = 0
        for byte in data[8:-2]:  # Start after DT1 command, exclude checksum and F7
            checksum += byte
            
        # Calculate 2's complement of 7-bit sum
        checksum = (-checksum) & 0x7F
        return checksum

    def _send_parameter(self, section, parameter, value):
        """Send parameter change to synth"""
        if not self.midi_out:
            return
            
        try:
            # Validate parameter
            DigitalSynthValidator.validate_parameter(section, parameter, value)
            
            # Use 0x01/0x02 for synth number instead of 0x20/0x21
            synth_num = 0x01 if self.synth_num == 1 else 0x02
            
            msg = bytes([
                0xF0, 0x41, 0x10,             # SysEx header
                0x00, 0x00, 0x00,             # Model ID
                0x0E,                         # JD-Xi ID
                0x12,                         # DT1 Command
                0x19,                         # Digital Synth area
                synth_num,                    # Synth number (0x01/0x02)
                section,                      # Section (OSC/FILTER/etc)
                parameter,                    # Parameter number
                value & 0x7F,                # Parameter value (7-bit)
                0x00,                        # Placeholder for checksum
                0xF7                         # End of SysEx
            ])
            
            # Calculate and update checksum
            checksum = 0
            for byte in msg[8:-2]:  # Sum from address to value
                checksum += byte
            checksum = (-checksum) & 0x7F
            msg_list = list(msg)
            msg_list[-2] = checksum
            msg = bytes(msg_list)
            
            self.midi_out.send_message(msg)
            
            # Log the MIDI message
            logging.debug(f"Raw MIDI: hex = {' '.join([hex(b) for b in msg])}")
            logging.debug(f"Raw MIDI: dec = {' '.join([str(b) for b in msg])}")
            
        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")

    def _handle_midi_input(self, message, timestamp):
        """Handle incoming MIDI messages"""
        try:
            data = message[0]  # Get the raw MIDI data
            
            # Check if it's a SysEx message
            if data[0] != 0xF0:
                return  # Not a SysEx message
                
            # Get address and parameter data
            addr = data[8:12]  # 4-byte address
            param_data = data[12:-2]  # Parameter data (excluding checksum and F7)
            
            # Log received MIDI data
            logging.debug(f"MIDI IN: hex = {' '.join([hex(b) for b in data])}")
            logging.debug(f"MIDI IN: dec = {' '.join([str(b) for b in data])}")
            
            # Queue UI update on main thread
            QTimer.singleShot(0, lambda: self._update_ui_from_sysex(addr, param_data))
            
        except Exception as e:
            logging.error(f"Error handling MIDI input: {str(e)}")

    def _update_ui_from_sysex(self, addr, data):
        """Update UI controls based on received SysEx data"""
        # Check if it's for this synth (0x19 0x01/0x02)
        if (addr[0] != 0x19 or 
            addr[1] != (0x01 if self.synth_num == 1 else 0x02)):
            return
            
        section = addr[2]  # Section address
        param = addr[3]    # Parameter number
        value = data[0]    # Parameter value
        
        try:
            # Update the appropriate control based on section/parameter
            if section == 0x20:  # Oscillator
                if param == 0x00:
                    self.osc1_wave.setCurrentIndex(value)
                elif param == 0x01:
                    self.osc1_range.setValue(value - 24)  # Convert 0-48 to -24-+24
                # ... etc for other oscillator parameters
                
            elif section == 0x21:  # Filter
                if param == 0x00:
                    self.filter_cutoff.setValue(value)
                elif param == 0x01:
                    self.filter_resonance.setValue(value)
                # ... etc for other filter parameters
                
            elif section == 0x22:  # Amplifier
                if param == 0x00:
                    self.amp_level.setValue(value)
                elif param == 0x01:
                    self.amp_pan.setValue(value - 64)  # Convert 0-127 to -64-+63
                # ... etc for other amplifier parameters
                
            elif section == 0x26:  # LFO (changed from 0x23)
                if param == 0x00:
                    self.lfo1_wave.setWaveform(value)
                elif param == 0x01:
                    self.lfo1_rate.setValue(value)
                elif param == 0x10:
                    self.lfo2_wave.setWaveform(value)
                elif param == 0x11:
                    self.lfo2_rate.setValue(value)
                elif param == 0x20:
                    self.lfo_mix.setValue(value)
                
        except Exception as e:
            logging.error(f"Error updating UI from SysEx: {str(e)}")

    def set_midi_ports(self, midi_in, midi_out):
        """Update MIDI port connections"""
        self.midi_in = midi_in
        self.midi_out = midi_out
        
        if midi_in:
            midi_in.set_callback(self._handle_midi_input)
            logging.debug(f"Set MIDI input callback for Digital Synth {self.synth_num}")
            
        # Request current patch data when ports are set
        self._request_patch_data()

    def _load_patch(self):
        """Open file dialog to load a SysEx patch file"""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption="Load Patch File",
                dir=str(Path.home()),  # Start in user's home directory
                filter="SysEx Files (*.syx);;All Files (*.*)"
            )
            
            if filename:
                with open(filename, 'rb') as f:
                    sysex_data = f.read()
                    
                # Verify it's a valid JD-Xi SysEx message
                if (len(sysex_data) > 8 and
                    sysex_data[0] == 0xF0 and
                    sysex_data[1] == 0x41 and  # Roland ID
                    sysex_data[4:8] == bytes([0x00, 0x00, 0x00, 0x0E])):  # JD-Xi ID
                    
                    # Send the SysEx message
                    self.midi_out.send_message(sysex_data)
                    logging.info(f"Loaded patch from {filename}")
                    
                    # Request current patch data to update UI
                    self._request_patch_data()
                    
                else:
                    QMessageBox.warning(
                        self,
                        "Invalid File",
                        "The selected file is not a valid JD-Xi patch file."
                    )
                    
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load patch file: {str(e)}"
            )
            logging.error(f"Error loading patch: {str(e)}")

    def _save_patch(self):
        """Save current patch as SysEx file"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                parent=self,
                caption="Save Patch File",
                dir=str(Path.home()),  # Start in user's home directory
                filter="SysEx Files (*.syx)"
            )
            
            if filename:
                # Add .syx extension if not present
                if not filename.lower().endswith('.syx'):
                    filename += '.syx'
                    
                # Request current patch data from synth
                base_addr = bytes([0x19, 0x20 if self.synth_num == 1 else 0x21, 0x00, 0x00])
                msg = MIDIHelper.create_sysex_message(base_addr, bytes([0x00]))
                self.midi_out.send_message(msg)
                
                # TODO: Wait for response and save to file
                # For now, just show a message
                QMessageBox.information(
                    self,
                    "Save Patch",
                    f"Patch will be saved to: {filename}\n\n"
                    "Note: Save functionality not yet implemented."
                )
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save patch file: {str(e)}"
            )
            logging.error(f"Error saving patch: {str(e)}")

    # ... (to be continued in next message) 