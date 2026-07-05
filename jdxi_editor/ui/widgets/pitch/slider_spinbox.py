from typing import Callable

from decologr import Decologr as log
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDoubleSpinBox, QSpinBox, QVBoxLayout, QWidget

from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
from picomidi.constant import Midi
from picomidi.sysex.parameter.address import AddressParameter
from picomidi.utils.conversion import (
    fraction_to_midi_value,
    midi_value_to_fraction,
    midi_value_to_ms,
    ms_to_midi_value,
)


def create_spinbox(min_value: int, max_value: int, suffix: str, value: int) -> QSpinBox:
    """
    Create a spinbox with specified range and suffix

    :param min_value: int
    :param max_value: int
    :param suffix: str
    :param value: int
    :return: QSpinBox
    """
    sb = QSpinBox()
    sb.setRange(min_value, max_value)
    sb.setSuffix(suffix)
    sb.setValue(value)
    return sb


def create_double_spinbox(
    min_value: float, max_value: float, step: float, value: int
) -> QDoubleSpinBox:
    """
    Create a double spinbox with specified range, step, and initial value.

    :param min_value: int
    :param max_value: int
    :param step: float
    :param value: int
    :return: QDoubleSpinBox
    """
    sb = QDoubleSpinBox()
    sb.setRange(min_value, max_value)
    sb.setSingleStep(step)
    sb.setValue(value)
    return sb


class PitchEnvSliderSpinbox(QWidget):
    """
    Pitch Env Slider and Spinbox widget for Roland JD-Xi
    """

    envelope_changed = Signal(dict)
    valueChanged = Signal(
        object
    )  # Emitted when value changes (avoids AttributeError in shared controls)

    def __init__(
        self,
        param: AddressParameter,
        min_value: float = 0.0,
        max_value: float = 1.0,
        units: str = "",
        label: str = "",
        value: int = None,
        create_parameter_slider: Callable = None,
        parent: QWidget = None,
        show_spinbox: bool = False
    ):
        """
        Initialize the ADSR slider and spinbox widget.

        :param param: AddressParameter
        :param min_value: int
        :param max_value: int
        :param units: str
        :param label: str
        :param value: int
        :param create_parameter_slider: Callable
        :param parent: QWidget
        """
        super().__init__(parent)

        self.param = param
        self.factor = Midi.value.max.SEVEN_BIT
        if max_value > 1:
            self.factor = max_value
        self.create_parameter_slider = create_parameter_slider
        param_type = param.get_envelope_param_type()
        self._bipolar_depth = (
            param_type == EnvelopeParameter.PEAK_LEVEL and param.is_bipolar
        )
        slider_initial = value
        spin_initial = value
        if self._bipolar_depth:
            if value is not None:
                spin_initial = float(value)
                slider_initial = int(round(float(value)))
        elif param_type in (
            EnvelopeParameter.SUSTAIN_LEVEL,
            EnvelopeParameter.PEAK_LEVEL,
            EnvelopeParameter.MOD_DEPTH,
            EnvelopeParameter.DEPTH,
        ):
            if value is not None and float(value) <= float(max_value) and float(value) <= 2.0:
                spin_initial = float(value)
                slider_initial = self.convert_from_envelope(spin_initial)
            elif value is not None:
                slider_initial = int(value)
                spin_initial = midi_value_to_fraction(int(value))
        self.slider = self.create_parameter_slider(
            param=param,
            label=label,
            vertical=True,
            initial_value=slider_initial,
        )
        if param_type in [
            EnvelopeParameter.SUSTAIN_LEVEL,
            EnvelopeParameter.PEAK_LEVEL,
        ]:
            self.spinbox = create_double_spinbox(
                min_value=min_value, max_value=max_value, step=0.01, value=spin_initial
            )
        else:
            self.spinbox = create_spinbox(
                min_value=int(min_value),
                max_value=int(max_value),
                suffix=units,
                value=value,
            )
        self.spinbox.setRange(min_value, max_value)

        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        if show_spinbox:
            layout.addWidget(self.spinbox)
        self.setLayout(layout)

        # Connect both ways
        self.slider.valueChanged.connect(self._slider_changed)
        self.spinbox.valueChanged.connect(self._spinbox_changed)

    def convert_to_envelope(self, value: float) -> float:
        """
        Convert MIDI value to envelope value

        :param value: float
        :return: float
        """
        param_type = self.param.get_envelope_param_type()
        if self._bipolar_depth:
            converted_value = float(value)
        elif param_type in [
            EnvelopeParameter.SUSTAIN_LEVEL,
            EnvelopeParameter.PEAK_LEVEL,
            EnvelopeParameter.MOD_DEPTH,
            EnvelopeParameter.DEPTH,
        ]:
            converted_value = midi_value_to_fraction(int(value))
        elif param_type in [
            EnvelopeParameter.ATTACK_TIME,
            EnvelopeParameter.DECAY_TIME,
            EnvelopeParameter.RELEASE_TIME,
            EnvelopeParameter.FADE_LOWER,
            EnvelopeParameter.FADE_UPPER,
            EnvelopeParameter.RANGE_LOWER,
            EnvelopeParameter.DEPTH,
            EnvelopeParameter.RANGE_UPPER,
        ]:
            converted_value = midi_value_to_ms(int(value), min_time=10, max_time=5000)
        else:
            log.error(f"Unknown envelope parameter type {param_type} for {self.param}")
            converted_value = 0.0  # or raise an error, depending on design
        return converted_value

    def convert_from_envelope(self, value: float) -> int:
        """
        Convert envelope value to MIDI value

        :param value: int
        :return: int
        """
        param_type = self.param.get_envelope_param_type()
        if self._bipolar_depth:
            converted_value = int(round(float(value)))
        elif param_type in [
            EnvelopeParameter.PEAK_LEVEL,
            EnvelopeParameter.SUSTAIN_LEVEL,
            EnvelopeParameter.MOD_DEPTH,
            EnvelopeParameter.DEPTH,
        ]:
            converted_value = fraction_to_midi_value(float(value))
        elif param_type in [
            EnvelopeParameter.ATTACK_TIME,
            EnvelopeParameter.DECAY_TIME,
            EnvelopeParameter.RELEASE_TIME,
            EnvelopeParameter.FADE_LOWER,
            EnvelopeParameter.FADE_UPPER,
            EnvelopeParameter.RANGE_LOWER,
            EnvelopeParameter.RANGE_UPPER,
        ]:
            # Ensure value is a number, not a string
            value_num = float(value) if not isinstance(value, (int, float)) else value
            converted_value = int(
                ms_to_midi_value(value_num, min_time=10, max_time=5000)
            )
        else:
            converted_value = 64
        log.message(f"convert_from_envelope: {value} -> {converted_value}")
        return converted_value

    def _slider_changed(self, value: int) -> None:
        """
        slider changed

        :param value: int slider value
        :return: None
        """
        envelope_value = self.convert_to_envelope(value)
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(envelope_value)
        self.spinbox.blockSignals(False)
        self.envelope_changed.emit(
            {self.param.get_envelope_param_type(): envelope_value}
        )
        self.valueChanged.emit(self.value())

    def _spinbox_changed(self, value: float):
        """
        Spinbox changed

        :param value: float double spinbox value
        :return: None
        """
        if value is None:
            return

        param_type = self.param.get_envelope_param_type()
        if param_type in (
            EnvelopeParameter.SUSTAIN_LEVEL,
            EnvelopeParameter.PEAK_LEVEL,
            EnvelopeParameter.MOD_DEPTH,
            EnvelopeParameter.DEPTH,
        ):
            envelope_value = float(value)
            midi_value = self.convert_from_envelope(envelope_value)
        else:
            if isinstance(value, float):
                try:
                    value = int(value)
                except Exception as ex:
                    log.error(f"Error {ex} occurred casting float {value} to int")
                    return
            if not isinstance(value, int):
                log.error(f"{value} is neither int nor castable float")
                return
            envelope_value = value
            midi_value = self.convert_from_envelope(envelope_value)

        if midi_value is None:
            log.error(f"convert_from_envelope({value}) returned None")
            return

        self.slider.blockSignals(True)
        self.slider.setValue(int(midi_value))
        self.slider.blockSignals(False)
        self.envelope_changed.emit({self.param.get_envelope_param_type(): envelope_value})
        self.valueChanged.emit(self.value())

    def setValue(self, value: float):
        """
        Set the value of the double spinbox and slider

        :param value: float
        :return: None
        """
        try:
            param_type = self.param.get_envelope_param_type()
            if param_type in (
                EnvelopeParameter.SUSTAIN_LEVEL,
                EnvelopeParameter.PEAK_LEVEL,
                EnvelopeParameter.MOD_DEPTH,
                EnvelopeParameter.DEPTH,
            ):
                midi_val = self.convert_from_envelope(float(value))
                self.slider.blockSignals(True)
                self.spinbox.blockSignals(True)
                self.slider.setValue(midi_val)
                self.spinbox.setValue(float(value))
                self.slider.blockSignals(False)
                self.spinbox.blockSignals(False)
            else:
                self.slider.setValue(int(value))
                self.spinbox.setValue(int(value))
        except RuntimeError:
            pass

    def value(self) -> float:
        """
        Get the semantic envelope value (fraction for depth, ms for time).

        :return: float
        """
        param_type = self.param.get_envelope_param_type()
        if self._bipolar_depth:
            return float(self.slider.value())
        if param_type in (
            EnvelopeParameter.SUSTAIN_LEVEL,
            EnvelopeParameter.PEAK_LEVEL,
            EnvelopeParameter.MOD_DEPTH,
            EnvelopeParameter.DEPTH,
        ):
            return midi_value_to_fraction(self.slider.value())
        return float(self.spinbox.value())

    def update(self):
        """Update the envelope values and plot"""
        super().update()
        self.slider.update()
        self.spinbox.update()
        self.parent.update()
