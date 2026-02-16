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
    ms_to_midi_value, midi_value_to_ms,
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
    env_param: EnvelopeParameter
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
                attack_param, EnvelopeParameter.ATTACK_TIME,
                0, 5000, "Attack", " ms"
            ),
            EnvelopeControlSpec(
                decay_param, EnvelopeParameter.DECAY_TIME,
                0, 5000, "Decay", " ms"
            ),
            EnvelopeControlSpec(
                depth_param, EnvelopeParameter.PEAK_LEVEL,
                0, Midi.VALUE.MAX.SEVEN_BIT, "Depth", "", enabled=False
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

        self.layout.addWidget(self.plot, 0, len(specs)+1, 3, 1)

        if analog:
            JDXi.UI.Theme.apply_adsr_style(self, analog=True)

        self.plot.set_values(self.envelope)

    def _create_control_layout(self, specs: list[EnvelopeControlSpec]) -> QGridLayout:
        layout = QGridLayout()

        self.param_to_env: dict[AddressParameter, EnvelopeParameter] = {}

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
            control.envelope_changed.connect(lambda ch, s=spec: self.apply_envelope(ch, "controls"))

            self.controls[spec.param] = control
            self.param_to_env[spec.param] = spec.env_param
            self._control_widgets.append(control)

            layout.addWidget(control, 0, col)
        return layout

    def update_envelope_from_controls(self):
        for param, control in self.controls.items():
            env_param = self.param_to_env[param]

            if env_param == EnvelopeParameter.PEAK_LEVEL:
                self.envelope[env_param] = control.value()
            else:
                self.envelope[env_param] = midi_value_to_ms(control.value())

    def update_controls_from_envelope(self):
        for param, control in self.controls.items():
            env_param = self.param_to_env[param]

            if env_param == EnvelopeParameter.PEAK_LEVEL:
                control.setValue(self.envelope[env_param])
            else:
                control.setValue(int(ms_to_midi_value(self.envelope[env_param])))

    def refresh_plot_from_controls(self):
        self.update_envelope_from_controls()
        self.plot.set_values(self.envelope)


class PitchEnvWidgetOld(EnvelopeWidgetBase):
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

        self.address = address
        self.midi_helper = midi_helper
        if controls is not None:
            self.controls = controls
        else:
            self.controls = {}
        self._create_parameter_slider = create_parameter_slider
        self.envelope = {
            EnvelopeParameter.ATTACK_TIME: 300,
            EnvelopeParameter.DECAY_TIME: 800,
            EnvelopeParameter.RELEASE_TIME: 500,
            EnvelopeParameter.INITIAL_LEVEL: 0.0,
            EnvelopeParameter.PEAK_LEVEL: 64,  # MIDI center = no modulation (-63..+63 display)
            EnvelopeParameter.SUSTAIN_LEVEL: 0.0,
        }
        self.attack_control = PitchEnvSliderSpinbox(
            attack_param,
            min_value=0,
            max_value=5000,
            units=" ms",
            label="Attack",
            value=self.envelope[EnvelopeParameter.ATTACK_TIME],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.decay_control = PitchEnvSliderSpinbox(
            decay_param,
            min_value=0,
            max_value=5000,
            units=" ms",
            label="Decay",
            value=self.envelope[EnvelopeParameter.DECAY_TIME],
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self._create_parameter_slider = create_parameter_slider
        self.depth_control = PitchEnvSliderSpinbox(
            depth_param,
            min_value=0,
            max_value=Midi.VALUE.MAX.SEVEN_BIT,
            units="",
            label="Depth",
            value=self.envelope[EnvelopeParameter.PEAK_LEVEL],
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
            EnvelopeParameter.ATTACK_TIME: self.attack_control.spinbox,
            EnvelopeParameter.DECAY_TIME: self.decay_control.spinbox,
            EnvelopeParameter.PEAK_LEVEL: self.depth_control.spinbox,
        }
        self.plot = PitchEnvPlot(
            width=JDXi.UI.Style.ADSR_PLOT_WIDTH,
            height=JDXi.UI.Style.ADSR_PLOT_HEIGHT,
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
        if analog:
            JDXi.UI.Theme.apply_adsr_style(self, analog=True)
        self.envelope_changed.emit(self.envelope)

    def refresh_plot_from_controls(self):
        env = {
            EnvelopeParameter.ATTACK_TIME: self.attack_control.value(),
            EnvelopeParameter.DECAY_TIME: self.decay_control.value(),
            EnvelopeParameter.PEAK_LEVEL: self.depth_control.value(),
        }
        self.apply_envelope(env, source="sysex")

    def update_controls_from_envelope(self) -> None:
        """Update slider controls from envelope values."""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == EnvelopeParameter.SUSTAIN_LEVEL:
                    slider.setValue(
                        int(self.envelope[EnvelopeParameter.SUSTAIN_LEVEL] * 127)
                    )
                elif envelope_param_type == EnvelopeParameter.PEAK_LEVEL:
                    slider.setValue(self.envelope[EnvelopeParameter.PEAK_LEVEL])  # MIDI 0-127
                else:
                    slider.setValue(
                        int(ms_to_midi_value(self.envelope[envelope_param_type]))
                    )
        except Exception as ex:
            log.error(
                f"[update_controls_from_envelope] Error updating controls from envelope: {ex}",
                scope=self.__class__.__name__
            )
        self.plot.set_values(self.envelope)
