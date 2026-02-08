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
from PySide6.QtWidgets import QGridLayout, QSlider, QWidget

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.envelope.base import EnvelopeWidgetBase
from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
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
        analog: bool = False,
    ):
        super().__init__(
            envelope_keys=[EnvelopeParameter.ATTACK_TIME, EnvelopeParameter.DECAY_TIME, EnvelopeParameter.PEAK_LEVEL],
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
            EnvelopeParameter.PEAK_LEVEL: 0.0,
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
            min_value=1,
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
        self.envelope[EnvelopeParameter.ATTACK_TIME] = self.attack_control.value()
        self.envelope[EnvelopeParameter.DECAY_TIME] = self.decay_control.value()
        self.envelope[EnvelopeParameter.PEAK_LEVEL] = self.depth_control.value()
        self.plot.set_values(self.envelope)
        self.envelope_changed.emit(self.envelope)

    def update_spinboxes_from_envelope(self):
        """
        Update spinboxes from envelope values
        :emits: dict pitch envelope parameters
        """
        self.attack_control.setValue(self.envelope[EnvelopeParameter.ATTACK_TIME])
        self.decay_control.setValue(self.envelope[EnvelopeParameter.DECAY_TIME])
        self.depth_control.setValue(self.envelope[EnvelopeParameter.PEAK_LEVEL])
        self.plot.set_values(self.envelope)
        self.envelope_changed.emit(self.envelope)

    def update_envelope_from_slider(self, slider: QSlider) -> None:
        """Update envelope with value from a single slider"""
        for param, ctrl in self.controls.items():
            if ctrl is slider:
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == EnvelopeParameter.SUSTAIN_LEVEL:
                    self.envelope[EnvelopeParameter.SUSTAIN_LEVEL] = slider.value() / 127
                elif envelope_param_type == EnvelopeParameter.PEAK_LEVEL:
                    self.envelope[EnvelopeParameter.PEAK_LEVEL] = slider.value() / 127
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
                if envelope_param_type == EnvelopeParameter.SUSTAIN_LEVEL:
                    self.envelope[EnvelopeParameter.SUSTAIN_LEVEL] = slider.STATUS() / 127
                elif envelope_param_type == EnvelopeParameter.PEAK_LEVEL:
                    pass
                    # self.envelope[EnvelopeParameter.PEAK_LEVEL] = (slider.value() / 127)
                else:
                    self.envelope[envelope_param_type] = midi_value_to_ms(
                        slider.STATUS()
                    )
            log.message(f"{self.envelope}")
        except Exception as ex:
            log.error(f"[PitchEnvelopeWidget] [update_envelope_from_controls] Error updating envelope from controls: {ex}")
        self.plot.set_values(self.envelope)

    def update_controls_from_envelope(self) -> None:
        """Update slider controls from envelope values."""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == EnvelopeParameter.SUSTAIN_LEVEL:
                    slider.setValue(int(self.envelope[EnvelopeParameter.SUSTAIN_LEVEL] * 127))
                elif envelope_param_type == EnvelopeParameter.PEAK_LEVEL:
                    pass
                    # slider.setValue(int((self.envelope[EnvelopeParameter.PEAK_LEVEL] + 0.5) * 127))
                else:
                    slider.setValue(
                        int(ms_to_midi_value(self.envelope[envelope_param_type]))
                    )
        except Exception as ex:
            log.error(f"[PitchEnvelopeWidget] [update_controls_from_envelope] Error updating controls from envelope: {ex}")
        self.plot.set_values(self.envelope)

    def refresh_plot_from_controls(self) -> None:
        """
        Sync envelope from current control values and redraw the plot without emitting.
        Call after programmatically setting control values (e.g. from incoming SysEx)
        when blockSignals(True) was used, so the plot reflects the new values.
        """
        try:
            self.envelope[EnvelopeParameter.ATTACK_TIME] = self.attack_control.value()
            self.envelope[EnvelopeParameter.DECAY_TIME] = self.decay_control.value()
            self.envelope[EnvelopeParameter.PEAK_LEVEL] = self.depth_control.value()
            self.plot.set_values(self.envelope)
        except Exception as ex:
            log.error(f"[PitchEnvelopeWidget] [refresh_plot_from_controls] Error: {ex}")
