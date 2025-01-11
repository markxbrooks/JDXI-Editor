from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QFrame, QLabel, QComboBox, QCheckBox, QPushButton,
    QGroupBox, QTabWidget, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import logging

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
    MODEL_ID, JD_XI_ID, DT1_COMMAND_12, END_OF_SYSEX,
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
    AnalogSynthPatch
)
from jdxi_manager.ui.editors.base_editor import BaseEditor

class AnalogSynthEditor(QMainWindow):
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.main_window = parent
        self.current_patch = AnalogSynthPatch()
        
        # Set window properties
        self.setStyleSheet(Style.MAIN_STYLESHEET)
        self.setFixedWidth(1000)
        self.setMinimumHeight(600)
        
        # Create UI
        self._create_ui()
        
        # Request current patch data
        self._request_patch_data()

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
        
        # Waveform selector (0x16: 0-2)
        wave = QComboBox()
        wave.addItems(['SAW', 'TRI', 'PW-SQR'])  # Updated names to match spec
        wave.currentIndexChanged.connect(
            lambda idx: self._send_parameter(0x16, idx)
        )
        layout.addWidget(wave)
        
        # Pitch Coarse (0x17: 40-88 maps to -24 - +24)
        pitch = Slider(
            "Pitch", -24, 24,
            lambda v: self._send_parameter(0x17, v + 64)  # Center at 64
        )
        layout.addWidget(pitch)
        
        # Pitch Fine (0x18: 14-114 maps to -50 - +50)
        fine = Slider(
            "Fine", -50, 50,
            lambda v: self._send_parameter(0x18, v + 64)  # Center at 64
        )
        layout.addWidget(fine)
        
        # Pulse Width (0x19: 0-127)
        pw = Slider(
            "Pulse Width", 0, 127,
            lambda v: self._send_parameter(0x19, v)
        )
        layout.addWidget(pw)
        
        # PW Mod Depth (0x1A: 0-127)
        pwm = Slider(
            "PW Mod Depth", 0, 127,
            lambda v: self._send_parameter(0x1A, v)
        )
        layout.addWidget(pwm)
        
        # Pitch Envelope controls
        # Velocity (0x1B: 1-127 maps to -63 - +63)
        pitch_velo = Slider(
            "Pitch Env Velocity", -63, 63,
            lambda v: self._send_parameter(0x1B, v + 64)
        )
        layout.addWidget(pitch_velo)
        
        # Attack (0x1C: 0-127)
        pitch_atk = Slider(
            "Pitch Env Attack", 0, 127,
            lambda v: self._send_parameter(0x1C, v)
        )
        layout.addWidget(pitch_atk)
        
        # Decay (0x1D: 0-127)
        pitch_dec = Slider(
            "Pitch Env Decay", 0, 127,
            lambda v: self._send_parameter(0x1D, v)
        )
        layout.addWidget(pitch_dec)
        
        # Depth (0x1E: 1-127 maps to -63 - +63)
        pitch_depth = Slider(
            "Pitch Env Depth", -63, 63,
            lambda v: self._send_parameter(0x1E, v + 64)
        )
        layout.addWidget(pitch_depth)
        
        # Sub oscillator type (0x1F: 0-2)
        if osc_num == 1:
            sub_type = QComboBox()
            sub_type.addItems(['OFF', 'OCT-1', 'OCT-2'])  # Updated names to match spec
            sub_type.currentIndexChanged.connect(
                lambda idx: self._send_parameter(0x1F, idx)
            )
            layout.addWidget(sub_type)
        
        return frame

    def _create_mixer_section(self):
        """Create mixer section controls"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Add header
        layout.addWidget(self._create_section_header("MIXER", Style.MIX_BG))
        
        # Create controls
        balance = Slider(
            "OSC Balance", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.OSC_BALANCE.value, v)
        )
        noise = Slider(
            "Noise Level", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.NOISE_LEVEL.value, v)
        )
        ring_mod = Slider(
            "Ring Mod", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.RING_MOD.value, v)
        )
        cross_mod = Slider(
            "Cross Mod", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.CROSS_MOD.value, v)
        )
        
        # Add controls to layout
        layout.addWidget(balance)
        layout.addWidget(noise)
        layout.addWidget(ring_mod)
        layout.addWidget(cross_mod)
        
        return frame

    def _send_parameter(self, param: int, value: int):
        """Send analog synth parameter change with value validation"""
        try:
            # Validate parameter ranges
            if param in [0x31, 0x33]:  # Portamento and Legato switches
                if value not in [0, 1]:
                    logging.error(f"Switch value {value} invalid (must be 0 or 1)")
                    return
            elif param == 0x34:  # Octave Shift
                if value < 61 or value > 67:
                    logging.error(f"Octave shift value {value} out of range (61-67)")
                    return
            elif param in [0x35, 0x36]:  # Pitch Bend Ranges
                if value < 0 or value > 24:
                    logging.error(f"Pitch bend range {value} out of range (0-24)")
                    return
            elif param == 0x0D:  # LFO Shape
                if value not in range(6):  # 0-5
                    logging.error(f"LFO Shape value {value} invalid (must be 0-5)")
                    return
            elif param in [0x10, 0x15]:  # Switches (Tempo Sync, Key Trigger)
                if value not in [0, 1]:
                    logging.error(f"Switch value {value} invalid (must be 0 or 1)")
                    return
            elif param == 0x11:  # Sync Note
                if value not in range(20):  # 0-19
                    logging.error(f"Sync Note value {value} invalid (must be 0-19)")
                    return
            elif param in [0x12, 0x13, 0x14]:  # LFO Depths
                if value < 1 or value > 127:
                    logging.error(f"LFO Depth value {value} out of range (1-127)")
                    return
            elif param == 0x16:  # OSC Waveform
                if value not in [0, 1, 2]:
                    logging.error(f"Waveform value {value} invalid (must be 0-2)")
                    return
            elif param == 0x17:  # Pitch Coarse
                if value < 40 or value > 88:
                    logging.error(f"Pitch value {value} out of range (40-88)")
                    return
            elif param == 0x18:  # Pitch Fine
                if value < 14 or value > 114:
                    logging.error(f"Fine value {value} out of range (14-114)")
                    return
            elif param in [0x1B, 0x1E]:  # Velocity and Depth
                if value < 1 or value > 127:
                    logging.error(f"Parameter value {value} out of range (1-127)")
                    return
            elif param == 0x1F:  # Sub OSC Type
                if value not in [0, 1, 2]:
                    logging.error(f"Sub OSC type {value} invalid (must be 0-2)")
                    return
            elif param in [0x38, 0x39, 0x3A, 0x3B]:  # LFO Modulation controls
                if value < 1 or value > 127:
                    logging.error(f"LFO Modulation value {value} out of range (1-127)")
                    return
            else:  # Standard parameters
                if value < 0 or value > 127:
                    logging.error(f"Parameter value {value} out of range (0-127)")
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
                logging.debug(f"Sent analog parameter: {hex(param)}={value}")
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
            lambda v: self._send_parameter(0x2A, v)  # Direct address instead of enum
        )
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
        
        # LFO Shape (0x0D: 0-5)
        shape = QComboBox()
        shape.addItems(['TRI', 'SIN', 'SAW', 'SQR', 'S&H', 'RND'])  # Match spec names
        shape.currentIndexChanged.connect(
            lambda idx: self._send_parameter(0x0D, idx)
        )
        layout.addWidget(shape)
        
        # Rate (0x0E: 0-127)
        rate = Slider(
            "Rate", 0, 127,
            lambda v: self._send_parameter(0x0E, v)
        )
        layout.addWidget(rate)
        
        # Fade Time (0x0F: 0-127)
        fade = Slider(
            "Fade Time", 0, 127,
            lambda v: self._send_parameter(0x0F, v)
        )
        layout.addWidget(fade)
        
        # Tempo Sync switch (0x10: 0-1)
        sync_sw = QCheckBox("Tempo Sync")
        sync_sw.toggled.connect(
            lambda v: self._send_parameter(0x10, int(v))
        )
        layout.addWidget(sync_sw)
        
        # Sync Note selector (0x11: 0-19)
        sync_note = QComboBox()
        sync_note.addItems([
            "16", "12", "8", "4", "2", "1", "3/4", "2/3", "1/2",
            "3/8", "1/3", "1/4", "3/16", "1/6", "1/8", "3/32",
            "1/12", "1/16", "1/24", "1/32"
        ])
        sync_note.currentIndexChanged.connect(
            lambda idx: self._send_parameter(0x11, idx)
        )
        layout.addWidget(sync_note)
        
        # Depth controls (all 1-127 map to -63 - +63)
        pitch_depth = Slider(
            "Pitch Depth", -63, 63,
            lambda v: self._send_parameter(0x12, v + 64)
        )
        layout.addWidget(pitch_depth)
        
        filter_depth = Slider(
            "Filter Depth", -63, 63,
            lambda v: self._send_parameter(0x13, v + 64)
        )
        layout.addWidget(filter_depth)
        
        amp_depth = Slider(
            "Amp Depth", -63, 63,
            lambda v: self._send_parameter(0x14, v + 64)
        )
        layout.addWidget(amp_depth)
        
        # Key Trigger switch (0x15: 0-1)
        key_trig = QCheckBox("Key Trigger")
        key_trig.toggled.connect(
            lambda v: self._send_parameter(0x15, int(v))
        )
        layout.addWidget(key_trig)
        
        # Add separator for modulation controls
        layout.addWidget(QLabel("Modulation Controls"))
        
        # LFO Modulation controls (all 1-127 map to -63 - +63)
        pitch_mod = Slider(
            "Pitch Mod", -63, 63,
            lambda v: self._send_parameter(0x38, v + 64)
        )
        layout.addWidget(pitch_mod)
        
        filter_mod = Slider(
            "Filter Mod", -63, 63,
            lambda v: self._send_parameter(0x39, v + 64)
        )
        layout.addWidget(filter_mod)
        
        amp_mod = Slider(
            "Amp Mod", -63, 63,
            lambda v: self._send_parameter(0x3A, v + 64)
        )
        layout.addWidget(amp_mod)
        
        rate_mod = Slider(
            "Rate Mod", -63, 63,
            lambda v: self._send_parameter(0x3B, v + 64)
        )
        layout.addWidget(rate_mod)
        
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
        
        # Get correct parameter set based on envelope type
        params = {
            "PITCH": {
                "attack": AnalogParameter.OSC_PITCH_ATK,
                "decay": AnalogParameter.OSC_PITCH_DEC,
                "depth": AnalogParameter.OSC_PITCH_DEPTH,
                "velo": AnalogParameter.OSC_PITCH_VELO
            },
            "FILTER": {
                "attack": AnalogParameter.FILTER_ENV_ATK,
                "decay": AnalogParameter.FILTER_ENV_DEC,
                "sustain": AnalogParameter.FILTER_ENV_SUS,
                "release": AnalogParameter.FILTER_ENV_REL,
                "depth": AnalogParameter.FILTER_ENV_DEPTH,
                "velo": AnalogParameter.FILTER_ENV_VELO
            },
            "AMP": {
                "attack": AnalogParameter.AMP_ENV_ATK,
                "decay": AnalogParameter.AMP_ENV_DEC,
                "sustain": AnalogParameter.AMP_ENV_SUS,
                "release": AnalogParameter.AMP_ENV_REL,
                "velo": AnalogParameter.AMP_VELO
            }
        }[env_type]
        
        # Create ADSR controls with correct parameters
        if "attack" in params:
            attack = Slider(
                "Attack", 0, 127,
                lambda v: self._send_parameter(params["attack"].value, v)
            )
            layout.addWidget(attack)
            
        if "decay" in params:
            decay = Slider(
                "Decay", 0, 127,
                lambda v: self._send_parameter(params["decay"].value, v)
            )
            layout.addWidget(decay)
            
        if "sustain" in params:
            sustain = Slider(
                "Sustain", 0, 127,
                lambda v: self._send_parameter(params["sustain"].value, v)
            )
            layout.addWidget(sustain)
            
        if "release" in params:
            release = Slider(
                "Release", 0, 127,
                lambda v: self._send_parameter(params["release"].value, v)
            )
            layout.addWidget(release)
            
        if "depth" in params:
            depth = Slider(
                "Depth", -63, 63,
                lambda v: self._send_parameter(params["depth"].value, v + 64)
            )
            layout.addWidget(depth)
            
        if "velo" in params:
            velo = Slider(
                "Velocity", -63, 63,
                lambda v: self._send_parameter(params["velo"].value, v + 64)
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
        """Request current patch data from device"""
        try:
            logging.debug("Requesting Analog Synth patch data")
            
            # Calculate base address for analog synth
            base_addr = [
                ANALOG_SYNTH_AREA,  # Analog synth area
                SUBGROUP_ZERO,      # Part number (always 0 for analog)
                0x00,               # Start at first parameter
                0x00                # Parameter offset
            ]
            
            # Request common parameters
            common_msg = create_sysex_message(
                bytes(base_addr),
                bytes([0x20])  # Request 32 bytes of common parameters
            )
            
            # Request oscillator parameters
            osc_addr = base_addr.copy()
            osc_addr[2] = AnalogParameter.OSC1_WAVE.value
            osc_msg = create_sysex_message(
                bytes(osc_addr),
                bytes([0x40])  # Request 64 bytes of oscillator parameters
            )
            
            # Request filter parameters
            filter_addr = base_addr.copy()
            filter_addr[2] = AnalogParameter.CUTOFF.value
            filter_msg = create_sysex_message(
                bytes(filter_addr),
                bytes([0x20])  # Request 32 bytes of filter parameters
            )
            
            # Request amp parameters
            amp_addr = base_addr.copy()
            amp_addr[2] = AnalogParameter.LEVEL.value
            amp_msg = create_sysex_message(
                bytes(amp_addr),
                bytes([0x20])  # Request 32 bytes of amp parameters
            )
            
            # Request LFO parameters
            lfo_addr = base_addr.copy()
            lfo_addr[2] = AnalogParameter.LFO_WAVE.value
            lfo_msg = create_sysex_message(
                bytes(lfo_addr),
                bytes([0x20])  # Request 32 bytes of LFO parameters
            )
            
            # Send all requests if MIDI is available
            if self.midi_helper:
                # Send requests with slight delays between
                self.midi_helper.send_message(common_msg)
                logging.debug("Sent common parameters request")
                
                self.midi_helper.send_message(osc_msg)
                logging.debug("Sent oscillator parameters request")
                
                self.midi_helper.send_message(filter_msg)
                logging.debug("Sent filter parameters request")
                
                self.midi_helper.send_message(amp_msg)
                logging.debug("Sent amp parameters request")
                
                self.midi_helper.send_message(lfo_msg)
                logging.debug("Sent LFO parameters request")
                
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
                data = msg[12:-1]  # Data bytes (excluding end of sysex)
                
                # Update UI based on received data
                self._update_ui_from_sysex(addr, data)
                
        except Exception as e:
            logging.error(f"Error handling MIDI input: {str(e)}")

    def _update_ui_from_sysex(self, addr, data):
        """Update UI controls based on received SysEx data"""
        try:
            # Extract section from address
            section = addr[2]  # Third byte indicates parameter section
            
            # Update appropriate controls based on section
            if section == AnalogParameter.OSC1_WAVE.value:
                # Update oscillator controls
                self._update_oscillator_controls(data)
                
            elif section == AnalogParameter.CUTOFF.value:
                # Update filter controls
                self._update_filter_controls(data)
                
            elif section == AnalogParameter.LEVEL.value:
                # Update amp controls
                self._update_amp_controls(data)
                
            elif section == AnalogParameter.LFO_WAVE.value:
                # Update LFO controls
                self._update_lfo_controls(data)
            
        except Exception as e:
            logging.error(f"Error updating UI from SysEx: {str(e)}") 

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