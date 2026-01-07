from typing import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox, QWidget, QVBoxLayout

from picomidi.constant import MidiConstant
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.parameter.synth import AddressParameter


def create_spinbox(min_value: int,
                   max_value: int,
                   suffix: str,
                   value: int) -> QSpinBox:
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


class PWMSliderSpinbox(QWidget):
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
        self.factor = MidiConstant.VALUE_MAX_SEVEN_BIT
        if max_value > 1:
            self.factor = max_value
        self.create_parameter_slider = create_parameter_slider
        self.slider = self.create_parameter_slider(
            param=param,
            label=label,
            vertical=True,
            initial_value=int(value * self.factor) if value is not None else 0,
        )
        self.spinbox = create_double_spinbox(
            min_value=min_value,
            max_value=max_value,
            step=0.01,
            value=value
        )
        self.spinbox.setRange(min_value,
                              max_value)
        self.factor = MidiConstant.VALUE_MAX_SEVEN_BIT
        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(self.spinbox)
        self.setLayout(layout)

        # Connect both ways
        self.slider.valueChanged.connect(self._slider_changed)
        self.spinbox.valueChanged.connect(self._spinbox_changed)

    def convert_to_envelope(self, value: float):
        """
        convert_to_envelope

        :param value:
        :return:
        Convert the slider value to envelope value based on parameter type
        """
        if self.param is None:
            log.error("Parameter is None, cannot convert to envelope")
            return 0.0
        if value is None:
            log.error("Value is None, cannot convert to envelope")
            return 0.0
        param_type = self.param.get_envelope_param_type()
        if param_type is None:
            log.error(f"Parameter type for {self.param.name} is None, cannot convert to envelope")
            return 0.0
        if param_type in ["filter_cutoff", "filter_resonance"]:
            return value
        if param_type == "mod_depth":
            return value / self.factor
        if param_type == "pulse_width":
            return value / self.factor
        else:
            log.error(f"Unknown envelope parameter type: {param_type}")
            return 0.0  # or raise an error, depending on design

    def convert_from_envelope(self, value: float):
        param_type = self.param.get_envelope_param_type()
        if param_type is None:
            log.error(f"Parameter type for {self.param.name} is None, cannot convert from envelope")
            return 0.0
        if param_type in ["filter_cutoff", "filter_resonance"]:
            return value
        if param_type in ["mod_depth"]:
            return int(value * self.factor)
        if param_type in ["pulse_width"]:
            return int(value * self.factor)
        else:
            return self.factor / 2  # Default case, or raise an error

    def _slider_changed(self, value: int) -> None:
        """
        slider changed

        :param value: int slider value
        :return: None
        """
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(self.convert_to_envelope(value))
        self.spinbox.blockSignals(False)
        self.envelope_changed.emit(
            {self.param.get_envelope_param_type(): self.convert_to_envelope(value)}
        )

    def _spinbox_changed(self, value: float):
        """
        spinbox changed

        :param value: float double spinbox value
        :return: None
        """
        self.slider.blockSignals(True)
        self.slider.setValue(int(self.convert_from_envelope(int(value))))
        self.slider.blockSignals(False)
        self.envelope_changed.emit({self.param.get_envelope_param_type(): value})

    def setValue(self, value: float):
        """
        Set the value of the double spinbox and slider

        :param value: float
        :return: None
        """
        self.slider.setValue(value * self.factor)
        self.spinbox.setValue(value)
        self.envelope_changed.emit(
            {self.param.get_envelope_param_type(): value}
        )

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
