"""
PWM Widget
==========

This widget provides a user interface for controlling Pulse Width Modulation (PWM) parameters,
with a graphical plot to visualize the modulation envelope.
It includes controls for pulse width and modulation depth,
and can communicate with MIDI devices.

"""

from typing import Callable, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QSlider, QWidget

from decologr import Decologr as log
from jdxi_editor.jdxi.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.envelope.base import TOOLTIPS, EnvelopeWidgetBase
from jdxi_editor.ui.widgets.pitch.pwm_plot import PWMPlot
from jdxi_editor.ui.widgets.pulse_width.slider_spinbox import PWMSliderSpinbox
from picomidi.constant import Midi
from picomidi.sysex.parameter.address import AddressParameter
from picomidi.utils.conversion import midi_value_to_ms, ms_to_midi_value


class PWMWidget(EnvelopeWidgetBase):

    mod_depth_changed = Signal(dict)
    pulse_width_changed = Signal(dict)
    envelope_changed = Signal(dict)

    def __init__(
        self,
        pulse_width_param: AddressParameter,
        mod_depth_param: AddressParameter,
        midi_helper: Optional[MidiIOHelper] = None,
        controls: dict[AddressParameter, QWidget] = None,
        address: Optional[RolandSysExAddress] = None,
        create_parameter_slider: Callable = None,
        parent: Optional[QWidget] = None,
        analog: bool = False,
    ):
        super().__init__(
            envelope_keys=["pulse_width", "mod_depth"],
            create_parameter_slider=create_parameter_slider,
            parameters=[pulse_width_param, mod_depth_param],
            midi_helper=midi_helper,
            address=address,
            controls=controls,
            parent=parent,
        )
        self.plot = None
        self.setWindowTitle("PWM Widget")
        self.address = address
        self.midi_helper = midi_helper
        self._create_parameter_slider = create_parameter_slider
        if controls:
            self.controls = controls
        else:
            self.controls = {}
        self.envelope = {"pulse_width": 0.5, "mod_depth": 0.5}
        self.pulse_width_control = PWMSliderSpinbox(
            pulse_width_param,
            min_value=0,
            max_value=Midi.VALUE.MAX.SEVEN_BIT,
            units=" %",
            label="Width",
            value=self.envelope["pulse_width"]
            * Midi.VALUE.MAX.SEVEN_BIT,  # Convert from 0.0–1.0 to 0–100
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.mod_depth_control = PWMSliderSpinbox(
            mod_depth_param,
            min_value=0,
            max_value=Midi.VALUE.MAX.SEVEN_BIT,
            units=" %",
            label="Mod Depth",
            value=self.envelope["mod_depth"]
            * Midi.VALUE.MAX.SEVEN_BIT,  # Convert from 0.0–1.0 to 0–100
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.controls[pulse_width_param] = self.pulse_width_control
        self.controls[mod_depth_param] = self.mod_depth_control
        self._control_widgets = [
            self.pulse_width_control,
            self.mod_depth_control,
        ]
        for key, widget in [
            ("pulse_width", self.pulse_width_control),
            ("mod_depth", self.mod_depth_control),
        ]:
            if tooltip := TOOLTIPS.get(key):
                widget.setToolTip(tooltip)
        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 1)  # left side stretches
        self.layout.addWidget(self.mod_depth_control, 0, 1)
        self.layout.addWidget(self.pulse_width_control, 0, 2)
        self.setLayout(self.layout)
        self.plot = PWMPlot(
            width=JDXi.Dimensions.PWM_WIDGET.WIDTH - 20,
            height=JDXi.Dimensions.PWM_WIDGET.HEIGHT - 20,
            parent=self,
            envelope=self.envelope,
        )
        self.layout.addWidget(self.plot, 0, 3)
        self.layout.setColumnStretch(4, 1)  # right side stretches
        self.pulse_width_control.slider.valueChanged.connect(
            self.on_pulse_width_changed
        )
        self.mod_depth_control.slider.valueChanged.connect(self.on_mod_depth_changed)
        self.pulse_width_control.setValue(
            self.envelope["pulse_width"] * Midi.VALUE.MAX.SEVEN_BIT
        )
        self.mod_depth_control.setValue(
            self.envelope["mod_depth"] * Midi.VALUE.MAX.SEVEN_BIT
        )
        JDXi.ThemeManager.apply_adsr_style(self, analog=analog)

    def on_envelope_changed(self, envelope: dict) -> None:
        """
        Handle envelope changes from controls

        :param envelope: dict
        :return: None
        """
        self.envelope = envelope
        print(f"Envelope changed: {self.envelope}")
        self.update()  # Trigger repaint if needed

    def on_pulse_width_changed(self, val: int) -> None:
        """
        Handle pulse width changes from slider

        :param val: int
        :return: None
        """
        self.envelope["pulse_width"] = (
            val / Midi.VALUE.MAX.SEVEN_BIT
        )  # Convert from 0–100 to 0.0–1.0
        self.update()  # Trigger repaint if needed

    def on_mod_depth_changed(self, val: int) -> None:
        """
        Handle modulation depth changes from slider

        :param val: int
        :return: None
        """
        self.envelope["mod_depth"] = (
            val / Midi.VALUE.MAX.SEVEN_BIT
        )  # Convert from 0–100 to 0.0–1.0
        self.update()  # Trigger repaint if needed

    def update_envelope_from_slider(self, slider: QSlider) -> None:
        """Update envelope with value from a single slider"""
        for param, ctrl in self.controls.items():
            if ctrl is slider:
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "mod_depth":
                    self.envelope["mod_depth"] = (
                        slider.value() / Midi.VALUE.MAX.SEVEN_BIT
                    )
                elif envelope_param_type == "pulse_width":
                    self.envelope["pulse_width"] = (
                        slider.value() / Midi.VALUE.MAX.SEVEN_BIT
                    )
                else:
                    pass
                break

    def update_envelope_from_controls(self) -> None:
        """Update envelope values from slider controls"""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                log.message(f"envelope_param_type = {envelope_param_type}")
                if envelope_param_type == "mod_depth":
                    self.envelope["mod_depth"] = (
                        slider.STATUS() / Midi.VALUE.MAX.SEVEN_BIT
                    )
                if envelope_param_type == "pulse_width":
                    self.envelope["pulse_width"] = (
                        slider.STATUS() / Midi.VALUE.MAX.SEVEN_BIT
                    )
                else:
                    self.envelope[envelope_param_type] = midi_value_to_ms(
                        slider.STATUS()
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
                if envelope_param_type == "mod_depth":
                    slider.setValue(
                        int(self.envelope["mod_depth"] * Midi.VALUE.MAX.SEVEN_BIT)
                    )
                if envelope_param_type == "pulse_width":
                    slider.setValue(
                        int(self.envelope["pulse_width"] * Midi.VALUE.MAX.SEVEN_BIT)
                    )
                else:
                    slider.setValue(
                        int(ms_to_midi_value(self.envelope[envelope_param_type]))
                    )
        except Exception as ex:
            log.error(f"Error updating controls from envelope: {ex}")
        self.plot.set_values(self.envelope)
