from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QFrame, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt
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
    DIGITAL_PART_1, DIGITAL_PART_2
)

class DigitalSynthEditor(BaseEditor):
    """Editor for digital synth settings"""
    def __init__(self, synth_num=1, midi_helper=None, parent=None):
        super().__init__(midi_helper, parent)
        self.synth_num = synth_num
        self.setWindowTitle(f"Digital Synth {synth_num}")
        
        # Set area based on synth number
        self.area = DIGITAL_SYNTH_1 if synth_num == 1 else DIGITAL_SYNTH_2
        self.part = DIGITAL_PART_1 if synth_num == 1 else DIGITAL_PART_2
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Create sections
        self._create_osc_section(main_layout)
        self._create_filter_section(main_layout)
        self._create_amp_section(main_layout)
        self._create_effects_section(main_layout)
        
        # Set window properties
        self.setMinimumWidth(500)
        self.setMinimumHeight(700)

    def _create_osc_section(self, parent_layout):
        """Create oscillator section"""
        group = QGroupBox("Oscillator")
        layout = QVBoxLayout(group)
        
        # PCM wave selection
        wave_layout = QHBoxLayout()
        wave_layout.addWidget(QLabel("PCM Wave"))
        self.wave_combo = QComboBox()
        self.wave_combo.addItems(DigitalSynth.PCM_WAVES)
        self.wave_combo.currentIndexChanged.connect(
            lambda v: self._send_parameter(DigitalParameter.OSC_WAVE, v))
        wave_layout.addWidget(self.wave_combo)
        layout.addLayout(wave_layout)
        
        # Pitch controls
        self.pitch = Slider("Pitch", -24, 24,
            lambda v: self._send_parameter(DigitalParameter.OSC_PITCH, v + 64))
        layout.addWidget(self.pitch)
        
        parent_layout.addWidget(group)

    def _create_filter_section(self, parent_layout):
        """Create filter section"""
        group = QGroupBox("Filter")
        layout = QVBoxLayout(group)
        
        # Filter controls
        self.cutoff = Slider("Cutoff", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.FILTER_CUTOFF, v))
        layout.addWidget(self.cutoff)
        
        self.resonance = Slider("Resonance", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.FILTER_RESONANCE, v))
        layout.addWidget(self.resonance)
        
        parent_layout.addWidget(group)

    def _create_amp_section(self, parent_layout):
        """Create amplifier section"""
        group = QGroupBox("Amplifier")
        layout = QVBoxLayout(group)
        
        # Level and pan
        self.level = Slider("Level", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.AMP_LEVEL, v))
        layout.addWidget(self.level)
        
        self.pan = Slider("Pan", -64, 63,
            lambda v: self._send_parameter(DigitalParameter.AMP_PAN, v + 64))
        layout.addWidget(self.pan)
        
        parent_layout.addWidget(group)

    def _create_effects_section(self, parent_layout):
        """Create effects section"""
        group = QGroupBox("Effects")
        layout = QVBoxLayout(group)
        
        # Effect sends
        self.reverb = Slider("Reverb Send", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.REVERB_SEND, v))
        layout.addWidget(self.reverb)
        
        self.delay = Slider("Delay Send", 0, 127,
            lambda v: self._send_parameter(DigitalParameter.DELAY_SEND, v))
        layout.addWidget(self.delay)
        
        parent_layout.addWidget(group)

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
                self.pitch.setValue(value - 64)
            elif param == DigitalParameter.FILTER_CUTOFF.value:
                self.cutoff.setValue(value)
            elif param == DigitalParameter.FILTER_RESONANCE.value:
                self.resonance.setValue(value)
            elif param == DigitalParameter.AMP_LEVEL.value:
                self.level.setValue(value)
            elif param == DigitalParameter.AMP_PAN.value:
                self.pan.setValue(value - 64)
            elif param == DigitalParameter.REVERB_SEND.value:
                self.reverb.setValue(value)
            elif param == DigitalParameter.DELAY_SEND.value:
                self.delay.setValue(value)
                
            logging.debug(f"Updated digital synth {self.synth_num} parameter {hex(param)}: {value}")
            
        except Exception as e:
            logging.error(f"Error handling digital MIDI message: {str(e)}") 