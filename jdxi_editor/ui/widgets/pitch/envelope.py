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

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QGridLayout, QSlider
from typing import Dict, Optional

from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.address.helpers import apply_address_offset
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.ui.widgets.pitch.envelope_plot import PitchEnvPlot
from jdxi_editor.ui.widgets.pitch.slider_spinbox import PitchEnvSliderSpinbox
from jdxi_editor.ui.widgets.slider.slider import Slider
from jdxi_editor.midi.utils.conversions import (
    midi_value_to_ms,
    ms_to_midi_value,
)


class PitchEnvelopeWidget(QWidget):
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
        controls: dict[AddressParameter, QWidget] = None,
        address: Optional[RolandSysExAddress] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.address = address
        self.midi_helper = midi_helper
        if controls:
            self.controls = controls
        else:
            self.controls = {}
        self.envelope = {
            "attack_time": 300,
            "decay_time": 800,
            "release_time": 500,
            "initial_level": 0.0,
            "peak_level": 0.0,
            "sustain_level": 0.0,
        }
        self.attack_control = PitchEnvSliderSpinbox(
            attack_param,
            min_value=0,
            max_value=5000,
            suffix=" ms",
            label="Attack",
            value=self.envelope["attack_time"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.decay_control = PitchEnvSliderSpinbox(
            decay_param,
            min_value=0,
            max_value=5000,
            suffix=" ms",
            label="Decay",
            value=self.envelope["decay_time"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.depth_control = PitchEnvSliderSpinbox(
            depth_param,
            min_value=1,
            max_value=127,
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
        self.depth_control.spinbox.setEnabled(False)
        self.envelope_spinbox_map = {
            "attack_time": self.attack_control.spinbox,
            "decay_time": self.decay_control.spinbox,
            "peak_level": self.depth_control.spinbox,
        }
        self.plot = PitchEnvPlot(
            width=300, height=250, envelope=self.envelope, parent=self
        )
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
        self.envelope["peak_level"] = self.depth_control.value()
        self.plot.set_values(self.envelope)
        self.pitchEnvelopeChanged.emit(self.envelope)

    def update_spinboxes_from_envelope(self):
        """
        Update spinboxes from envelope values
        :emits: dict pitch envelope parameters
        """
        self.attack_control.setValue(self.envelope["attack_time"])
        self.decay_control.setValue(self.envelope["decay_time"])
        self.depth_control.setValue(self.envelope["peak_level"])
        self.plot.set_values(self.envelope)
        self.pitchEnvelopeChanged.emit(self.envelope)

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
            label,
            min_value=display_min,
            max_value=display_max,
            midi_helper=self.midi_helper,
            vertical=True,
            show_value_label=False,
            is_bipolar=param.is_bipolar,
        )
        slider.setValue(value)
        # Connect value changed signal
        slider.valueChanged.connect(
            lambda v, s=slider: self.update_envelope_from_slider(s)
        )
        slider.valueChanged.connect(lambda v: self.send_parameter_message(param, v))
        self.controls[param] = slider
        return slider

    def send_parameter_message(self, param: AddressParameter, value: int) -> None:
        """
        Handle slider value changes and send midi message
        :param param: AddressParameter
        :param value: int
        :return: None
        Convert display value to MIDI value if needed then send message
        """
        try:
            if hasattr(param, "convert_to_midi"):
                midi_value = param.convert_to_midi(value)
            elif hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(value)
            else:
                midi_value = param.validate_value(value)
            if not self.send_midi_parameter(param, midi_value):
                log.parameter("Failed to send parameter", param)
        except ValueError as ex:
            log.error(f"Error updating parameter: {ex}")

    def _on_parameter_changed(self, param: AddressParameter, value: int) -> None:
        """
        Handle parameter value changes and update envelope accordingly
        :param param: AddressParameter
        :param value: int
        :return: None
        """
        # Update envelope based on slider values
        self.update_envelope_from_controls()
        self.pitchEnvelopeChanged.emit(self.envelope)
        # self._update_spin_box(param)
        self.send_parameter_message(param, value)
        self.plot.set_values(self.envelope)
        self.pitchEnvelopeChanged.emit(self.envelope)

    def update_envelope_from_slider(self, slider: QSlider) -> None:
        """Update envelope with value from a single slider"""
        for param, ctrl in self.controls.items():
            if ctrl is slider:
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "sustain_level":
                    self.envelope["sustain_level"] = slider.value() / 127
                elif envelope_param_type == "peak_level":
                    self.envelope["peak_level"] = slider.value() / 127
                else:
                    self.envelope[envelope_param_type] = midi_value_to_ms(
                        slider.value(), min_time=10, max_time=5000
                    )
                break

    def log_envelope(self) -> None:
        """
        log_envelope
        :return: None
        """
        log.message(f"{self.envelope}")

    def update_envelope_from_controls(self) -> None:
        """Update envelope values from slider controls"""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                log.message(f"envelope_param_type = {envelope_param_type}")
                if envelope_param_type == "sustain_level":
                    self.envelope["sustain_level"] = slider.value() / 127
                elif envelope_param_type == "peak_level":
                    pass
                    # self.envelope["peak_level"] = (slider.value() / 127)
                else:
                    self.envelope[envelope_param_type] = midi_value_to_ms(
                        slider.value()
                    )
            log.message(f"{self.envelope}")
        except Exception as ex:
            log.error(f"Error updating envelope from controls: {ex}")
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
                    # slider.setValue(int((self.envelope["peak_level"] + 0.5) * 127))
                else:
                    slider.setValue(
                        int(ms_to_midi_value(self.envelope[envelope_param_type]))
                    )
        except Exception as ex:
            log.error(f"Error updating controls from envelope: {ex}")
        self.plot.set_values(self.envelope)

    def send_midi_parameter(self, param: AddressParameter, value: int) -> bool:
        """
        Send MIDI parameter with error handling
        :param param: AddressParameter
        :param value: int
        :return: bool True on success, false otherwise
        """
        if not self.midi_helper:
            log.message("No MIDI helper available - parameter change ignored")
            return False
        address = apply_address_offset(self.address, param)

        try:
            sysex_message = RolandSysEx(
                msb=address.msb,
                umb=address.umb,
                lmb=address.lmb,
                lsb=address.lsb,
                value=value,
            )
            return self.midi_helper.send_midi_message(sysex_message)
        except Exception as ex:
            log.error(f"MIDI error setting {param}: {str(ex)}")
            return False
