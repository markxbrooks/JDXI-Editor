from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QFrame, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt
import logging

from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.waveform import WaveformButton
from jdxi_manager.ui.editors.base_editor import BaseEditor
from jdxi_manager.data.analog import AnalogParameter, AnalogSynthPatch, AnalogTone
from jdxi_manager.midi.constants import ANALOG_SYNTH_AREA

class AnalogSynthEditor(BaseEditor):
    """Editor for analog synth settings"""
    def __init__(self, midi_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        self.setWindowTitle("Analog Synth")
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Create sections
        self._create_oscillator_section(main_layout)
        self._create_filter_section(main_layout)
        self._create_amp_section(main_layout)
        self._create_lfo_section(main_layout)
        
        # Set window properties
        self.setMinimumWidth(400)
        self.setMinimumHeight(600)
        
        # Send init data when window opens
        if self.connection:
            AnalogTone.send_init_data(self.connection)

    def _create_oscillator_section(self, parent_layout):
        """Create oscillator controls"""
        group = QGroupBox("Oscillator")
        layout = QVBoxLayout(group)
        
        # Waveform selection
        wave_layout = QHBoxLayout()
        wave_layout.addWidget(QLabel("Waveform"))
        self.wave_combo = QComboBox()
        self.wave_combo.addItems(["Saw", "Square", "Triangle"])
        self.wave_combo.currentIndexChanged.connect(
            lambda v: self._send_parameter(AnalogParameter.OSC_WAVE, v))
        wave_layout.addWidget(self.wave_combo)
        layout.addLayout(wave_layout)
        
        # Pitch controls
        self.pitch = Slider("Pitch", -24, 24,
            lambda v: self._send_parameter(AnalogParameter.OSC_PITCH, v + 64))
        layout.addWidget(self.pitch)
        
        parent_layout.addWidget(group)

    def _create_filter_section(self, parent_layout):
        """Create filter controls"""
        group = QGroupBox("Filter")
        layout = QVBoxLayout(group)
        
        # Cutoff and resonance
        self.cutoff = Slider("Cutoff", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.FILTER_CUTOFF, v))
        layout.addWidget(self.cutoff)
        
        self.resonance = Slider("Resonance", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.FILTER_RESONANCE, v))
        layout.addWidget(self.resonance)
        
        parent_layout.addWidget(group)

    def _create_amp_section(self, parent_layout):
        """Create amplifier controls"""
        group = QGroupBox("Amplifier")
        layout = QVBoxLayout(group)
        
        # Level control
        self.level = Slider("Level", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.AMP_LEVEL, v))
        layout.addWidget(self.level)
        
        parent_layout.addWidget(group)

    def _create_lfo_section(self, parent_layout):
        """Create LFO controls"""
        group = QGroupBox("LFO")
        layout = QVBoxLayout(group)
        
        # Rate and depth
        self.lfo_rate = Slider("Rate", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.LFO_RATE, v))
        layout.addWidget(self.lfo_rate)
        
        self.lfo_depth = Slider("Depth", 0, 127,
            lambda v: self._send_parameter(AnalogParameter.LFO_DEPTH, v))
        layout.addWidget(self.lfo_depth)
        
        parent_layout.addWidget(group)

    def _send_parameter(self, param: AnalogParameter, value: int):
        """Send parameter change to device"""
        try:
            if self.midi_helper:
                self.midi_helper.send_parameter(
                    ANALOG_SYNTH_AREA,
                    0x01,  # Part 1
                    0x00,  # Group 0
                    param.value,
                    value
                )
                logging.debug(f"Sent analog parameter {param.name}: {value}")
                
        except Exception as e:
            logging.error(f"Error sending analog parameter: {str(e)}")

    def _handle_midi_message(self, message):
        """Handle incoming MIDI message"""
        try:
            # Extract parameter and value
            param = message[3]  # Parameter number
            value = message[4]  # Parameter value
            
            # Update corresponding control
            if param == AnalogParameter.OSC_WAVE.value:
                self.wave_combo.setCurrentIndex(value)
            elif param == AnalogParameter.OSC_PITCH.value:
                self.pitch.setValue(value - 64)  # Convert to -24/+24
            elif param == AnalogParameter.FILTER_CUTOFF.value:
                self.cutoff.setValue(value)
            elif param == AnalogParameter.FILTER_RESONANCE.value:
                self.resonance.setValue(value)
            elif param == AnalogParameter.AMP_LEVEL.value:
                self.level.setValue(value)
            elif param == AnalogParameter.LFO_RATE.value:
                self.lfo_rate.setValue(value)
            elif param == AnalogParameter.LFO_DEPTH.value:
                self.lfo_depth.setValue(value)
                
            logging.debug(f"Updated analog parameter {hex(param)}: {value}")
            
        except Exception as e:
            logging.error(f"Error handling analog MIDI message: {str(e)}") 

    def showEvent(self, event):
        super().showEvent(event)
        if self.connection:
            AnalogTone.send_init_data(self.connection) 