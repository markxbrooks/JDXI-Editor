"""
ADSR Widget for Roland JD-Xi

This widget provides a visual interface for editing ADSR (Attack, Decay, Sustain, Release) 
envelope parameters. It includes:
- Interactive sliders for each ADSR parameter
- Visual envelope plot
- Real-time parameter updates
- MIDI parameter integration via SynthParameter objects

The widget supports both analog and digital synth parameters and provides visual feedback
through an animated envelope curve.
"""
import logging
import re

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QLabel, QSpinBox, QDoubleSpinBox, QGridLayout, QHBoxLayout
from typing import Dict, List, Union
from jdxi_manager.data.parameter.synth import SynthParameter
from jdxi_manager.ui.widgets.adsr.plot import ADSRPlot
from jdxi_manager.ui.widgets.slider.slider import Slider
from jdxi_manager.ui.style import Style
from jdxi_manager.midi.conversions import midi_cc_to_ms, midi_cc_to_frac, ms_to_midi_cc, ms_to_midi_cc, frac_to_midi_cc

# Precompile the regex pattern at module level or in the class constructor
ENVELOPE_PATTERN = re.compile(r'(attack|decay|release)', re.IGNORECASE)

class ADSRWidgetNew(QWidget):
    envelopeChanged = Signal(dict)

    def __init__(self, attack_param: SynthParameter, decay_param: SynthParameter,
                 sustain_param: SynthParameter, release_param: SynthParameter, parent=None):
        super().__init__(parent)
        
        # Store parameter controls
        self.controls: Dict[SynthParameter, Slider] = {}
        
        # Store ADSR parameters
        self.parameters = {
            'attack': attack_param,
            'decay': decay_param,
            'sustain': sustain_param,
            'release': release_param
        }

        self.envelope = {
            "attack_time": 300,
            "decay_time": 800,
            "release_time": 500,
            "initial_level": 0,
            "peak_level": 1,
            "sustain_level": 0.8,
        }
        self.setMinimumHeight(100)  # Adjust height as needed
        self.attack_sb = self.create_spinbox(
            0, 1000, " ms", self.envelope["attack_time"]
        )
        self.decay_sb = self.create_spinbox(0, 1000, " ms", self.envelope["decay_time"])
        self.release_sb = self.create_spinbox(
            0, 1000, " ms", self.envelope["release_time"]
        )
        #self.initial_sb = self.create_double_spinbox(
        #    0, 1, 0.01, self.envelope["initial_level"]
        #)
        # self.peak_sb = self.create_double_spinbox(0, 1, 0.01, self.envelope["peak_level"])
        self.sustain_sb = self.create_double_spinbox(
            0, 1, 0.01, self.envelope["sustain_level"]
        )
        self.setStyleSheet(Style.EDITOR_STYLE)

        # Create layout
        self.layout = QGridLayout(self)
        self.plot = ADSRPlot()
        
        # Create sliders
        self.attack_slider = self._create_parameter_slider(attack_param, "Attack", value=self.envelope["attack_time"])
        self.decay_slider = self._create_parameter_slider(decay_param, "Decay", value=self.envelope["decay_time"])
        self.sustain_slider = self._create_parameter_slider(sustain_param, "Sustain", value=self.envelope["sustain_level"]* 127)
        self.release_slider = self._create_parameter_slider(release_param, "Release", value=self.envelope["release_time"])

        # Add sliders to layout
        self.layout.addWidget(self.attack_slider, 0, 0)
        self.layout.addWidget(self.decay_slider, 0, 1)
        self.layout.addWidget(self.sustain_slider, 0, 2)
        self.layout.addWidget(self.release_slider, 0, 3)

        self.layout.addWidget(self.attack_sb, 1, 0)
        self.layout.addWidget(self.decay_sb, 1, 1)
        self.layout.addWidget(self.sustain_sb, 1, 2)
        self.layout.addWidget(self.release_sb, 1, 3)
        
        # Add plot
        self.layout.addWidget(self.plot, 0, 4, 4, 1)
        self.layout.setColumnMinimumWidth(4, 150)

        # Connect signals
        #for slider in self.controls.values():
        #    slider.valueChanged.connect(self.valueChanged)
        spin_boxes = [ self.attack_sb, self.decay_sb, self.sustain_sb, self.release_sb ]
        for sb in spin_boxes:
            sb.valueChanged.connect(self.valueChanged)

        self.setLayout(self.layout)
        self.plot.set_values(self.envelope)
        self.update_from_envelope()


    def update_from_envelope(self):
        """Initialize controls with parameter values"""
        self.update_spinboxes_from_envelope()
        self.update_sliders_from_envelope()
        self.update_controls_from_envelope()

    def set_envelope(self, envelope: Dict[str, Union[int, float]]):
        """Set envelope values and update controls"""
        self.envelope = envelope
        self.update_controls_from_envelope()
        self.plot.set_values(self.envelope)

    def _create_parameter_slider(self, param: SynthParameter, label: str, value: int = None) -> Slider:
        """Create a slider for a parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        
        # Create vertical slider
        slider = Slider(label, display_min, display_max, vertical=True, show_value_label=False)
        slider.setValue(value)
        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = slider
        return slider

    def update_envelope_from_controls(self):
        """Update envelope values from slider controls. @@"""
        for param, slider in self.controls.items():
            if param == self.parameters['sustain']:
                self.envelope["sustain_level"] = slider.value() + 1/ 128
                logging.info(f"param: {param} slider value: {slider.value()}")
                logging.info(f'sustain_level: {self.envelope["sustain_level"]}')
            else:
                if match := ENVELOPE_PATTERN.search(param.name):
                    key = f"{match.group().lower()}_time"
                    self.envelope[key] = midi_cc_to_ms(slider.value())
                    logging.info(f"param: {param} slider value: {slider.value()}")
                    logging.info(f'{key}: {self.envelope[key]}')

    def update_controls_from_envelope(self):
        """Update slider controls from envelope values."""
        for param, slider in self.controls.items():
            if param == self.parameters['sustain']:
                slider.setValue(int(self.envelope["sustain_level"] * 128))
                #logging.info(
                #    f"param: {param} value {self.envelope['sustain_level']} slider value: {slider.value()}")
            else:
                if match := ENVELOPE_PATTERN.search(param.name):
                    key = f"{match.group().lower()}_time"
                    slider.setValue(ms_to_midi_cc(self.envelope[key]))

    def _on_parameter_changed(self, param: SynthParameter, value: int):
        """Handle parameter value changes and update envelope accordingly."""
        # logging.info(f"_on_parameter_changed param: {param} value: {value}")

        # Update display range if available
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        # Update envelope based on slider values
        self.update_envelope_from_controls()
        # Update plot and emit change signal
        """
        if param == self.parameters['attack']:
            # self.envelope["attack_time"] = value
            self.attack_sb.blockSignals(True)
            self.attack_sb.setValue(ms_to_midi_cc(self.envelope["attack_time"]))
            self.attack_sb.blockSignals(False)
        elif param == self.parameters['decay']:
            # self.envelope["decay_time"] = value
            self.decay_sb.blockSignals(True)
            self.decay_sb.setValue(frac_to_midi_cc(self.envelope["decay_time"] ))
            self.decay_sb.blockSignals(False)
        elif param == self.parameters['sustain']:
            self.envelope["sustain_level"] = value + 1 /128
            self.sustain_sb.blockSignals(True)
            self.sustain_sb.setValue(self.envelope["sustain_level"])
            self.sustain_sb.blockSignals(False)
        elif param == self.parameters['release']:
            # self.envelope["release_time"] = value
            self.release_sb.blockSignals(True)
            self.release_sb.setValue(ms_to_midi_cc(self.envelope["release_time"]))
            self.release_sb.blockSignals(False)
            self.plot.set_values(self.envelope)
            self.envelopeChanged.emit(self.envelope)
        """
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def update_sliders_from_envelope(self):
        """Update sliders from envelope values and update the plot."""
        self.update_controls_from_envelope()
        self.plot.set_values(self.envelope)

    def valueChanged(self):
        """Update envelope values when spin boxes change"""
        self.updating_from_spinbox = True
        self.envelopeChanged.emit(self.envelope)
        self.update_envelope_from_spinboxes()
        self.update_sliders_from_envelope()
        self.plot.set_values(self.envelope)
        self.updating_from_spinbox = False
        self.envelopeChanged.emit(self.envelope)

    def update_envelope_from_spinboxes(self):
        self.updating_from_spinbox = True
        self.envelope["attack_time"] = (
            self.attack_sb.value()
        )
        self.envelope["decay_time"] = (
            self.decay_sb.value()
        )
        self.envelope["release_time"] = (
            self.release_sb.value()
        )
        self.envelope["sustain_level"] = (
            self.sustain_sb.value()
        )
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)
        self.updating_from_spinbox = False

    def update_spinboxes_from_envelope(self):
        """Updates an ADSR parameter from an external control, avoiding feedback loops."""
        self.blockSignals(True)
        self.attack_sb.setValue(self.envelope["attack_time"])
        self.decay_sb.setValue(self.envelope["decay_time"])
        self.release_sb.setValue(self.envelope["release_time"])
        self.sustain_sb.setValue(self.envelope["sustain_level"])
        self.blockSignals(False)

    def create_spinbox(self, min_value, max_value, suffix, value):
        sb = QSpinBox()
        sb.setRange(min_value, max_value)
        sb.setSuffix(suffix)
        sb.setValue(value)
        return sb

    def create_double_spinbox(self, min_value, max_value, step, value):
        sb = QDoubleSpinBox()
        sb.setRange(min_value, max_value)
        sb.setSingleStep(step)
        sb.setValue(value)
        return sb