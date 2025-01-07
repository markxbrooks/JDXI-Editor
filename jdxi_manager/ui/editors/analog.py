from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFrame, QLabel, QPushButton, QComboBox, QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor

from ...data import AN
from ...midi import MIDIHelper
from ..style import Style
from ..widgets import Slider, WaveformButton

class AnalogSynthEditor(QMainWindow):
    def __init__(self, midi_out=None):
        super().__init__()
        self.setStyleSheet(Style.DARK_THEME)
        self.midi_out = midi_out
        
        # Set window properties - taller with fixed width
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        
        # Create UI
        self._create_ui()
        
        # Request current patch data
        self._request_patch_data()
        
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
        layout.setSpacing(25)  # Increased spacing
        layout.setContentsMargins(25, 25, 25, 25)  # Increased margins
        
        # Create sections
        osc = self._create_oscillator_section()
        vcf = self._create_filter_section()
        amp = self._create_amplifier_section()
        mod = self._create_modulation_section()
        
        # Add sections to layout with spacing and separators
        layout.addWidget(osc)
        layout.addWidget(self._create_separator())
        layout.addWidget(vcf)
        layout.addWidget(self._create_separator())
        layout.addWidget(amp)
        layout.addWidget(self._create_separator())
        layout.addWidget(mod)
        
        # Add stretch at the bottom
        layout.addStretch()
        
        # Set the widget to scroll area
        scroll.setWidget(central)
        
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
        
    def _create_oscillator_section(self):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Add header
        layout.addWidget(self._create_section_header("Oscillator", Style.OSC_BG))
        layout.addSpacing(10)
        
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
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Add header
        layout.addWidget(self._create_section_header("Filter", Style.VCF_BG))
        layout.addSpacing(10)
        
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
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Add header
        layout.addWidget(self._create_section_header("Amplifier", Style.AMP_BG))
        layout.addSpacing(10)
        
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
        layout.setSpacing(20)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Add header
        layout.addWidget(self._create_section_header("Modulation", Style.MOD_BG))
        layout.addSpacing(10)
        
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
            
        # OSC 2 parameters (0x20)
        self.osc2_wave.waveformChanged.connect(
            lambda v: self._send_parameter(0x20, v))  # Wave Type
        self.osc2_range.valueChanged.connect(
            lambda v: self._send_parameter(0x21, v + 64))  # Range
        self.osc2_fine.valueChanged.connect(
            lambda v: self._send_parameter(0x22, v + 64))  # Fine Tune
        self.osc2_sync.toggled.connect(
            lambda v: self._send_parameter(0x23, 1 if v else 0))  # Sync
            
        # Mix parameters (0x30)
        self.osc_mix.valueChanged.connect(
            lambda v: self._send_parameter(0x30, v))  # OSC Mix
        self.cross_mod.valueChanged.connect(
            lambda v: self._send_parameter(0x31, v))  # Cross Mod
            
        # Filter parameters (0x40)
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
            
        # Amp parameters (0x50)
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
            
        # LFO parameters (0x60)
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
        # Check if it's for analog synth (0x17)
        if addr[0] != 0x17:
            return
            
        section = addr[2]  # Section address
        param = addr[3]    # Parameter number
        value = data[0]    # Parameter value
        
        try:
            # Common parameters (0x00)
            if section == 0x00:
                if param == 0x01:
                    self.volume.setValue(value)
                elif param == 0x02:
                    self.pan.setValue(value - 64)  # Convert 0-127 to -64-+63
                elif param == 0x03:
                    self.portamento.setValue(value)
                elif param == 0x04:
                    self.porta_mode.setChecked(bool(value))
                    
            # OSC 1 parameters (0x10)
            elif section == 0x10:
                if param == 0x00:
                    self.osc1_wave.setCurrentIndex(value)
                elif param == 0x01:
                    self.osc1_range.setValue(value - 64)  # Convert 0-127 to -64-+63
                elif param == 0x02:
                    self.osc1_fine.setValue(value - 64)  # Convert 0-127 to -64-+63
                    
            # OSC 2 parameters (0x20)
            elif section == 0x20:
                if param == 0x00:
                    self.osc2_wave.setCurrentIndex(value)
                elif param == 0x01:
                    self.osc2_range.setValue(value - 64)  # Convert 0-127 to -64-+63
                elif param == 0x02:
                    self.osc2_fine.setValue(value - 64)  # Convert 0-127 to -64-+63
                elif param == 0x03:
                    self.osc2_sync.setChecked(bool(value))
                    
            # Mix parameters (0x30)
            elif section == 0x30:
                if param == 0x00:
                    self.osc_mix.setValue(value)
                elif param == 0x01:
                    self.cross_mod.setValue(value)
                    
            # Filter parameters (0x40)
            elif section == 0x40:
                if param == 0x00:
                    self.cutoff.setValue(value)
                elif param == 0x01:
                    self.resonance.setValue(value)
                elif param == 0x02:
                    self.key_follow.setValue(value - 64)  # Convert 0-127 to -64-+63
                elif param == 0x03:
                    self.filter_attack.setValue(value)
                elif param == 0x04:
                    self.filter_decay.setValue(value)
                elif param == 0x05:
                    self.filter_sustain.setValue(value)
                elif param == 0x06:
                    self.filter_release.setValue(value)
                elif param == 0x07:
                    self.env_depth.setValue(value - 64)  # Convert 0-127 to -64-+63
                    
            # Amp parameters (0x50)
            elif section == 0x50:
                if param == 0x00:
                    self.amp_level.setValue(value)
                elif param == 0x01:
                    self.velocity_sens.setValue(value - 64)  # Convert 0-127 to -64-+63
                elif param == 0x02:
                    self.amp_attack.setValue(value)
                elif param == 0x03:
                    self.amp_decay.setValue(value)
                elif param == 0x04:
                    self.amp_sustain.setValue(value)
                elif param == 0x05:
                    self.amp_release.setValue(value)
                    
            # LFO parameters (0x60)
            elif section == 0x60:
                if param == 0x00:
                    self.lfo_wave.setCurrentIndex(value)
                elif param == 0x01:
                    self.lfo_sync.setChecked(bool(value))
                elif param == 0x02:
                    self.lfo_rate.setValue(value)
                elif param == 0x03:
                    self.lfo_note.setCurrentIndex(value)
                elif param == 0x04:
                    self.lfo_key_trigger.setChecked(bool(value))
                elif param == 0x05:
                    self.lfo_fade.setValue(value)
                elif param == 0x06:
                    self.lfo_pitch.setValue(value)
                elif param == 0x07:
                    self.lfo_filter.setValue(value)
                elif param == 0x08:
                    self.lfo_amp.setValue(value)
                    
            # Modulation Matrix (0x70)
            elif section == 0x70:
                if param == 0x00:
                    self.mod_source.setCurrentIndex(value)
                elif param == 0x01:
                    self.mod_dest.setCurrentIndex(value)
                elif param == 0x02:
                    self.mod_depth.setValue(value - 64)  # Convert 0-127 to -64-+63
                    
            logging.debug(f"Updated analog synth parameter - Section: {hex(section)}, Param: {hex(param)}, Value: {value}")
            
        except Exception as e:
            logging.error(f"Error updating UI from SysEx: {str(e)}") 