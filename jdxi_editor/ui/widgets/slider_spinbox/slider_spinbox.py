"""
Slider Spinbox Widget for Roland JD-Xi
"""

from typing import Callable

from decologr import Decologr as log
from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
from picomidi.constant import Midi
from picomidi.sysex.parameter.address import AddressParameter
from picomidi.utils.conversion import midi_value_to_ms, ms_to_midi_value
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDoubleSpinBox, QSpinBox, QVBoxLayout, QWidget


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


class AdsrSliderSpinbox(QWidget):
    """
    ADSR Slider and Spinbox widget for Roland JD-Xi
    """

    envelope_changed = Signal(dict)

    def __init__(
        self,
        param: AddressParameter,
        min_value: float = 0.0,
        max_value: float = 1.0,
        units: str = "",
        label: str = "",
        value: int | None | float = None,
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
        Convert the slider value to envelope value based on parameter type

        :param value: float
        :return: float
        """
        if self.param is None:
            log.error("Parameter is None, cannot convert to envelope")
            return 0.0
        if value is None:
            log.error("Value is None, cannot convert to envelope")
            return 0.0
        param_type = self.param.get_envelope_param_type()
        if param_type is None:
            log.error(
                f"Parameter type for {self.param.name} is None, cannot convert to envelope"
            )
            return 0.0
        if param_type == "sustain_level":
            converted_value = value / self.factor
            log.message(
                f"convert_to_envelope param type: {param_type} value {value} -> env {converted_value}"
            )
            return converted_value
        if param_type == "peak_level":
            return value / self.factor
        elif param_type in [EnvelopeParameter.ATTACK_TIME, EnvelopeParameter.DECAY_TIME, EnvelopeParameter.RELEASE_TIME]:
            return midi_value_to_ms(int(value))
        else:
            log.error(f"Unknown envelope parameter type: {param_type}")
            return 0.0  # or raise an error, depending on design

    def convert_from_envelope(self, value: float):
        """convert from envelope"""
        param_type = self.param.get_envelope_param_type()
        if param_type in [EnvelopeParameter.PEAK_LEVEL]:
            return int(value * self.factor)
        if param_type in [EnvelopeParameter.SUSTAIN_LEVEL]:
            converted_value = int(value * self.factor)
            log.message(
                f"convert_from_envelope param type: "
                f"{param_type} value {value} -> Slider {converted_value}",
                silent=True,
            )
            return converted_value
        elif param_type in [EnvelopeParameter.ATTACK_TIME, EnvelopeParameter.DECAY_TIME, EnvelopeParameter.RELEASE_TIME]:
            return ms_to_midi_value(value)
        else:
            return 64

    def _slider_changed(self, value: int) -> None:
        """
        Handle changes from the slider and update the spinbox and envelope

        :param value:
        :return:
        """
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(self.convert_to_envelope(value))
        self.spinbox.blockSignals(False)
        self.envelope_changed.emit(
            {self.param.get_envelope_param_type(): self.convert_to_envelope(value)}
        )

    def _spinbox_changed(self, value: float) -> None:
        """
        Handle changes from the spinbox and update the slider and envelope

        :param value:
        :return: None
        """
        self.slider.blockSignals(True)
        self.slider.setValue(self.convert_from_envelope(value))
        self.slider.blockSignals(False)
        self.envelope_changed.emit({self.param.get_envelope_param_type(): value})

    def setValue(self, value: float):
        """
        Set the value of the spinbox and slider

        :param value: int
        :return: None
        """
        self.spinbox.setValue(value)

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
