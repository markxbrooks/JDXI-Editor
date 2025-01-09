from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QCheckBox, QPushButton,
    QFileDialog, QMessageBox, QScrollArea, QProgressDialog,
    QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
import logging

from ..style import Style
from ..widgets import Slider, WaveformButton
from ..widgets.preset_panel import PresetPanel
from ...midi import MIDIHelper, MIDIConnection


class DigitalSynthEditor(QMainWindow):
    def __init__(self, synth_num=1, midi_helper=None, parent=None):
        """Initialize digital synth editor"""
        super().__init__(parent)
        self.synth_num = synth_num
        self.midi_helper = midi_helper
        self.main_window = parent
        
        # Set window properties
        self.setStyleSheet(Style.DARK_THEME)
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        
        # Create UI and set up bindings
        self._create_ui()
        self._setup_parameter_bindings()
        
        # Request initial patch data
        QTimer.singleShot(100, self._request_patch_data)

    def _create_ui(self):
        """Create the user interface"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(scroll)
        
        # Create main widget and store layout reference
        central = QWidget()
        self.central_layout = QVBoxLayout(central)
        self.central_layout.setSpacing(25)
        self.central_layout.setContentsMargins(25, 25, 25, 25)
        
        # Create all sections first
        common = self._create_common_section()
        osc = self._create_oscillator_section()
        vcf = self._create_filter_section()
        amp = self._create_amplifier_section()
        mod = self._create_modulation_section()
        
        # Add preset panel at the top
        self.preset_panel = PresetPanel(f'digital{self.synth_num}', self, parent=central)
        self.central_layout.addWidget(self.preset_panel)
        
        # Add sections to layout
        self.central_layout.addWidget(common)
        self.central_layout.addWidget(self._create_separator())
        self.central_layout.addWidget(osc)
        self.central_layout.addWidget(self._create_separator())
        self.central_layout.addWidget(vcf)
        self.central_layout.addWidget(self._create_separator())
        self.central_layout.addWidget(amp)
        self.central_layout.addWidget(self._create_separator())
        self.central_layout.addWidget(mod)
        
        # Add stretch at the bottom
        self.central_layout.addStretch()
        
        # Set the widget to scroll area
        scroll.setWidget(central)

    def _create_separator(self):
        """Create a separator line"""
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

    def _create_common_section(self):
        """Create common parameters section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # Create controls
        self.volume = Slider("Volume", 0, 127)
        self.pan = Slider("Pan", -64, 63)
        self.portamento = Slider("Portamento", 0, 127)
        self.porta_mode = QPushButton("Porta Mode")
        self.porta_mode.setCheckable(True)
        
        # Add to layout
        layout.addWidget(self.volume)
        layout.addWidget(self.pan)
        layout.addWidget(self.portamento)
        layout.addWidget(self.porta_mode)
        
        return section

    def _create_oscillator_section(self):
        """Create oscillator section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # OSC 1
        osc1_group = QGroupBox("OSC 1")
        osc1_layout = QVBoxLayout(osc1_group)
        
        self.osc1_wave = WaveformButton("Waveform")
        self.osc1_range = Slider("Range", -24, 24)
        self.osc1_fine = Slider("Fine Tune", -50, 50)
        
        osc1_layout.addWidget(self.osc1_wave)
        osc1_layout.addWidget(self.osc1_range)
        osc1_layout.addWidget(self.osc1_fine)
        
        # OSC 2
        osc2_group = QGroupBox("OSC 2")
        osc2_layout = QVBoxLayout(osc2_group)
        
        self.osc2_wave = WaveformButton("Waveform")
        self.osc2_range = Slider("Range", -24, 24)
        self.osc2_fine = Slider("Fine Tune", -50, 50)
        
        osc2_layout.addWidget(self.osc2_wave)
        osc2_layout.addWidget(self.osc2_range)
        osc2_layout.addWidget(self.osc2_fine)
        
        # Add groups to main layout
        layout.addWidget(osc1_group)
        layout.addWidget(osc2_group)
        
        return section

    def _create_filter_section(self):
        """Create filter section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # Filter parameters
        filter_group = QGroupBox("Filter")
        filter_layout = QVBoxLayout(filter_group)
        
        self.cutoff = Slider("Cutoff", 0, 127)
        self.resonance = Slider("Resonance", 0, 127)
        self.key_follow = Slider("Key Follow", -64, 63)
        
        filter_layout.addWidget(self.cutoff)
        filter_layout.addWidget(self.resonance)
        filter_layout.addWidget(self.key_follow)
        
        # Filter envelope
        env_group = QGroupBox("Filter Envelope")
        env_layout = QVBoxLayout(env_group)
        
        self.filter_attack = Slider("Attack", 0, 127)
        self.filter_decay = Slider("Decay", 0, 127)
        self.filter_sustain = Slider("Sustain", 0, 127)
        self.filter_release = Slider("Release", 0, 127)
        
        env_layout.addWidget(self.filter_attack)
        env_layout.addWidget(self.filter_decay)
        env_layout.addWidget(self.filter_sustain)
        env_layout.addWidget(self.filter_release)
        
        # Add groups to main layout
        layout.addWidget(filter_group)
        layout.addWidget(env_group)
        
        return section

    def _create_amplifier_section(self):
        """Create amplifier section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # Amp envelope
        env_group = QGroupBox("Amplifier Envelope")
        env_layout = QVBoxLayout(env_group)
        
        self.amp_attack = Slider("Attack", 0, 127)
        self.amp_decay = Slider("Decay", 0, 127)
        self.amp_sustain = Slider("Sustain", 0, 127)
        self.amp_release = Slider("Release", 0, 127)
        
        env_layout.addWidget(self.amp_attack)
        env_layout.addWidget(self.amp_decay)
        env_layout.addWidget(self.amp_sustain)
        env_layout.addWidget(self.amp_release)
        
        # Add group to main layout
        layout.addWidget(env_group)
        
        return section

    def _create_modulation_section(self):
        """Create modulation section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # LFO parameters
        lfo_group = QGroupBox("LFO")
        lfo_layout = QVBoxLayout(lfo_group)
        
        self.lfo_wave = WaveformButton("Waveform")
        self.lfo_rate = Slider("Rate", 0, 127)
        self.lfo_depth = Slider("Depth", 0, 127)
        
        lfo_layout.addWidget(self.lfo_wave)
        lfo_layout.addWidget(self.lfo_rate)
        lfo_layout.addWidget(self.lfo_depth)
        
        # Add group to main layout
        layout.addWidget(lfo_group)
        
        return section

    def _setup_parameter_bindings(self):
        """Set up parameter change handlers"""
        try:
            logging.debug("Setting up parameter bindings...")
            
            # Common parameters
            self.volume.valueChanged.connect(
                lambda v: self._send_parameter(0x12, v))  # Volume
            self.pan.valueChanged.connect(
                lambda v: self._send_parameter(0x13, v + 64))  # Pan
            self.portamento.valueChanged.connect(
                lambda v: self._send_parameter(0x14, v))  # Portamento
            
            # Test send a parameter to verify MIDI is working
            if self.midi_helper and self.midi_helper.midi_out:
                logging.debug("Testing MIDI output...")
                self._send_parameter(0x12, 100)  # Send test volume message
            else:
                logging.warning("No MIDI output available during parameter binding setup")
            
            # OSC 1 parameters
            self.osc1_wave.waveformChanged.connect(
                lambda v: self._send_parameter(0x01, v))  # Wave Type
            self.osc1_range.valueChanged.connect(
                lambda v: self._send_parameter(0x02, v + 64))  # Range
            self.osc1_fine.valueChanged.connect(
                lambda v: self._send_parameter(0x03, v + 64))  # Fine Tune
            
            # OSC 2 parameters
            self.osc2_wave.waveformChanged.connect(
                lambda v: self._send_parameter(0x04, v))  # Wave Type
            self.osc2_range.valueChanged.connect(
                lambda v: self._send_parameter(0x05, v + 64))  # Range
            self.osc2_fine.valueChanged.connect(
                lambda v: self._send_parameter(0x06, v + 64))  # Fine Tune
            
            # Filter parameters
            self.cutoff.valueChanged.connect(
                lambda v: self._send_parameter(0x07, v))  # Cutoff
            self.resonance.valueChanged.connect(
                lambda v: self._send_parameter(0x08, v))  # Resonance
            self.key_follow.valueChanged.connect(
                lambda v: self._send_parameter(0x09, v + 64))  # Key Follow
            
            # Filter envelope
            self.filter_attack.valueChanged.connect(
                lambda v: self._send_parameter(0x0A, v))  # Attack
            self.filter_decay.valueChanged.connect(
                lambda v: self._send_parameter(0x0B, v))  # Decay
            self.filter_sustain.valueChanged.connect(
                lambda v: self._send_parameter(0x0C, v))  # Sustain
            self.filter_release.valueChanged.connect(
                lambda v: self._send_parameter(0x0D, v))  # Release
            
            # Amp envelope
            self.amp_attack.valueChanged.connect(
                lambda v: self._send_parameter(0x0E, v))  # Attack
            self.amp_decay.valueChanged.connect(
                lambda v: self._send_parameter(0x0F, v))  # Decay
            self.amp_sustain.valueChanged.connect(
                lambda v: self._send_parameter(0x10, v))  # Sustain
            self.amp_release.valueChanged.connect(
                lambda v: self._send_parameter(0x11, v))  # Release
            
            # LFO parameters
            self.lfo_wave.waveformChanged.connect(
                lambda v: self._send_parameter(0x15, v))  # Wave Type
            self.lfo_rate.valueChanged.connect(
                lambda v: self._send_parameter(0x16, v))  # Rate
            self.lfo_depth.valueChanged.connect(
                lambda v: self._send_parameter(0x17, v))  # Depth
            
            logging.debug("Parameter bindings completed")
            
        except Exception as e:
            logging.error(f"Error setting up parameter bindings: {str(e)}")
            raise

    def _request_patch_data(self):
        """Request current patch data"""
        try:
            msg = MIDIHelper.create_sysex_message(
                bytes([0x19, self.synth_num, 0x00, 0x00]),  # Address
                bytes([0x00])  # Data
            )
            MIDIConnection().send_message(msg)
            
        except Exception as e:
            logging.error(f"Error requesting patch data: {str(e)}")

    def _send_parameter(self, parameter, value):
        """Send parameter change to JD-Xi"""
        try:
            msg = MIDIHelper.create_parameter_message(
                0x19,  # Digital synth address
                self.synth_num,  # Part number (1 or 2)
                parameter,
                value
            )
            MIDIConnection().send_message(msg)
            
        except Exception as e:
            logging.error(f"Error sending parameter: {str(e)}")

    def set_midi_ports(self, midi_in, midi_out):
        """Update MIDI port connections"""
        self.midi_in = midi_in
        self.midi_out = midi_out
        
        # Set main window reference for indicators
        if hasattr(self, 'main_window'):
            if midi_in:
                midi_in.main_window = self.main_window
            if midi_out:
                midi_out.main_window = self.main_window
        
        if midi_in:
            midi_in.set_callback(self._handle_midi_input)
            logging.debug(f"Set MIDI input callback for Digital Synth {self.synth_num}")

    def _handle_midi_input(self, message, timestamp):
        """Handle incoming MIDI message"""
        try:
            # Validate message is for this synth
            if not self._validate_sysex_message(message):
                return
            
            # Parse parameter values and update UI
            self._update_parameters(message)
            
        except Exception as e:
            logging.error(f"Error handling MIDI input: {str(e)}")

    def _validate_sysex_message(self, message):
        """Validate incoming SysEx message"""
        try:
            # Check message format
            if len(message) < 8:
                return False
            
            # Check if it's a Roland SysEx message
            if message[0] != 0xF0 or message[1] != 0x41:
                return False
            
            # Check if it's for the digital synth
            if message[7] != 0x19:
                return False
            
            # Check if it's for this part number
            if message[8] != self.synth_num:
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error validating SysEx message: {str(e)}")
            return False

    # ... (rest of the file remains unchanged) 