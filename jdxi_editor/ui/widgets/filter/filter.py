"""
PWM Widget
==========

This widget provides a user interface for controlling Pulse Width Modulation (PWM) parameters,
with a graphical plot to visualize the modulation envelope.
It includes controls for pulse width and modulation depth,
and can communicate with MIDI devices.

"""

from typing import Callable, Optional

from decologr import Decologr as log
from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
from picomidi.constant import Midi
from picomidi.sysex.parameter.address import AddressParameter
from picomidi.utils.conversion import midi_value_to_ms, ms_to_midi_value
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QSlider, QVBoxLayout, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.envelope.base import EnvelopeWidgetBase
from jdxi_editor.ui.widgets.filter.filter_plot import FilterPlot
from jdxi_editor.ui.widgets.pulse_width.slider_spinbox import PWMSliderSpinbox


class FilterWidget(EnvelopeWidgetBase):

    slope_param_changed = Signal(dict)
    cutoff_param_changed = Signal(dict)
    envelope_changed = Signal(dict)

    def __init__(
        self,
        cutoff_param: AddressParameter,
        slope_param: AddressParameter = None,
        midi_helper: Optional[MidiIOHelper] = None,
        controls: dict[AddressParameter, QWidget] = None,
        address: Optional[JDXiSysExAddress] = None,
        create_parameter_slider: Callable = None,
        create_parameter_switch: Callable = None,
        parent: Optional[QWidget] = None,
        analog: bool = False,
    ):
        super().__init__(
            envelope_keys=[EnvelopeParameter.FILTER_CUTOFF, EnvelopeParameter.FILTER_SLOPE],
            create_parameter_slider=create_parameter_slider,
            parameters=[cutoff_param, slope_param],
            midi_helper=midi_helper,
            address=address,
            controls=controls,
            parent=parent,
        )
        self.analog = analog
        self.plot: FilterPlot | None = None
        self.parent = parent
        self.setWindowTitle("Filter Widget")
        self.address = address
        self.midi_helper = midi_helper
        self.slope_param = slope_param  # None for analog (no slope control)
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        if controls is not None:
            self.controls = controls
        else:
            self.controls = {}
        self.envelope = {EnvelopeParameter.FILTER_CUTOFF: 0.5, EnvelopeParameter.FILTER_SLOPE: 0.0}
        self.cutoff_param_control = PWMSliderSpinbox(
            cutoff_param,
            min_value=0,
            max_value=Midi.VALUE.MAX.SEVEN_BIT,
            units=" Hz/10",
            label="Cutoff (Hz /10)",
            value=int(
                self.envelope[EnvelopeParameter.FILTER_CUTOFF] * Midi.VALUE.MAX.SEVEN_BIT
            ),  # Convert from 0.0–1.0 to 0–100
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.controls[cutoff_param] = self.cutoff_param_control
        self._control_widgets = [
            self.cutoff_param_control,
        ]

        self.horizontal_layout = QHBoxLayout()
        self.setLayout(self.horizontal_layout)
        self.filter_mode = "lpf"  # Default filter mode
        self.plot = FilterPlot(
            width=JDXi.UI.Dimensions.PWM_WIDGET.WIDTH - 20,
            height=JDXi.UI.Dimensions.PWM_WIDGET.HEIGHT - 20,
            parent=self,
            envelope=self.envelope,
            filter_mode=self.filter_mode,
        )
        self.controls_vertical_layout = QVBoxLayout()
        self.horizontal_layout.addLayout(self.controls_vertical_layout)
        self.controls_vertical_layout.addWidget(self.cutoff_param_control)
        self.horizontal_layout.addWidget(self.plot)
        self.cutoff_param_control.slider.valueChanged.connect(
            self.on_cutoff_param_changed
        )

        self.cutoff_param_control.setValue(
            self.envelope[EnvelopeParameter.FILTER_CUTOFF] * Midi.VALUE.MAX.SEVEN_BIT
        )
        if self.slope_param:
            self.slope_param_control = self._create_parameter_switch(
                DigitalPartialParam.FILTER_SLOPE,
                label="Slope",
                values=["-12dB", "-24dB"],
            )
            self.controls_vertical_layout.addWidget(self.slope_param_control)
            self.controls[slope_param] = self.slope_param_control
            self._control_widgets.append(self.slope_param_control)
            self.slope_param_control.valueChanged.connect(self.on_slope_param_changed)
            self.slope_param_control.setValue(self.envelope[EnvelopeParameter.FILTER_SLOPE])
            JDXi.UI.Theme.apply_editor_style(self, analog=self.analog)
            JDXi.UI.Theme.apply_adsr_style(self, analog=self.analog)

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
        self.envelope[EnvelopeParameter.FILTER_CUTOFF] = (
            val / Midi.VALUE.MAX.SEVEN_BIT
        )  # Convert from 0–100 to 0.0–1.0
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
            if not hasattr(param, "get_envelope_param_type"):
                continue
            if ctrl is slider:
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == EnvelopeParameter.FILTER_CUTOFF:
                    self.envelope[EnvelopeParameter.FILTER_CUTOFF] = (
                        slider.value() / Midi.VALUE.MAX.SEVEN_BIT
                    )
                else:
                    pass
                break

    def update_envelope_from_controls(self) -> None:
        """Update envelope values from slider controls"""
        try:
            for param, ctrl in self.controls.items():
                if not hasattr(param, "get_envelope_param_type"):
                    continue
                envelope_param_type = param.get_envelope_param_type()
                log.message(f"envelope_param_type = {envelope_param_type}")
                if envelope_param_type == EnvelopeParameter.FILTER_SLOPE:
                    self.envelope[EnvelopeParameter.FILTER_SLOPE] = ctrl.STATUS()  # Keep as 1 or 0
                if envelope_param_type == EnvelopeParameter.FILTER_CUTOFF:
                    self.envelope[EnvelopeParameter.FILTER_CUTOFF] = (
                        ctrl.STATUS() / Midi.VALUE.MAX.SEVEN_BIT
                    )
                else:
                    self.envelope[envelope_param_type] = midi_value_to_ms(ctrl.STATUS())
            log.message(f"{self.envelope}")
        except Exception as ex:
            log.error(f"Error updating envelope from controls: {ex}")
        self.plot.set_values(self.envelope)

    def update_controls_from_envelope(self) -> None:
        """Update slider controls from envelope values."""
        try:
            for param, ctrl in self.controls.items():
                if not hasattr(param, "get_envelope_param_type"):
                    continue
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == EnvelopeParameter.FILTER_SLOPE:
                    ctrl.setValue(int(self.envelope[EnvelopeParameter.FILTER_SLOPE]))
                if envelope_param_type == EnvelopeParameter.FILTER_CUTOFF:
                    ctrl.setValue(
                        int(self.envelope[EnvelopeParameter.FILTER_CUTOFF] * Midi.VALUE.MAX.SEVEN_BIT)
                    )
                else:
                    ctrl.setValue(
                        int(ms_to_midi_value(self.envelope[envelope_param_type]))
                    )
        except Exception as ex:
            log.error(f"Error updating controls from envelope: {ex}", scope=self.__class__.__name__)
        self.plot.set_values(self.envelope)

    def refresh_plot_from_controls(self) -> None:
        """
        Sync envelope from current control values and redraw the plot without emitting.
        Call this after programmatically setting control values (e.g. from incoming SysEx)
        when blockSignals(True) was used, so the plot reflects the new values.
        """
        self.envelope[EnvelopeParameter.FILTER_CUTOFF] = self.cutoff_param_control.value()
        self.envelope[EnvelopeParameter.FILTER_SLOPE] = self.slope_param_control.value()
        self.plot.set_values(self.envelope)