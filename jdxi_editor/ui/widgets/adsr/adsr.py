"""
ADSR Widget for Roland JD-Xi

This widget provides address visual interface for editing ADSR (Attack, Decay, Sustain, Release)
envelope parameters. It includes:
- Interactive sliders for each ADSR parameter
- Visual envelope plot
- Real-time parameter updates
- MIDI parameter integration via SynthParameter objects

The widget supports both analog and digital synth parameters and provides visual feedback
through an animated envelope curve.
"""

import re
import logging
from typing import Dict, Union

from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QWidget, QSpinBox, QDoubleSpinBox, QGridLayout

from jdxi_editor.midi.data.address.address import MemoryAreaAddress, ProgramAddressGroup, TemporaryToneAddressOffset
from jdxi_editor.midi.data.parameter.synth import SynthParameter
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.utils.conversions import (
    midi_cc_to_ms,
    ms_to_midi_cc,
)
from jdxi_editor.ui.widgets.adsr.parameter import ADSRParameter
from jdxi_editor.ui.widgets.adsr.plot import ADSRPlot
from jdxi_editor.ui.widgets.slider.slider import Slider
from jdxi_editor.ui.style import JDXIStyle


# Precompile the regex pattern at module level or in the class constructor
ENVELOPE_PATTERN = re.compile(r'(attack|decay|release)', re.IGNORECASE)


class ADSR(QWidget):
    envelopeChanged = Signal(dict)

    def __init__(self,
                 attack_param: SynthParameter,
                 decay_param: SynthParameter,
                 sustain_param: SynthParameter,
                 release_param: SynthParameter,
                 initial_param: SynthParameter = None,
                 peak_param: SynthParameter = None,
                 midi_helper=None,
                 group=None,
                 area=None,
                 part=None,
                 parent=None):
        super().__init__(parent)

        # Store parameter controls
        self.controls: Dict[SynthParameter, Slider] = {}

        # Store ADSR parameters
        self.parameters = {
            ADSRParameter.ATTACK_TIME: attack_param,
            ADSRParameter.DECAY_TIME: decay_param,
            ADSRParameter.SUSTAIN_LEVEL: sustain_param,
            ADSRParameter.RELEASE_TIME: release_param,
            ADSRParameter.INITIAL_LEVEL: initial_param,
            ADSRParameter.PEAK_LEVEL: peak_param,
        }
        self.envelope = {
            "attack_time": 300,
            "decay_time": 800,
            "release_time": 500,
            "initial_level": 0,
            "peak_level": 1,
            "sustain_level": 0.8,
        }
        self.address_lmb = group if group else ProgramAddressGroup.PROGRAM_COMMON
        self.address_msb = area if area else MemoryAreaAddress.TEMPORARY_TONE
        self.address_umb = part if part else TemporaryToneAddressOffset.ANALOG_PART
        self.midi_helper = midi_helper
        self.updating_from_spinbox = False

        self.setMinimumHeight(100)  # Adjust height as needed
        self.attack_sb = self.create_spinbox(
            0, 1000, " ms", self.envelope["attack_time"]
        )
        self.decay_sb = self.create_spinbox(0, 1000, " ms", self.envelope["decay_time"])
        self.release_sb = self.create_spinbox(
            0, 1000, " ms", self.envelope["release_time"]
        )
        # no initial level or peak level in jdxi
        # self.initial_sb = self.create_double_spinbox(
        #    0, 1, 0.01, self.envelope["initial_level"]
        # )
        # self.peak_sb = self.create_double_spinbox(0, 1, 0.01, self.envelope["peak_level"])
        self.sustain_sb = self.create_double_spinbox(
            0, 1, 0.01, self.envelope["sustain_level"]
        )
        self.setStyleSheet(JDXIStyle.ADSR_ANALOG)

        # Create layout
        self.layout = QGridLayout(self)
        self.plot = ADSRPlot(width=300, height=250)

        # Create sliders
        self.attack_slider = self._create_parameter_slider(attack_param, "Attack", value=self.envelope["attack_time"])
        self.decay_slider = self._create_parameter_slider(decay_param, "Decay", value=self.envelope["decay_time"])
        self.sustain_slider = self._create_parameter_slider(sustain_param, "Sustain",
                                                            value=self.envelope["sustain_level"] * 127)
        self.release_slider = self._create_parameter_slider(release_param, "Release",
                                                            value=self.envelope["release_time"])

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
        self.layout.addWidget(self.plot, 0, 4, 3, 1)
        self.layout.setColumnMinimumWidth(4, 150)

        # Connect signals
        spin_boxes = [self.attack_sb, self.decay_sb, self.sustain_sb, self.release_sb]
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

    def setEnabled(self, enabled):
        super().setEnabled(enabled)  # Ensure QWidget's default behavior is applied

        for slider in self.controls.values():
            slider.setEnabled(enabled)

        self.attack_sb.setEnabled(enabled)
        self.decay_sb.setEnabled(enabled)
        self.sustain_sb.setEnabled(enabled)
        self.release_sb.setEnabled(enabled)

        self.plot.setEnabled(enabled)  # Disable the ADSR plot interaction if needed

    def _create_parameter_slider(self, param: SynthParameter, label: str, value: int = None) -> Slider:
        """Create address slider for address parameter with proper display conversion"""
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
            if param == self.parameters[ADSRParameter.SUSTAIN_LEVEL]:
                self.envelope["sustain_level"] = slider.value() / 127
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
            if param == self.parameters[ADSRParameter.SUSTAIN_LEVEL]:
                slider.setValue(int(self.envelope["sustain_level"] * 127))
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
        self.update_spin_box(param)
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(value)
            else:
                midi_value = param.validate_value(value)

            # Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")
        except ValueError as ex:
            logging.error(f"Error updating parameter: {ex}")
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def update_spin_box(self, param):
        """Update the corresponding spin box based on the given parameter."""
        # Mapping of parameters to their corresponding spin box and envelope keys
        param_mapping = {
            self.parameters[ADSRParameter.SUSTAIN_LEVEL]: (self.sustain_sb, "sustain_level"),
            self.parameters[ADSRParameter.ATTACK_TIME]: (self.attack_sb, "attack_time"),
            self.parameters[ADSRParameter.DECAY_TIME]: (self.decay_sb, "decay_time"),
            self.parameters[ADSRParameter.RELEASE_TIME]: (self.release_sb, "release_time"),
        }

        # Update the corresponding spin box if the parameter is in the mapping
        if param in param_mapping:
            spin_box, envelope_key = param_mapping[param]
            spin_box.blockSignals(True)
            spin_box.setValue(self.envelope[envelope_key])
            spin_box.blockSignals(False)

    def send_midi_parameter(self, param, value) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False

        try:
            group = self.group  # Common parameters area
            param_address = param.address
            sysex_message = RolandSysEx(area=self.address_msb,
                                        section=self.part,
                                        group=group,
                                        address_lsb=param_address,
                                        value=value)
            return self.midi_helper.send_midi_message(sysex_message)
        except Exception as e:
            logging.error(f"MIDI error setting {param}: {str(e)}")
            return False

    def update_sliders_from_envelope(self):
        """Update sliders from envelope values and update the plot."""
        self.update_controls_from_envelope()
        self.plot.set_values(self.envelope)

    def valueChanged(self):
        """Update envelope values when spin boxes change"""
        self.updating_from_spinbox = True
        self.blockSignals(True)
        self.update_envelope_from_spinboxes()
        self.update_sliders_from_envelope()
        self.updating_from_spinbox = False
        self.blockSignals(False)
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def update_envelope_from_spinboxes(self):
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
