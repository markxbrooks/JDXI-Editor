import logging
from typing import Dict, Optional, Union
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox
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
from jdxi_manager.midi.constants import DIGITAL_SYNTH_AREA, PART_1
from jdxi_manager.ui.widgets.partial_switch import PartialsPanel
from jdxi_manager.ui.widgets.switch import Switch

class DigitalSynthEditor(BaseEditor):
    def __init__(self, midi_helper=None, synth_num=1, parent=None):
        super().__init__(midi_helper, parent)
        self.synth_num = synth_num
        self.part = PART_1 if synth_num == 1 else PART_2
        self.setWindowTitle(f"Digital Synth {synth_num}")
        
        # Store parameter controls for easy access
        self.controls: Dict[Union[DigitalParameter, DigitalCommonParameter], QWidget] = {}
        
        # Check MIDI helper
        if not midi_helper:
            logging.warning("No MIDI helper provided - editor will be in view-only mode")
        
        # Main layout with vertical organization
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Add partials panel at the top
        self.partials_panel = PartialsPanel()
        main_layout.addWidget(self.partials_panel)
        
        # Create horizontal layout for sections
        sections_layout = QHBoxLayout()
        
        # Left column: Performance and Oscillator
        left_column = QVBoxLayout()
        left_column.addWidget(self._create_performance_section())
        left_column.addWidget(self._create_oscillator_section())
        sections_layout.addLayout(left_column)
        
        # Other sections
        sections_layout.addWidget(self._create_filter_section())
        sections_layout.addWidget(self._create_amp_section())
        sections_layout.addWidget(self._create_lfo_section())
        main_layout.addLayout(sections_layout)
        
        # Connect partial switches
        for switch in self.partials_panel.switches.values():
            switch.stateChanged.connect(self._on_partial_state_changed)
        
        # Update initial states
        self.update_partial_states()

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
        
        # Waveform buttons
        wave_layout = QHBoxLayout()
        self.wave_buttons = {}
        for wave in [OscWave.SAW, OscWave.SQUARE, OscWave.TRIANGLE]:
            btn = WaveformButton(wave)
            btn.clicked.connect(lambda checked, w=wave: self._on_waveform_selected(w))
            self.wave_buttons[wave] = btn
            wave_layout.addWidget(btn)
        layout.addLayout(wave_layout)
        
        # Tuning controls
        layout.addWidget(self._create_parameter_slider(DigitalParameter.OSC_COARSE, "Coarse"))
        layout.addWidget(self._create_parameter_slider(DigitalParameter.OSC_FINE, "Fine"))
        
        return group

    def _create_filter_section(self):
        group = QGroupBox("Filter")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Filter controls
        layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_CUTOFF, "Cutoff"))
        layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_RESONANCE, "Resonance"))
        
        # Filter envelope
        env_group = QGroupBox("Envelope")
        env_layout = QHBoxLayout()
        env_group.setLayout(env_layout)
        
        env_layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_ENV_ATTACK, "A"))
        env_layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_ENV_DECAY, "D"))
        env_layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_ENV_SUSTAIN, "S"))
        env_layout.addWidget(self._create_parameter_slider(DigitalParameter.FILTER_ENV_RELEASE, "R"))
        
        layout.addWidget(env_group)
        return group

    def _create_amp_section(self):
        group = QGroupBox("Amplifier")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # Level control
        layout.addWidget(self._create_parameter_slider(DigitalParameter.AMP_LEVEL, "Level"))
        
        # Amp envelope
        env_group = QGroupBox("Envelope")
        env_layout = QHBoxLayout()
        env_group.setLayout(env_layout)
        
        env_layout.addWidget(self._create_parameter_slider(DigitalParameter.AMP_ENV_ATTACK, "A"))
        env_layout.addWidget(self._create_parameter_slider(DigitalParameter.AMP_ENV_DECAY, "D"))
        env_layout.addWidget(self._create_parameter_slider(DigitalParameter.AMP_ENV_SUSTAIN, "S"))
        env_layout.addWidget(self._create_parameter_slider(DigitalParameter.AMP_ENV_RELEASE, "R"))
        
        layout.addWidget(env_group)
        return group

    def _create_lfo_section(self):
        group = QGroupBox("LFO")
        layout = QVBoxLayout()
        group.setLayout(layout)
        
        # LFO controls
        layout.addWidget(self._create_parameter_slider(DigitalParameter.LFO_RATE, "Rate"))
        layout.addWidget(self._create_parameter_slider(DigitalParameter.LFO_DEPTH, "Depth"))
        
        return group

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

    def send_midi_parameter(self, param, value) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False
            
        try:
            return self.midi_helper.send_parameter(
                area=DIGITAL_SYNTH_AREA,
                part=self.part,
                group=0x00,
                param=param,
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
            if not self.send_midi_parameter(param.address, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")
            
        except Exception as e:
            logging.error(f"Error handling parameter {param.name}: {str(e)}")

    def _on_waveform_selected(self, waveform: OscWave):
        """Handle waveform button clicks"""
        # Update button states
        for wave, btn in self.wave_buttons.items():
            btn.setChecked(wave == waveform)
            
        # Send MIDI message
        if not self.send_midi_parameter(DigitalParameter.OSC_WAVE.address, waveform.value):
            logging.warning(f"Failed to set waveform to {waveform.name}") 

    def _on_partial_state_changed(self, partial: DigitalPartial, enabled: bool, selected: bool):
        """Handle partial state changes"""
        if self.midi_helper:
            set_partial_state(self.midi_helper, partial, enabled, selected)

    def update_partial_states(self):
        """Update partial switch states from synth"""
        if not self.midi_helper:
            return
            
        for partial in DigitalPartial.get_partials():  # Only get actual partials
            enabled, selected = get_partial_state(self.midi_helper, partial)
            self.partials_panel.switches[partial].setState(enabled, selected) 