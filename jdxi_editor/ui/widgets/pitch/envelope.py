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

from decologr import Decologr as log
from picomidi.constant import Midi
from picomidi.sysex.parameter.address import AddressParameter
from picomidi.utils.conversion import (
    midi_value_to_ms,
    ms_to_midi_value,
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QGridLayout, QSlider, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.envelope.base import EnvelopeWidgetBase
from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
from jdxi_editor.ui.widgets.pitch.envelope_plot import PitchEnvPlot
from jdxi_editor.ui.widgets.pitch.slider_spinbox import PitchEnvSliderSpinbox


class PitchEnvWidget(EnvelopeWidgetBase):
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

    def apply_envelope(self, envelope: dict, source: str):
        """
        Central state synchronizer.
        source: "controls" | "plot" | "sysex"
        """

        self.envelope.update(envelope)

        # 1) update controls (unless they caused it)
        if source != "controls":
            self.block_control_signals(True)
            self.update_controls_from_envelope()
            self.block_control_signals(False)

        # 2) update plot (unless plot caused it)
        if source != "plot":
            self.plot.set_values(self.envelope)

        # 3) emit + midi
        self.envelope_changed.emit(self.envelope)

    def block_control_signals(self, state: bool):
        for ctrl in self._control_widgets:
            ctrl.blockSignals(state)


    def showEvent(self, event: QShowEvent) -> None:
        """When widget is shown, sync plot from current control values (e.g. after startup load)."""
        super().showEvent(event)
        self.refresh_plot_from_controls()

    def on_control_changed(self, change: dict) -> None:
        """
        Control Change callback

        :param change: dict envelope
        :return: None
        :emits: dict pitch envelope parameters
        """
        self.apply_envelope(change, source="controls")

    def on_plot_envelope_changed(self, envelope: dict):
        self.apply_envelope(envelope, source="plot")

    def update_envelope_from_spinboxes(self):
        """
        Update envelope values from spinboxes
        :emits: dict pitch envelope parameters
        """
        self.refresh_plot_from_controls()
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
                f"[PitchEnvelopeWidget] [update_controls_from_envelope] Error updating controls from envelope: {ex}"
            )
        self.plot.set_values(self.envelope)
