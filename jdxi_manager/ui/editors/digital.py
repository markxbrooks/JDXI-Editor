import logging
from typing import Dict, Optional, Union
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTabWidget,
    QScrollArea, QSpinBox, QLabel
)
from PySide6.QtCore import Qt

from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.waveform import WaveformButton
from jdxi_manager.data.digital import (
    DigitalParameter, 
    DigitalCommonParameter,
    OscWave, 
    DigitalPartial, 
    set_partial_state, 
    get_partial_state
)
from jdxi_manager.midi.constants import (
    DIGITAL_SYNTH_AREA, PART_1, PART_2
)
from jdxi_manager.ui.widgets.partial_switch import PartialsPanel
from jdxi_manager.ui.widgets.switch import Switch

class PartialEditor(QWidget):
    """Editor for a single partial"""
    def __init__(self, midi_helper=None, partial_num=1, part=PART_1, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.partial_num = partial_num
        self.part = part
        
        # Store parameter controls for easy access
        self.controls: Dict[Union[DigitalParameter, DigitalCommonParameter], QWidget] = {}
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create vertical scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create container widget
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        
        # Add sections in a vertical layout
        container_layout.addWidget(self._create_oscillator_section())
        container_layout.addWidget(self._create_filter_section())
        container_layout.addWidget(self._create_amp_section())
        container_layout.addWidget(self._create_lfo_section())
        container_layout.addWidget(self._create_mod_lfo_section())
        
        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _create_parameter_slider(self, param: Union[DigitalParameter, DigitalCommonParameter], label: str) -> Slider:
        """Create a slider for a parameter with proper display conversion"""
        if hasattr(param, 'get_display_value'):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        
        slider = Slider(label, display_min, display_max)
        
        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        
        # Store control reference
        self.controls[param] = slider
        return slider

    def _create_oscillator_section(self):
        group = QGroupBox("Oscillator")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Top row: Waveform buttons and variation
        top_row = QHBoxLayout()
        
        # Waveform buttons
        wave_layout = QHBoxLayout()
        self.wave_buttons = {}
        for wave in [
            OscWave.SAW, 
            OscWave.SQUARE, 
            OscWave.PW_SQUARE, 
            OscWave.TRIANGLE, 
            OscWave.SINE,
            OscWave.NOISE,
            OscWave.SUPER_SAW,
            OscWave.PCM
        ]:
            btn = WaveformButton(wave)
            btn.clicked.connect(lambda checked, w=wave: self._on_waveform_selected(w))
            self.wave_buttons[wave] = btn
            wave_layout.addWidget(btn)
        top_row.addLayout(wave_layout)
        
        # Wave variation switch
        self.wave_var = Switch("Var", ["A", "B", "C"])
        self.wave_var.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.OSC_WAVE_VAR, v)
        )
        top_row.addWidget(self.wave_var)
        layout.addLayout(top_row)
        
        # Tuning controls
        tuning_group = QGroupBox("Tuning")
        tuning_layout = QVBoxLayout()
        tuning_group.setLayout(tuning_layout)
        
        tuning_layout.addWidget(self._create_parameter_slider(DigitalParameter.OSC_PITCH, "Pitch"))
        tuning_layout.addWidget(self._create_parameter_slider(DigitalParameter.OSC_DETUNE, "Detune"))
        layout.addWidget(tuning_group)
        
        # Pulse Width controls (only enabled for PW-SQUARE wave)
        pw_group = QGroupBox("Pulse Width")
        pw_layout = QVBoxLayout()
        pw_group.setLayout(pw_layout)
        
        self.pw_slider = self._create_parameter_slider(DigitalParameter.OSC_PW, "Width")
        self.pwm_slider = self._create_parameter_slider(DigitalParameter.OSC_PWM_DEPTH, "Mod")
        pw_layout.addWidget(self.pw_slider)
        pw_layout.addWidget(self.pwm_slider)
        layout.addWidget(pw_group)
        
        # Pitch Envelope
        pitch_env_group = QGroupBox("Pitch Envelope")
        pitch_env_layout = QVBoxLayout()
        pitch_env_group.setLayout(pitch_env_layout)
        
        pitch_env_layout.addWidget(self._create_parameter_slider(DigitalParameter.OSC_PITCH_ATTACK, "Attack"))
        pitch_env_layout.addWidget(self._create_parameter_slider(DigitalParameter.OSC_PITCH_DECAY, "Decay"))
        pitch_env_layout.addWidget(self._create_parameter_slider(DigitalParameter.OSC_PITCH_DEPTH, "Depth"))
        layout.addWidget(pitch_env_group)
        
        # Wave gain control
        self.wave_gain = Switch("Gain", ["-6dB", "0dB", "+6dB", "+12dB"])
        self.wave_gain.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.WAVE_GAIN, v)
        )
        layout.addWidget(self.wave_gain)

        # Super Saw detune (only for SUPER-SAW wave)
        self.super_saw_detune = self._create_parameter_slider(
            DigitalParameter.SUPER_SAW_DETUNE, "S-Saw Detune"
        )
        layout.addWidget(self.super_saw_detune)
        
        # Update PW controls enabled state when waveform changes
        self._update_pw_controls_state(OscWave.SAW)  # Initial state
        
        # PCM Wave number selector (only for PCM wave)
        pcm_group = QGroupBox("PCM Wave")
        pcm_layout = QVBoxLayout()
        pcm_group.setLayout(pcm_layout)
        
        # Wave number spinner/selector
        wave_row = QHBoxLayout()
        self.wave_number = QSpinBox()
        self.wave_number.setRange(0, 16384)
        self.wave_number.setValue(0)
        self.wave_number.valueChanged.connect(self._on_wave_number_changed)
        wave_row.addWidget(QLabel("Number:"))
        wave_row.addWidget(self.wave_number)
        pcm_layout.addLayout(wave_row)
        
        layout.addWidget(pcm_group)
        pcm_group.setVisible(False)  # Hide initially
        self.pcm_group = pcm_group  # Store reference for visibility control
        
        return group

    def _update_pw_controls_state(self, waveform: OscWave):
        """Update pulse width controls enabled state based on waveform"""
        pw_enabled = (waveform == OscWave.PW_SQUARE)
        self.pw_slider.setEnabled(pw_enabled)
        self.pwm_slider.setEnabled(pw_enabled)

    def _update_pcm_controls_state(self, waveform: OscWave):
        """Update PCM wave controls visibility based on waveform"""
        self.pcm_group.setVisible(waveform == OscWave.PCM)

    def _on_wave_number_changed(self, value: int):
        """Handle wave number changes"""
        try:
            # Send wave number in 4-bit chunks
            b1 = (value >> 12) & 0x0F  # Most significant 4 bits
            b2 = (value >> 8) & 0x0F   # Next 4 bits
            b3 = (value >> 4) & 0x0F   # Next 4 bits
            b4 = value & 0x0F          # Least significant 4 bits
            
            # Send each byte
            self.send_midi_parameter(DigitalParameter.WAVE_NUMBER_1, b1)
            self.send_midi_parameter(DigitalParameter.WAVE_NUMBER_2, b2)
            self.send_midi_parameter(DigitalParameter.WAVE_NUMBER_3, b3)
            self.send_midi_parameter(DigitalParameter.WAVE_NUMBER_4, b4)
            
        except Exception as e:
            logging.error(f"Error setting wave number: {str(e)}")

    def _create_filter_section(self):
        group = QGroupBox("Filter")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Filter type controls
        type_row = QHBoxLayout()
        
        # Filter mode switch
        self.filter_mode = Switch("Mode", ["BYPASS", "LPF", "HPF", "BPF", "PKG", "LPF2", "LPF3", "LPF4"])
        self.filter_mode.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.FILTER_MODE, v)
        )
        type_row.addWidget(self.filter_mode)
        
        # Filter slope switch
        self.filter_slope = Switch("Slope", ["-12dB", "-24dB"])
        self.filter_slope.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.FILTER_SLOPE, v)
        )
        type_row.addWidget(self.filter_slope)
        layout.addLayout(type_row)
        
        # Main filter controls
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        controls_group.setLayout(controls_layout)
        
        controls_layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_CUTOFF, "Cutoff"))
        controls_layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_RESONANCE, "Resonance"))
        controls_layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_KEYFOLLOW, "KeyFollow"))
        controls_layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_VELOCITY, "Velocity"))
        layout.addWidget(controls_group)
        
        # Filter envelope
        env_group = QGroupBox("Envelope")
        env_layout = QVBoxLayout()
        env_group.setLayout(env_layout)
        
        # ADSR controls
        adsr_layout = QHBoxLayout()
        adsr_layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_ENV_ATTACK, "A"))
        adsr_layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_ENV_DECAY, "D"))
        adsr_layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_ENV_SUSTAIN, "S"))
        adsr_layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_ENV_RELEASE, "R"))
        env_layout.addLayout(adsr_layout)
        
        # Envelope depth
        env_layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_ENV_DEPTH, "Depth"))
        layout.addWidget(env_group)
        
        # HPF cutoff
        controls_layout.addWidget(self._create_parameter_slider(
            DigitalParameter.HPF_CUTOFF, "HPF Cutoff"
        ))

        # Aftertouch sensitivity
        controls_layout.addWidget(self._create_parameter_slider(
            DigitalParameter.CUTOFF_AFTERTOUCH, "AT Sens"
        ))
        
        # Update enabled states based on filter mode
        self._update_filter_controls_state(0)  # Initial state BYPASS
        
        return group

    def _update_filter_controls_state(self, mode: int):
        """Update filter controls enabled state based on mode"""
        enabled = (mode != 0)  # Enable if not BYPASS
        for param in [
            DigitalParameter.FILTER_CUTOFF,
            DigitalParameter.FILTER_RESONANCE,
            DigitalParameter.FILTER_KEYFOLLOW,
            DigitalParameter.FILTER_VELOCITY,
            DigitalParameter.FILTER_ENV_ATTACK,
            DigitalParameter.FILTER_ENV_DECAY,
            DigitalParameter.FILTER_ENV_SUSTAIN,
            DigitalParameter.FILTER_ENV_RELEASE,
            DigitalParameter.FILTER_ENV_DEPTH
        ]:
            if param in self.controls:
                self.controls[param].setEnabled(enabled)

    def _create_amp_section(self):
        group = QGroupBox("Amplifier")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Level and velocity controls
        controls_group = QGroupBox("Controls")
        controls_layout = QVBoxLayout()
        controls_group.setLayout(controls_layout)
        
        controls_layout.addWidget(self._create_parameter_slider(DigitalParameter.AMP_LEVEL, "Level"))
        controls_layout.addWidget(self._create_parameter_slider(DigitalParameter.AMP_VELOCITY, "Velocity"))
        
        # Create and center the pan slider
        pan_slider = self._create_parameter_slider(DigitalParameter.AMP_PAN, "Pan")
        pan_slider.setValue(0)  # Center the pan slider
        controls_layout.addWidget(pan_slider)
        
        layout.addWidget(controls_group)
        
        # Amp envelope
        env_group = QGroupBox("Envelope")
        env_layout = QHBoxLayout()
        env_group.setLayout(env_layout)
        
        env_layout.addWidget(self._create_parameter_slider(DigitalParameter.AMP_ENV_ATTACK, "A"))
        env_layout.addWidget(self._create_parameter_slider(DigitalParameter.AMP_ENV_DECAY, "D"))
        env_layout.addWidget(self._create_parameter_slider(DigitalParameter.AMP_ENV_SUSTAIN, "S"))
        env_layout.addWidget(self._create_parameter_slider(DigitalParameter.AMP_ENV_RELEASE, "R"))
        
        layout.addWidget(env_group)
        
        # Keyfollow and aftertouch
        controls_layout.addWidget(self._create_parameter_slider(
            DigitalParameter.AMP_KEYFOLLOW, "KeyFollow"
        ))
        controls_layout.addWidget(self._create_parameter_slider(
            DigitalParameter.LEVEL_AFTERTOUCH, "AT Sens"
        ))
        
        return group

    def _create_lfo_section(self):
        group = QGroupBox("LFO")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Shape and sync controls
        top_row = QHBoxLayout()
        
        # Shape switch
        self.lfo_shape = Switch("Shape", ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"])
        self.lfo_shape.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.LFO_SHAPE, v)
        )
        top_row.addWidget(self.lfo_shape)
        
        # Sync switch
        self.lfo_sync = Switch("Sync", ["OFF", "ON"])
        self.lfo_sync.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.LFO_SYNC, v)
        )
        top_row.addWidget(self.lfo_sync)
        layout.addLayout(top_row)
        
        # Rate and fade controls
        layout.addWidget(self._create_parameter_slider(DigitalParameter.LFO_RATE, "Rate"))
        layout.addWidget(self._create_parameter_slider(DigitalParameter.LFO_FADE, "Fade"))
        
        # Key trigger switch
        self.lfo_trigger = Switch("Key Trigger", ["OFF", "ON"])
        self.lfo_trigger.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.LFO_TRIGGER, v)
        )
        layout.addWidget(self.lfo_trigger)
        
        # Modulation depths
        depths_group = QGroupBox("Depths")
        depths_layout = QVBoxLayout()
        depths_group.setLayout(depths_layout)
        
        depths_layout.addWidget(self._create_parameter_slider(DigitalParameter.LFO_PITCH, "Pitch"))
        depths_layout.addWidget(self._create_parameter_slider(DigitalParameter.LFO_FILTER, "Filter"))
        depths_layout.addWidget(self._create_parameter_slider(DigitalParameter.LFO_AMP, "Amp"))
        depths_layout.addWidget(self._create_parameter_slider(DigitalParameter.LFO_PAN, "Pan"))
        layout.addWidget(depths_group)
        
        return group

    def _create_mod_lfo_section(self):
        """Create modulation LFO section"""
        group = QGroupBox("Mod LFO")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Shape and sync controls
        top_row = QHBoxLayout()
        
        # Shape switch
        self.mod_lfo_shape = Switch("Shape", ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"])
        self.mod_lfo_shape.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.MOD_LFO_SHAPE, v)
        )
        top_row.addWidget(self.mod_lfo_shape)
        
        # Sync switch
        self.mod_lfo_sync = Switch("Sync", ["OFF", "ON"])
        self.mod_lfo_sync.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.MOD_LFO_SYNC, v)
        )
        top_row.addWidget(self.mod_lfo_sync)
        layout.addLayout(top_row)
        
        # Rate and note controls
        rate_row = QHBoxLayout()
        rate_row.addWidget(self._create_parameter_slider(DigitalParameter.MOD_LFO_RATE, "Rate"))
        
        # Note selection (only visible when sync is ON)
        self.mod_lfo_note = Switch("Note", ["16", "12", "8", "4", "2", "1", "3/4", "2/3", "1/2",
                                          "3/8", "1/3", "1/4", "3/16", "1/6", "1/8", "3/32",
                                          "1/12", "1/16", "1/24", "1/32"])
        self.mod_lfo_note.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalParameter.MOD_LFO_NOTE, v)
        )
        rate_row.addWidget(self.mod_lfo_note)
        layout.addLayout(rate_row)
        
        # Modulation depths
        depths_group = QGroupBox("Depths")
        depths_layout = QVBoxLayout()
        depths_group.setLayout(depths_layout)
        
        depths_layout.addWidget(self._create_parameter_slider(DigitalParameter.MOD_LFO_PITCH, "Pitch"))
        depths_layout.addWidget(self._create_parameter_slider(DigitalParameter.MOD_LFO_FILTER, "Filter"))
        depths_layout.addWidget(self._create_parameter_slider(DigitalParameter.MOD_LFO_AMP, "Amp"))
        depths_layout.addWidget(self._create_parameter_slider(DigitalParameter.MOD_LFO_PAN, "Pan"))
        layout.addWidget(depths_group)
        
        # Rate control
        layout.addWidget(self._create_parameter_slider(
            DigitalParameter.MOD_LFO_RATE_CTRL, "Rate Ctrl"
        ))
        
        return group

    def send_midi_parameter(self, param, value) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False
            
        try:
            # Get parameter group and address with partial offset
            if isinstance(param, DigitalParameter):
                group, param_address = param.get_address_for_partial(self.partial_num)
            else:
                group = 0x00  # Common parameters group
                param_address = param.address

            return self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=self.part,
                group=group,
                param=param_address,
                value=value
            )
        except Exception as e:
            logging.error(f"MIDI error setting {param}: {str(e)}")
            return False

    def _on_parameter_changed(self, param: Union[DigitalParameter, DigitalCommonParameter], display_value: int):
        """Handle parameter value changes from UI controls"""
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, 'convert_from_display'):
                midi_value = param.convert_from_display(display_value)
            else:
                midi_value = param.validate_value(display_value)
            
            # Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")
            
        except Exception as e:
            logging.error(f"Error handling parameter {param.name}: {str(e)}")

    def _on_waveform_selected(self, waveform: OscWave):
        """Handle waveform button clicks"""
        # Update button states
        for wave, btn in self.wave_buttons.items():
            btn.setChecked(wave == waveform)
            
        # Send MIDI message
        if not self.send_midi_parameter(DigitalParameter.OSC_WAVE, waveform.value):
            logging.warning(f"Failed to set waveform to {waveform.name}")
        
        # Update control visibility
        self._update_pw_controls_state(waveform)
        self._update_pcm_controls_state(waveform)

class DigitalSynthEditor(BaseEditor):
    def __init__(self, midi_helper=None, synth_num=1, parent=None):
        super().__init__(midi_helper, parent)
        self.synth_num = synth_num
        self.part = PART_1 if synth_num == 1 else PART_2
        self.setWindowTitle(f"Digital Synth {synth_num}")
        
        # Store parameter controls for easy access
        self.controls: Dict[Union[DigitalParameter, DigitalCommonParameter], QWidget] = {}
        
        # Allow resizing
        self.setMinimumSize(800, 400)
        self.resize(1000, 600)
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create container widget
        container = QWidget()
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        
        # Add partials panel at the top
        self.partials_panel = PartialsPanel()
        container_layout.addWidget(self.partials_panel)
        
        # Add performance section
        container_layout.addWidget(self._create_performance_section())
        
        # Create tab widget for partials
        self.tabs = QTabWidget()
        self.partial_editors = {}
        
        # Create editor for each partial
        for i in range(1, 4):
            editor = PartialEditor(midi_helper, i, self.part)
            self.partial_editors[i] = editor
            self.tabs.addTab(editor, f"Partial {i}")
        
        container_layout.addWidget(self.tabs)
        
        # Add container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        # Connect partial switches to enable/disable tabs
        for switch in self.partials_panel.switches.values():
            switch.stateChanged.connect(self._on_partial_state_changed)
        
        # Initialize with default states
        self.initialize_partial_states()

    def _create_performance_section(self):
        """Create performance controls section"""
        group = QGroupBox("Performance")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Create two rows of controls
        top_row = QHBoxLayout()
        bottom_row = QHBoxLayout()
        
        # Ring Modulator switch
        self.ring_switch = Switch("Ring", ["OFF", "---", "ON"])
        self.ring_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalCommonParameter.RING_SWITCH, v)
        )
        top_row.addWidget(self.ring_switch)
        
        # Unison switch and size
        self.unison_switch = Switch("Unison", ["OFF", "ON"])
        self.unison_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalCommonParameter.UNISON_SWITCH, v)
        )
        top_row.addWidget(self.unison_switch)
        
        self.unison_size = Switch("Size", ["2 VOICE", "3 VOICE", "4 VOICE", "5 VOICE"])
        self.unison_size.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalCommonParameter.UNISON_SIZE, v)
        )
        top_row.addWidget(self.unison_size)
        
        # Portamento mode and legato
        self.porto_mode = Switch("Porto", ["NORMAL", "LEGATO"])
        self.porto_mode.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalCommonParameter.PORTAMENTO_MODE, v)
        )
        bottom_row.addWidget(self.porto_mode)
        
        self.legato_switch = Switch("Legato", ["OFF", "ON"])
        self.legato_switch.valueChanged.connect(
            lambda v: self._on_parameter_changed(DigitalCommonParameter.LEGATO_SWITCH, v)
        )
        bottom_row.addWidget(self.legato_switch)
        
        # Analog Feel and Wave Shape
        analog_feel = self._create_parameter_slider(DigitalCommonParameter.ANALOG_FEEL, "Analog")
        wave_shape = self._create_parameter_slider(DigitalCommonParameter.WAVE_SHAPE, "Shape")
        
        # Add all controls to layout
        layout.addLayout(top_row)
        layout.addLayout(bottom_row)
        layout.addWidget(analog_feel)
        layout.addWidget(wave_shape)
        
        return group

    def _create_parameter_slider(self, param: Union[DigitalParameter, DigitalCommonParameter], label: str) -> Slider:
        """Create a slider for a parameter with proper display conversion"""
        if hasattr(param, 'get_display_value'):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        
        slider = Slider(label, display_min, display_max)
        
        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        
        # Store control reference
        self.controls[param] = slider
        return slider

    def _on_parameter_changed(self, param: Union[DigitalParameter, DigitalCommonParameter], display_value: int):
        """Handle parameter value changes from UI controls"""
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, 'convert_from_display'):
                midi_value = param.convert_from_display(display_value)
            else:
                midi_value = param.validate_value(display_value)
            
            # Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")
            
        except Exception as e:
            logging.error(f"Error handling parameter {param.name}: {str(e)}")

    def _on_partial_state_changed(self, partial: DigitalPartial, enabled: bool, selected: bool):
        """Handle partial state changes"""
        if self.midi_helper:
            set_partial_state(self.midi_helper, partial, enabled, selected)
            
        # Enable/disable corresponding tab
        partial_num = partial.value
        self.tabs.setTabEnabled(partial_num - 1, enabled)
        
        # Switch to selected partial's tab
        if selected:
            self.tabs.setCurrentIndex(partial_num - 1)

    def initialize_partial_states(self):
        """Initialize partial states with defaults"""
        # Default: Partial 1 enabled and selected, others disabled
        for partial in DigitalPartial.get_partials():
            enabled = (partial == DigitalPartial.PARTIAL_1)
            selected = enabled
            self.partials_panel.switches[partial].setState(enabled, selected)
            self.tabs.setTabEnabled(partial.value - 1, enabled)
            
        # Show first tab
        self.tabs.setCurrentIndex(0)