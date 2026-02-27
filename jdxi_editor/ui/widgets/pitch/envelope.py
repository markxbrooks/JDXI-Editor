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

from dataclasses import dataclass
from typing import Callable, Optional

from decologr import Decologr as log
from picomidi.constant import Midi
from picomidi.sysex.parameter.address import AddressParameter
from picomidi.utils.conversion import (
    midi_value_to_ms,
    ms_to_midi_value,
)
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.envelope.base import EnvelopeWidgetBase
from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
from jdxi_editor.ui.widgets.pitch.envelope_plot import PitchEnvPlot
from jdxi_editor.ui.widgets.pitch.slider_spinbox import PitchEnvSliderSpinbox


@dataclass
class EnvelopeControlSpec:
    param: AddressParameter
    env_param: str
    min_value: int
    max_value: int
    label: str
    units: str = ""
    enabled: bool = True


class PitchEnvWidget(EnvelopeWidgetBase):
    """Pitch Envelope Class"""

    envelope_changed = Signal(dict)

    def __init__(
        self,
        attack_param: AddressParameter,
        decay_param: AddressParameter,
        depth_param: AddressParameter,
        midi_helper: Optional[MidiIOHelper] = None,
        create_parameter_slider: Callable = None,
        controls: dict[AddressParameter, QWidget] = None,
        address: Optional[JDXiSysExAddress] = None,
        parent: Optional[QWidget] = None,
        analog: bool = False,
    ):
        super().__init__(
            envelope_keys=[
                EnvelopeParameter.ATTACK_TIME,
                EnvelopeParameter.DECAY_TIME,
                EnvelopeParameter.PEAK_LEVEL,
            ],
            create_parameter_slider=create_parameter_slider,
            parameters=[attack_param, decay_param, depth_param],
            midi_helper=midi_helper,
            address=address,
            controls=controls,
            parent=parent,
        )

        self.controls = controls or {}
        self._create_parameter_slider = create_parameter_slider

        # canonical state
        self.envelope = {
            EnvelopeParameter.ATTACK_TIME: 300,
            EnvelopeParameter.DECAY_TIME: 800,
            EnvelopeParameter.RELEASE_TIME: 500,
            EnvelopeParameter.INITIAL_LEVEL: 0.0,
            EnvelopeParameter.PEAK_LEVEL: 64,
            EnvelopeParameter.SUSTAIN_LEVEL: 0.0,
        }

        specs = [
            EnvelopeControlSpec(
                attack_param, EnvelopeParameter.ATTACK_TIME, 0, 5000, "Attack", " ms"
            ),
            EnvelopeControlSpec(
                decay_param, EnvelopeParameter.DECAY_TIME, 0, 5000, "Decay", " ms"
            ),
            EnvelopeControlSpec(
                depth_param,
                EnvelopeParameter.PEAK_LEVEL,
                0,
                Midi.value.max.SEVEN_BIT,
                "Depth",
                "",
                enabled=False,
            ),
        ]

        self._control_widgets = []
        self.layout = self._create_control_layout(specs)

        self.setLayout(self.layout)

        self.plot = PitchEnvPlot(
            width=JDXi.UI.Style.ADSR_PLOT_WIDTH,
            height=JDXi.UI.Style.ADSR_PLOT_HEIGHT,
            envelope=self.envelope,
            parent=self,
        )

        self.layout.addWidget(self.plot, 0, len(specs) + 1, 3, 1)

        if analog:
            JDXi.UI.Theme.apply_adsr_style(self, analog=True)

        self.plot.set_values(self.envelope)

    def _create_control_layout(self, specs: list[EnvelopeControlSpec]) -> QGridLayout:
        layout = QGridLayout()

        self.param_to_env: dict[AddressParameter, EnvelopeParameter] = {}
        self.attack_control = None
        self.decay_control = None
        self.depth_control = None

        for col, spec in enumerate(specs, start=1):
            control = PitchEnvSliderSpinbox(
                spec.param,
                min_value=spec.min_value,
                max_value=spec.max_value,
                units=spec.units,
                label=spec.label,
                value=self.envelope[spec.env_param],
                create_parameter_slider=self._create_parameter_slider,
                parent=self,
            )

            control.spinbox.setEnabled(spec.enabled)
            control.envelope_changed.connect(
                lambda ch, s=spec: self.apply_envelope(ch, "controls")
            )

            self.controls[spec.param] = control
            self.param_to_env[spec.param] = spec.env_param
            self._control_widgets.append(control)
            if spec.env_param == EnvelopeParameter.ATTACK_TIME:
                self.attack_control = control
            elif spec.env_param == EnvelopeParameter.DECAY_TIME:
                self.decay_control = control
            elif spec.env_param == EnvelopeParameter.PEAK_LEVEL:
                self.depth_control = control

            layout.addWidget(control, 0, col)
        return layout

    def update_envelope_from_controls(self):
        for param, control in self.controls.items():
            env_param = self.param_to_env.get(param)
            if env_param is None:
                continue

            if env_param == EnvelopeParameter.PEAK_LEVEL:
                self.envelope[env_param] = control.value()
            else:
                self.envelope[env_param] = midi_value_to_ms(control.value())

    def update_controls_from_envelope(self):
        for param, control in self.controls.items():
            env_param = self.param_to_env.get(param)
            if env_param is None:
                continue

            if env_param == EnvelopeParameter.PEAK_LEVEL:
                control.setValue(self.envelope[env_param])
            else:
                control.setValue(int(ms_to_midi_value(self.envelope[env_param])))

    def refresh_plot_from_controls(self):
        self.update_envelope_from_controls()
        self.plot.set_values(self.envelope)
