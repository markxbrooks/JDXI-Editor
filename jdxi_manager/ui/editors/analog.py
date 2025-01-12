from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFrame, QLabel, QComboBox, QCheckBox, QPushButton,
    QGroupBox, QTabWidget, QScrollArea, QListWidget, QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import logging
from typing import Optional

from jdxi_manager.ui.style import Style
from jdxi_manager.ui.widgets import Slider, WaveformButton
from jdxi_manager.ui.widgets.preset_panel import PresetPanel
from jdxi_manager.midi import MIDIHelper
from jdxi_manager.midi.messages import (
    create_sysex_message,
    create_patch_load_message,
    create_patch_save_message,
    JDXiSysEx
)
from jdxi_manager.midi.constants import (
    START_OF_SYSEX, ROLAND_ID, DEVICE_ID, MODEL_ID_1, MODEL_ID_2,
    MODEL_ID, JD_XI_ID, DT1_COMMAND_12, RQ1_COMMAND_11, END_OF_SYSEX,
    ANALOG_SYNTH_AREA, ANALOG_PART,
    PROGRAM_GROUP, COMMON_GROUP, PARTIAL_GROUP,
    SUBGROUP_ZERO,
    Waveform, AnalogParameter, AnalogLFO, AnalogLFOSync
)
from jdxi_manager.data.analog import (
    AnalogOscillator,
    AnalogFilter,
    AnalogAmplifier,
    AnalogLFO,
    AnalogEnvelope,
    AnalogSynthPatch, ANALOG_PRESETS
)
from jdxi_manager.ui.editors.base_editor import BaseEditor

class AnalogSynthEditor(BaseEditor):
    """Analog synth patch editor window"""
    
    def __init__(self, midi_helper: Optional[MIDIHelper] = None, parent: Optional[QWidget] = None):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Analog Synth Editor")
        
        # Set up area and part for parameter requests
        self.area = ANALOG_SYNTH_AREA
        self.part = ANALOG_PART
        self.group = 0x00
        self.start_param = 0x16  # Start from OSC section
        self.param_size = 0x40   # Request 64 bytes to cover parameters
        
        # Store references
        self.midi_helper = midi_helper
        self.main_window = parent
        self.current_patch = AnalogSynthPatch()
        
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
        
        # Create horizontal layout for presets and editor
        h_layout = QHBoxLayout()
        
        # Add preset list to left side
        preset_frame = QFrame()
        preset_frame.setFrameStyle(QFrame.StyledPanel)
        preset_layout = QVBoxLayout(preset_frame)
        preset_layout.addWidget(QLabel("Presets"))
        
        # Create and setup preset list
        self.preset_list = QListWidget()
        self.preset_list.addItems(ANALOG_PRESETS.keys())
        self.preset_list.currentItemChanged.connect(self._load_preset)
        preset_layout.addWidget(self.preset_list)
        
        # Add save preset button
        save_btn = QPushButton("Save as Preset")
        save_btn.clicked.connect(self._save_preset)
        preset_layout.addWidget(save_btn)
        
        h_layout.addWidget(preset_frame)
        
        # Create sections container
        sections = QVBoxLayout()
        sections.setSpacing(20)
        
        # Add all sections vertically
        sections.addWidget(self._create_oscillator_section(1))
        sections.addWidget(self._create_oscillator_section(2))
        sections.addWidget(self._create_mixer_section())
        sections.addWidget(self._create_filter_section())
        sections.addWidget(self._create_amp_section())
        sections.addWidget(self._create_lfo_section())
        sections.addWidget(self._create_envelope_section("PITCH"))
        sections.addWidget(self._create_envelope_section("FILTER"))
        sections.addWidget(self._create_envelope_section("AMP"))
        sections.addWidget(self._create_performance_section())
        
        # Add sections to horizontal layout
        h_layout.addLayout(sections)
        
        # Add horizontal layout to main layout
        layout.addLayout(h_layout)
        
        # Set the widget to scroll area
        scroll.setWidget(central)
        
        # Request current patch data
        self._request_patch_data()
        
    def _load_preset(self, current, previous):
        """Load selected preset"""
        if not current:
            return
            
        preset_name = current.text()
        if preset_name in ANALOG_PRESETS:
            preset = ANALOG_PRESETS[preset_name]
            for param, value in preset.items():
                self._send_parameter(param, value)
            logging.debug(f"Loaded preset: {preset_name}")
            
    def _save_preset(self):
        """Save current settings as new preset"""
        name, ok = QInputDialog.getText(self, 'Save Preset', 'Enter preset name:')
        if ok and name:
            # Collect current parameter values
            preset = {}
            # Add code to collect current parameter values
            
            # Add to presets
            ANALOG_PRESETS[name] = preset
            
            # Update preset list
            self.preset_list.addItem(name)
            logging.debug(f"Saved new preset: {name}")
            
    def _create_editor_controls(self, layout):
        """Create the editor control sections"""
        # Add all sections vertically
        # Oscillators
        layout.addWidget(self._create_oscillator_section(1))
        layout.addWidget(self._create_oscillator_section(2))
        
        # Mixer
        layout.addWidget(self._create_mixer_section())
        
        # Filter
        layout.addWidget(self._create_filter_section())
        
        # Amplifier
        layout.addWidget(self._create_amp_section())
        
        # LFO
        layout.addWidget(self._create_lfo_section())
        
        # Add stretch at the bottom
        layout.addStretch()

    def _create_section_header(self, text: str, bg_color: str) -> QLabel:
        """Create a section header label
        
        Args:
            text: Header text
            bg_color: Background color from Style class
            
        Returns:
            QLabel with styled header
        """
        header = QLabel(text)
        header.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: white;
                padding: 5px;
                font-weight: bold;
                border-radius: 4px;
            }}
        """)
        return header
        
    def _create_oscillator_section(self, osc_num: int):
        """Create oscillator section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header(f"OSC {osc_num}", Style.OSC_BG))
        
        # Waveform selector
        wave = QComboBox()
        wave.setObjectName("osc_wave_control")
        wave.addItems(['SAW', 'TRI', 'PW-SQR'])
        wave.currentIndexChanged.connect(
            lambda idx: self._send_parameter(AnalogParameter.OSC1_WAVE.value, idx)
        )
        layout.addWidget(wave)
        
        # Pitch Coarse
        pitch = Slider(
            "Pitch", -24, 24,
            callback=lambda v: self._send_parameter(AnalogParameter.OSC1_PITCH.value, v + 64)
        )
        pitch.setObjectName("osc_pitch_control")
        layout.addWidget(pitch)
        
        # Pitch Fine
        fine = Slider(
            "Fine", -50, 50,
            callback=lambda v: self._send_parameter(AnalogParameter.OSC1_FINE.value, v + 64)
        )
        fine.setObjectName("osc_fine_control")
        layout.addWidget(fine)
        
        # Pulse Width
        pw = Slider(
            "Pulse Width", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.OSC1_PW.value, v)
        )
        layout.addWidget(pw)
        
        # PW Mod Depth
        pwm = Slider(
            "PW Mod Depth", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.OSC1_PWM.value, v)
        )
        layout.addWidget(pwm)
        
        # Pitch Envelope controls
        # Velocity (0x1B: 1-127 maps to -63 - +63)
        pitch_velo = Slider(
            "Pitch Env Velocity", -63, 63,
            lambda v: self._send_parameter(AnalogParameter.OSC_PITCH_VELO.value, v + 64)
        )
        layout.addWidget(pitch_velo)
        
        # Attack (0x1C: 0-127)
        pitch_atk = Slider(
            "Pitch Env Attack", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.OSC_PITCH_ATK.value, v)
        )
        layout.addWidget(pitch_atk)
        
        # Decay (0x1D: 0-127)
        pitch_dec = Slider(
            "Pitch Env Decay", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.OSC_PITCH_DEC.value, v)
        )
        layout.addWidget(pitch_dec)
        
        # Depth (0x1E: 1-127 maps to -63 - +63)
        pitch_depth = Slider(
            "Pitch Env Depth", -63, 63,
            lambda v: self._send_parameter(AnalogParameter.OSC_PITCH_DEPTH.value, v + 64)
        )
        layout.addWidget(pitch_depth)
        
        # Sub oscillator type
        if osc_num == 1:
            sub_type = QComboBox()
            sub_type.addItems(['OFF', 'OCT-1', 'OCT-2'])
            sub_type.currentIndexChanged.connect(
                lambda idx: self._send_parameter(AnalogParameter.SUB_OSC_TYPE.value, idx)
            )
        
        return frame

    def _create_mixer_section(self):
        """Create mixer section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("MIXER", Style.MIX_BG))
        
        # OSC Balance (0x3C: 1-127 maps to -63 - +63)
        balance = Slider(
            "OSC Balance", -63, 63,
            lambda v: self._send_parameter(0x3C, v + 64)
        )
        layout.addWidget(balance)
        
        # Noise Level (0x3D: 0-127)
        noise = Slider(
            "Noise Level", 0, 127,
            lambda v: self._send_parameter(0x3D, v)
        )
        layout.addWidget(noise)
        
        # Ring Mod Level (0x3E: 0-127)
        ring_mod = Slider(
            "Ring Mod Level", 0, 127,
            lambda v: self._send_parameter(0x3E, v)
        )
        layout.addWidget(ring_mod)
        
        # Cross Mod Depth (0x3F: 0-127)
        cross_mod = Slider(
            "Cross Mod Depth", 0, 127,
            lambda v: self._send_parameter(0x3F, v)
        )
        layout.addWidget(cross_mod)
        
        return frame

    def _send_parameter(self, param: int, value: int):
        """Send analog synth parameter change with value validation"""
        try:
            # Convert enum to value if needed
            if isinstance(param, AnalogParameter):
                param = param.value
                
            # Validate parameter value using enum class method
            if not AnalogParameter.validate_value(param, value):
                logging.error(f"Parameter value {value} out of range for param {hex(param)}")
                return
                
            msg = JDXiSysEx.create_parameter_message(
                area=ANALOG_SYNTH_AREA,
                part=0x00,
                group=0x00,
                param=param,
                value=value
            )
            
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                display_value = AnalogParameter.get_display_value(param, value)
                logging.debug(f"Sent analog parameter: {hex(param)}={display_value}")
                
        except Exception as e:
            logging.error(f"Error sending analog parameter: {str(e)}")

    def _update_ui_from_patch(self):
        """Update UI controls from current patch data"""
        try:
            # Update OSC1 controls
            self.osc1_wave.setWaveform(self.current_patch.osc1.wave)
            self.osc1_range.setValue(self.current_patch.osc1.range)
            self.osc1_fine.setValue(self.current_patch.osc1.fine)
            self.osc1_detune.setValue(self.current_patch.osc1.detune)
            
            # Update OSC2 controls
            self.osc2_wave.setWaveform(self.current_patch.osc2.wave)
            self.osc2_range.setValue(self.current_patch.osc2.range)
            self.osc2_fine.setValue(self.current_patch.osc2.fine)
            self.osc2_detune.setValue(self.current_patch.osc2.detune)
            self.osc2_sync.setChecked(self.current_patch.osc2.sync)
            
            # Update mixer controls
            self.mix_balance.setValue(self.current_patch.mixer.osc_balance)
            self.mix_noise.setValue(self.current_patch.mixer.noise_level)
            self.mix_ring.setValue(self.current_patch.mixer.ring_mod)
            self.mix_cross.setValue(self.current_patch.mixer.cross_mod)
            
            # Continue updating other sections...
            
        except Exception as e:
            logging.error(f"Error updating UI from patch: {str(e)}") 
        
    def _create_filter_section(self):
        """Create filter section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("FILTER", Style.VCF_BG))
        
        # Filter type selector (0x20: 0-1)
        filter_type = QComboBox()
        filter_type.setObjectName("filter_type_control")
        filter_type.addItems(['BYPASS', 'LPF'])
        filter_type.currentIndexChanged.connect(
            lambda idx: self._send_parameter(0x20, idx)
        )
        layout.addWidget(filter_type)
        
        # Cutoff control (0x21: 0-127)
        cutoff = Slider(
            "Cutoff", 0, 127,
            lambda v: self._send_parameter(0x21, v)
        )
        cutoff.setObjectName("filter_cutoff_control")
        layout.addWidget(cutoff)
        
        # Keyfollow (0x22: 54-74 maps to -100 - +100)
        keyfollow = Slider(
            "Keyfollow", -100, 100,
            lambda v: self._send_parameter(0x22, int(((v + 100) * 20 / 200) + 54))
        )
        layout.addWidget(keyfollow)
        
        # Resonance (0x23: 0-127)
        resonance = Slider(
            "Resonance", 0, 127,
            lambda v: self._send_parameter(0x23, v)
        )
        layout.addWidget(resonance)
        
        # Filter envelope controls
        # Velocity sensitivity (0x24: 1-127 maps to -63 - +63)
        env_velo = Slider(
            "Env Velocity", -63, 63,
            lambda v: self._send_parameter(0x24, v + 64)
        )
        layout.addWidget(env_velo)
        
        # ADSR controls (0x25-0x28: all 0-127)
        env_atk = Slider(
            "Attack", 0, 127,
            lambda v: self._send_parameter(0x25, v)
        )
        layout.addWidget(env_atk)
        
        env_dec = Slider(
            "Decay", 0, 127,
            lambda v: self._send_parameter(0x26, v)
        )
        layout.addWidget(env_dec)
        
        env_sus = Slider(
            "Sustain", 0, 127,
            lambda v: self._send_parameter(0x27, v)
        )
        layout.addWidget(env_sus)
        
        env_rel = Slider(
            "Release", 0, 127,
            lambda v: self._send_parameter(0x28, v)
        )
        layout.addWidget(env_rel)
        
        # Envelope depth (0x29: 1-127 maps to -63 - +63)
        env_depth = Slider(
            "Env Depth", -63, 63,
            lambda v: self._send_parameter(0x29, v + 64)
        )
        layout.addWidget(env_depth)
        
        return frame

    def _create_amp_section(self):
        """Create amplifier section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("AMP", Style.VCA_BG))
        
        # Level control (0x2A: 0-127)
        level = Slider(
            "Level", 0, 127,
            lambda v: self._send_parameter(0x2A, v)
        )
        level.setObjectName("amp_level_control")
        layout.addWidget(level)
        
        # Keyfollow (0x2B: 54-74 maps to -100 - +100)
        keyfollow = Slider(
            "Keyfollow", -100, 100,
            lambda v: self._send_parameter(0x2B, int(((v + 100) * 20 / 200) + 54))
        )
        layout.addWidget(keyfollow)
        
        # Velocity sensitivity (0x2C: 1-127 maps to -63 - +63)
        velocity = Slider(
            "Velocity Sens", -63, 63,
            lambda v: self._send_parameter(0x2C, v + 64)
        )
        layout.addWidget(velocity)
        
        # ADSR envelope controls (0x2D-0x30: all 0-127)
        env_atk = Slider(
            "Attack", 0, 127,
            lambda v: self._send_parameter(0x2D, v)
        )
        layout.addWidget(env_atk)
        
        env_dec = Slider(
            "Decay", 0, 127,
            lambda v: self._send_parameter(0x2E, v)
        )
        layout.addWidget(env_dec)
        
        env_sus = Slider(
            "Sustain", 0, 127,
            lambda v: self._send_parameter(0x2F, v)
        )
        layout.addWidget(env_sus)
        
        env_rel = Slider(
            "Release", 0, 127,
            lambda v: self._send_parameter(0x30, v)
        )
        layout.addWidget(env_rel)
        
        return frame
        
    def _create_lfo_section(self):
        """Create LFO section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("LFO", Style.LFO_BG))
        
        # LFO Shape
        shape = QComboBox()
        shape.setObjectName("lfo_wave_control")
        shape.addItems(['TRI', 'SIN', 'SAW', 'SQR', 'S&H', 'RND'])
        shape.currentIndexChanged.connect(
            lambda idx: self._send_parameter(0x0D, idx)
        )
        layout.addWidget(shape)
        
        # Rate
        rate = Slider("Rate", 0, 127,
            lambda v: self._send_parameter(0x0E, v))
        rate.setObjectName("lfo_rate_control")
        
        # Fade Time
        fade = Slider("Fade Time", 0, 127,
            lambda v: self._send_parameter(0x0F, v))
        fade.setObjectName("lfo_fade_control")
        
        # Tempo Sync switch
        sync_sw = QCheckBox("Tempo Sync")
        sync_sw.setObjectName("lfo_sync_control")
        
        # Sync Note selector
        sync_note = QComboBox()
        sync_note.setObjectName("lfo_sync_note_control")
        
        # Depth controls
        pitch_depth = Slider("Pitch Depth", -63, 63,
            lambda v: self._send_parameter(0x12, v + 64))
        pitch_depth.setObjectName("lfo_pitch_depth_control")
        
        filter_depth = Slider("Filter Depth", -63, 63,
            lambda v: self._send_parameter(0x13, v + 64))
        filter_depth.setObjectName("lfo_filter_depth_control")
        
        amp_depth = Slider("Amp Depth", -63, 63,
            lambda v: self._send_parameter(0x14, v + 64))
        amp_depth.setObjectName("lfo_amp_depth_control")
        
        # Key Trigger switch
        key_trig = QCheckBox("Key Trigger")
        key_trig.setObjectName("lfo_key_trigger_control")
        
        # Modulation controls
        pitch_mod = Slider("Pitch Mod", -63, 63,
            lambda v: self._send_parameter(0x38, v + 64))
        pitch_mod.setObjectName("mod_pitch_control")
        
        filter_mod = Slider("Filter Mod", -63, 63,
            lambda v: self._send_parameter(0x39, v + 64))
        filter_mod.setObjectName("mod_filter_control")
        
        amp_mod = Slider("Amp Mod", -63, 63,
            lambda v: self._send_parameter(0x3A, v + 64))
        amp_mod.setObjectName("mod_amp_control")
        
        rate_mod = Slider("Rate Mod", -63, 63,
            lambda v: self._send_parameter(0x3B, v + 64))
        rate_mod.setObjectName("mod_rate_control")
        
        return frame

    def _create_envelope_section(self, env_type: str):
        """Create envelope section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header with appropriate background color
        bg_color = {
            "PITCH": Style.PITCH_ENV_BG,
            "FILTER": Style.VCF_ENV_BG,
            "AMP": Style.VCA_ENV_BG
        }[env_type]
        layout.addWidget(self._create_section_header(f"{env_type} ENV", bg_color))
        
        # Get correct parameter addresses based on envelope type
        params = {
            "PITCH": {
                "attack": 0x1C,    # OSC Pitch Env Attack Time
                "decay": 0x1D,     # OSC Pitch Env Decay
                "depth": 0x1E,     # OSC Pitch Env Depth
                "velo": 0x1B       # OSC Pitch Env Velocity Sens
            },
            "FILTER": {
                "attack": 0x25,    # Filter Env Attack Time
                "decay": 0x26,     # Filter Env Decay Time
                "sustain": 0x27,   # Filter Env Sustain Level
                "release": 0x28,   # Filter Env Release Time
                "depth": 0x29,     # Filter Env Depth
                "velo": 0x24       # Filter Env Velocity Sens
            },
            "AMP": {
                "attack": 0x2D,    # AMP Env Attack Time
                "decay": 0x2E,     # AMP Env Decay Time
                "sustain": 0x2F,   # AMP Env Sustain Level
                "release": 0x30,   # AMP Env Release Time
                "velo": 0x2C       # AMP Level Velocity Sens
            }
        }[env_type]
        
        # Create ADSR controls with correct parameters
        if "attack" in params:
            attack = Slider(
                "Attack", 0, 127,
                lambda v: self._send_parameter(params["attack"], v)
            )
            layout.addWidget(attack)
            
        if "decay" in params:
            decay = Slider(
                "Decay", 0, 127,
                lambda v: self._send_parameter(params["decay"], v)
            )
            layout.addWidget(decay)
            
        if "sustain" in params:
            sustain = Slider(
                "Sustain", 0, 127,
                lambda v: self._send_parameter(params["sustain"], v)
            )
            layout.addWidget(sustain)
            
        if "release" in params:
            release = Slider(
                "Release", 0, 127,
                lambda v: self._send_parameter(params["release"], v)
            )
            layout.addWidget(release)
            
        if "depth" in params:
            depth = Slider(
                "Depth", -63, 63,
                lambda v: self._send_parameter(params["depth"], v + 64)
            )
            layout.addWidget(depth)
            
        if "velo" in params:
            velo = Slider(
                "Velocity", -63, 63,
                lambda v: self._send_parameter(params["velo"], v + 64)
            )
            layout.addWidget(velo)
        
        return frame
        
    def _create_ui(self):
        """Create the complete user interface"""
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
        
        # Add preset panel at the top
        self.preset_panel = PresetPanel('analog', self)
        layout.addWidget(self.preset_panel)
        
        # Create sections container
        sections = QVBoxLayout()
        sections.setSpacing(20)
        
        # Add all sections vertically
        # Oscillators
        sections.addWidget(self._create_oscillator_section(1))
        sections.addWidget(self._create_oscillator_section(2))
        
        # Mixer
        sections.addWidget(self._create_mixer_section())
        
        # Filter
        sections.addWidget(self._create_filter_section())
        
        # Amplifier
        sections.addWidget(self._create_amp_section())
        
        # LFO
        sections.addWidget(self._create_lfo_section())
        
        # Envelopes
        sections.addWidget(self._create_envelope_section("PITCH"))
        sections.addWidget(self._create_envelope_section("FILTER"))
        sections.addWidget(self._create_envelope_section("AMP"))
        
        # Add performance section
        sections.addWidget(self._create_performance_section())
        
        # Add sections to main layout
        layout.addLayout(sections)
        
        # Add stretch at the bottom
        layout.addStretch()
        
        # Set the widget to scroll area
        scroll.setWidget(central)
            
    def _request_patch_data(self):
        """Request current patch data from synth"""
        try:
            # Request parameters starting from OSC section (0x16)
            msg = JDXiSysEx.create_parameter_request(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,      # First byte of address (00)
                param=0x16,      # Second byte of address (16)
                size=0x40        # Request 64 bytes to cover all parameters
            )
            
            if self.midi_helper:
                self.midi_helper.send_message(msg)
                logging.debug(f"Requested analog patch data starting from {hex(0x16)}")
            else:
                logging.warning("No MIDI helper available - cannot request patch data")
            
        except Exception as e:
            logging.error(f"Error requesting patch data: {str(e)}")
            
    def _handle_midi_input(self, msg):
        """Handle incoming MIDI messages"""
        try:
        # Check if it's a SysEx message
            if msg[0] == START_OF_SYSEX and msg[-1] == END_OF_SYSEX:
                # Extract address and data
                addr = msg[8:12]  # 4 bytes of address
                data = msg[12:-2]  # Data bytes (excluding checksum and end of sysex)
                
                # Update UI based on received data
                self._update_ui_from_sysex(addr, data)
                logging.debug(f"Received patch data: addr={[hex(b) for b in addr]}, data={[hex(b) for b in data]}")
                
        except Exception as e:
            logging.error(f"Error handling MIDI input: {str(e)}")

    def _update_ui_from_sysex(self, addr, data):
        """Update UI controls based on received SysEx data"""
        try:
            param = addr[3]  # Parameter number is in fourth byte
            value = data[0]  # First data byte is the value
            
            # Update UI based on parameter type
            if 0x16 <= param <= 0x1F:  # Oscillator parameters
                self._update_oscillator_controls(param, value)
            elif 0x20 <= param <= 0x29:  # Filter parameters
                self._update_filter_controls(param, value)
            elif 0x2A <= param <= 0x30:  # Amp parameters
                self._update_amp_controls(param, value)
            # ... etc for other parameter ranges
            
        except Exception as e:
            logging.error(f"Error updating analog UI: {str(e)}")

    def _create_performance_section(self):
        """Create performance controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("PERFORMANCE", Style.PERF_BG))
        
        # Portamento switch (0x31: 0-1)
        porta_sw = QCheckBox("Portamento")
        porta_sw.toggled.connect(
            lambda v: self._send_parameter(0x31, int(v))
        )
        layout.addWidget(porta_sw)
        
        # Portamento time (0x32: 0-127)
        porta_time = Slider(
            "Portamento Time", 0, 127,
            lambda v: self._send_parameter(0x32, v)
        )
        layout.addWidget(porta_time)
        
        # Legato switch (0x33: 0-1)
        legato_sw = QCheckBox("Legato")
        legato_sw.toggled.connect(
            lambda v: self._send_parameter(0x33, int(v))
        )
        layout.addWidget(legato_sw)
        
        # Octave shift (0x34: 61-67 maps to -3 - +3)
        octave = Slider(
            "Octave Shift", -3, 3,
            lambda v: self._send_parameter(0x34, v + 64)  # Center at 64
        )
        layout.addWidget(octave)
        
        # Pitch bend ranges (0x35, 0x36: 0-24)
        bend_up = Slider(
            "Bend Range Up", 0, 24,
            lambda v: self._send_parameter(0x35, v)
        )
        layout.addWidget(bend_up)
        
        bend_down = Slider(
            "Bend Range Down", 0, 24,
            lambda v: self._send_parameter(0x36, v)
        )
        layout.addWidget(bend_down)
        
        return frame 

    def _handle_parameter_change(self, parameter: str, value: int):
        """Handle parameter change from synth"""
        try:
            if not hasattr(self.current_patch, parameter.lower()):
                logging.warning(f"Unknown parameter received: {parameter}")
            return
            
            setattr(self.current_patch, parameter.lower(), value)
            logging.debug(f"Updated parameter {parameter}: {value}")
            
            # Update UI if needed
            self._update_ui_for_parameter(parameter, value)
            
        except Exception as e:
            logging.error(f"Error handling parameter change {parameter}: {str(e)}")
            
    def _update_ui_for_parameter(self, parameter: str, value: int):
        """Update UI controls for parameter change"""
        try:
            # Find and update the corresponding control
            control = self.findChild(QWidget, f"{parameter.lower()}_control")
            if control and hasattr(control, 'setValue'):
                control.setValue(value)
                logging.debug(f"Updated UI control for {parameter}")
            
        except Exception as e:
            logging.error(f"Error updating UI for {parameter}: {str(e)}") 

    def _update_oscillator_controls(self, param: int, value: int):
        """Update oscillator controls based on received parameter
        
        Args:
            param: Parameter number (0x16-0x1F)
            value: Parameter value
        """
        try:
            # Find the control by its object name
            control_map = {
                0x16: "osc_wave",           # Waveform selector
                0x17: "osc_pitch",          # Pitch coarse
                0x18: "osc_fine",           # Pitch fine
                0x19: "osc_pw",             # Pulse width
                0x1A: "osc_pwm",            # PWM depth
                0x1B: "pitch_env_velo",     # Pitch envelope velocity
                0x1C: "pitch_env_attack",   # Pitch envelope attack
                0x1D: "pitch_env_decay",    # Pitch envelope decay
                0x1E: "pitch_env_depth",    # Pitch envelope depth
                0x1F: "sub_osc_type"        # Sub oscillator type
            }
            
            if param not in control_map:
                logging.warning(f"Unknown oscillator parameter: {hex(param)}")
                return
            
            control_name = control_map[param]
            control = self.findChild(QWidget, f"{control_name}_control")
            
            if not control:
                logging.warning(f"Control not found: {control_name}")
                return
            
            # Convert value based on parameter type
            if param == 0x16:  # Waveform
                # QComboBox for waveform
                control.setCurrentIndex(value)
            
            elif param == 0x17:  # Pitch coarse (-24 to +24)
                # Slider centered at 64
                control.setValue(value - 64)
            
            elif param == 0x18:  # Pitch fine (-50 to +50)
                # Slider centered at 64
                control.setValue(value - 64)
            
            elif param in (0x19, 0x1A, 0x1C, 0x1D):  # Direct 0-127 values
                # Regular sliders
                control.setValue(value)
            
            elif param in (0x1B, 0x1E):  # Bipolar -63 to +63
                # Sliders centered at 64
                control.setValue(value - 64)
            
            elif param == 0x1F:  # Sub oscillator type
                # QComboBox for sub osc type
                control.setCurrentIndex(value)
            
            logging.debug(f"Updated oscillator control {control_name}: {value}")
            
        except Exception as e:
            logging.error(f"Error updating oscillator control: {str(e)}") 

    def _update_filter_controls(self, param: int, value: int):
        """Update filter controls based on received parameter
        
        Args:
            param: Parameter number (0x20-0x29)
            value: Parameter value
        """
        try:
            # Find the control by its object name
            control_map = {
                0x20: "filter_type",        # Filter type selector
                0x21: "filter_cutoff",      # Cutoff frequency
                0x22: "filter_keyfollow",   # Key follow
                0x23: "filter_resonance",   # Resonance
                0x24: "filter_env_velo",    # Envelope velocity
                0x25: "filter_env_attack",  # Attack time
                0x26: "filter_env_decay",   # Decay time
                0x27: "filter_env_sustain", # Sustain level
                0x28: "filter_env_release", # Release time
                0x29: "filter_env_depth"    # Envelope depth
            }
            
            if param not in control_map:
                logging.warning(f"Unknown filter parameter: {hex(param)}")
                return
            
            control_name = control_map[param]
            control = self.findChild(QWidget, f"{control_name}_control")
            
            if not control:
                logging.warning(f"Control not found: {control_name}")
                return
            
            # Convert value based on parameter type
            if param == 0x20:  # Filter type
                # QComboBox for filter type
                control.setCurrentIndex(value)
            
            elif param == 0x21:  # Cutoff (direct 0-127)
                control.setValue(value)
            
            elif param == 0x22:  # Keyfollow (-100 to +100)
                # Convert from 54-74 range to -100 to +100
                normalized = ((value - 54) * 200 / 20) - 100
                control.setValue(int(normalized))
            
            elif param == 0x23:  # Resonance (direct 0-127)
                control.setValue(value)
            
            elif param in (0x24, 0x29):  # Bipolar -63 to +63
                # Velocity sens and env depth
                control.setValue(value - 64)
            
            elif param in (0x25, 0x26, 0x27, 0x28):  # Direct 0-127
                # ADSR controls
                control.setValue(value)
            
            logging.debug(f"Updated filter control {control_name}: {value}")
            
        except Exception as e:
            logging.error(f"Error updating filter control: {str(e)}")

    def _update_amp_controls(self, param: int, value: int):
        """Update amplifier controls based on received parameter
        
        Args:
            param: Parameter number (0x2A-0x30)
            value: Parameter value
        """
        try:
            # Find the control by its object name
            control_map = {
                0x2A: "amp_level",          # Level
                0x2B: "amp_keyfollow",      # Key follow
                0x2C: "amp_velocity",       # Velocity sensitivity
                0x2D: "amp_env_attack",     # Attack time
                0x2E: "amp_env_decay",      # Decay time
                0x2F: "amp_env_sustain",    # Sustain level
                0x30: "amp_env_release"     # Release time
            }
            
            if param not in control_map:
                logging.warning(f"Unknown amp parameter: {hex(param)}")
                return
            
            control_name = control_map[param]
            control = self.findChild(QWidget, f"{control_name}_control")
            
            if not control:
                logging.warning(f"Control not found: {control_name}")
                return
            
            # Convert value based on parameter type
            if param == 0x2A:  # Level (direct 0-127)
                control.setValue(value)
            
            elif param == 0x2B:  # Keyfollow (-100 to +100)
                # Convert from 54-74 range to -100 to +100
                normalized = ((value - 54) * 200 / 20) - 100
                control.setValue(int(normalized))
            
            elif param == 0x2C:  # Velocity sens (-63 to +63)
                control.setValue(value - 64)
            
            elif param in (0x2D, 0x2E, 0x2F, 0x30):  # ADSR (direct 0-127)
                control.setValue(value)
            
            logging.debug(f"Updated amp control {control_name}: {value}")
            
        except Exception as e:
            logging.error(f"Error updating amp control: {str(e)}") 

    def _update_lfo_controls(self, param: int, value: int):
        """Update LFO controls based on received parameter
        
        Args:
            param: Parameter number (0x0D-0x15 for LFO, 0x38-0x3B for modulation)
            value: Parameter value
        """
        try:
            # Find the control by its object name
            control_map = {
                # LFO parameters
                0x0D: "lfo_wave",           # LFO waveform
                0x0E: "lfo_rate",           # Rate
                0x0F: "lfo_fade",           # Fade time
                0x10: "lfo_sync",           # Tempo sync switch
                0x11: "lfo_sync_note",      # Sync note value
                0x12: "lfo_pitch_depth",    # Pitch modulation depth
                0x13: "lfo_filter_depth",   # Filter modulation depth
                0x14: "lfo_amp_depth",      # Amp modulation depth
                0x15: "lfo_key_trigger",    # Key trigger switch
                
                # Modulation parameters
                0x38: "mod_pitch",          # Pitch modulation
                0x39: "mod_filter",         # Filter modulation
                0x3A: "mod_amp",            # Amp modulation
                0x3B: "mod_rate"            # Rate modulation
            }
            
            if param not in control_map:
                logging.warning(f"Unknown LFO parameter: {hex(param)}")
                return
            
            control_name = control_map[param]
            control = self.findChild(QWidget, f"{control_name}_control")
            
            if not control:
                logging.warning(f"Control not found: {control_name}")
                return
            
            # Convert value based on parameter type
            if param == 0x0D:  # LFO waveform
                # QComboBox for waveform (TRI, SIN, SAW, SQR, S&H, RND)
                control.setCurrentIndex(value)
            
            elif param == 0x0E:  # Rate (direct 0-127)
                control.setValue(value)
            
            elif param == 0x0F:  # Fade time (direct 0-127)
                control.setValue(value)
            
            elif param in (0x10, 0x15):  # Boolean switches
                # QCheckBox for sync and key trigger
                control.setChecked(bool(value))
            
            elif param == 0x11:  # Sync note value
                # QComboBox for note values (0-19)
                control.setCurrentIndex(value)
            
            elif param in (0x12, 0x13, 0x14):  # Depth controls (-63 to +63)
                # Bipolar sliders centered at 64
                control.setValue(value - 64)
            
            elif param in (0x38, 0x39, 0x3A, 0x3B):  # Modulation (-63 to +63)
                # Bipolar sliders centered at 64
                control.setValue(value - 64)
            
            logging.debug(f"Updated LFO control {control_name}: {value}")
            
        except Exception as e:
            logging.error(f"Error updating LFO control: {str(e)}") 