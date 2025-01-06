from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QFrame, QLabel, QPushButton,
    QComboBox, QSpinBox, QLineEdit
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor
from ...data import SN1, SN2
from ...midi import MIDIHelper
from ..style import Style
from ..widgets import Slider, WaveformButton

class DigitalSynthEditor(QMainWindow):
    def __init__(self, midi_out=None, synth_num=1):
        super().__init__()
        self.synth_num = synth_num
        self.midi_out = midi_out
        
        # Initialize control lists
        self.wave_buttons = []
        self.pitch_sliders = []
        self.fine_sliders = []
        self.pwm_sliders = []
        self.cutoff_sliders = []
        self.resonance_sliders = []
        self.keyfollow_sliders = []
        self.filter_env_attack = []
        self.filter_env_decay = []
        self.filter_env_sustain = []
        self.filter_env_release = []
        self.level_sliders = []
        self.velocity_sliders = []
        self.amp_env_attack = []
        self.amp_env_decay = []
        self.amp_env_sustain = []
        self.amp_env_release = []
        
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
                
        # LFO parameters
        self.lfo_wave.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x70, v))  # LFO Wave
        
        self.lfo_sync.toggled.connect(
            lambda v: self._send_parameter(0x71, 1 if v else 0))  # LFO Sync
        
        self.lfo_rate.valueChanged.connect(
            lambda v: self._send_parameter(0x72, v))  # LFO Rate
        
        self.lfo_note.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x73, v))  # LFO Note
        
        self.lfo_key_trigger.toggled.connect(
            lambda v: self._send_parameter(0x74, 1 if v else 0))  # LFO Key Trigger
        
        self.lfo_fade.valueChanged.connect(
            lambda v: self._send_parameter(0x75, v))  # LFO Fade Time
        
        self.lfo_pitch.valueChanged.connect(
            lambda v: self._send_parameter(0x76, v))  # LFO Pitch Depth
        
        self.lfo_filter.valueChanged.connect(
            lambda v: self._send_parameter(0x77, v))  # LFO Filter Depth
        
        self.lfo_amp.valueChanged.connect(
            lambda v: self._send_parameter(0x78, v))  # LFO Amp Depth
        
        # Modulation Matrix
        self.mod_source.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x80, v))  # Mod Source
        
        self.mod_dest.currentIndexChanged.connect(
            lambda v: self._send_parameter(0x81, v))  # Mod Destination
        
        self.mod_depth.valueChanged.connect(
            lambda v: self._send_parameter(0x82, v + 64))  # Mod Depth
        
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
        # Check if it's for this synth (Digital 1 or 2)
        if addr[0] != 0x19 or addr[1] != (0x20 if self.synth_num == 1 else 0x21):
            return
        
        # Common parameters (addr[2] == 0x00)
        if addr[2] == 0x00:
            param = addr[3]
            value = data[0]
            
            if param == 0x00:  # Patch name (12 bytes)
                name = ''.join(chr(b) for b in data[:12]).strip()
                self.patch_name.setText(name)
                
            elif param == 0x01:  # Volume
                self.volume_slider.setValue(value)
                
            elif param == 0x02:  # Pan
                self.pan_slider.setValue(value - 64)
                
            elif param == 0x03:  # Portamento Time
                self.portamento_slider.setValue(value)
                
            elif param == 0x04:  # Portamento Switch
                self.portamento_switch.setChecked(bool(value))
                
            elif param == 0x0D:  # Category
                self.category_combo.setCurrentIndex(value)
                
        # Partial parameters (addr[2] == 0x20-0x22)
        elif 0x20 <= addr[2] <= 0x22:
            partial = addr[2] - 0x20  # 0-2
            param = addr[3]
            value = data[0]
            
            # OSC parameters
            if param == 0x00:  # Wave Type
                self.wave_buttons[partial].current_wave = value
                self.wave_buttons[partial].update()
                
            elif param == 0x01:  # Coarse Tune
                self.pitch_sliders[partial].setValue(value - 64)
                
            elif param == 0x02:  # Fine Tune
                self.fine_sliders[partial].setValue(value - 64)
                
            elif param == 0x03:  # PWM
                self.pwm_sliders[partial].setValue(value)
                
            # FILTER parameters
            elif param == 0x10:  # Cutoff
                self.cutoff_sliders[partial].setValue(value)
                
            elif param == 0x11:  # Resonance
                self.resonance_sliders[partial].setValue(value)
                
            elif param == 0x12:  # Key Follow
                self.keyfollow_sliders[partial].setValue(value - 64)
                
            # Filter Envelope
            elif param == 0x13:  # Attack
                self.filter_env_attack[partial].setValue(value)
                
            elif param == 0x14:  # Decay
                self.filter_env_decay[partial].setValue(value)
                
            elif param == 0x15:  # Sustain
                self.filter_env_sustain[partial].setValue(value)
                
            elif param == 0x16:  # Release
                self.filter_env_release[partial].setValue(value)
                
            # AMP parameters
            elif param == 0x20:  # Level
                self.level_sliders[partial].setValue(value)
                
            elif param == 0x21:  # Velocity Sensitivity
                self.velocity_sliders[partial].setValue(value - 64)
                
            # Amp Envelope
            elif param == 0x22:  # Attack
                self.amp_env_attack[partial].setValue(value)
                
            elif param == 0x23:  # Decay
                self.amp_env_decay[partial].setValue(value)
                
            elif param == 0x24:  # Sustain
                self.amp_env_sustain[partial].setValue(value)
                
            elif param == 0x25:  # Release
                self.amp_env_release[partial].setValue(value)
        
        # LFO parameters
        elif param == 0x70:  # LFO Wave
            self.lfo_wave.setCurrentIndex(value)
        
        elif param == 0x71:  # LFO Sync
            self.lfo_sync.setChecked(bool(value))
            self.lfo_note.setVisible(bool(value))
            self.lfo_rate.setVisible(not bool(value))
        
        elif param == 0x72:  # LFO Rate
            self.lfo_rate.setValue(value)
        
        elif param == 0x73:  # LFO Note
            self.lfo_note.setCurrentIndex(value)
        
        elif param == 0x74:  # LFO Key Trigger
            self.lfo_key_trigger.setChecked(bool(value))
        
        elif param == 0x75:  # LFO Fade Time
            self.lfo_fade.setValue(value)
        
        elif param == 0x76:  # LFO Pitch Depth
            self.lfo_pitch.setValue(value)
        
        elif param == 0x77:  # LFO Filter Depth
            self.lfo_filter.setValue(value)
        
        elif param == 0x78:  # LFO Amp Depth
            self.lfo_amp.setValue(value)
        
        # Modulation Matrix
        elif param == 0x80:  # Mod Source
            self.mod_source.setCurrentIndex(value)
        
        elif param == 0x81:  # Mod Destination
            self.mod_dest.setCurrentIndex(value)
        
        elif param == 0x82:  # Mod Depth
            self.mod_depth.setValue(value - 64)
        
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
        
        # Left side controls
        left = QVBoxLayout()
        left.setSpacing(15)
        
        # Patch name with border
        name_frame = QFrame()
        name_frame.setFrameStyle(QFrame.StyledPanel)
        name_layout = QVBoxLayout(name_frame)
        name_layout.addWidget(QLabel("Patch Name"))
        self.patch_name = QLineEdit()
        self.patch_name.setMaxLength(12)
        self.patch_name.setFont(Style.PATCH_NAME_FONT)
        name_layout.addWidget(self.patch_name)
        left.addWidget(name_frame)
        
        # Category in its own frame
        cat_frame = QFrame()
        cat_frame.setFrameStyle(QFrame.StyledPanel)
        cat_layout = QVBoxLayout(cat_frame)
        cat_layout.addWidget(QLabel("Category"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "00: not assigned", "09: Keyboard", "21: Bass", "34: Lead",
            "35: Brass", "36: Strings/Pad", "39: FX/Other", "40: Seq"
        ])
        cat_layout.addWidget(self.category_combo)
        left.addWidget(cat_frame)
        
        controls.addLayout(left, stretch=1)
        
        # Right side controls
        right = QVBoxLayout()
        right.setSpacing(15)
        
        # Volume and Pan in frame
        vol_frame = QFrame()
        vol_frame.setFrameStyle(QFrame.StyledPanel)
        vol_layout = QHBoxLayout(vol_frame)
        self.volume_slider = Slider("Volume", 0, 127)
        self.pan_slider = Slider("Pan", -64, 63, center=True)
        vol_layout.addWidget(self.volume_slider)
        vol_layout.addWidget(self.pan_slider)
        right.addWidget(vol_frame)
        
        # Portamento in frame
        porta_frame = QFrame()
        porta_frame.setFrameStyle(QFrame.StyledPanel)
        porta_layout = QHBoxLayout(porta_frame)
        self.portamento_slider = Slider("Portamento Time", 0, 127)
        self.portamento_switch = QPushButton("Portamento")
        self.portamento_switch.setCheckable(True)
        self.portamento_switch.setFixedWidth(100)
        porta_layout.addWidget(self.portamento_slider)
        porta_layout.addWidget(self.portamento_switch)
        right.addWidget(porta_frame)
        
        controls.addLayout(right, stretch=2)
        layout.addLayout(controls)
        
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
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Oscillator", Style.OSC_BG))
        
        # Controls in horizontal layout
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Wave selection in its own frame
        wave_frame = QFrame()
        wave_frame.setFrameStyle(QFrame.StyledPanel)
        wave_layout = QVBoxLayout(wave_frame)
        wave_layout.addWidget(QLabel("Waveform"))
        wave_btn = WaveformButton()
        self.wave_buttons.append(wave_btn)
        wave_layout.addWidget(wave_btn)
        controls.addWidget(wave_frame)
        
        # Oscillator controls in frame
        params_frame = QFrame()
        params_frame.setFrameStyle(QFrame.StyledPanel)
        params = QVBoxLayout(params_frame)
        pitch_slider = Slider("Pitch", -24, 24, center=True)
        fine_slider = Slider("Fine Tune", -50, 50, center=True)
        pwm_slider = Slider("PWM", 0, 127)
        
        self.pitch_sliders.append(pitch_slider)
        self.fine_sliders.append(fine_slider)
        self.pwm_sliders.append(pwm_slider)
        
        params.addWidget(pitch_slider)
        params.addWidget(fine_slider)
        params.addWidget(pwm_slider)
        controls.addWidget(params_frame)
        
        layout.addLayout(controls)
        return frame
        
    def _create_filter_section(self, partial_num):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Filter", Style.VCF_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Filter parameters frame
        params_frame = QFrame()
        params_frame.setFrameStyle(QFrame.StyledPanel)
        params_layout = QVBoxLayout(params_frame)
        params_layout.setSpacing(10)
        
        # Cutoff and Resonance
        cutoff = Slider("Cutoff", 0, 127)
        resonance = Slider("Resonance", 0, 127)
        keyfollow = Slider("Key Follow", -100, 100, center=True)
        
        self.cutoff_sliders.append(cutoff)
        self.resonance_sliders.append(resonance)
        self.keyfollow_sliders.append(keyfollow)
        
        params_layout.addWidget(cutoff)
        params_layout.addWidget(resonance)
        params_layout.addWidget(keyfollow)
        controls.addWidget(params_frame)
        
        # Filter envelope frame
        env_frame = QFrame()
        env_frame.setFrameStyle(QFrame.StyledPanel)
        env_layout = QVBoxLayout(env_frame)
        env_layout.setSpacing(10)
        
        # Add envelope label
        env_header = QLabel("Envelope")
        env_header.setStyleSheet("font-weight: bold;")
        env_layout.addWidget(env_header)
        
        # ADSR controls
        attack = Slider("Attack", 0, 127)
        decay = Slider("Decay", 0, 127)
        sustain = Slider("Sustain", 0, 127)
        release = Slider("Release", 0, 127)
        
        self.filter_env_attack.append(attack)
        self.filter_env_decay.append(decay)
        self.filter_env_sustain.append(sustain)
        self.filter_env_release.append(release)
        
        env_layout.addWidget(attack)
        env_layout.addWidget(decay)
        env_layout.addWidget(sustain)
        env_layout.addWidget(release)
        controls.addWidget(env_frame)
        
        layout.addLayout(controls)
        return frame
        
    def _create_amplifier_section(self, partial_num):
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add header
        layout.addWidget(self._create_section_header("Amplifier", Style.AMP_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # Level controls frame
        level_frame = QFrame()
        level_frame.setFrameStyle(QFrame.StyledPanel)
        level_layout = QVBoxLayout(level_frame)
        level_layout.setSpacing(10)
        
        # Add level label
        level_header = QLabel("Level")
        level_header.setStyleSheet("font-weight: bold;")
        level_layout.addWidget(level_header)
        
        # Level and velocity controls
        level = Slider("Level", 0, 127)
        velocity = Slider("Velocity Sens", -63, 63, center=True)
        
        self.level_sliders.append(level)
        self.velocity_sliders.append(velocity)
        
        level_layout.addWidget(level)
        level_layout.addWidget(velocity)
        controls.addWidget(level_frame)
        
        # Amp envelope frame
        env_frame = QFrame()
        env_frame.setFrameStyle(QFrame.StyledPanel)
        env_layout = QVBoxLayout(env_frame)
        env_layout.setSpacing(10)
        
        # Add envelope label
        env_header = QLabel("Envelope")
        env_header.setStyleSheet("font-weight: bold;")
        env_layout.addWidget(env_header)
        
        # ADSR controls
        attack = Slider("Attack", 0, 127)
        decay = Slider("Decay", 0, 127)
        sustain = Slider("Sustain", 0, 127)
        release = Slider("Release", 0, 127)
        
        self.amp_env_attack.append(attack)
        self.amp_env_decay.append(decay)
        self.amp_env_sustain.append(sustain)
        self.amp_env_release.append(release)
        
        env_layout.addWidget(attack)
        env_layout.addWidget(decay)
        env_layout.addWidget(sustain)
        env_layout.addWidget(release)
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
        layout.addWidget(self._create_section_header("Modulation", Style.LFO_BG))
        
        # Controls container
        controls = QHBoxLayout()
        controls.setSpacing(20)
        
        # LFO Frame
        lfo_frame = QFrame()
        lfo_frame.setFrameStyle(QFrame.StyledPanel)
        lfo_layout = QVBoxLayout(lfo_frame)
        lfo_layout.setSpacing(10)
        
        # LFO Wave selection
        wave_layout = QHBoxLayout()
        wave_layout.addWidget(QLabel("Waveform:"))
        self.lfo_wave = QComboBox()
        self.lfo_wave.addItems(["Triangle", "Sine", "Square", "Sample & Hold", "Random"])
        wave_layout.addWidget(self.lfo_wave)
        lfo_layout.addLayout(wave_layout)
        
        # Rate controls in frame
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
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.StyledPanel)
        controls_layout = QVBoxLayout(controls_frame)
        
        self.lfo_key_trigger = QPushButton("Key Trigger")
        self.lfo_key_trigger.setCheckable(True)
        self.lfo_key_trigger.setFixedWidth(80)
        controls_layout.addWidget(self.lfo_key_trigger)
        
        self.lfo_fade = Slider("Fade Time", 0, 127)
        controls_layout.addWidget(self.lfo_fade)
        lfo_layout.addWidget(controls_frame)
        
        # LFO Depths in frame
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
        
        # Modulation Matrix frame
        mod_frame = QFrame()
        mod_frame.setFrameStyle(QFrame.StyledPanel)
        mod_layout = QVBoxLayout(mod_frame)
        mod_layout.setSpacing(10)
        
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