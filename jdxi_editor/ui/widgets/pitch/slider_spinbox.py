from typing import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDoubleSpinBox, QSpinBox, QVBoxLayout, QWidget

from decologr import Decologr as log
from picomidi.constant import Midi
from picomidi.sysex.parameter.address import AddressParameter
from picomidi.utils.conversion import midi_value_to_ms, ms_to_midi_value


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
        self.factor = Midi.VALUE.MAX.SEVEN_BIT
        if max_value > 1:
            self.factor = max_value
        self.create_parameter_slider = create_parameter_slider
        self.slider = self.create_parameter_slider(
            param=param,
            label=label,
            vertical=True,
            initial_value=value,
        )
        param_type = param.get_envelope_param_type()
        if param_type in ["sustain_level", "peak_level"]:
            self.spinbox = create_double_spinbox(
                min_value=min_value, max_value=max_value, step=0.01, value=value
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
        if param_type in ["sustain_level", "peak_level", "depth"]:
            converted_value = value / Midi.VALUE.MAX.SEVEN_BIT
        elif param_type in [
            "attack_time",
            "decay_time",
            "release_time",
            "fade_lower",
            "fade_upper",
            "range_lower",
            "depth",
            "range_upper",
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
        if param_type in ["peak_level", "sustain_level" "mod_depth", "depth"]:
            converted_value = int(value * Midi.VALUE.MAX.SEVEN_BIT)
        elif param_type in [
            "attack_time",
            "decay_time",
            "release_time" "fade_lower",
            "fade_upper",
            "range_lower",
            "range_upper",
        ]:
            converted_value = int(ms_to_midi_value(value, min_time=10, max_time=5000))
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
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(int(self.convert_to_envelope(value)))
        self.spinbox.blockSignals(False)
        self.envelope_changed.emit(
            {self.param.get_envelope_param_type(): self.convert_to_envelope(value)}
        )

    def _spinbox_changed(self, value: float):
        """
        Spinbox changed

        :param value: float double spinbox value
        :return: None
        """
        if value is None:
            return

        # Defensive: make sure we can work with the value
        if isinstance(value, float):
            try:
                value = int(value)
            except Exception as ex:
                log.error(f"Error {ex} occurred casting float {value} to int")
                return

        if not isinstance(value, int):
            log.error(f"{value} is neither int nor castable float")
            return

        converted_value = self.convert_from_envelope(value)
        if converted_value is None:
            log.error(f"convert_from_envelope({value}) returned None")
            return

        self.slider.blockSignals(True)
        self.slider.setValue(int(converted_value))
        self.slider.blockSignals(False)
        self.envelope_changed.emit({self.param.get_envelope_param_type(): value})

    def setValue(self, value: float):
        """
        Set the value of the double spinbox and slider

        :param value: float
        :return: None
        """
        self.slider.setValue(value)
        self.spinbox.setValue(int(value))

    def value(self) -> float:
        """
        Get the value of the spinbox

        :return: int
        """
        return self.spinbox.value()

    def update(self):
        """Update the envelope values and plot"""
        super().update()
        self.slider.update()
        self.spinbox.update()
        self.parent.update()
