from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QFrame, QLabel, QPushButton,
    QComboBox, QSpinBox, QLineEdit
)
from PySide6.QtCore import Qt
from ...data import SN1, SN2
from ...midi import MIDIHelper
from ..widgets import Slider, WaveformButton

class DigitalSynthEditor(QMainWindow):
    def __init__(self, midi_out=None, synth_num=1):
        super().__init__()
        self.synth_num = synth_num
        self.midi_out = midi_out
        
        # Initialize synth data
        self.data = SN1 if synth_num == 1 else SN2
        
        # Create UI
        self._create_ui()
        
        # Request current patch data
        self._request_patch_data()
        
    def _create_ui(self):
        # Set window properties
        self.setFixedSize(1150, 740)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create common controls section
        common_frame = self._create_common_section()
        layout.addWidget(common_frame)
        
        # Create tab widget for partials
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Add partial tabs
        for i in range(1, 4):
            partial = self._create_partial_tab(i)
            self.tabs.addTab(partial, f"Partial {i}")
            
        # Create modulation section
        mod_frame = self._create_modulation_section()
        layout.addWidget(mod_frame)
        
        # Add MIDI parameter bindings
        self._setup_parameter_bindings()
        
    def _setup_parameter_bindings(self):
        """Set up MIDI parameter bindings for all controls"""
        # Common parameters
        self.volume_slider.valueChanged.connect(
            lambda v: self._send_parameter(0x01, v))  # Volume
        self.pan_slider.valueChanged.connect(
            lambda v: self._send_parameter(0x02, v + 64))  # Pan
        self.portamento_slider.valueChanged.connect(
            lambda v: self._send_parameter(0x03, v))  # Portamento Time
        self.portamento_switch.toggled.connect(
            lambda v: self._send_parameter(0x04, 1 if v else 0))  # Portamento Switch
            
        # Partial parameters (for each partial 1-3)
        for partial in range(1, 4):
            # OSC
            self.wave_buttons[partial-1].waveformChanged.connect(
                lambda v, p=partial: self._send_parameter(0x40, v, p))  # Wave Type
            self.pitch_sliders[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x41, v + 64, p))  # Coarse Tune
            self.fine_sliders[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x42, v + 64, p))  # Fine Tune
            self.pwm_sliders[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x43, v, p))  # PWM
                
            # FILTER
            self.cutoff_sliders[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x50, v, p))  # Cutoff
            self.resonance_sliders[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x51, v, p))  # Resonance
            self.keyfollow_sliders[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x52, v + 64, p))  # Key Follow
                
            # Filter Envelope
            self.filter_env_attack[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x53, v, p))  # Attack
            self.filter_env_decay[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x54, v, p))  # Decay
            self.filter_env_sustain[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x55, v, p))  # Sustain
            self.filter_env_release[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x56, v, p))  # Release
                
            # AMP
            self.level_sliders[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x60, v, p))  # Level
            self.velocity_sliders[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x61, v + 64, p))  # Velocity Sens
                
            # Amp Envelope
            self.amp_env_attack[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x62, v, p))  # Attack
            self.amp_env_decay[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x63, v, p))  # Decay
            self.amp_env_sustain[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x64, v, p))  # Sustain
            self.amp_env_release[partial-1].valueChanged.connect(
                lambda v, p=partial: self._send_parameter(0x65, v, p))  # Release
                
    def _send_parameter(self, parameter, value, partial=None):
        """Send a parameter change via MIDI"""
        if self.midi_out:
            msg = MIDIHelper.create_parameter_message(
                self.synth_num, partial, parameter, value)
            self.midi_out.send_message(msg)
            
    def _request_patch_data(self):
        """Request current patch data from synth"""
        if self.midi_out:
            # Request common parameters
            addr = bytes([0x19, 0x20 + self.synth_num - 1, 0x00, 0x00])
            msg = MIDIHelper.create_sysex_message(addr, bytes([0x00]))
            self.midi_out.send_message(msg)
            
            # Request partial parameters
            for partial in range(1, 4):
                addr = bytes([0x19, 0x20 + self.synth_num - 1, 0x20 + partial - 1, 0x00])
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
        # TODO: Parse incoming SysEx messages and update UI
        pass
        
    def _create_common_section(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QHBoxLayout(frame)
        
        # Left side controls
        left = QVBoxLayout()
        
        # Patch name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Patch Name:"))
        # TODO: Add patch name editor
        left.addLayout(name_layout)
        
        # Category selection
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Category:"))
        cat_combo = QComboBox()
        cat_combo.addItems([
            "00: not assigned", "09: Keyboard", "21: Bass", "34: Lead",
            "35: Brass", "36: Strings/Pad", "39: FX/Other", "40: Seq"
        ])
        cat_layout.addWidget(cat_combo)
        left.addLayout(cat_layout)
        
        layout.addLayout(left)
        
        # Right side controls
        right = QVBoxLayout()
        
        # Volume and Pan
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(Slider("Volume", 0, 127))
        vol_layout.addWidget(Slider("Pan", -64, 63, center=True))
        right.addLayout(vol_layout)
        
        # Portamento
        porta_layout = QHBoxLayout()
        porta_layout.addWidget(Slider("Portamento Time", 0, 127))
        porta_switch = QPushButton("Portamento")
        porta_switch.setCheckable(True)
        porta_layout.addWidget(porta_switch)
        right.addLayout(porta_layout)
        
        layout.addLayout(right)
        
        return frame
        
    def _create_partial_tab(self, partial_num):
        partial = QWidget()
        layout = QVBoxLayout(partial)
        
        # Create sections
        osc_frame = self._create_oscillator_section(partial_num)
        filter_frame = self._create_filter_section(partial_num)
        amp_frame = self._create_amplifier_section(partial_num)
        
        layout.addWidget(osc_frame)
        layout.addWidget(filter_frame)
        layout.addWidget(amp_frame)
        
        return partial
        
    def _create_oscillator_section(self, partial_num):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QHBoxLayout(frame)
        
        # Wave selection
        wave_layout = QVBoxLayout()
        wave_layout.addWidget(QLabel("Waveform"))
        wave_btn = WaveformButton()
        wave_layout.addWidget(wave_btn)
        layout.addLayout(wave_layout)
        
        # Oscillator controls
        controls = QVBoxLayout()
        controls.addWidget(Slider("Pitch", -24, 24, center=True))
        controls.addWidget(Slider("Fine Tune", -50, 50, center=True))
        controls.addWidget(Slider("PWM", 0, 127))
        layout.addLayout(controls)
        
        return frame
        
    def _create_filter_section(self, partial_num):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QHBoxLayout(frame)
        
        # Filter controls
        controls = QVBoxLayout()
        controls.addWidget(Slider("Cutoff", 0, 127))
        controls.addWidget(Slider("Resonance", 0, 127))
        controls.addWidget(Slider("Key Follow", -100, 100, center=True))
        layout.addLayout(controls)
        
        # Filter envelope
        env = QVBoxLayout()
        env.addWidget(Slider("Attack", 0, 127))
        env.addWidget(Slider("Decay", 0, 127))
        env.addWidget(Slider("Sustain", 0, 127))
        env.addWidget(Slider("Release", 0, 127))
        layout.addLayout(env)
        
        return frame
        
    def _create_amplifier_section(self, partial_num):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QHBoxLayout(frame)
        
        # Level controls
        controls = QVBoxLayout()
        controls.addWidget(Slider("Level", 0, 127))
        controls.addWidget(Slider("Velocity Sens", -63, 63, center=True))
        layout.addLayout(controls)
        
        # Amp envelope
        env = QVBoxLayout()
        env.addWidget(Slider("Attack", 0, 127))
        env.addWidget(Slider("Decay", 0, 127))
        env.addWidget(Slider("Sustain", 0, 127))
        env.addWidget(Slider("Release", 0, 127))
        layout.addLayout(env)
        
        return frame
        
    def _create_modulation_section(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QHBoxLayout(frame)
        
        # LFO controls
        lfo = QVBoxLayout()
        lfo.addWidget(QLabel("LFO"))
        lfo.addWidget(Slider("Rate", 0, 127))
        lfo.addWidget(Slider("Pitch Depth", 0, 127))
        lfo.addWidget(Slider("Filter Depth", 0, 127))
        lfo.addWidget(Slider("Amp Depth", 0, 127))
        layout.addLayout(lfo)
        
        return frame 