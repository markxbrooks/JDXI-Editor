"""
Base Envelope Widget
"""

from typing import Callable, Optional

from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from picomidi.utils.conversion import midi_value_to_ms
from PySide6.QtCore import Signal
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QGridLayout, QWidget

from jdxi_editor.midi.data.address.address import JDXiSysExAddress
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.envelope.data_source import EnvelopeDataSource
from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
from jdxi_editor.ui.widgets.envelope.slider_spec import EnvControlSpec
from jdxi_editor.ui.widgets.pitch.slider_spinbox import PitchEnvSliderSpinbox
from jdxi_editor.ui.widgets.slider import Slider

TOOLTIPS = {
    EnvelopeParameter.ATTACK_TIME: "Time taken for the pitch to reach peak after note-on.",
    EnvelopeParameter.DECAY_TIME: "Time taken for the pitch to fall from peak to sustain.",
    EnvelopeParameter.SUSTAIN_LEVEL: "Sustain level of the pitch envelope (0.0 to 1.0).",
    EnvelopeParameter.INITIAL_LEVEL: "Initial pitch level at note-on (0.0 to 1.0).",
    EnvelopeParameter.RELEASE_TIME: "Time taken for the pitch to fall to zero after note-off.",
    EnvelopeParameter.PEAK_LEVEL: "Maximum pitch modulation depth.",
    EnvelopeParameter.PULSE_WIDTH: "Width of the pulse waveform (0% = narrow, 100% = square).",
    EnvelopeParameter.MOD_DEPTH: "Modulation depth of the PWM LFO.",
}


class EnvelopeWidgetBase(QWidget):
    """Base class for envelope widgets in the JD-Xi editor"""

    envelope_changed = Signal(dict)

    def __init__(
        self,
        parameters: list[AddressParameter],
        envelope_keys: list[str],
        create_parameter_slider: Callable,
        midi_helper: Optional[MidiIOHelper] = None,
        address: Optional[JDXiSysExAddress] = None,
        controls: Optional[dict[AddressParameter, Slider]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.plot = None
        self.address = address
        self.midi_helper = midi_helper
        self.controls = controls
        self.envelope = {}
        self._create_parameter_slider = create_parameter_slider
        self._params = parameters
        self._keys = envelope_keys
        self._control_widgets = []

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        for control in self._control_widgets:
            control.setEnabled(enabled)
        if hasattr(self, "plot") and self.plot:
            self.plot.setEnabled(enabled)

    def update(self):
        """Update the envelope values and plot"""
        super().update()
        if hasattr(self, "plot") and self.plot:
            self.plot.update()

    def _create_control_layout(self, slider_specs: list[EnvControlSpec]) -> QGridLayout:
        """Create Control Layout"""
        layout = QGridLayout()

        self.param_to_env = {}
        for idx, spec in enumerate(slider_specs):
            control = PitchEnvSliderSpinbox(
                spec.param,
                min_value=spec.min_value,
                max_value=spec.max_value,
                units=spec.units,
                label=spec.label,
                value=spec.default_value,
                create_parameter_slider=self._create_parameter_slider,
                parent=self,
            )
            self.controls[spec.param] = control
            self.param_to_env[spec.param] = spec.env_param
            control.spinbox.setEnabled(spec.enabled)
            control.envelope_changed.connect(
                lambda ch, p=spec.param: self.apply_envelope(
                    ch, EnvelopeDataSource.CONTROLS
                )
            )

            self._control_widgets.append(control)
            self.controls[spec.param] = control
            layout.addWidget(control, 0, idx)
        return layout

    def set_values(self, envelope: dict) -> None:
        """
        Update envelope values and trigger address redraw

        :param envelope: dict
        :return: None
        """
        self.envelope = envelope
        self.update()

    def emit_envelope_changed(self) -> None:
        """
        Emit the envelope changed signal

        :return: None
        """
        if hasattr(self, "plot") and self.plot:
            self.plot.set_values(self.envelope)

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

    def update_envelope_from_controls(self) -> None:
        """
        Update envelope values from slider controls.

        :return:
        """

        if self.controls is None:
            return
        try:
            self._ui_editing = True
            for param, slider in self.controls.items():
                if not hasattr(param, "get_envelope_param_type"):
                    continue
                try:
                    key = param.get_envelope_param_type()
                except NotImplementedError:
                    # Parameter doesn't implement get_envelope_param_type, skip it
                    continue
                val = slider.value()
                if isinstance(self.envelope.get(key), float):
                    if key.endswith("_level"):
                        self.envelope[key] = val  # 0.0 to 1.0 float
                    else:
                        self.envelope[key] = midi_value_to_ms(val)
                else:
                    self.envelope[key] = val
                self._ui_editing = False
            self.envelope_changed.emit(self.envelope)
        except Exception as ex:
            log.error(f"Error updating envelope from controls: {ex}")
        if hasattr(self, "plot") and self.plot:
            self.plot.set_values(self.envelope)

    def update_controls_from_envelope(self) -> None:
        """
        Update slider controls from envelope values.

        :return: None
        """
        if self.controls is None:
            return
        try:
            for param, slider in self.controls.items():
                if not hasattr(param, "get_envelope_param_type"):
                    continue
                try:
                    key = param.get_envelope_param_type()
                except NotImplementedError:
                    # Parameter doesn't implement get_envelope_param_type, skip it
                    continue
                if key is None:
                    log.info(
                        scope="EnvelopeWidgetBase",
                        message=f"parameter {param.name} is not in envelope, skipping update",
                    )
                elif hasattr(slider, "setValue"):
                    if param.name in ["OSC_WAVE"]:
                        continue
                    elif isinstance(self.envelope.get(key), float) and key.endswith(
                        "_level"
                    ):
                        if hasattr(slider, "setValue"):
                            slider.setValue(self.envelope[key])
                    elif isinstance(self.envelope.get(key), float) and key.endswith(
                        "_width"
                    ):
                        if hasattr(slider, "setValue"):
                            slider.setValue(self.envelope[key])
                    elif isinstance(self.envelope.get(key), float):
                        if hasattr(slider, "setValue"):
                            slider.setValue(self.envelope[key])
                    else:
                        pass  # Not in envelope or not a float
        except Exception as ex:
            log.error(
                scope="EnvelopeWidgetBase",
                message=f"Error updating controls from envelope: {ex}",
            )
        if hasattr(self, "plot") and self.plot:
            self.plot.set_values(self.envelope)

    def showEvent(self, event: QShowEvent) -> None:
        """When widget is shown, sync plot from current control values (e.g. after startup load)."""
        super().showEvent(event)
        self.refresh_plot_from_controls()

    def apply_envelope(self, envelope: dict, source: str):
        """
        Central state synchronizer.
        source: "controls" | "plot" | "sysex"
        """
        log.message(f"applying envelope {envelope}", scope=self.__class__.__name__)
        # Skip only when the same dict object is passed (avoid re-entry). Do not skip
        # when a new dict with equal content is passed, or we never update/repaint.
        if envelope is self.envelope:
            return
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

    def refresh_plot_from_controls(self):
        raise NotImplementedError("To be implemented in subclass")
