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

from typing import Callable, Optional

from picomidi.constant import Midi
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QSlider, QWidget

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.utils.conversions import (
    midi_value_to_ms,
    ms_to_midi_value,
)
from jdxi_editor.ui.widgets.envelope.base import EnvelopeWidgetBase
from jdxi_editor.ui.widgets.pitch.envelope_plot import PitchEnvPlot
from jdxi_editor.ui.widgets.pitch.slider_spinbox import PitchEnvSliderSpinbox


class PitchEnvelopeWidget(EnvelopeWidgetBase):
    """
    Pitch Envelope Class
    """

    envelope_changed = Signal(dict)

    def __init__(
        self,
        attack_param: AddressParameter,
        decay_param: AddressParameter,
        depth_param: AddressParameter,
        midi_helper: Optional[MidiIOHelper] = None,
        create_parameter_slider: Callable = None,
        controls: dict[AddressParameter, QWidget] = None,
        address: Optional[RolandSysExAddress] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(
            envelope_keys=["attack_time", "decay_time", "peak_level"],
            create_parameter_slider=create_parameter_slider,
            parameters=[attack_param, decay_param, depth_param],
            midi_helper=midi_helper,
            address=address,
            controls=controls,
            parent=parent,
        )

        self.address = address
        self.midi_helper = midi_helper
        if controls:
            self.controls = controls
        else:
            self.controls = {}
        self._create_parameter_slider = create_parameter_slider
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
            units=" ms",
            label="Attack",
            value=self.envelope["attack_time"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.decay_control = PitchEnvSliderSpinbox(
            decay_param,
            min_value=0,
            max_value=5000,
            units=" ms",
            label="Decay",
            value=self.envelope["decay_time"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self._create_parameter_slider = create_parameter_slider
        self.depth_control = PitchEnvSliderSpinbox(
            depth_param,
            min_value=1,
            max_value=Midi.VALUE.MAX.SEVEN_BIT,
            units="",
            label="Depth",
            value=self.envelope["peak_level"],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self._control_widgets = [
            self.attack_control,
            self.decay_control,
            self.depth_control,
        ]
        self.controls[attack_param] = self.attack_control
        self.controls[decay_param] = self.decay_control
        self.controls[depth_param] = self.depth_control

        self.depth_control.spinbox.setEnabled(False)
        self.envelope_spinbox_map = {
            "attack_time": self.attack_control.spinbox,
            "decay_time": self.decay_control.spinbox,
            "peak_level": self.depth_control.spinbox,
        }
        self.plot = PitchEnvPlot(
            width=JDXiStyle.ADSR_PLOT_WIDTH,
            height=JDXiStyle.ADSR_PLOT_HEIGHT,
            envelope=self.envelope,
            parent=self,
        )

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setColumnStretch(0, 1)
        self.layout.addWidget(self.attack_control, 0, 1)
        self.layout.addWidget(self.decay_control, 0, 2)
        self.layout.addWidget(self.depth_control, 0, 3)
        self.layout.addWidget(self.plot, 0, 4, 3, 1)
        self.layout.setColumnStretch(5, 1)

        self.plot.set_values(self.envelope)
        for control in self._control_widgets:
            control.envelope_changed.connect(self.on_control_changed)
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

    def update_envelope_from_spinboxes(self):
        """
        Update envelope values from spinboxes
        :emits: dict pitch envelope parameters
        """
        self.envelope["attack_time"] = self.attack_control.value()
        self.envelope["decay_time"] = self.decay_control.value()
        self.envelope["peak_level"] = self.depth_control.value()
        self.plot.set_values(self.envelope)
        self.envelope_changed.emit(self.envelope)

    def update_spinboxes_from_envelope(self):
        """
        Update spinboxes from envelope values
        :emits: dict pitch envelope parameters
        """
        self.attack_control.setValue(self.envelope["attack_time"])
        self.decay_control.setValue(self.envelope["decay_time"])
        self.depth_control.setValue(self.envelope["peak_level"])
        self.plot.set_values(self.envelope)
        self.envelope_changed.emit(self.envelope)

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

    def update_envelope_from_controls(self) -> None:
        """Update envelope values from slider controls"""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                log.message(f"envelope_param_type = {envelope_param_type}")
                if envelope_param_type == "sustain_level":
                    self.envelope["sustain_level"] = slider.STATUS() / 127
                elif envelope_param_type == "peak_level":
                    pass
                    # self.envelope["peak_level"] = (slider.value() / 127)
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
