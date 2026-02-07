"""
Base Envelope Widget
"""

from typing import Callable, Optional

from decologr import Decologr as log
from picomidi.sysex.parameter.address import AddressParameter
from picomidi.utils.conversion import midi_value_to_ms
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
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
        address: Optional[RolandSysExAddress] = None,
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

    def update_envelope_from_controls(self) -> None:
        """
        Update envelope values from slider controls.

        :return:
        """
        try:
            for param, slider in self.controls.items():
                if not hasattr(param, "get_envelope_param_type"):
                    continue
                key = param.get_envelope_param_type()
                val = slider.value()
                if isinstance(self.envelope.get(key), float):
                    if key.endswith("_level"):
                        self.envelope[key] = val  # 0.0 to 1.0 float
                    else:
                        self.envelope[key] = midi_value_to_ms(val)
                else:
                    self.envelope[key] = val
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
        try:
            for param, slider in self.controls.items():
                if not hasattr(param, "get_envelope_param_type"):
                    continue
                key = param.get_envelope_param_type()
                if key is None:
                    log.info(
                        scope="EnvelopeWidgetBase", message=f"parameter {param.name} is not in envelope, skipping update"
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
            log.error(scope="EnvelopeWidgetBase", message=f"Error updating controls from envelope: {ex}")
        if hasattr(self, "plot") and self.plot:
            self.plot.set_values(self.envelope)
