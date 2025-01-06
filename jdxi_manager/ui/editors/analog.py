from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFrame, QLabel, QPushButton, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor

from ...data import AN
from ...midi import MIDIHelper
from ..widgets import Slider, WaveformButton

class AnalogSynthEditor(QMainWindow):
    def __init__(self, midi_out=None):
        super().__init__()
        self.midi_out = midi_out
        
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
        layout.setSpacing(10)
        
        # Create sections
        common = self._create_common_section()
        osc = self._create_oscillator_section()
        filter_section = self._create_filter_section()
        amp = self._create_amplifier_section()
        mod = self._create_modulation_section()
        
        # Add sections to layout
        layout.addWidget(common)
        layout.addWidget(osc)
        layout.addWidget(filter_section)
        layout.addWidget(amp)
        layout.addWidget(mod)
        
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
        layout.addWidget(self._create_section_header("Common", "#3A464E"))
        
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
        
        # Portamento
        porta_frame = QFrame()
        porta_frame.setFrameStyle(QFrame.StyledPanel)
        porta_layout = QHBoxLayout(porta_frame)
        self.portamento = Slider("Portamento Time", 0, 127)
        self.porta_mode = QPushButton("Portamento")
        self.porta_mode.setCheckable(True)
        self.porta_mode.setFixedWidth(100)
        porta_layout.addWidget(self.portamento)
        porta_layout.addWidget(self.porta_mode)
        controls.addWidget(porta_frame)
        
        layout.addLayout(controls)
        return frame
        
    def _create_oscillator_section(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Oscillator", "#FFA200"))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # OSC 1
        osc1_frame = QFrame()
        osc1_frame.setFrameStyle(QFrame.StyledPanel)
        osc1_layout = QVBoxLayout(osc1_frame)
        osc1_layout.addWidget(QLabel("OSC 1"))
        
        self.osc1_wave = WaveformButton()
        self.osc1_range = Slider("Range", -24, 24, center=True)
        self.osc1_fine = Slider("Fine", -50, 50, center=True)
        
        osc1_layout.addWidget(self.osc1_wave)
        osc1_layout.addWidget(self.osc1_range)
        osc1_layout.addWidget(self.osc1_fine)
        controls.addWidget(osc1_frame)
        
        # OSC 2
        osc2_frame = QFrame()
        osc2_frame.setFrameStyle(QFrame.StyledPanel)
        osc2_layout = QVBoxLayout(osc2_frame)
        osc2_layout.addWidget(QLabel("OSC 2"))
        
        self.osc2_wave = WaveformButton()
        self.osc2_range = Slider("Range", -24, 24, center=True)
        self.osc2_fine = Slider("Fine", -50, 50, center=True)
        self.osc2_sync = QPushButton("Sync")
        self.osc2_sync.setCheckable(True)
        
        osc2_layout.addWidget(self.osc2_wave)
        osc2_layout.addWidget(self.osc2_range)
        osc2_layout.addWidget(self.osc2_fine)
        osc2_layout.addWidget(self.osc2_sync)
        controls.addWidget(osc2_frame)
        
        # Mix
        mix_frame = QFrame()
        mix_frame.setFrameStyle(QFrame.StyledPanel)
        mix_layout = QVBoxLayout(mix_frame)
        mix_layout.addWidget(QLabel("Mix"))
        
        self.osc_mix = Slider("OSC Mix", 0, 127)
        self.cross_mod = Slider("Cross Mod", 0, 127)
        
        mix_layout.addWidget(self.osc_mix)
        mix_layout.addWidget(self.cross_mod)
        controls.addWidget(mix_frame)
        
        layout.addLayout(controls)
        return frame
        
    def _create_filter_section(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Filter", "#E83939"))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Filter parameters
        params_frame = QFrame()
        params_frame.setFrameStyle(QFrame.StyledPanel)
        params_layout = QVBoxLayout(params_frame)
        
        self.cutoff = Slider("Cutoff", 0, 127)
        self.resonance = Slider("Resonance", 0, 127)
        self.key_follow = Slider("Key Follow", -100, 100, center=True)
        
        params_layout.addWidget(self.cutoff)
        params_layout.addWidget(self.resonance)
        params_layout.addWidget(self.key_follow)
        controls.addWidget(params_frame)
        
        # Filter envelope
        env_frame = QFrame()
        env_frame.setFrameStyle(QFrame.StyledPanel)
        env_layout = QVBoxLayout(env_frame)
        env_layout.addWidget(QLabel("Envelope"))
        
        self.filter_attack = Slider("Attack", 0, 127)
        self.filter_decay = Slider("Decay", 0, 127)
        self.filter_sustain = Slider("Sustain", 0, 127)
        self.filter_release = Slider("Release", 0, 127)
        self.env_depth = Slider("Env Depth", -63, 63, center=True)
        
        env_layout.addWidget(self.filter_attack)
        env_layout.addWidget(self.filter_decay)
        env_layout.addWidget(self.filter_sustain)
        env_layout.addWidget(self.filter_release)
        env_layout.addWidget(self.env_depth)
        controls.addWidget(env_frame)
        
        layout.addLayout(controls)
        return frame

    def _create_amplifier_section(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Amplifier", "#AF7200"))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Level controls
        level_frame = QFrame()
        level_frame.setFrameStyle(QFrame.StyledPanel)
        level_layout = QVBoxLayout(level_frame)
        level_layout.addWidget(QLabel("Level"))
        
        self.amp_level = Slider("Level", 0, 127)
        self.velocity_sens = Slider("Velocity Sens", -63, 63, center=True)
        
        level_layout.addWidget(self.amp_level)
        level_layout.addWidget(self.velocity_sens)
        controls.addWidget(level_frame)
        
        # Amp envelope
        env_frame = QFrame()
        env_frame.setFrameStyle(QFrame.StyledPanel)
        env_layout = QVBoxLayout(env_frame)
        env_layout.addWidget(QLabel("Envelope"))
        
        self.amp_attack = Slider("Attack", 0, 127)
        self.amp_decay = Slider("Decay", 0, 127)
        self.amp_sustain = Slider("Sustain", 0, 127)
        self.amp_release = Slider("Release", 0, 127)
        
        env_layout.addWidget(self.amp_attack)
        env_layout.addWidget(self.amp_decay)
        env_layout.addWidget(self.amp_sustain)
        env_layout.addWidget(self.amp_release)
        controls.addWidget(env_frame)
        
        layout.addLayout(controls)
        return frame
        
    def _create_modulation_section(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Modulation", "#E86333"))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # LFO Frame
        lfo_frame = QFrame()
        lfo_frame.setFrameStyle(QFrame.StyledPanel)
        lfo_layout = QVBoxLayout(lfo_frame)
        lfo_layout.addWidget(QLabel("LFO"))
        
        # LFO Wave selection
        wave_layout = QHBoxLayout()
        wave_layout.addWidget(QLabel("Waveform:"))
        self.lfo_wave = QComboBox()
        self.lfo_wave.addItems(["Triangle", "Sine", "Square", "Sample & Hold", "Random"])
        wave_layout.addWidget(self.lfo_wave)
        lfo_layout.addLayout(wave_layout)
        
        # Rate controls
        rate_frame = QFrame()
        rate_frame.setFrameStyle(QFrame.StyledPanel)
        rate_layout = QVBoxLayout(rate_frame)
        
        sync_layout = QHBoxLayout()
        self.lfo_sync = QPushButton("Sync")
        self.lfo_sync.setCheckable(True)
        self.lfo_sync.setFixedWidth(80)
        sync_layout.addWidget(self.lfo_sync)
        self.lfo_rate = Slider("Rate", 0, 127)
        sync_layout.addWidget(self.lfo_rate)
        rate_layout.addLayout(sync_layout)
        
        self.lfo_note = QComboBox()
        self.lfo_note.addItems([
            "16", "12", "8", "4", "2", "1", "3/4", "2/3", "1/2", "3/8", "1/3",
            "1/4", "3/16", "1/6", "1/8", "3/32", "1/12", "1/16", "1/24", "1/32"
        ])
        self.lfo_note.setVisible(False)
        rate_layout.addWidget(self.lfo_note)
        lfo_layout.addWidget(rate_frame)
        
        # Other LFO controls
        self.lfo_key_trigger = QPushButton("Key Trigger")
        self.lfo_key_trigger.setCheckable(True)
        self.lfo_key_trigger.setFixedWidth(80)
        lfo_layout.addWidget(self.lfo_key_trigger)
        
        self.lfo_fade = Slider("Fade Time", 0, 127)
        lfo_layout.addWidget(self.lfo_fade)
        
        # LFO Depths
        depths_frame = QFrame()
        depths_frame.setFrameStyle(QFrame.StyledPanel)
        depths_layout = QVBoxLayout(depths_frame)
        self.lfo_pitch = Slider("Pitch Depth", 0, 127)
        self.lfo_filter = Slider("Filter Depth", 0, 127)
        self.lfo_amp = Slider("Amp Depth", 0, 127)
        depths_layout.addWidget(self.lfo_pitch)
        depths_layout.addWidget(self.lfo_filter)
        depths_layout.addWidget(self.lfo_amp)
        lfo_layout.addWidget(depths_frame)
        
        controls.addWidget(lfo_frame)
        
        # Modulation Matrix
        mod_frame = QFrame()
        mod_frame.setFrameStyle(QFrame.StyledPanel)
        mod_layout = QVBoxLayout(mod_frame)
        mod_layout.addWidget(QLabel("Modulation Matrix"))
        
        # Source selection
        source_frame = QFrame()
        source_frame.setFrameStyle(QFrame.StyledPanel)
        source_layout = QVBoxLayout(source_frame)
        source_layout.addWidget(QLabel("Source:"))
        self.mod_source = QComboBox()
        self.mod_source.addItems([
            "Off", "Velocity", "Key Follow", "Bender", "Modulation",
            "Aftertouch", "Expression"
        ])
        source_layout.addWidget(self.mod_source)
        mod_layout.addWidget(source_frame)
        
        # Destination selection
        dest_frame = QFrame()
        dest_frame.setFrameStyle(QFrame.StyledPanel)
        dest_layout = QVBoxLayout(dest_frame)
        dest_layout.addWidget(QLabel("Destination:"))
        self.mod_dest = QComboBox()
        self.mod_dest.addItems([
            "Off", "Pitch", "Filter", "Amp", "LFO Rate", "LFO Pitch",
            "LFO Filter", "LFO Amp"
        ])
        dest_layout.addWidget(self.mod_dest)
        mod_layout.addWidget(dest_frame)
        
        # Depth control
        depth_frame = QFrame()
        depth_frame.setFrameStyle(QFrame.StyledPanel)
        self.mod_depth = Slider("Depth", -63, 63, center=True)
        depth_frame.setLayout(QVBoxLayout())
        depth_frame.layout().addWidget(self.mod_depth)
        mod_layout.addWidget(depth_frame)
        
        controls.addWidget(mod_frame)
        layout.addLayout(controls)
        
        return frame

    def _setup_parameter_bindings(self):
        """Set up MIDI parameter bindings for all controls"""
        # Common parameters
        self.volume.valueChanged.connect(
            lambda v: self._send_parameter(0x01, v))  # Volume
        self.pan.valueChanged.connect(
            lambda v: self._send_parameter(0x02, v + 64))  # Pan
        self.portamento.valueChanged.connect(
            lambda v: self._send_parameter(0x03, v))  # Portamento Time
        self.porta_mode.toggled.connect(
            lambda v: self._send_parameter(0x04, 1 if v else 0))  # Portamento Mode
            
        # OSC 1 parameters
        self.osc1_wave.waveformChanged.connect(
            lambda v: self._send_parameter(0x10, v))  # Wave Type
        self.osc1_range.valueChanged.connect(
            lambda v: self._send_parameter(0x11, v + 64))  # Range
        self.osc1_fine.valueChanged.connect(
            lambda v: self._send_parameter(0x12, v + 64))  # Fine Tune
            
        # OSC 2 parameters
        self.osc2_wave.waveformChanged.connect(
            lambda v: self._send_parameter(0x20, v))  # Wave Type
        self.osc2_range.valueChanged.connect(
            lambda v: self._send_parameter(0x21, v + 64))  # Range
        self.osc2_fine.valueChanged.connect(
            lambda v: self._send_parameter(0x22, v + 64))  # Fine Tune
        self.osc2_sync.toggled.connect(
            lambda v: self._send_parameter(0x23, 1 if v else 0))  # Sync
            
        # Mix parameters
        self.osc_mix.valueChanged.connect(
            lambda v: self._send_parameter(0x30, v))  # OSC Mix
        self.cross_mod.valueChanged.connect(
            lambda v: self._send_parameter(0x31, v))  # Cross Mod
            
        # Filter parameters
        self.cutoff.valueChanged.connect(
            lambda v: self._send_parameter(0x40, v))  # Cutoff
        self.resonance.valueChanged.connect(
            lambda v: self._send_parameter(0x41, v))  # Resonance
        self.key_follow.valueChanged.connect(
            lambda v: self._send_parameter(0x42, v + 64))  # Key Follow
            
        # Filter Envelope
        self.filter_attack.valueChanged.connect(
            lambda v: self._send_parameter(0x43, v))  # Attack
        self.filter_decay.valueChanged.connect(
            lambda v: self._send_parameter(0x44, v))  # Decay
        self.filter_sustain.valueChanged.connect(
            lambda v: self._send_parameter(0x45, v))  # Sustain
        self.filter_release.valueChanged.connect(
            lambda v: self._send_parameter(0x46, v))  # Release
        self.env_depth.valueChanged.connect(
            lambda v: self._send_parameter(0x47, v + 64))  # Env Depth
            
        # Amp parameters
        self.amp_level.valueChanged.connect(
            lambda v: self._send_parameter(0x50, v))  # Level
        self.velocity_sens.valueChanged.connect(
            lambda v: self._send_parameter(0x51, v + 64))  # Velocity Sens
            
        # Amp Envelope
        self.amp_attack.valueChanged.connect(
            lambda v: self._send_parameter(0x52, v))  # Attack
        self.amp_decay.valueChanged.connect(
            lambda v: self._send_parameter(0x53, v))  # Decay
        self.amp_sustain.valueChanged.connect(
            lambda v: self._send_parameter(0x54, v))  # Sustain
        self.amp_release.valueChanged.connect(
            lambda v: self._send_parameter(0x55, v))  # Release
            
        # LFO parameters
        self.lfo_wave.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x60, v))  # LFO Wave
        self.lfo_sync.toggled.connect(
            lambda v: self._send_parameter(0x61, 1 if v else 0))  # LFO Sync
        self.lfo_rate.valueChanged.connect(
            lambda v: self._send_parameter(0x62, v))  # LFO Rate
        self.lfo_note.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x63, v))  # LFO Note
        self.lfo_key_trigger.toggled.connect(
            lambda v: self._send_parameter(0x64, 1 if v else 0))  # LFO Key Trigger
        self.lfo_fade.valueChanged.connect(
            lambda v: self._send_parameter(0x65, v))  # LFO Fade Time
            
        # LFO Depths
        self.lfo_pitch.valueChanged.connect(
            lambda v: self._send_parameter(0x66, v))  # Pitch Depth
        self.lfo_filter.valueChanged.connect(
            lambda v: self._send_parameter(0x67, v))  # Filter Depth
        self.lfo_amp.valueChanged.connect(
            lambda v: self._send_parameter(0x68, v))  # Amp Depth
            
        # Modulation Matrix
        self.mod_source.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x70, v))  # Mod Source
        self.mod_dest.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x71, v))  # Mod Destination
        self.mod_depth.valueChanged.connect(
            lambda v: self._send_parameter(0x72, v + 64))  # Mod Depth
            
    def _send_parameter(self, parameter, value):
        """Send a parameter change via MIDI"""
        if self.midi_out:
            msg = MIDIHelper.create_parameter_message(
                0x18,  # Analog synth address
                None,  # No partial for analog synth
                parameter,
                value
            )
            self.midi_out.send_message(msg)
            
    def _request_patch_data(self):
        """Request current patch data from synth"""
        if self.midi_out:
            # Request all analog synth parameters
            addr = bytes([0x18, 0x00, 0x00, 0x00])
            msg = MIDIHelper.create_sysex_message(addr, bytes([0x00]))
            self.midi_out.send_message(msg)
            
    def set_midi_ports(self, midi_in, midi_out):
        """Update MIDI port connections"""
        self.midi_in = midi_in
        self.midi_out = midi_out
        
        if midi_in:
            midi_in.set_callback(self._handle_midi_input) 