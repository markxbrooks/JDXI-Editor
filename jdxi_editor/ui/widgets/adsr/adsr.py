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
from typing import Dict, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QGridLayout

from jdxi_editor.log.error import log_error
from jdxi_editor.log.message import log_message
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.utils.conversions import (
    midi_value_to_ms,
    ms_to_midi_value,
)
from jdxi_editor.ui.widgets.adsr.plot import ADSRPlot
from jdxi_editor.ui.widgets.slider_spinbox.slider_spinbox import AdsrSliderSpinbox
from jdxi_editor.ui.widgets.slider.slider import Slider


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
        """
        Initialize the ADSR widget
        :param attack_param: AddressParameter
        :param decay_param: AddressParameter
        :param sustain_param: AddressParameter
        :param release_param: AddressParameter
        :param initial_param: Optional[AddressParameter]
        :param peak_param: Optional[AddressParameter]
        :param midi_helper: Optional[MidiIOHelper]
        :param address: Optional[RolandSysExAddress]
        :param parent: Optional[QWidget]
        """
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
        self.update_controls_from_envelope()

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
        for control in self.adsr_controls:
            control.setEnabled(enabled)
        self.plot.setEnabled(enabled)

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

    def _create_parameter_slider(
        self, param: AddressParameter, label: str, value: int = None
    ) -> Slider:
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
            label, display_min, display_max, midi_helper=self.midi_helper, vertical=True, show_value_label=False
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
            log_error(f"Error updating parameter: {ex}")
        # 4) Update plot
        self.plot.set_values(self.envelope)
        self.envelopeChanged.emit(self.envelope)

    def update_envelope_from_controls(self):
        """Update envelope values from slider controls"""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type in ["sustain_level", "peak_level"]:
                    self.envelope["sustain_level"] = slider.value() / 127
                else:
                    self.envelope[envelope_param_type] = midi_value_to_ms(
                        slider.value()
                    )
        except Exception as ex:
            log_error(f"Error updating envelope from controls: {ex}")
        self.plot.set_values(self.envelope)

    def update_controls_from_envelope(self):
        """Update slider controls from envelope values."""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "sustain_level":
                    slider.setValue(int(self.envelope["sustain_level"] * 127))
                else:
                    slider.setValue(
                        int(ms_to_midi_value(self.envelope[envelope_param_type]))
                    )
        except Exception as ex:
            log_error(f"Error updating controls from envelope: {ex}")
        self.plot.set_values(self.envelope)

    def send_midi_parameter(self, param: AddressParameter, value: int) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            log_message("No MIDI helper available - parameter change ignored")
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
        except Exception as ex:
            log_error(f"MIDI error setting {param}: {str(ex)}")
            return False
