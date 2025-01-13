from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QFrame, QGridLayout, QGroupBox,
    QSpinBox, QSlider, QStackedWidget, QCheckBox,
    QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
import logging

from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.waveform import WaveformButton
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.data.digital import (
    DigitalSynth, DigitalParameter, 
    DigitalPartial, DigitalPatch
)
from jdxi_manager.midi.constants import (
    DIGITAL_SYNTH_1, DIGITAL_SYNTH_2,
    DIGITAL_PART_1, DIGITAL_PART_2,
    DIGITAL_SYNTH_AREA,
    PART_1,
    OSC_1_GROUP,
    FILTER_GROUP,
    EFFECTS_GROUP,
    REVERB_SEND_PARAM,
    DELAY_SEND_PARAM,
    EFFECTS_SEND_PARAM,
    EffectType,
    # Partial Parameters
    PARTIAL_1_SWITCH, PARTIAL_1_SELECT,
    PARTIAL_2_SWITCH, PARTIAL_2_SELECT,
    PARTIAL_3_SWITCH, PARTIAL_3_SELECT,
    RING_SWITCH,
    OSC_WAVE_PARAM,
    WAVE_SAW,
    WAVE_SQUARE,
    WAVE_PULSE,
    WAVE_TRIANGLE,
    WAVE_SINE,
    WAVE_NOISE,
    WAVE_SUPER_SAW,
    WAVE_PCM,
    OSC_VARIATION_PARAM, OSC_PITCH_PARAM,
    OSC_DETUNE_PARAM, OSC_PWM_DEPTH_PARAM, OSC_PW_PARAM,
    OSC_PITCH_ENV_A_PARAM, OSC_PITCH_ENV_D_PARAM, OSC_PITCH_ENV_DEPTH_PARAM,
    FILTER_MODE_PARAM, FILTER_SLOPE_PARAM, FILTER_CUTOFF_PARAM,
    FILTER_KEYFOLLOW_PARAM, FILTER_ENV_VELO_PARAM, FILTER_RESONANCE_PARAM,
    FILTER_ENV_A_PARAM, FILTER_ENV_D_PARAM, FILTER_ENV_S_PARAM,
    FILTER_ENV_R_PARAM, FILTER_ENV_DEPTH_PARAM,
    FILTER_MODE_BYPASS, FILTER_MODE_LPF, FILTER_MODE_HPF,
    FILTER_MODE_BPF, FILTER_MODE_PKG, FILTER_MODE_LPF2,
    FILTER_MODE_LPF3, FILTER_MODE_LPF4,
    FILTER_SLOPE_12DB, FILTER_SLOPE_24DB,
    AMP_LEVEL_PARAM, AMP_VELO_SENS_PARAM, AMP_ENV_A_PARAM,
    AMP_ENV_D_PARAM, AMP_ENV_S_PARAM, AMP_ENV_R_PARAM,
    AMP_PAN_PARAM,
    LFO_SHAPE_PARAM, LFO_RATE_PARAM, LFO_TEMPO_SYNC_PARAM,
    LFO_SYNC_NOTE_PARAM, LFO_FADE_TIME_PARAM, LFO_KEY_TRIGGER_PARAM,
    LFO_PITCH_DEPTH_PARAM, LFO_FILTER_DEPTH_PARAM, LFO_AMP_DEPTH_PARAM,
    LFO_PAN_DEPTH_PARAM,
    CUTOFF_AFTERTOUCH_PARAM, LEVEL_AFTERTOUCH_PARAM,
    LFOSyncNote,
    # ... rest of imports ...
)

class DigitalSynthEditor(BaseEditor):
    """Editor for digital synth settings"""
    def __init__(self, synth_num=1, midi_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        self.synth_num = synth_num
        self.setWindowTitle(f"Digital Synth {synth_num}")
        
        # Define section colors
        self.section_colors = {
            "oscillator": "#FF4D4D",     # Bright red
            "filter": "#FF6B4D",         # Red-orange
            "amp": "#FF884D",            # Orange-red
            "effects": "#FFA54D",        # Light orange-red
            "lfo": "#FFC24D",            # Peach
            "aftertouch": "#FFDF4D",      # Light peach
            "partials": "#FF3333"        # Bright red
        }
        
        # Define header style
        self.header_style = """
            QLabel {
                background-color: #FF4D4D;
                color: white;
                padding: 2px;
                margin: 2px;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Myriad Pro', 'Arial', sans-serif;
            }
        """
        
        # Define global style sheet
        self.setStyleSheet("""
            QWidget {
                font-family: 'Myriad Pro', 'Arial', sans-serif;
                padding: 2px;
                color: #EEEEEE;
                margin: 2px;           
            }
            QSlider {
                padding: 2px;
                margin: 2px;
            }
            QSlider::handle:horizontal {
                background-color: #EEEEEE;
                border: 1px solid #DDDDDD;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background-color: #FF884D;
                border: 1px solid #FF6B4D;
            }
            QSlider::handle:horizontal:pressed {
                background-color: #FFA54D;
                border: 1px solid #FF884D;
            }
            QSlider::groove:horizontal {
                border: 1px solid #CC0000;
                height: 6px;
                border-radius: 3px;
            }
            QLabel {
                padding: 1px;
                margin: 1px;
            }
            QComboBox {
                font-family: 'Myriad Pro', 'Arial', sans-serif;
            }
            QSpinBox {
                font-family: 'Myriad Pro', 'Arial', sans-serif;
            }
            QCheckBox {
                font-family: 'Myriad Pro', 'Arial', sans-serif;
            }
        """)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll)
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Create sections
        self._create_partial_section(main_layout)
        self._create_osc_section(main_layout)
        self._create_filter_section(main_layout)
        self._create_amp_section(main_layout)
        self._create_effects_section(main_layout)
        self._create_lfo_section(main_layout)
        self._create_aftertouch_section(main_layout)
        
        # Add stretch at the bottom to keep widgets at top
        main_layout.addStretch()
        
        # Set the scroll area widget
        scroll.setWidget(main_widget)
        
        # Set window properties
        self.setMinimumWidth(800)
        self.setMinimumHeight(900)

    def _create_header(self, text: str) -> QLabel:
        """Create a styled header label"""
        header = QLabel(text)
        header.setStyleSheet(self.header_style)
        header.setAlignment(Qt.AlignCenter)
        return header

    def _create_osc_section(self, parent_layout):
        """Create oscillator section"""
        layout = QVBoxLayout()
        
        # Add styled header
        header = self._create_header("Oscillator")
        layout.addWidget(header)
        
        # Waveform selection
        wave_layout = QHBoxLayout()
        wave_layout.addWidget(QLabel("Wave:"))
        self.wave_combo = QComboBox()
        self.wave_combo.addItems([
            "SAW", "SQUARE", "PW-SQUARE", "TRIANGLE",
            "SINE", "NOISE", "SUPER-SAW", "PCM"
        ])
        self.wave_combo.currentIndexChanged.connect(self._on_wave_changed)
        wave_layout.addWidget(self.wave_combo)
        layout.addLayout(wave_layout)
        
        # Wave Variation
        var_layout = QHBoxLayout()
        var_layout.addWidget(QLabel("Variation:"))
        self.var_combo = QComboBox()
        self.var_combo.addItems(["A", "B", "C"])
        self.var_combo.currentIndexChanged.connect(self._on_variation_changed)
        var_layout.addWidget(self.var_combo)
        layout.addLayout(var_layout)
        
        # Pitch control (-24 to +24)
        pitch_layout = QHBoxLayout()
        pitch_layout.addWidget(QLabel("Pitch:"))
        self.pitch_spin = QSpinBox()
        self.pitch_spin.setRange(-24, 24)
        self.pitch_spin.valueChanged.connect(self._on_pitch_changed)
        pitch_layout.addWidget(self.pitch_spin)
        layout.addLayout(pitch_layout)
        
        # Detune control (-50 to +50)
        detune_layout = QHBoxLayout()
        detune_layout.addWidget(QLabel("Detune:"))
        self.detune_spin = QSpinBox()
        self.detune_spin.setRange(-50, 50)
        self.detune_spin.valueChanged.connect(self._on_detune_changed)
        detune_layout.addWidget(self.detune_spin)
        layout.addLayout(detune_layout)
        
        # PW Mod Depth slider (0-127)
        pwm_layout = QHBoxLayout()
        pwm_layout.addWidget(QLabel("PW Mod Depth:"))
        self.pwm_slider = QSlider(Qt.Horizontal)
        self.pwm_slider.setRange(0, 127)
        self.pwm_slider.valueChanged.connect(self._on_pwm_changed)
        pwm_layout.addWidget(self.pwm_slider)
        layout.addLayout(pwm_layout)
        
        # Pulse Width slider (0-127)
        pw_layout = QHBoxLayout()
        pw_layout.addWidget(QLabel("Pulse Width:"))
        self.pw_slider = QSlider(Qt.Horizontal)
        self.pw_slider.setRange(0, 127)
        self.pw_slider.valueChanged.connect(self._on_pw_changed)
        pw_layout.addWidget(self.pw_slider)
        layout.addLayout(pw_layout)
        
        # Pitch Envelope controls
        pitch_env_group = QGroupBox("Pitch Envelope")
        pitch_env_layout = QVBoxLayout()
        
        # Attack Time (0-127)
        attack_layout = QHBoxLayout()
        attack_layout.addWidget(QLabel("Attack:"))
        self.pitch_attack_slider = QSlider(Qt.Horizontal)
        self.pitch_attack_slider.setRange(0, 127)
        self.pitch_attack_slider.valueChanged.connect(self._on_pitch_attack_changed)
        attack_layout.addWidget(self.pitch_attack_slider)
        pitch_env_layout.addLayout(attack_layout)
        
        # Decay Time (0-127)
        decay_layout = QHBoxLayout()
        decay_layout.addWidget(QLabel("Decay:"))
        self.pitch_decay_slider = QSlider(Qt.Horizontal)
        self.pitch_decay_slider.setRange(0, 127)
        self.pitch_decay_slider.valueChanged.connect(self._on_pitch_decay_changed)
        decay_layout.addWidget(self.pitch_decay_slider)
        pitch_env_layout.addLayout(decay_layout)
        
        # Envelope Depth (-63 to +63)
        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("Depth:"))
        self.pitch_depth_spin = QSpinBox()
        self.pitch_depth_spin.setRange(-63, 63)
        self.pitch_depth_spin.valueChanged.connect(self._on_pitch_depth_changed)
        depth_layout.addWidget(self.pitch_depth_spin)
        pitch_env_layout.addLayout(depth_layout)
        
        pitch_env_group.setLayout(pitch_env_layout)
        layout.addWidget(pitch_env_group)
        
        parent_layout.addLayout(layout)

    def _create_filter_section(self, parent_layout):
        """Create filter section"""
        layout = QVBoxLayout()
        
        # Add styled header
        header = self._create_header("Filter")
        layout.addWidget(header)
        
        # Filter controls
        cutoff_layout = QHBoxLayout()
        cutoff_layout.addWidget(QLabel("Cutoff:"))
        self.cutoff_slider = QSlider(Qt.Horizontal)
        self.cutoff_slider.setRange(0, 127)
        self.cutoff_slider.valueChanged.connect(self._on_filter_cutoff_changed)
        cutoff_layout.addWidget(self.cutoff_slider)
        layout.addLayout(cutoff_layout)
        
        resonance_layout = QHBoxLayout()
        resonance_layout.addWidget(QLabel("Resonance:"))
        self.resonance_slider = QSlider(Qt.Horizontal)
        self.resonance_slider.setRange(0, 127)
        self.resonance_slider.valueChanged.connect(self._on_filter_resonance_changed)
        resonance_layout.addWidget(self.resonance_slider)
        layout.addLayout(resonance_layout)
        
        parent_layout.addLayout(layout)

    def _create_amp_section(self, parent_layout):
        """Create amplifier section"""
        layout = QVBoxLayout()
        
        # Add styled header
        header = self._create_header("Amplifier")
        layout.addWidget(header)
        
        # Level
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Level:"))
        self.amp_level_slider = QSlider(Qt.Horizontal)
        self.amp_level_slider.setRange(0, 127)
        self.amp_level_slider.valueChanged.connect(self._on_amp_level_changed)
        level_layout.addWidget(self.amp_level_slider)
        layout.addLayout(level_layout)
        
        # Velocity Sensitivity
        velo_layout = QHBoxLayout()
        velo_layout.addWidget(QLabel("Velocity Sens:"))
        self.amp_velo_spin = QSpinBox()
        self.amp_velo_spin.setRange(-63, 63)
        self.amp_velo_spin.valueChanged.connect(self._on_amp_velo_changed)
        velo_layout.addWidget(self.amp_velo_spin)
        layout.addLayout(velo_layout)
        
        # ADSR Envelope
        env_group = QGroupBox("Envelope")
        env_layout = QVBoxLayout()
        
        for name, param in [
            ("Attack", AMP_ENV_A_PARAM),
            ("Decay", AMP_ENV_D_PARAM),
            ("Sustain", AMP_ENV_S_PARAM),
            ("Release", AMP_ENV_R_PARAM)
        ]:
            slider_layout = QHBoxLayout()
            slider_layout.addWidget(QLabel(f"{name}:"))
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 127)
            slider.valueChanged.connect(
                lambda v, p=param: self._on_amp_env_changed(p, v)
            )
            slider_layout.addWidget(slider)
            env_layout.addLayout(slider_layout)
            setattr(self, f"amp_env_{name.lower()}", slider)
        
        env_group.setLayout(env_layout)
        layout.addWidget(env_group)
        
        # Pan
        pan_layout = QHBoxLayout()
        pan_layout.addWidget(QLabel("Pan:"))
        self.amp_pan_slider = QSlider(Qt.Horizontal)
        self.amp_pan_slider.setRange(0, 127)
        self.amp_pan_slider.setValue(64)  # Center
        self.amp_pan_slider.valueChanged.connect(self._on_amp_pan_changed)
        self.pan_value_label = QLabel("C")  # Display pan position
        pan_layout.addWidget(self.amp_pan_slider)
        pan_layout.addWidget(self.pan_value_label)
        layout.addLayout(pan_layout)
        
        parent_layout.addLayout(layout)

    def _create_effects_section(self, parent_layout):
        """Create effects section"""
        layout = QVBoxLayout()
        
        # Add styled header
        header = self._create_header("Effects")
        layout.addWidget(header)
        
        # Effect sends
        reverb_layout = QHBoxLayout()
        reverb_layout.addWidget(QLabel("Reverb Send:"))
        self.reverb_slider = QSlider(Qt.Horizontal)
        self.reverb_slider.setRange(0, 127)
        self.reverb_slider.valueChanged.connect(self._on_reverb_send_changed)
        reverb_layout.addWidget(self.reverb_slider)
        layout.addLayout(reverb_layout)
        
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Delay Send:"))
        self.delay_slider = QSlider(Qt.Horizontal)
        self.delay_slider.setRange(0, 127)
        self.delay_slider.valueChanged.connect(self._on_delay_send_changed)
        delay_layout.addWidget(self.delay_slider)
        layout.addLayout(delay_layout)
        
        fx_layout = QHBoxLayout()
        fx_layout.addWidget(QLabel("FX Send:"))
        self.fx_slider = QSlider(Qt.Horizontal)
        self.fx_slider.setRange(0, 127)
        self.fx_slider.valueChanged.connect(self._on_fx_send_changed)
        fx_layout.addWidget(self.fx_slider)
        layout.addLayout(fx_layout)
        
        parent_layout.addLayout(layout)

    def _create_lfo_section(self, parent_layout):
        """Create LFO section"""
        layout = QVBoxLayout()
        
        # Add styled header
        header = self._create_header("LFO")
        layout.addWidget(header)
        
        # LFO Shape
        shape_layout = QHBoxLayout()
        shape_layout.addWidget(QLabel("Shape:"))
        self.lfo_shape_combo = QComboBox()
        self.lfo_shape_combo.addItems([
            "Triangle", "Sine", "Saw", "Square",
            "S&H", "Random"
        ])
        self.lfo_shape_combo.currentIndexChanged.connect(self._on_lfo_shape_changed)
        shape_layout.addWidget(self.lfo_shape_combo)
        layout.addLayout(shape_layout)
        
        # Rate/Sync Controls
        rate_group = QGroupBox()
        rate_layout = QVBoxLayout()
        
        # Tempo Sync Switch
        sync_layout = QHBoxLayout()
        self.tempo_sync_check = QCheckBox("Tempo Sync")
        self.tempo_sync_check.stateChanged.connect(self._on_lfo_sync_changed)
        sync_layout.addWidget(self.tempo_sync_check)
        rate_layout.addLayout(sync_layout)
        
        # Rate Control (stack widget to switch between free/sync)
        self.rate_stack = QStackedWidget()
        
        # Free Rate Slider
        free_rate_widget = QWidget()
        free_rate_layout = QHBoxLayout()
        free_rate_layout.addWidget(QLabel("Rate:"))
        self.lfo_rate_slider = QSlider(Qt.Horizontal)
        self.lfo_rate_slider.setRange(0, 127)
        self.lfo_rate_slider.valueChanged.connect(self._on_lfo_rate_changed)
        free_rate_layout.addWidget(self.lfo_rate_slider)
        free_rate_widget.setLayout(free_rate_layout)
        self.rate_stack.addWidget(free_rate_widget)
        
        # Sync Note Combo
        sync_note_widget = QWidget()
        sync_note_layout = QHBoxLayout()
        sync_note_layout.addWidget(QLabel("Note:"))
        self.sync_note_combo = QComboBox()
        self.sync_note_combo.addItems(LFOSyncNote.get_all_display_names())
        self.sync_note_combo.currentIndexChanged.connect(self._on_lfo_sync_note_changed)
        sync_note_layout.addWidget(self.sync_note_combo)
        sync_note_widget.setLayout(sync_note_layout)
        self.rate_stack.addWidget(sync_note_widget)
        
        rate_layout.addWidget(self.rate_stack)
        rate_group.setLayout(rate_layout)
        layout.addWidget(rate_group)
        
        # Fade Time
        fade_layout = QHBoxLayout()
        fade_layout.addWidget(QLabel("Fade Time:"))
        self.fade_time_slider = QSlider(Qt.Horizontal)
        self.fade_time_slider.setRange(0, 127)
        self.fade_time_slider.valueChanged.connect(self._on_lfo_fade_changed)
        fade_layout.addWidget(self.fade_time_slider)
        layout.addLayout(fade_layout)
        
        # Key Trigger
        key_layout = QHBoxLayout()
        self.key_trigger_check = QCheckBox("Key Trigger")
        self.key_trigger_check.stateChanged.connect(self._on_lfo_key_trigger_changed)
        key_layout.addWidget(self.key_trigger_check)
        layout.addLayout(key_layout)
        
        # Depth Controls
        depth_group = QGroupBox("Modulation Depth")
        depth_layout = QVBoxLayout()
        
        for name, param in [
            ("Pitch", LFO_PITCH_DEPTH_PARAM),
            ("Filter", LFO_FILTER_DEPTH_PARAM),
            ("Amp", LFO_AMP_DEPTH_PARAM),
            ("Pan", LFO_PAN_DEPTH_PARAM)
        ]:
            slider_layout = QHBoxLayout()
            slider_layout.addWidget(QLabel(f"{name}:"))
            spin = QSpinBox()
            spin.setRange(-63, 63)
            spin.valueChanged.connect(
                lambda v, p=param: self._on_lfo_depth_changed(p, v)
            )
            slider_layout.addWidget(spin)
            depth_layout.addLayout(slider_layout)
            setattr(self, f"lfo_{name.lower()}_depth", spin)
        
        depth_group.setLayout(depth_layout)
        layout.addWidget(depth_group)
        
        parent_layout.addLayout(layout)

    def _create_aftertouch_section(self, parent_layout):
        """Create aftertouch section"""
        layout = QVBoxLayout()
        
        # Add styled header
        header = self._create_header("Aftertouch")
        layout.addWidget(header)
        
        # Cutoff Sensitivity
        cutoff_layout = QHBoxLayout()
        cutoff_layout.addWidget(QLabel("Cutoff Sens:"))
        self.cutoff_aftertouch_spin = QSpinBox()
        self.cutoff_aftertouch_spin.setRange(-63, 63)
        self.cutoff_aftertouch_spin.valueChanged.connect(self._on_cutoff_aftertouch_changed)
        cutoff_layout.addWidget(self.cutoff_aftertouch_spin)
        layout.addLayout(cutoff_layout)
        
        # Level Sensitivity
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Level Sens:"))
        self.level_aftertouch_spin = QSpinBox()
        self.level_aftertouch_spin.setRange(-63, 63)
        self.level_aftertouch_spin.valueChanged.connect(self._on_level_aftertouch_changed)
        level_layout.addWidget(self.level_aftertouch_spin)
        layout.addLayout(level_layout)
        
        parent_layout.addLayout(layout)

    def _create_partial_section(self, parent_layout):
        """Create partial selection section"""
        layout = QVBoxLayout()
        
        # Add styled header
        header = self._create_header("Partials")
        layout.addWidget(header)
        
        # Add partial colors to section colors
        self.section_colors["partials"] = "#FF3333"  # Bright red
        
        # Create grid for partial controls
        grid = QGridLayout()
        
        # Add partial switches and selects
        for i, (switch_param, select_param) in enumerate([
            (PARTIAL_1_SWITCH, PARTIAL_1_SELECT),
            (PARTIAL_2_SWITCH, PARTIAL_2_SELECT),
            (PARTIAL_3_SWITCH, PARTIAL_3_SELECT)
        ]):
            # Partial label
            grid.addWidget(QLabel(f"Partial {i+1}:"), i, 0)
            
            # Switch checkbox
            switch = QCheckBox("On/Off")
            switch.stateChanged.connect(
                lambda state, param=switch_param: self._on_partial_switch_changed(param, state)
            )
            grid.addWidget(switch, i, 1)
            setattr(self, f"partial_{i+1}_switch", switch)
            
            # Select checkbox
            select = QCheckBox("Select")
            select.stateChanged.connect(
                lambda state, param=select_param: self._on_partial_select_changed(param, state)
            )
            grid.addWidget(select, i, 2)
            setattr(self, f"partial_{i+1}_select", select)
        
        # Add ring modulation
        ring_layout = QHBoxLayout()
        ring_layout.addWidget(QLabel("Ring Mod:"))
        ring_combo = QComboBox()
        ring_combo.addItems(["OFF", "---", "ON"])
        ring_combo.currentIndexChanged.connect(self._on_ring_changed)
        ring_layout.addWidget(ring_combo)
        self.ring_combo = ring_combo
        
        # Add layouts to main layout
        layout.addLayout(grid)
        layout.addLayout(ring_layout)
        parent_layout.addLayout(layout)

    def _send_parameter(self, param: DigitalParameter, value: int):
        """Send parameter change to device"""
        try:
            if self.midi_helper:
                self.midi_helper.send_parameter(
                    self.area,
                    self.part,
                    0x00,  # Group 0
                    param.value,
                    value
                )
                logging.debug(f"Sent digital synth {self.synth_num} parameter {param.name}: {value}")
                
        except Exception as e:
            logging.error(f"Error sending digital parameter: {str(e)}")

    def _handle_midi_message(self, message):
        """Handle incoming MIDI message"""
        try:
            # Extract parameter and value
            param = message[3]  # Parameter number
            value = message[4]  # Parameter value
            
            # Update corresponding control
            if param == DigitalParameter.OSC_WAVE.value:
                self.wave_combo.setCurrentIndex(value)
            elif param == DigitalParameter.OSC_PITCH.value:
                self.pitch_spin.setValue(value - 64)
            elif param == DigitalParameter.FILTER_CUTOFF.value:
                self.cutoff.setValue(value)
            elif param == DigitalParameter.FILTER_RESONANCE.value:
                self.resonance.setValue(value)
            elif param == DigitalParameter.AMP_LEVEL.value:
                self.amp_level_slider.setValue(value)
            elif param == DigitalParameter.AMP_PAN.value:
                self.amp_pan_slider.setValue(value)
            elif param == DigitalParameter.REVERB_SEND.value:
                self.reverb.setValue(value)
            elif param == DigitalParameter.DELAY_SEND.value:
                self.delay.setValue(value)
                
            logging.debug(f"Updated digital synth {self.synth_num} parameter {hex(param)}: {value}")
            
        except Exception as e:
            logging.error(f"Error handling digital MIDI message: {str(e)}") 

    def _on_wave_changed(self, index):
        """Handle wave selection change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=OSC_WAVE_PARAM,
                value=index
            )
            logging.debug(f"Set wave to {index}")
            
    def _on_variation_changed(self, index):
        """Handle wave variation change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_VARIATION_PARAM,
                param=OSC_VARIATION_PARAM,
                value=index
            )
            logging.debug(f"Set variation to {index}")
            
    def _on_pitch_changed(self, value):
        """Handle pitch change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_PITCH_PARAM,
                param=OSC_PITCH_PARAM,
                value=value + 64
            )
            logging.debug(f"Set pitch to {value}")
            
    def _on_detune_changed(self, value):
        """Handle detune change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_DETUNE_PARAM,
                param=OSC_DETUNE_PARAM,
                value=value
            )
            logging.debug(f"Set detune to {value}")
            
    def _on_pwm_changed(self, value):
        """Handle PWM depth change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_PWM_DEPTH_PARAM,
                param=OSC_PWM_DEPTH_PARAM,
                value=value
            )
            logging.debug(f"Set PWM depth to {value}")
            
    def _on_pw_changed(self, value):
        """Handle pulse width change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_PW_PARAM,
                param=OSC_PW_PARAM,
                value=value
            )
            logging.debug(f"Set pulse width to {value}")
            
    def _on_pitch_attack_changed(self, value):
        """Handle pitch attack change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_PITCH_ENV_A_PARAM,
                param=OSC_PITCH_ENV_A_PARAM,
                value=value
            )
            logging.debug(f"Set pitch attack to {value}")
            
    def _on_pitch_decay_changed(self, value):
        """Handle pitch decay change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_PITCH_ENV_D_PARAM,
                param=OSC_PITCH_ENV_D_PARAM,
                value=value
            )
            logging.debug(f"Set pitch decay to {value}")
            
    def _on_pitch_depth_changed(self, value):
        """Handle pitch depth change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_PITCH_ENV_DEPTH_PARAM,
                param=OSC_PITCH_ENV_DEPTH_PARAM,
                value=value
            )
            logging.debug(f"Set pitch depth to {value}")

    def _on_amp_level_changed(self, value):
        """Handle amp level change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=AMP_LEVEL_PARAM,
                value=value
            )
            logging.debug(f"Set amp level to {value}")

    def _on_amp_velo_changed(self, value):
        """Handle velocity sensitivity change"""
        if self.midi_helper:
            # Convert -63/+63 to 1-127
            midi_value = value + 64
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=AMP_VELO_SENS_PARAM,
                value=midi_value
            )
            logging.debug(f"Set amp velocity sensitivity to {value}")

    def _on_amp_pan_changed(self, value):
        """Handle pan position change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=AMP_PAN_PARAM,
                value=value
            )
            # Update pan display label
            if value < 64:
                self.pan_value_label.setText(f"L{64-value}")
            elif value > 64:
                self.pan_value_label.setText(f"R{value-64}")
            else:
                self.pan_value_label.setText("C")
            logging.debug(f"Set amp pan to {value}")

    def _on_amp_env_changed(self, param, value):
        """Handle envelope parameter change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=param,
                value=value
            )
            logging.debug(f"Set amp envelope parameter {param} to {value}") 

    def _on_lfo_shape_changed(self, index):
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=LFO_SHAPE_PARAM,
                value=index
            )
            logging.debug(f"Set LFO shape to {index}")

    def _on_lfo_rate_changed(self, value):
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=LFO_RATE_PARAM,
                value=value
            )
            logging.debug(f"Set LFO rate to {value}")

    def _on_lfo_sync_changed(self, state):
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=LFO_TEMPO_SYNC_PARAM,
                value=state
            )
            logging.debug(f"Set LFO tempo sync to {state}")

    def _on_lfo_sync_note_changed(self, index):
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=LFO_SYNC_NOTE_PARAM,
                value=index
            )
            logging.debug(f"Set LFO sync note to {index}")

    def _on_lfo_fade_changed(self, value):
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=LFO_FADE_TIME_PARAM,
                value=value
            )
            logging.debug(f"Set LFO fade time to {value}")

    def _on_lfo_key_trigger_changed(self, state):
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=LFO_KEY_TRIGGER_PARAM,
                value=state
            )
            logging.debug(f"Set LFO key trigger to {state}")

    def _on_lfo_depth_changed(self, param, value):
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=param,
                value=value
            )
            logging.debug(f"Set LFO modulation depth to {value}") 

    def _on_cutoff_aftertouch_changed(self, value):
        """Handle cutoff aftertouch sensitivity change"""
        if self.midi_helper:
            # Convert -63/+63 to 1-127
            midi_value = value + 64
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=CUTOFF_AFTERTOUCH_PARAM,
                value=midi_value
            )
            logging.debug(f"Set cutoff aftertouch sensitivity to {value}")

    def _on_level_aftertouch_changed(self, value):
        """Handle level aftertouch sensitivity change"""
        if self.midi_helper:
            # Convert -63/+63 to 1-127
            midi_value = value + 64
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=LEVEL_AFTERTOUCH_PARAM,
                value=midi_value
            )
            logging.debug(f"Set level aftertouch sensitivity to {value}") 

    def _on_partial_switch_changed(self, param, state):
        """Handle partial switch change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=param,
                value=1 if state else 0
            )
            logging.debug(f"Set partial switch parameter {param} to {state}")

    def _on_partial_select_changed(self, param, state):
        """Handle partial select change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=param,
                value=1 if state else 0
            )
            logging.debug(f"Set partial select parameter {param} to {state}")

    def _on_ring_changed(self, index):
        """Handle ring modulation change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=OSC_1_GROUP,
                param=RING_SWITCH,
                value=index
            )
            logging.debug(f"Set ring modulation to {index}") 

    def _on_filter_cutoff_changed(self, value):
        """Handle filter cutoff change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=FILTER_GROUP,  # Use FILTER_GROUP instead of OSC_1_GROUP
                param=FILTER_CUTOFF_PARAM,
                value=value
            )
            logging.debug(f"Set filter cutoff to {value}")

    def _on_filter_resonance_changed(self, value):
        """Handle filter resonance change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=FILTER_GROUP,  # Use FILTER_GROUP instead of OSC_1_GROUP
                param=FILTER_RESONANCE_PARAM,
                value=value
            )
            logging.debug(f"Set filter resonance to {value}") 

    def _on_reverb_send_changed(self, value):
        """Handle reverb send change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=EFFECTS_GROUP,  # Use EFFECTS_GROUP
                param=REVERB_SEND_PARAM,
                value=value
            )
            logging.debug(f"Set reverb send to {value}")

    def _on_delay_send_changed(self, value):
        """Handle delay send change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=EFFECTS_GROUP,  # Use EFFECTS_GROUP
                param=DELAY_SEND_PARAM,
                value=value
            )
            logging.debug(f"Set delay send to {value}")

    def _on_fx_send_changed(self, value):
        """Handle effects send change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=PART_1,
                group=EFFECTS_GROUP,  # Use EFFECTS_GROUP
                param=EFFECTS_SEND_PARAM,
                value=value
            )
            logging.debug(f"Set effects send to {value}") 