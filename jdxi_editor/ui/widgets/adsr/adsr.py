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
from typing import Dict, Union, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QSpinBox, QDoubleSpinBox, QGridLayout, QVBoxLayout

from jdxi_editor.globals import LOG_PADDING_WIDTH
from jdxi_editor.log.message import log_slider_parameters
from jdxi_editor.midi.data.address.address import (
    AddressMemoryAreaMSB,
    AddressOffsetTemporaryToneUMB,
    AddressOffsetProgramLMB, RolandSysExAddress,
)
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.utils.conversions import (
    midi_cc_to_ms,
    ms_to_midi_cc,
)
from jdxi_editor.ui.widgets.adsr.graph import ADSRGraph
from jdxi_editor.ui.widgets.adsr.parameter import ADSRParameter
from jdxi_editor.ui.widgets.adsr.plot import ADSRPlot
from jdxi_editor.ui.widgets.slider.slider import Slider
from jdxi_editor.ui.style import JDXIStyle


# Precompile the regex pattern at module level or in the class constructor
ENVELOPE_PATTERN = re.compile(r"(attack|decay|release)", re.IGNORECASE)


def create_spinbox(min_value, max_value, suffix, value):
    sb = QSpinBox()
    sb.setRange(min_value, max_value)
    sb.setSuffix(suffix)
    sb.setValue(value)
    return sb


def create_double_spinbox(min_value, max_value, step, value):
    sb = QDoubleSpinBox()
    sb.setRange(min_value, max_value)
    sb.setSingleStep(step)
    sb.setValue(value)
    return sb

# from PySide6.QtWidgets import QWidget, QSlider, QDoubleSpinBox, QHBoxLayout
# from PySide6.QtCore import Qt


class AdsrSliderSpinbox(QWidget):
    def __init__(self,
                 param,
                 min_value=0,
                 max_value=1,
                 suffix='',
                 label="",
                 value=None,
                 create_parameter_slider=None,
                 parent=None):
        super().__init__(parent)
        self.factor = 1
        if max_value > 1:
            self.factor = max_value
        self.create_parameter_slider = create_parameter_slider
        self.slider = self.create_parameter_slider(param, label, value)
        self.spinbox = create_spinbox(min_value=min_value, max_value=max_value, suffix=suffix, value=value)
        self.spinbox.setRange(min_value, max_value)

        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(self.spinbox)
        self.setLayout(layout)

        # Connect both ways
        self.slider.valueChanged.connect(self._slider_changed)
        self.spinbox.valueChanged.connect(self._spinbox_changed)

    def _slider_changed(self, value):
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(value / self.factor)
        self.spinbox.blockSignals(False)

    def _spinbox_changed(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(int(value * self.factor))
        self.slider.blockSignals(False)

    def setValue(self, value: float):
        self.spinbox.setValue(value)

    def value(self) -> float:
        return self.spinbox.value()


class ADSR(QWidget):
    envelopeChanged = Signal(dict)

    def __init__(
        self,
        attack_param: AddressParameter,
        decay_param: AddressParameter,
        sustain_param: AddressParameter,
        release_param: AddressParameter,
        initial_param: Optional[AddressParameter] = None,
        peak_param: Optional[AddressParameter] = None,
        midi_helper: Optional[MidiIOHelper] = None,
        address: Optional[RolandSysExAddress] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.address = address
        self.midi_helper = midi_helper
        self.controls: Dict[AddressParameter, Slider] = {}
        self.envelope = {
            "attack_time": 300,
            "decay_time": 800,
            "release_time": 500,
            "initial_level": 0,
            "peak_level": 1,
            "sustain_level": 0.8,
        }
        self.attack_control = AdsrSliderSpinbox(
            attack_param,
            min_value=0,
            max_value=1000,
            suffix=" ms",
            label="Attack",
            value=self.envelope["attack_time"],
            create_parameter_slider=self._create_parameter_slider,
        )
        self.decay_control = AdsrSliderSpinbox(
            decay_param,
            min_value=0,
            max_value=1000,
            suffix=" ms",
            label="Decay",
            value=self.envelope["decay_time"],
            create_parameter_slider=self._create_parameter_slider,
        )
        self.release_control = AdsrSliderSpinbox(
            release_param,
            min_value=0,
            max_value=1000,
            suffix=" ms",
            label="Release",
            value=self.envelope["release_time"],
            create_parameter_slider=self._create_parameter_slider,
        )
        self.sustain_control = AdsrSliderSpinbox(
            sustain_param,
            min_value=0,
            max_value=1,
            suffix="",
            label="Sustain",
            value=self.envelope["sustain_level"],
            create_parameter_slider=self._create_parameter_slider,
        )

        self.layout = QGridLayout()
        self.layout.addWidget(self.attack_control, 0, 0)
        self.layout.addWidget(self.decay_control, 0, 1)
        self.layout.addWidget(self.sustain_control, 0, 2)
        self.layout.addWidget(self.release_control, 0, 3)
        self.setLayout(self.layout)

        self.envelope_spinbox_map = {
            "attack_time": self.attack_control.spinbox,
            "decay_time": self.decay_control.spinbox,
            "sustain_level": self.sustain_control.spinbox,
            "release_time": self.release_control.spinbox,
        }
        # Create layout
        self.plot = ADSRPlot(width=300, height=250)
        self.layout.addWidget(self.plot, 0, 4, 3, 1)

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        for control in [self.attack_control, self.decay_control, self.sustain_control, self.release_control]:
            control.setEnabled(enabled)
        self.plot.setEnabled(enabled)

    def update_controls_from_envelope(self):
        self.attack_control.setValue(self.envelope["attack_time"])
        self.decay_control.setValue(self.envelope["decay_time"])
        self.sustain_control.setValue(self.envelope["sustain_level"])
        self.release_control.setValue(self.envelope["release_time"])

    def update_envelope_from_spinboxes(self):
        self.envelope["attack_time"] = self.attack_control.value()
        self.envelope["decay_time"] = self.decay_control.value()
        self.envelope["sustain_level"] = self.sustain_control.value()
        self.envelope["release_time"] = self.release_control.value()

    def update_spinboxes_from_envelope(self):
        self.attack_control.setValue(self.envelope["attack_time"])
        self.decay_control.setValue(self.envelope["decay_time"])
        self.sustain_control.setValue(self.envelope["sustain_level"])
        self.release_control.setValue(self.envelope["release_time"])

    def _create_parameter_slider(self,
                                 param: AddressParameter,
                                 label: str,
                                 value: int = None) -> Slider:
        """ Create address slider for address parameter with proper display conversion """
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        # Create vertical slider
        slider = Slider(
            label, display_min, display_max, vertical=True, show_value_label=False
        )
        slider.setValue(value)
        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        self.controls[param] = slider
        return slider

    def _on_parameter_changed(self, param: AddressParameter, value: int):
        """ Handle parameter value changes and update envelope accordingly """
        # 1) Update envelope based on slider values
        self.update_envelope_from_controls()
        # self._update_spin_box(param)
        try:
            # 2) Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(value)
            else:
                midi_value = param.validate_value(value)
            # 3) Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")
        except ValueError as ex:
            logging.error(f"Error updating parameter: {ex}")
        # 4) Update plot
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def update_envelope_from_controls(self):
        """Update envelope values from slider controls"""
        for param, slider in self.controls.items():
            envelope_param_type = param.get_envelope_param_type()
            if envelope_param_type == "sustain_level":
                self.envelope["sustain_level"] = slider.value() / 127
                log_slider_parameters(self.address.umb, self.address.lmb, param, param.value[0], slider.value())
            else:
                self.envelope[envelope_param_type] = midi_cc_to_ms(slider.value())
                log_slider_parameters(self.address.umb, self.address.lmb, param, param.value[0], slider.value())

    def update_controls_from_envelope(self):
        """Update slider controls from envelope values."""
        for param, slider in self.controls.items():
            envelope_param_type = param.get_envelope_param_type()
            if envelope_param_type == "sustain_level":
                slider.setValue(int(self.envelope["sustain_level"] * 127))
            else:
                slider.setValue(int(ms_to_midi_cc(self.envelope[envelope_param_type])))

    def send_midi_parameter(self, param: AddressParameter, value: int) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False

        try:
            sysex_message = RolandSysEx(
                msb=self.address.msb,
                umb=self.address.umb,
                lmb=self.address.lmb,
                lsb=param.address,
                value=value,
            )
            return self.midi_helper.send_midi_message(sysex_message)
        except Exception as e:
            logging.error(f"MIDI error setting {param}: {str(e)}")
            return False

class AdsrSliderSpinboxOld(QWidget):
    def __init__(self,
                 param,
                 min_value=0,
                 max_value=1,
                 suffix='',
                 label="",
                 value=None,
                 create_parameter_slider=None,
                 parent=None):
        super().__init__(parent)
        self.create_parameter_slider = create_parameter_slider
        self.slider = self.create_parameter_slider(param, label, value)
        self.spinbox = create_spinbox(min_value=min_value, max_value=max_value, suffix=suffix, value=value)
        self.spinbox.setRange(min_value, max_value)

        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(self.spinbox)
        self.setLayout(layout)

        # Connect both ways
        self.slider.valueChanged.connect(self._slider_changed)
        self.spinbox.valueChanged.connect(self._spinbox_changed)

    def _slider_changed(self, value):
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(value / self.factor)
        self.spinbox.blockSignals(False)

    def _spinbox_changed(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(int(value * self.factor))
        self.slider.blockSignals(False)

    def setValue(self, value: float):
        self.spinbox.setValue(value)

    def value(self) -> float:
        return self.spinbox.value()





class ADSROld(QWidget):
    """
    ADSR Editor widget for Roland JD-Xi.

    Provides sliders, spin boxes, and a visual graph to interact with
    ADSR (Attack, Decay, Sustain, Release) MIDI parameters.
    """
    envelopeChanged = Signal(dict)

    def __init__(
        self,
        attack_param: AddressParameter,
        decay_param: AddressParameter,
        sustain_param: AddressParameter,
        release_param: AddressParameter,
        initial_param: Optional[AddressParameter] = None,
        peak_param: Optional[AddressParameter] = None,
        midi_helper: Optional[MidiIOHelper] = None,
        address: Optional[RolandSysExAddress] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        # Store parameter controls
        self.controls: Dict[AddressParameter, Slider] = {}
        self.envelope = {
            "attack_time": 300,
            "decay_time": 800,
            "release_time": 500,
            "initial_level": 0,
            "peak_level": 1,
            "sustain_level": 0.8,
        }
        self.address = address
        self.midi_helper = midi_helper
        self.updating_from_spinbox = False

        self.setMinimumHeight(100)  # Adjust height as needed
        self.attack_sb = create_spinbox(
            0, 1000, " ms", self.envelope["attack_time"]
        )
        self.decay_sb = create_spinbox(0, 1000, " ms", self.envelope["decay_time"])
        self.release_sb = create_spinbox(
            0, 1000, " ms", self.envelope["release_time"]
        )
        # no initial level or peak level in jdxi
        # self.initial_sb = self.create_double_spinbox(
        #    0, 1, 0.01, self.envelope["initial_level"]
        # )
        # self.peak_sb = self.create_double_spinbox(0, 1, 0.01, self.envelope["peak_level"])
        self.sustain_sb = create_double_spinbox(
            0, 1, 0.01, self.envelope["sustain_level"]
        )
        self.setStyleSheet(JDXIStyle.ADSR_ANALOG)

        # Create layout
        self.layout = QGridLayout(self)
        self.plot = ADSRPlot(width=300, height=250)

        # Create sliders
        self.attack_slider = self._create_parameter_slider(
            attack_param, "Attack", value=self.envelope["attack_time"]
        )
        self.decay_slider = self._create_parameter_slider(
            decay_param, "Decay", value=self.envelope["decay_time"]
        )
        self.sustain_slider = self._create_parameter_slider(
            sustain_param, "Sustain", value=self.envelope["sustain_level"] * 127
        )
        self.release_slider = self._create_parameter_slider(
            release_param, "Release", value=self.envelope["release_time"]
        )
        if peak_param:
            self.peak_slider = self._create_parameter_slider(
                peak_param, "Peak", value=self.envelope["peak_level"]
            )
            self.layout.addWidget(self.peak_slider, 0, 4)

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
        self.envelope_spinbox_map = {
            "attack_time": self.attack_sb,
            "decay_time": self.decay_sb,
            "sustain_level": self.sustain_sb,
            "release_time": self.release_sb,
        }
        # Connect signals
        self.spin_boxes = [self.attack_sb, self.decay_sb, self.sustain_sb, self.release_sb]
        for sb in self.spin_boxes:
            sb.valueChanged.connect(self._on_spinbox_value_changed)

        self.setLayout(self.layout)
        self.plot.set_values(self.envelope)
        self.update_from_envelope()
        self.adsr_graph = ADSRGraph()
        self.adsr_graph.point_moved.connect(self.handle_graph_movement)

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

    def setEnabled(self, enabled: bool):
        """
        Set the enabled state (ON/OFF)
        :param enabled: True or False
        """
        super().setEnabled(enabled)  # Ensure QWidget's default behavior is applied
        for slider in self.controls.values():
            slider.setEnabled(enabled)
        for sb in self.spin_boxes:
            sb.setEnabled(enabled)
        self.plot.setEnabled(enabled)  # Disable the ADSR plot interaction if needed

    def _create_parameter_slider(self,
                                 param: AddressParameter,
                                 label: str,
                                 value: int = None) -> Slider:
        """ Create address slider for address parameter with proper display conversion """
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        # Create vertical slider
        slider = Slider(
            label, display_min, display_max, vertical=True, show_value_label=False
        )
        slider.setValue(value)
        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        self.controls[param] = slider
        return slider

    def update_envelope_from_controls(self):
        """Update envelope values from slider controls"""
        for param, slider in self.controls.items():
            envelope_param_type = param.get_envelope_param_type()
            if envelope_param_type == "sustain_level":
                self.envelope["sustain_level"] = slider.value() / 127
                log_slider_parameters(self.address.umb, self.address.lmb, param, param.value[0], slider.value())
            else:
                self.envelope[envelope_param_type] = midi_cc_to_ms(slider.value())
                log_slider_parameters(self.address.umb, self.address.lmb, param, param.value[0], slider.value())

    def update_controls_from_envelope(self):
        """Update slider controls from envelope values."""
        for param, slider in self.controls.items():
            envelope_param_type = param.get_envelope_param_type()
            if envelope_param_type == "sustain_level":
                slider.setValue(int(self.envelope["sustain_level"] * 127))
            else:
                slider.setValue(int(ms_to_midi_cc(self.envelope[envelope_param_type])))

    def _on_parameter_changed(self, param: AddressParameter, value: int):
        """ Handle parameter value changes and update envelope accordingly """
        # 1) Update envelope based on slider values
        self.update_envelope_from_controls()
        self._update_spin_box(param)
        try:
            # 2) Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(value)
            else:
                midi_value = param.validate_value(value)
            # 3) Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")
        except ValueError as ex:
            logging.error(f"Error updating parameter: {ex}")
        # 4) Update plot
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def _update_spin_box(self, param: AddressParameter):
        """Update the corresponding spin box based on the given parameter."""
        envelope_key = param.get_envelope_param_type()
        if envelope_key and envelope_key in self.envelope_spinbox_map:
            spin_box = self.envelope_spinbox_map[envelope_key]
            spin_box.blockSignals(True)
            spin_box.setValue(self.envelope[envelope_key])
            spin_box.blockSignals(False)

    def send_midi_parameter(self, param: AddressParameter, value: int) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False

        try:
            sysex_message = RolandSysEx(
                msb=self.address.msb,
                umb=self.address.umb,
                lmb=self.address.lmb,
                lsb=param.address,
                value=value,
            )
            return self.midi_helper.send_midi_message(sysex_message)
        except Exception as e:
            logging.error(f"MIDI error setting {param}: {str(e)}")
            return False

    def update_sliders_from_envelope(self):
        """Update sliders from envelope values and update the plot."""
        self.update_controls_from_envelope()
        self.plot.set_values(self.envelope)

    def _on_spinbox_value_changed(self):
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
        for key, spinbox in self.envelope_spinbox_map.items():
            self.envelope[key] = spinbox.value()

    def update_spinboxes_from_envelope(self):
        """Updates all spinboxes from the envelope dictionary, avoiding feedback loops."""
        self.blockSignals(True)
        for key, spinbox in self.envelope_spinbox_map.items():
            spinbox.setValue(self.envelope[key])
        self.blockSignals(False)

    def handle_graph_movement(self, point, value):
        if point == "attack":
            self.attack_slider.setValue(int(value * 127))
        elif point == "decay":
            self.decay_slider.setValue(int(value * 127))
        elif point == "release":
            self.release_slider.setValue(int(value * 127))
        self.update_envelope_from_controls()
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)
