from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QFrame, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt
import logging

from jdxi_manager.ui.widgets import Slider
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.midi.constants import (
    ANALOG_SYNTH_AREA,
    ANALOG_PART,
    # Oscillator parameters
    ANALOG_OSC_WAVE,
    ANALOG_OSC_COARSE,
    ANALOG_OSC_FINE,
    # Filter parameters
    # Filter modes
    FILTER_MODE_BYPASS,
    FILTER_MODE_LPF,
    ANALOG_LFO_SHAPE,
    ANALOG_LFO_RATE
)
from jdxi_manager.midi.const.analog import (
    ANALOG_FILTER_CUTOFF,
    ANALOG_FILTER_KEYFOLLOW,
    ANALOG_FILTER_RESONANCE,
    ANALOG_FILTER_ENV_VELO,
    ANALOG_FILTER_ENV_A,
    ANALOG_FILTER_ENV_D,
    ANALOG_FILTER_ENV_S,
    ANALOG_FILTER_ENV_R,
    ANALOG_FILTER_ENV_DEPTH,
    # LFO parameters
)

class AnalogSynthEditor(BaseEditor):
    """Editor for JD-Xi Analog Synth parameters"""
    
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        
        # Set window properties
        self.setWindowTitle("Analog Synth Editor")
        self.resize(400, 600)
        
        # Create main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Create sections
        self._create_oscillator_section(main_layout)
        self._create_filter_section(main_layout)
        self._create_amp_section(main_layout)
        self._create_lfo_section(main_layout)
        
        # Add stretch at bottom
        main_layout.addStretch() 

    def _create_oscillator_section(self, parent_layout):
        """Create oscillator section controls"""
        group = QGroupBox("Oscillator")
        layout = QGridLayout()
        group.setLayout(layout)
        
        row = 0
        
        # Waveform selection
        layout.addWidget(QLabel("Wave"), row, 0)
        self.wave_combo = QComboBox()
        self.wave_combo.addItems(["SAW", "TRI", "P.W"])
        self.wave_combo.currentIndexChanged.connect(self._on_osc_wave_changed)
        layout.addWidget(self.wave_combo, row, 1)
        
        row += 1
        
        # Coarse tune (-24/+24)
        layout.addWidget(QLabel("Coarse"), row, 0)
        self.coarse_slider = Slider(-24, 24, 0)
        self.coarse_slider.valueChanged.connect(self._on_osc_coarse_changed)
        layout.addWidget(self.coarse_slider, row, 1)
        
        parent_layout.addWidget(group)

    def _create_filter_section(self, parent_layout):
        """Create filter section controls"""
        group = QGroupBox("Filter")
        layout = QGridLayout()
        group.setLayout(layout)
        
        row = 0
        
        # Filter Type
        layout.addWidget(QLabel("Type"), row, 0)
        self.filter_type_combo = QComboBox()
        self.filter_type_combo.addItems(["BYPASS", "LPF"])
        self.filter_type_combo.currentIndexChanged.connect(self._on_filter_type_changed)
        layout.addWidget(self.filter_type_combo, row, 1)
        
        row += 1
        
        # Cutoff frequency (0-127)
        layout.addWidget(QLabel("Cutoff"), row, 0)
        self.cutoff_slider = Slider(0, 127, 127)
        self.cutoff_slider.valueChanged.connect(self._on_filter_cutoff_changed)
        layout.addWidget(self.cutoff_slider, row, 1)
        
        row += 1
        
        # Resonance (0-127)
        layout.addWidget(QLabel("Resonance"), row, 0)
        self.resonance_slider = Slider(0, 127, 0)
        self.resonance_slider.valueChanged.connect(self._on_filter_resonance_changed)
        layout.addWidget(self.resonance_slider, row, 1)
        
        # Add envelope section
        env_group = QGroupBox("Filter Envelope")
        env_layout = QGridLayout()
        env_group.setLayout(env_layout)
        
        # Attack time
        env_layout.addWidget(QLabel("A"), 0, 0)
        self.filter_env_a = Slider(0, 127, 0)
        self.filter_env_a.valueChanged.connect(self._on_filter_env_a_changed)
        env_layout.addWidget(self.filter_env_a, 0, 1)
        
        # Decay time
        env_layout.addWidget(QLabel("D"), 1, 0)
        self.filter_env_d = Slider(0, 127, 64)
        self.filter_env_d.valueChanged.connect(self._on_filter_env_d_changed)
        env_layout.addWidget(self.filter_env_d, 1, 1)
        
        # Sustain level
        env_layout.addWidget(QLabel("S"), 2, 0)
        self.filter_env_s = Slider(0, 127, 127)
        self.filter_env_s.valueChanged.connect(self._on_filter_env_s_changed)
        env_layout.addWidget(self.filter_env_s, 2, 1)
        
        # Release time
        env_layout.addWidget(QLabel("R"), 3, 0)
        self.filter_env_r = Slider(0, 127, 64)
        self.filter_env_r.valueChanged.connect(self._on_filter_env_r_changed)
        env_layout.addWidget(self.filter_env_r, 3, 1)
        
        # Envelope depth (-63 to +63)
        env_layout.addWidget(QLabel("Depth"), 4, 0)
        self.filter_env_depth = Slider(-63, 63, 0)
        self.filter_env_depth.valueChanged.connect(self._on_filter_env_depth_changed)
        env_layout.addWidget(self.filter_env_depth, 4, 1)
        
        layout.addWidget(env_group, row, 0, 1, 2)
        
        parent_layout.addWidget(group)

    def _create_amp_section(self, parent_layout):
        """Create amplifier section controls"""
        group = QGroupBox("Amplifier")
        layout = QGridLayout()
        group.setLayout(layout)
        
        row = 0
        
        # Level (0-127)
        layout.addWidget(QLabel("Level"), row, 0)
        self.level_slider = Slider(0, 127, 100)
        self.level_slider.valueChanged.connect(self._on_amp_level_changed)
        layout.addWidget(self.level_slider, row, 1)
        
        parent_layout.addWidget(group)

    def _create_lfo_section(self, parent_layout):
        """Create LFO section controls"""
        group = QGroupBox("LFO")
        layout = QGridLayout()
        group.setLayout(layout)
        
        row = 0
        
        # LFO Shape
        layout.addWidget(QLabel("Shape"), row, 0)
        self.lfo_shape_combo = QComboBox()
        self.lfo_shape_combo.addItems(["TRI", "SIN", "SAW", "SQR", "S&H", "RND"])
        self.lfo_shape_combo.currentIndexChanged.connect(self._on_lfo_shape_changed)
        layout.addWidget(self.lfo_shape_combo, row, 1)
        
        row += 1
        
        # LFO Rate (0-127)
        layout.addWidget(QLabel("Rate"), row, 0)
        self.lfo_rate_slider = Slider(0, 127, 64)
        self.lfo_rate_slider.valueChanged.connect(self._on_lfo_rate_changed)
        layout.addWidget(self.lfo_rate_slider, row, 1)
        
        parent_layout.addWidget(group)

    def _on_osc_wave_changed(self, index):
        """Handle oscillator wave change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=ANALOG_OSC_WAVE,
                value=index
            )
            logging.debug(f"Set oscillator wave to {index}")

    def _on_osc_coarse_changed(self, value):
        """Handle oscillator coarse tune change"""
        if self.midi_helper:
            midi_value = value + 64  # Convert to 0-127
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=ANALOG_OSC_COARSE,
                value=midi_value
            )
            logging.debug(f"Set oscillator coarse tune to {value}") 

    def _on_filter_cutoff_changed(self, value):
        """Handle filter cutoff change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=ANALOG_FILTER_CUTOFF,
                value=value
            )
            logging.debug(f"Set filter cutoff to {value}")

    def _on_filter_resonance_changed(self, value):
        """Handle filter resonance change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=ANALOG_FILTER_RESONANCE,
                value=value
            )
            logging.debug(f"Set filter resonance to {value}")

    def _on_amp_level_changed(self, value):
        """Handle amplifier level change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=0x2A,  # Amp level
                value=value
            )
            logging.debug(f"Set amp level to {value}")

    def _on_lfo_shape_changed(self, index):
        """Handle LFO shape change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=ANALOG_LFO_SHAPE,
                value=index
            )
            logging.debug(f"Set LFO shape to {index}")

    def _on_lfo_rate_changed(self, value):
        """Handle LFO rate change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=ANALOG_LFO_RATE,
                value=value
            )
            logging.debug(f"Set LFO rate to {value}")

    def _on_filter_type_changed(self, index):
        """Handle filter type change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=ANALOG_FILTER_SWITCH,
                value=index
            )
            logging.debug(f"Set filter type to {index}")

    def _on_filter_env_a_changed(self, value):
        """Handle filter envelope attack change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=ANALOG_FILTER_ENV_A,
                value=value
            )
            logging.debug(f"Set filter env attack to {value}")

    def _on_filter_env_d_changed(self, value):
        """Handle filter envelope decay change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=ANALOG_FILTER_ENV_D,
                value=value
            )
            logging.debug(f"Set filter env decay to {value}")

    def _on_filter_env_s_changed(self, value):
        """Handle filter envelope sustain change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=ANALOG_FILTER_ENV_S,
                value=value
            )
            logging.debug(f"Set filter env sustain to {value}")

    def _on_filter_env_r_changed(self, value):
        """Handle filter envelope release change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=ANALOG_FILTER_ENV_R,
                value=value
            )
            logging.debug(f"Set filter env release to {value}")

    def _on_filter_env_depth_changed(self, value):
        """Handle filter envelope depth change"""
        if self.midi_helper:
            midi_value = value + 64  # Convert to 1-127
            self.midi_helper.send_parameter(
                area=ANALOG_SYNTH_AREA,
                part=ANALOG_PART,
                group=0x00,
                param=ANALOG_FILTER_ENV_DEPTH,
                value=midi_value
            )
            logging.debug(f"Set filter env depth to {value}") 