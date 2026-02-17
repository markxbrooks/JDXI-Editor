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
from PySide6.QtWidgets import QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.envelope.base import EnvelopeWidgetBase
from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
from jdxi_editor.ui.widgets.envelope.slider_spec import EnvControlSpec
from jdxi_editor.ui.widgets.pitch.slider_spinbox import PitchEnvSliderSpinbox
from jdxi_editor.ui.widgets.wmt.envelope_plot import WMTEnvPlot


class WMTEnvelopeWidget(EnvelopeWidgetBase):
    """Pitch Envelope Editor for JD-Xi"""

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
        address: Optional[JDXiSysExAddress] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(
            envelope_keys=[
                EnvelopeParameter.RANGE_LOWER,
                EnvelopeParameter.DEPTH,
                EnvelopeParameter.RANGE_UPPER,
            ],
            create_parameter_slider=create_parameter_slider,
            parameters=[
                fade_lower_param,
                range_lower_param,
                depth_param,
                range_upper_param,
                fade_upper_param,
            ],
            midi_helper=midi_helper,
            address=address,
            controls=controls,
            parent=parent,
        )

        self.address = address
        self.midi_helper = midi_helper
        self._create_parameter_slider = create_parameter_slider
        self.controls: dict[AddressParameter, PitchEnvSliderSpinbox] = controls or {}

        # Default envelope values
        self.envelope = {
            EnvelopeParameter.FADE_LOWER: 300,
            EnvelopeParameter.RANGE_LOWER: 500,
            EnvelopeParameter.RANGE_UPPER: 500,
            EnvelopeParameter.FADE_UPPER: 500,
            EnvelopeParameter.DEPTH: 1.0,
        }

        # Define slider specs
        slider_specs = [
            EnvControlSpec(
                fade_lower_param,
                EnvelopeParameter.FADE_LOWER,
                "Fade Lower",
                default_value=self.envelope[EnvelopeParameter.FADE_LOWER],
            ),
            EnvControlSpec(
                range_lower_param,
                EnvelopeParameter.RANGE_LOWER,
                "Range Lower",
                default_value=self.envelope[EnvelopeParameter.RANGE_LOWER],
            ),
            EnvControlSpec(
                depth_param,
                EnvelopeParameter.DEPTH,
                "Depth",
                default_value=self.envelope[EnvelopeParameter.DEPTH],
            ),
            EnvControlSpec(
                range_upper_param,
                EnvelopeParameter.RANGE_UPPER,
                "Range Upper",
                min_value=1,
                max_value=Midi.VALUE.MAX.SEVEN_BIT,
                default_value=self.envelope[EnvelopeParameter.RANGE_UPPER],
                enabled=False,
            ),
            EnvControlSpec(
                fade_upper_param,
                EnvelopeParameter.FADE_UPPER,
                "Fade Upper",
                min_value=1,
                max_value=Midi.VALUE.MAX.SEVEN_BIT,
                default_value=self.envelope[EnvelopeParameter.FADE_UPPER],
            ),
        ]

        self._control_widgets: list[PitchEnvSliderSpinbox] = []

        self.layout = self._create_control_layout(slider_specs)

        # Add plot
        self.plot = WMTEnvPlot(
            width=JDXi.UI.Style.ADSR_PLOT_WIDTH,
            height=JDXi.UI.Style.ADSR_PLOT_HEIGHT,
            envelope=self.envelope,
            parent=self,
        )
        self.layout.addWidget(self.plot, 0, len(slider_specs), 3, 1)
        self.plot.set_values(self.envelope)
        self.setLayout(self.layout)
        self.envelope_spinbox_map = {
            ctrl.param: ctrl.spinbox for ctrl in self._control_widgets
        }

    # --- Centralized Methods ---
    def update_envelope_from_controls(self):
        for param, control in self.controls.items():
            env_param = self.param_to_env.get(param)
            if env_param is None:
                continue
            self.envelope[env_param] = control.value()

    def update_controls_from_envelope(self):
        for param, control in self.controls.items():
            env_param = self.param_to_env.get(param)
            if env_param is None:
                continue
            control.setValue(self.envelope[env_param])

    def refresh_plot_from_controls(self):
        """Update plot based on current envelope values"""
        self.update_envelope_from_controls()
        self.plot.set_values(self.envelope)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    test_env = {
        EnvelopeParameter.FADE_LOWER: 200,
        EnvelopeParameter.RANGE_LOWER: 300,
        EnvelopeParameter.DEPTH: 0.7,
        EnvelopeParameter.RANGE_UPPER: 400,
        EnvelopeParameter.FADE_UPPER: 300,
    }
    plot = WMTEnvPlot(400, 200, test_env)
    plot.setStyleSheet("background-color: black;")
    plot.show()
    app.exec()
