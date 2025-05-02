f"""
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

import logging
import re

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QSpinBox, QGridLayout
from typing import Dict, Union, Optional

from jdxi_editor.log.message import log_message
from jdxi_editor.midi.data.address.address import (
    AddressMemoryAreaMSB,
    AddressOffsetTemporaryToneUMB,
    AddressOffsetProgramLMB, RolandSysExAddress,
)
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.ui.widgets.adsr.adsr import AdsrSliderSpinbox
from jdxi_editor.ui.widgets.adsr.plot import ADSRPlot, ADSRParameter
from jdxi_editor.ui.widgets.slider.slider import Slider
from jdxi_editor.jdxi.style import JDXIStyle
from jdxi_editor.midi.utils.conversions import (
    midi_cc_to_ms,
    ms_to_midi_cc,
)

# Precompile the regex pattern at module level or in the class constructor
ENVELOPE_PATTERN = re.compile(r"(attack|decay|release)", re.IGNORECASE)


class PitchEnvelope(QWidget):
    envelopeChanged = Signal(dict)

    def __init__(
            self,
            attack_param: AddressParameter,
            decay_param: AddressParameter,
            depth_param: AddressParameter,
            # release_param: AddressParameter,
            # initial_param: Optional[AddressParameter] = None,
            # peak_param: Optional[AddressParameter] = None,
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
        self.depth_control = AdsrSliderSpinbox(
            depth_param,
            min_value=0.0,
            max_value=1.0,
            suffix="",
            label="Sustain",
            value=self.envelope["peak_level"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.pitch_envelope_controls = [
            self.attack_control,
            self.decay_control,
            self.depth_control,
        ]
        self.layout = QGridLayout()
        self.layout.addWidget(self.attack_control, 0, 0)
        self.layout.addWidget(self.decay_control, 0, 1)
        self.layout.addWidget(self.depth_control, 0, 2)
        self.setLayout(self.layout)

        self.envelope_spinbox_map = {
            "attack_time": self.attack_control.spinbox,
            "decay_time": self.decay_control.spinbox,
            "sustain_level": self.depth_control.spinbox,
        }
        # Create layout
        self.plot = ADSRPlot(width=300, height=250, envelope=self.envelope, parent=self)
        self.layout.addWidget(self.plot, 0, 4, 3, 1)
        self.plot.set_values(self.envelope)
        for control in self.pitch_envelope_controls:
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
        self.plot.set_values(self.envelope)

    def setEnabled(self, enabled: bool):
        """
        Set the enabled state (ON/OFF)
        :param enabled:
        :return:
        """
        super().setEnabled(enabled)
        for control in self.pitch_envelope_controls:
            control.setEnabled(enabled)
        self.plot.setEnabled(enabled)

    def update_controls_from_envelope_old(self):
        """Update slider controls from envelope values."""
        self.attack_control.setValue(self.envelope["attack_time"])
        self.decay_control.setValue(self.envelope["decay_time"])
        self.depth_control.setValue(self.envelope["sustain_level"])
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def update_envelope_from_spinboxes(self):
        """Update envelope values from spinboxes"""
        self.envelope["attack_time"] = self.attack_control.value()
        self.envelope["decay_time"] = self.decay_control.value()
        self.envelope["sustain_level"] = self.depth_control.value()
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def update_spinboxes_from_envelope(self):
        """Update spinboxes from envelope values"""
        self.attack_control.setValue(self.envelope["attack_time"])
        self.decay_control.setValue(self.envelope["decay_time"])
        self.depth_control.setValue(self.envelope["sustain_level"])
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
            log_message(f"Error updating parameter: {ex}", level=logging.ERROR)
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
            log_message(f"Error updating envelope from controls: {ex}", level=logging.ERROR)
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
            log_message(f"Error updating controls from envelope: {ex}", level=logging.ERROR)
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


class PitchEnvelopeOld(QWidget):
    envelopeChanged = Signal(dict)

    def __init__(
        self,
        attack_param: AddressParameter,
        decay_param: AddressParameter,
        depth_param: AddressParameter,
        midi_helper=None,
        address=None,
        parent=None,
    ):
        super().__init__(parent)

        self.controls: Dict[AddressParameter, Slider] = {}
        self.midi_helper = midi_helper
        self.address = address
        self.updating_from_spinbox = False
        self.plot = ADSRPlot(width=300, height=250)

        self.setMinimumHeight(100)  # Adjust height as needed
        self.parameters = {
            "attack": attack_param,
            "decay": decay_param,
            "depth": depth_param,
            "release": 500,
            "sustain_level": 0.8,
        }

        self.envelope = {
            "attack_time": 300,
            "decay_time": 800,
            "depth": 64,  # Centered (0-127 range)
            "release_time": 500,
            "sustain_level": 0.8,
            "peak_level": 1,
        }

        self.setMinimumHeight(100)
        self.attack_sb = self.create_spinbox(
            0, 1000, " ms", self.envelope["attack_time"]
        )
        self.decay_sb = self.create_spinbox(
            0, 1000, " ms", self.envelope[ADSRParameter.DECAY_TIME]
        )
        self.depth_sb = self.create_spinbox(
            -63, 63, " ", self.envelope[ADSRParameter.PEAK_LEVEL]
        )

        self.layout = QGridLayout(self)

        # Create sliders
        self.attack_slider = self._create_parameter_slider(
            attack_param, "Attack", value=self.envelope["attack_time"]
        )
        self.decay_slider = self._create_parameter_slider(
            decay_param, "Decay", value=self.envelope[ADSRParameter.DECAY_TIME]
        )
        self.depth_slider = self._create_parameter_slider(
            depth_param, "Depth", value=self.envelope[ADSRParameter.PEAK_LEVEL]
        )

        # Add sliders to layout
        self.layout.addWidget(self.attack_slider, 0, 0)
        self.layout.addWidget(self.decay_slider, 0, 1)
        self.layout.addWidget(self.depth_slider, 0, 2)

        self.layout.addWidget(self.attack_sb, 1, 0)
        self.layout.addWidget(self.decay_sb, 1, 1)
        self.layout.addWidget(self.depth_sb, 1, 2)
        self.layout.addWidget(self.plot, 0, 4, 3, 1)

        # Connect signals
        for sb in [self.attack_sb, self.decay_sb, self.depth_sb]:
            sb.valueChanged.connect(self.valueChanged)

        self.setLayout(self.layout)
        self.update_from_envelope()
        self.setStyleSheet(JDXIStyle.EDITOR)

    def update_from_envelope(self):
        """Initialize controls with parameter values"""
        self.update_spinboxes_from_envelope()
        self.update_sliders_from_envelope()
        self.update_controls_from_envelope()

    def update_controls_from_envelope(self):
        """Update slider controls from envelope values."""
        for param, slider in self.controls.items():
            # if param == self.parameters['sustain']:
            #    slider.setValue(int(self.envelope[ADSRParameter.SUSTAIN_LEVEL] * 127))
            # else:
            if match := ENVELOPE_PATTERN.search(param.name):
                key = f"{match.group().lower()}_time"
                slider.setValue(ms_to_midi_cc(self.envelope[key]))

    def set_envelope(self, envelope: Dict[str, Union[int, float]]):
        """Set envelope values and update controls"""
        self.envelope = envelope
        self.update_controls_from_envelope()
        self.plot.set_values(self.envelope)

    def _create_parameter_slider(
        self, param: AddressParameter, label: str, value: int = None
    ) -> Slider:
        """Create address slider for address parameter with proper display conversion"""
        # Create vertical slider
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        slider = Slider(
            label, display_min, display_max, vertical=True, show_value_label=False
        )
        slider.setValue(value)
        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = slider
        return slider

    def valueChanged(self):
        self.envelope["attack_time"] = self.attack_sb.value()
        self.envelope[ADSRParameter.DECAY_TIME] = self.decay_sb.value()
        self.envelope[ADSRParameter.PEAK_LEVEL] = self.depth_sb.value()
        self.parameters[ADSRParameter.RELEASE_TIME] = 500

        self.update_sliders_from_envelope()
        self.envelopeChanged.emit(self.envelope)

    def update_envelope_from_controls(self):
        """Update envelope values from slider controls. @@"""
        for param, slider in self.controls.items():
            if match := ENVELOPE_PATTERN.search(param.name):
                key = f"{match.group().lower()}_time"
                self.envelope[key] = midi_cc_to_ms(slider.value())
                log_message(f"param: {param} slider value: {slider.value()}")
                log_message(f"{key}: {self.envelope[key]}")

    def update_spin_box(self, param):
        """Update the corresponding spin box based on the given parameter."""
        # Mapping of parameters to their corresponding spin box and envelope keys
        param_mapping = {
            self.parameters["decay"]: (self.decay_sb, ADSRParameter.DECAY_TIME),
            self.parameters["attack"]: (self.attack_sb, ADSRParameter.ATTACK_TIME),
            self.parameters["depth"]: (self.depth_sb, ADSRParameter.PEAK_LEVEL),
        }

        # Update the corresponding spin box if the parameter is in the mapping
        if param in param_mapping:
            spin_box, envelope_key = param_mapping[param]
            spin_box.blockSignals(True)
            spin_box.setValue(self.envelope[envelope_key])
            spin_box.blockSignals(False)

    def _on_parameter_changed(self, param: AddressParameter, value: int):
        """Handle parameter value changes and update envelope accordingly."""
        # log_message(f"_on_parameter_changed param: {param} value: {value}")
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
            log_message(f"Error updating parameter: {ex}", level=logging.ERROR)
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def update_sliders_from_envelope(self):
        self.attack_slider.setValue(self.envelope["attack_time"])
        self.decay_slider.setValue(self.envelope[ADSRParameter.DECAY_TIME])
        self.depth_slider.setValue(self.envelope[ADSRParameter.PEAK_LEVEL])

    def update_spinboxes_from_envelope(self):
        self.attack_sb.setValue(self.envelope["attack_time"])
        self.decay_sb.setValue(self.envelope[ADSRParameter.DECAY_TIME])
        self.depth_sb.setValue(self.envelope[ADSRParameter.PEAK_LEVEL])

    def create_spinbox(self, min_value, max_value, suffix, value):
        sb = QSpinBox()
        sb.setRange(min_value, max_value)
        sb.setSuffix(suffix)
        sb.setValue(value)
        return sb

    def send_midi_parameter(self, param, value) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False

        try:
            if hasattr(param, "get_nibbled_size"):
                size = param.get_nibbled_size()
            else:
                size = 1
            sysex_message = RolandSysEx(
                msb=self.address.msb,
                umb=self.address.umb,
                lmb=self.address.lmb,
                lsb=param.address,
                value=value,
                size=size,
            )
            return self.midi_helper.send_midi_message(sysex_message)
        except Exception as e:
            log_message(f"MIDI error setting {param}: {str(e)}")
            return False
