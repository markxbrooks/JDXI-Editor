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
from typing import Optional, Callable

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.envelope.base import EnvelopeWidgetBase
from jdxi_editor.ui.widgets.pitch.slider_spinbox import PitchEnvSliderSpinbox
from jdxi_editor.midi.utils.conversions import (
    midi_value_to_ms,
    ms_to_midi_value,
)
from jdxi_editor.ui.widgets.wmt.envelope_plot import WMTEnvPlot


class WMTEnvelopeWidget(EnvelopeWidgetBase):
    """
    Pitch Envelope Class
    """

    envelope_changed = Signal(dict)

    def __init__(
            self,
            fade_lower_param: AddressParameter,
            range_lower_param: AddressParameter,
            depth_param: AddressParameter,
            range_upper_param: AddressParameter,
            fade_upper_param: AddressParameter,
            midi_helper: Optional[MidiIOHelper] = None,
            create_parameter_slider: Callable = None,
            controls: dict[AddressParameter, QWidget] = None,
            address: Optional[RolandSysExAddress] = None,
            parent: Optional[QWidget] = None,
    ):
        super().__init__(envelope_keys=["range_lower", "depth", "range_upper"],
                         create_parameter_slider=create_parameter_slider,
                         parameters=[fade_lower_param,
                                     range_lower_param,
                                     depth_param,
                                     range_upper_param,
                                     fade_upper_param],
                         midi_helper=midi_helper,
                         address=address,
                         controls=controls,
                         parent=parent)

        self.address = address
        self.midi_helper = midi_helper
        self.level_param = fade_upper_param
        if controls:
            self.controls = controls
        else:
            self.controls = {}
        self._create_parameter_slider = create_parameter_slider
        self.envelope = {
            "fade_lower": 300,
            "range_lower": 500,
            "range_upper": 500,
            "fade_upper": 500,
            "depth": 1.0,
        }
        self.fade_lower_control = PitchEnvSliderSpinbox(
            fade_lower_param,
            min_value=0,
            max_value=5000,
            units=" ms",
            label="Fade Lower",
            value=self.envelope["fade_lower"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.range_lower_control = PitchEnvSliderSpinbox(
            range_lower_param,
            min_value=0,
            max_value=5000,
            units=" ms",
            label="Range Lower",
            value=self.envelope["range_lower"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.depth_control = PitchEnvSliderSpinbox(
            depth_param,
            min_value=0,
            max_value=5000,
            units=" ms",
            label="Depth",
            value=self.envelope["depth"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.range_upper_control = PitchEnvSliderSpinbox(
            range_upper_param,
            min_value=1,
            max_value=MidiConstant.VALUE_MAX_SEVEN_BIT,
            units="",
            label="Range Upper",
            value=self.envelope["range_upper"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.fade_upper_control = PitchEnvSliderSpinbox(
            fade_upper_param,
            min_value=1,
            max_value=MidiConstant.VALUE_MAX_SEVEN_BIT,
            units="",
            label="Fade Upper",
            value=self.envelope["fade_upper"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self._control_widgets = [
            self.fade_lower_control,
            self.range_lower_control,
            self.depth_control,
            self.range_upper_control,
            self.fade_upper_control,
        ]
        self.controls[fade_lower_param] = self.fade_lower_control
        self.controls[range_lower_param] = self.range_lower_control
        self.controls[depth_param] = self.depth_control
        self.controls[range_upper_param] = self.range_upper_control
        self.controls[fade_upper_param] = self.fade_upper_control

        self.layout = QGridLayout()
        self.layout.addWidget(self.fade_lower_control, 0, 0)
        self.layout.addWidget(self.range_lower_control, 0, 1)
        self.layout.addWidget(self.depth_control, 0, 2)
        self.layout.addWidget(self.range_upper_control, 0, 3)
        self.layout.addWidget(self.fade_upper_control, 0, 4)
        self.setLayout(self.layout)
        self.range_upper_control.spinbox.setEnabled(False)
        self.envelope_spinbox_map = {
            "fade_lower": self.fade_lower_control.spinbox,
            "range_lower": self.range_lower_control.spinbox,
            "depth": self.depth_control.spinbox,
            "range_upper": self.range_upper_control.spinbox,
            "fade_upper": self.fade_upper_control.spinbox,
        }
        self.plot = WMTEnvPlot(
            width=JDXiStyle.ADSR_PLOT_WIDTH,
            height=JDXiStyle.ADSR_PLOT_HEIGHT,
            envelope=self.envelope,
            parent=self
        )
        self.layout.addWidget(self.plot, 0, 5, 3, 1)
        self.plot.set_values(self.envelope)
        for control in self._control_widgets:
            control.envelope_changed.connect(self.on_control_changed)
        self.show()

    def set_values(self, envelope: dict):
        self.envelope = envelope
        self.update()

    def on_control_changed(self, change: dict) -> None:
        """
        Control Change callback
        :param change: dict envelope
        :return: None
        :emits: dict pitch envelope parameters
        """
        self.envelope.update(change)
        self.plot.set_values(self.envelope)

    def update_envelope_from_spinboxes(self):
        """
        Update envelope values from spinboxes
        :emits: dict pitch envelope parameters
        """
        self.envelope["fade_lower"] = self.fade_lower_control.value()
        self.envelope["range_lower"] = self.range_lower_control.value()
        self.envelope["depth"] = self.depth_control.value()
        self.envelope["range_upper"] = self.range_upper_control.value()
        self.envelope["fade_upper"] = self.fade_upper_control.value()
        self.plot.set_values(self.envelope)
        self.envelope_changed.emit(self.envelope)

    def update_spinboxes_from_envelope(self):
        """
        Update spinboxes from envelope values
        :emits: dict pitch envelope parameters
        """
        self.fade_lower_control.setValue(self.envelope["fade_lower"])
        self.range_lower_control.setValue(self.envelope["range_lower"])
        self.depth_control.setValue(self.envelope["depth"])
        self.range_upper_control.setValue(self.envelope["range_upper"])
        self.fade_upper_control.setValue(self.envelope["fade_upper"])
        self.plot.set_values(self.envelope)
        self.envelope_changed.emit(self.envelope)

    def update_envelope_from_slider(self, slider: QSlider) -> None:
        """
        Update envelope with value from a single slider
        :param slider: QSlider
        :return:
        """
        for param, ctrl in self.controls.items():
            if ctrl is slider:
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "depth":
                    self.envelope["depth"] = slider.value() / MidiConstant.VALUE_MAX_SEVEN_BIT
                elif envelope_param_type in ["range_upper",
                                             "fade_upper",
                                             "fade_lower",
                                             "range_lower"]:
                    self.envelope[envelope_param_type] = slider.value() / MidiConstant.VALUE_MAX_SEVEN_BIT
                else:
                    self.envelope[envelope_param_type] = midi_value_to_ms(
                        slider.value(), min_time=10, max_time=5000
                    )
                break

    def update_envelope_from_controls(self) -> None:
        """Update envelope values from slider controls"""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                log.message(f"envelope_param_type = {envelope_param_type}")
                if envelope_param_type == "depth":
                    self.envelope["depth"] = slider.value() / MidiConstant.VALUE_MAX_SEVEN_BIT
                    """elif envelope_param_type in ["range_upper",
                                                 "fade_upper",
                                                 "fade_lower",
                                                 "range_lower"]:
                        self.envelope["envelope_param_type"] = (slider.value() / MidiConstant.VALUE_MAX_SEVEN_BIT)"""
                else:
                    self.envelope[envelope_param_type] = midi_value_to_ms(
                        slider.value()
                    )
            log.message(f"{self.envelope}")
        except Exception as ex:
            log.error(f"Error updating envelope from controls: {ex}")
        self.plot.set_values(self.envelope)

    def update_controls_from_envelope_old(self) -> None:
        """Update slider controls from envelope values."""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "depth":
                    slider.setValue(int(self.envelope["depth"] * MidiConstant.VALUE_MAX_SEVEN_BIT))
                elif envelope_param_type == "range_upper":
                    pass
                    # slider.setValue(int((self.envelope["range_upper"] + 0.5) * 127))
                else:
                    slider.setValue(
                        int(ms_to_midi_value(self.envelope[envelope_param_type]))
                    )
        except Exception as ex:
            log.error(f"Error updating controls from envelope: {ex}")
        self.plot.set_values(self.envelope)

    def update_controls_from_envelope(self) -> None:
        """Update slider controls from envelope values."""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "depth":
                    slider.setValue(int(self.envelope["depth"] * MidiConstant.VALUE_MAX_SEVEN_BIT))
                elif envelope_param_type in ["range_upper", "fade_upper"]:
                    slider.setValue(int(self.envelope[envelope_param_type]))
                elif envelope_param_type in ["fade_lower", "range_lower"]:
                    slider.setValue(
                        ms_to_midi_value(self.envelope[envelope_param_type], min_time=10, max_time=5000)
                    )
        except Exception as ex:
            log.error(f"Error updating controls from envelope: {ex}")


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    test_env = {
        "fade_lower": 200,
        "range_lower": 300,
        "depth": 0.7,
        "range_upper": 400,
        "fade_upper": 300,
    }
    plot = WMTEnvPlot(400, 200, test_env)
    plot.setStyleSheet("background-color: black;")
    plot.show()
    app.exec()