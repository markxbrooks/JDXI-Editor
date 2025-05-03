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

import logging
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QGridLayout
from typing import Dict, Optional

from jdxi_editor.log.error import log_error
from jdxi_editor.log.message import log_message
from jdxi_editor.log.slider_parameter import log_slider_parameters
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.ui.widgets.pitch.envelope_plot import PitchEnvPlot
from jdxi_editor.ui.widgets.slider_spinbox.slider_spinbox import AdsrSliderSpinbox
from jdxi_editor.ui.widgets.slider.slider import Slider
from jdxi_editor.midi.utils.conversions import (
    midi_cc_to_ms,
    ms_to_midi_cc,
)


class PitchEnvelope(QWidget):
    """
    Pitch Envelope Class
    """
    pitchEnvelopeChanged = Signal(dict)

    def __init__(
            self,
            attack_param: AddressParameter,
            decay_param: AddressParameter,
            depth_param: AddressParameter,
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
            "initial_level": 0.0,
            "peak_level": 0.0,
            "sustain_level": 0.0,
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
            label="Depth",
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
            "peak_level": self.depth_control.spinbox,
        }
        self.plot = PitchEnvPlot(width=300,
                                 height=250,
                                 envelope=self.envelope,
                                 parent=self)
        self.layout.addWidget(self.plot, 0, 4, 3, 1)
        self.plot.set_values(self.envelope)
        for control in self.pitch_envelope_controls:
            control.envelopeChanged.connect(self.on_control_changed)
        self.show()

    def on_control_changed(self, change: dict) -> None:
        """
        Control Change callback
        :param change: dict envelope
        :return: None
        :emits: dict pitch envelope parameters
        """
        self.envelope.update(change)
        self.plot.set_values(self.envelope)
        # self.pitchEnvelopeChanged.emit(self.envelope)

    def update(self) -> None:
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

    def setEnabled(self, enabled: bool) -> None:
        """
        Set the enabled state (ON/OFF)
        :param enabled:
        :return: None
        """
        super().setEnabled(enabled)
        for control in self.pitch_envelope_controls:
            control.setEnabled(enabled)
        self.plot.setEnabled(enabled)

    def update_envelope_from_spinboxes(self):
        """
        Update envelope values from spinboxes
        :emits: dict pitch envelope parameters
        """
        self.envelope["attack_time"] = self.attack_control.value()
        self.envelope["decay_time"] = self.decay_control.value()
        # self.envelope["peak_level"] = self.depth_control.value()
        self.plot.set_values(self.envelope)
        self.pitchEnvelopeChanged.emit(self.envelope)

    def update_spinboxes_from_envelope(self):
        """
        Update spinboxes from envelope values
        :emits: dict pitch envelope parameters
        """
        self.attack_control.setValue(self.envelope["attack_time"])
        self.decay_control.setValue(self.envelope["decay_time"])
        # self.depth_control.setValue(self.envelope["peak_level"])
        self.plot.set_values(self.envelope)
        self.pitchEnvelopeChanged.emit(self.envelope)

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
        slider = Slider(label,
                        display_min,
                        display_max,
                        vertical=True,
                        show_value_label=False,
                        is_bipolar=param.is_bipolar)
        slider.setValue(value)
        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        self.controls[param] = slider
        return slider

    def _on_parameter_changed(self,
                              param: AddressParameter,
                              value: int) -> None:
        """
        Handle parameter value changes and update envelope accordingly
        :param param: AddressParameter
        :param value: int
        :return: None
        """
        # 1) Update envelope based on slider values
        self.update_envelope_from_controls()
        log_message(f"{self.envelope}")
        self.pitchEnvelopeChanged.emit(self.envelope)
        # self._update_spin_box(param)
        try:
            # 2) Convert display value to MIDI value if needed
            if hasattr(param, "convert_to_midi"):
                midi_value = param.convert_to_midi(value)
            elif hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(value)
            else:
                midi_value = param.validate_value(value)
            # 3) Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")
        except ValueError as ex:
            log_error(f"Error updating parameter: {ex}", level=logging.ERROR)
        # 4) Update plot
        self.plot.set_values(self.envelope)
        self.pitchEnvelopeChanged.emit(self.envelope)

    def update_envelope_from_controls(self) -> None:
        """Update envelope values from slider controls"""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "sustain_level":
                    self.envelope["sustain_level"] = slider.value() / 127
                elif envelope_param_type == "peak_level":
                    pass
                else:
                    self.envelope[envelope_param_type] = midi_cc_to_ms(slider.value())
        except Exception as ex:
            log_error(f"Error updating envelope from controls: {ex}")
        self.plot.set_values(self.envelope)

    def update_controls_from_envelope(self) -> None:
        """Update slider controls from envelope values."""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "sustain_level":
                    slider.setValue(int(self.envelope["sustain_level"] * 127))
                elif envelope_param_type == "peak_level":
                    pass
                else:
                    slider.setValue(int(ms_to_midi_cc(self.envelope[envelope_param_type])))
        except Exception as ex:
            log_error(f"Error updating controls from envelope: {ex}")
        self.plot.set_values(self.envelope)

    def send_midi_parameter(self,
                            param: AddressParameter,
                            value: int) -> bool:
        """
        Send MIDI parameter with error handling
        :param param: AddressParameter
        :param value: int
        :return: bool True on success, false otherwise
        """
        if not self.midi_helper:
            log_message("No MIDI helper available - parameter change ignored")
            return False

        try:
            sysex_message = RolandSysEx(
                msb=self.address.msb,
                umb=self.address.umb,
                lmb=self.address.lmb,
                lsb=param.lsb,
                value=value,
            )
            return self.midi_helper.send_midi_message(sysex_message)
        except Exception as ex:
            log_error(f"MIDI error setting {param}: {str(ex)}")
            return False
