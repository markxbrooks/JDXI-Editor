from typing import Callable

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox, QWidget, QVBoxLayout

from jdxi_editor.log.logger import Logger as log
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.utils.conversions import midi_value_to_ms, ms_to_midi_value


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


class PWMSliderSpinbox(QWidget):
    """
    Pitch Env Slider and Spinbox widget for Roland JD-Xi
    """

    envelopeChanged = Signal(dict)

    def __init__(
        self,
        param: AddressParameter,
        min_value: float = 0.0,
        max_value: float = 1.0,
        suffix: str = "",
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
        :param suffix: str
        :param label: str
        :param value: int
        :param create_parameter_slider: Callable
        :param parent: QWidget
        """
        super().__init__(parent)

        self.param = param
        self.factor = 127
        if max_value > 1:
            self.factor = max_value
        self.create_parameter_slider = create_parameter_slider
        self.slider = self.create_parameter_slider(
            param,
            label,
            value,
        )
        param_type = param.get_envelope_param_type()
        if param_type in ["mod_depth",
                          "pulse_width"]:
            self.spinbox = create_double_spinbox(
                min_value=min_value, max_value=max_value, step=0.01, value=value
            )
        else:
            self.spinbox = create_spinbox(
                min_value=int(min_value),
                max_value=int(max_value),
                suffix=suffix,
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

    def convert_to_envelope(self, value: float):
        param_type = self.param.get_envelope_param_type()
        if param_type == "mod_depth":
            return value / 127
        if param_type == "pulse_width":
            return value / 127
        else:
            log.error(f"Unknown envelope parameter type: {param_type}")
            return 0.0  # or raise an error, depending on design

    def convert_from_envelope(self, value: float):
        param_type = self.param.get_envelope_param_type()
        if param_type in ["mod_depth"]:
            return int(value * 127)
        if param_type in ["pulse_width"]:
            return int(value * 127)
        else:
            return 64

    def _slider_changed(self, value: int) -> None:
        """
        slider changed
        :param value: int slider value
        :return: None
        """
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(int(self.convert_to_envelope(value)))
        self.spinbox.blockSignals(False)
        self.envelopeChanged.emit(
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
        self.envelopeChanged.emit({self.param.get_envelope_param_type(): value})

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
