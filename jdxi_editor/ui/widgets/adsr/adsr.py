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
from collections.abc import Callable
from typing import Dict, Union, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QSpinBox, QDoubleSpinBox, QGridLayout, QVBoxLayout

from jdxi_editor.log.message import log_message
from jdxi_editor.log.slider_parameter import log_slider_parameters
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.utils.conversions import (
    midi_cc_to_ms,
    ms_to_midi_cc,
)
from jdxi_editor.ui.widgets.adsr.graph import ADSRGraph
from jdxi_editor.ui.widgets.adsr.plot import ADSRPlot
from jdxi_editor.ui.widgets.slider.slider import Slider
from jdxi_editor.ui.style import JDXIStyle


def create_spinbox(min_value: int, max_value: int, suffix: str, value: int) -> QSpinBox:
    """
    Create a spinbox with specified range and suffix
    :param min_value: int
    :param max_value: int
    :param suffix: str
    :param value: int
    :return: QSpinBox
    """
    sb = QSpinBox()
    sb.setRange(min_value, max_value)
    sb.setSuffix(suffix)
    sb.setValue(value)
    return sb


def create_double_spinbox(min_value: int,
                          max_value: int,
                          step: float,
                          value: int) -> QDoubleSpinBox:
    """
    Create a double spinbox with specified range, step, and initial value.
    :param min_value: int
    :param max_value: int
    :param step: float
    :param value: int
    :return: QDoubleSpinBox
    """
    sb = QDoubleSpinBox()
    sb.setRange(min_value, max_value)
    sb.setSingleStep(step)
    sb.setValue(value)
    return sb


class AdsrSliderSpinbox(QWidget):
    """
    ADSR Slider and Spinbox widget for Roland JD-Xi
    """

    envelopeChanged = Signal(dict)

    def __init__(self,
                 param: AddressParameter,
                 min_value: float = 0.0,
                 max_value: float = 1.0,
                 suffix: str = "",
                 label: str = "",
                 value: int = None,
                 create_parameter_slider: Callable = None,
                 parent: QWidget = None):
        """
        Initialize the ADSR slider and spinbox widget.
        :param param: AddressParameter
        :param min_value: int
        :param max_value: int
        :param suffix: str
        :param label: str
        :param value: int
        :param create_parameter_slider: Callable
        :param parent: QWidget
        """
        super().__init__(parent)

        self.param = param
        self.factor = 127
        if max_value > 1:
            self.factor = max_value
        self.create_parameter_slider = create_parameter_slider
        self.slider = self.create_parameter_slider(param,
                                                   label,
                                                   value)
        param_type = param.get_envelope_param_type()
        if param_type == "sustain_level":
            self.spinbox = create_double_spinbox(min_value=int(min_value),
                                                 max_value=int(min_value),
                                                 step=0.01,
                                                 value=value)
        else:
            self.spinbox = create_spinbox(min_value=int(min_value),
                                          max_value=int(max_value),
                                          suffix=suffix,
                                          value=value)
        self.spinbox.setRange(min_value, max_value)

        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(self.spinbox)
        self.setLayout(layout)

        # Connect both ways
        self.slider.valueChanged.connect(self._slider_changed)
        self.spinbox.valueChanged.connect(self._spinbox_changed)

    def convert_to_envelope(self, value: float):
        param_type = self.param.get_envelope_param_type()
        if param_type == "sustain_level":
            return value / 127
        elif param_type in ["attack_time", "decay_time", "release_time"]:
            return midi_cc_to_ms(int(value))

    def convert_from_envelope(self, value: float):
        param_type = self.param.get_envelope_param_type()
        if param_type == "sustain_level":
            return int(value * 127)
        elif param_type in ["attack_time", "decay_time", "release_time"]:
            return ms_to_midi_cc(value)
        else:
            return 64

    def _slider_changed(self, value: int):
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(int(self.convert_to_envelope(value)))
        self.spinbox.blockSignals(False)
        self.envelopeChanged.emit({self.param.get_envelope_param_type(): self.convert_to_envelope(value)})

    def _spinbox_changed(self, value: int):
        self.slider.blockSignals(True)
        self.slider.setValue(int(self.convert_from_envelope(int(value))))
        self.slider.blockSignals(False)
        self.envelopeChanged.emit({self.param.get_envelope_param_type(): value})

    def setValue(self, value: float):
        """
        Set the value of the spinbox and slider
        :param value: int
        :return: None
        """
        self.spinbox.setValue(value)

    def value(self) -> float:
        """
        Get the value of the spinbox
        :return: int
        """
        return self.spinbox.value()

    def update(self):
        """Update the envelope values and plot"""
        super().update()
        self.slider.update()
        self.spinbox.update()
        self.parent.update()


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
            parent=self,
        )
        self.decay_control = AdsrSliderSpinbox(
            decay_param,
            min_value=0,
            max_value=1000,
            suffix=" ms",
            label="Decay",
            value=self.envelope["decay_time"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.release_control = AdsrSliderSpinbox(
            release_param,
            min_value=0,
            max_value=1000,
            suffix=" ms",
            label="Release",
            value=self.envelope["release_time"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.sustain_control = AdsrSliderSpinbox(
            sustain_param,
            min_value=0.0,
            max_value=1.0,
            suffix="",
            label="Sustain",
            value=self.envelope["sustain_level"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.adsr_controls = [
            self.attack_control,
            self.decay_control,
            self.sustain_control,
            self.release_control,
        ]
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
        self.plot = ADSRPlot(width=300, height=250, envelope=self.envelope, parent=self)
        self.layout.addWidget(self.plot, 0, 4, 3, 1)
        self.plot.set_values(self.envelope)
        for control in self.adsr_controls:
            control.envelopeChanged.connect(self.on_control_changed)

    def on_control_changed(self, change: dict):
        self.envelope.update(change)
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def update(self):
        """Update the envelope values and plot"""
        super().update()
        self.plot.update()

    def emit_envelope_changed(self) -> None:
        """
        Emit the envelope changed signal
        :param envelope: dict
        :return: None
        """
        # self.envelopeChanged.emit(self.envelope)
        self.plot.set_values(self.envelope)

    def setEnabled(self, enabled: bool):
        """
        Set the enabled state (ON/OFF)
        :param enabled:
        :return:
        """
        super().setEnabled(enabled)
        for control in [self.attack_control, self.decay_control, self.sustain_control, self.release_control]:
            control.setEnabled(enabled)
        self.plot.setEnabled(enabled)

    def update_controls_from_envelope(self):
        """Update slider controls from envelope values."""
        self.attack_control.setValue(self.envelope["attack_time"])
        self.decay_control.setValue(self.envelope["decay_time"])
        self.sustain_control.setValue(self.envelope["sustain_level"])
        self.release_control.setValue(self.envelope["release_time"])
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def update_envelope_from_spinboxes(self):
        """Update envelope values from spinboxes"""
        self.envelope["attack_time"] = self.attack_control.value()
        self.envelope["decay_time"] = self.decay_control.value()
        self.envelope["sustain_level"] = self.sustain_control.value()
        self.envelope["release_time"] = self.release_control.value()
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def update_spinboxes_from_envelope(self):
        """Update spinboxes from envelope values"""
        self.attack_control.setValue(self.envelope["attack_time"])
        self.decay_control.setValue(self.envelope["decay_time"])
        self.sustain_control.setValue(self.envelope["sustain_level"])
        self.release_control.setValue(self.envelope["release_time"])
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def _create_parameter_slider(self,
                                 param: AddressParameter,
                                 label: str,
                                 value: int = None) -> Slider:
        """
        Create address slider for address parameter with proper display conversion
        :param param: AddressParameter
        :param label: str
        :param value: int
        :return: Slider
        """
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

    def _on_parameter_changed(self, param: AddressParameter, value: int) -> None:
        """
        Handle parameter value changes and update envelope accordingly
        :param param: AddressParameter
        :param value: int
        :return: None
        """
        # 1) Update envelope based on slider values
        self.update_envelope_from_controls()
        self.envelopeChanged.emit(self.envelope)
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
            log_message(f"Error updating parameter: {ex}")
        # 4) Update plot
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def update_envelope_from_controls(self):
        """Update envelope values from slider controls"""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "sustain_level":
                    self.envelope["sustain_level"] = slider.value() / 127
                    log_slider_parameters(self.address.umb, self.address.lmb, param, param.value[0], slider.value())
                else:
                    self.envelope[envelope_param_type] = midi_cc_to_ms(slider.value())
                    log_slider_parameters(self.address.umb, self.address.lmb, param, param.value[0], slider.value())
        except Exception as ex:
            log_message(f"Error updating envelope from controls: {ex}")
        self.plot.set_values(self.envelope)

    def update_controls_from_envelope(self):
        """Update slider controls from envelope values."""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "sustain_level":
                    slider.setValue(int(self.envelope["sustain_level"] * 127))
                else:
                    slider.setValue(int(ms_to_midi_cc(self.envelope[envelope_param_type])))
        except Exception as ex:
            log_message(f"Error updating controls from envelope: {ex}")
        self.plot.set_values(self.envelope)

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
            log_message(f"MIDI error setting {param}: {str(e)}")
            return False
