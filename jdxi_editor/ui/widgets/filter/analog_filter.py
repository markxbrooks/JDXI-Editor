"""
 PWM Widget
 ==========

 This widget provides a user interface for controlling Pulse Width Modulation (PWM) parameters,
 with a graphical plot to visualize the modulation envelope.
 It includes controls for pulse width and modulation depth,
 and can communicate with MIDI devices.

"""

from typing import Optional, Callable

from PySide6.QtWidgets import QWidget, QSlider, QGridLayout, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Signal

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter import AddressParameter
from jdxi_editor.midi.data.parameter.digital import AddressParameterDigitalPartial
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.utils.conversions import midi_value_to_ms, ms_to_midi_value
from jdxi_editor.ui.widgets.envelope.base import EnvelopeWidgetBase, TOOLTIPS
from jdxi_editor.ui.widgets.filter.filter_plot import FilterPlot
from jdxi_editor.ui.widgets.pulse_width.slider_spinbox import PWMSliderSpinbox
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


class AnalogFilterWidget(EnvelopeWidgetBase):

    slope_param_changed = Signal(dict)
    cutoff_param_changed = Signal(dict)
    envelope_changed = Signal(dict)

    def __init__(self,
                 cutoff_param: AddressParameter,
                 midi_helper: Optional[MidiIOHelper] = None,
                 controls: dict[AddressParameter, QWidget] = None,
                 address: Optional[RolandSysExAddress] = None,
                 create_parameter_slider: Callable = None,
                 parent: Optional[QWidget] = None,
                 ):
        super().__init__(envelope_keys=["cutoff_param"],
                         create_parameter_slider=create_parameter_slider,
                         parameters=[cutoff_param],
                         midi_helper=midi_helper,
                         address=address,
                         controls=controls,
                         parent=parent)
        self.plot = None
        self.parent = parent
        self.setWindowTitle("Filter Widget")
        self.address = address
        self.midi_helper = midi_helper
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_slider = create_parameter_slider
        if controls:
            self.controls = controls
        else:
            self.controls = {}
        self.envelope = {"cutoff_param": 0.5, "slope_param": 0.5}
        self.cutoff_param_control = PWMSliderSpinbox(
            cutoff_param,
            min_value=0,
            max_value=MidiConstant.VALUE_MAX_SEVEN_BIT,
            units=" Hz/10",
            label="Cutoff (Hz /10)",
            value=self.envelope["cutoff_param"] * MidiConstant.VALUE_MAX_SEVEN_BIT,  # Convert from 0.0–1.0 to 0–100
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.controls[cutoff_param] = self.cutoff_param_control
        self._control_widgets = [
            self.cutoff_param_control,
        ]

        self.horizontal_layout = QHBoxLayout()
        self.setLayout(self.horizontal_layout)
        self.plot = FilterPlot(width=JDXiDimensions.PWM_WIDGET_WIDTH - 20,
                               height=JDXiDimensions.PWM_WIDGET_HEIGHT - 20,
                               parent=self,
                               envelope=self.envelope)
        self.controls_vertical_layout = QVBoxLayout()
        self.horizontal_layout.addLayout(self.controls_vertical_layout)
        self.controls_vertical_layout.addWidget(self.cutoff_param_control)
        self.horizontal_layout.addWidget(self.plot)
        self.cutoff_param_control.slider.valueChanged.connect(self.on_cutoff_param_changed)

        self.cutoff_param_control.setValue(self.envelope["cutoff_param"] * MidiConstant.VALUE_MAX_SEVEN_BIT)

    def on_envelope_changed(self, envelope: dict) -> None:
        """
        Handle envelope changes from controls

        :param envelope: dict
        :return: None
        """
        self.envelope = envelope
        print(f"Envelope changed: {self.envelope}")
        self.update()  # Trigger repaint if needed

    def on_cutoff_param_changed(self, val: int) -> None:
        """
        Handle pulse width changes from slider

        :param val: int
        :return: None
        """
        self.envelope["cutoff_param"] = val / MidiConstant.VALUE_MAX_SEVEN_BIT  # Convert from 0–100 to 0.0–1.0
        self.update()  # Trigger repaint if needed

    def on_slope_param_changed(self, val: int) -> None:
        """
        Handle modulation depth changes from slider

        :param val: int
        :return: None
        """
        self.envelope["slope_param"] = val  # keep as binary 1/0
        self.update()  # Trigger repaint if needed

    def update_envelope_from_slider(self, slider: QSlider) -> None:
        """Update envelope with value from a single slider"""
        for param, ctrl in self.controls.items():
            if ctrl is slider:
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "cutoff_param":
                    self.envelope["cutoff_param"] = slider.value() / MidiConstant.VALUE_MAX_SEVEN_BIT
                else:
                    pass
                break

    def update_envelope_from_controls(self) -> None:
        """Update envelope values from slider controls"""
        try:
            for param, ctrl in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                log.message(f"envelope_param_type = {envelope_param_type}")
                if envelope_param_type == "slope_param":
                    self.envelope["slope_param"] = ctrl.value()  # Keep as 1 or 0
                if envelope_param_type == "cutoff_param":
                    self.envelope["cutoff_param"] = ctrl.value() / MidiConstant.VALUE_MAX_SEVEN_BIT
                else:
                    self.envelope[envelope_param_type] = midi_value_to_ms(
                        ctrl.value()
                    )
            log.message(f"{self.envelope}")
        except Exception as ex:
            log.error(f"Error updating envelope from controls: {ex}")
        self.plot.set_values(self.envelope)

    def update_controls_from_envelope(self) -> None:
        """Update slider controls from envelope values."""
        try:
            for param, ctrl in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "slope_param":
                    ctrl.setValue(int(self.envelope["slope_param"]))
                if envelope_param_type == "cutoff_param":
                    ctrl.setValue(int(self.envelope["cutoff_param"] * MidiConstant.VALUE_MAX_SEVEN_BIT))
                else:
                    ctrl.setValue(
                        int(ms_to_midi_value(self.envelope[envelope_param_type]))
                    )
        except Exception as ex:
            log.error(f"Error updating controls from envelope: {ex}")
        self.plot.set_values(self.envelope)
