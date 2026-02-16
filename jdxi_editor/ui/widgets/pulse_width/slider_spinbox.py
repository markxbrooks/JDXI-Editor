from typing import Callable

from decologr import Decologr as log
from picomidi.constant import Midi
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDoubleSpinBox, QSpinBox, QVBoxLayout, QWidget

from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter


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
    value_changed = Signal(int)
    valueChanged = value_changed  # alias for code that expects valueChanged (e.g. FilterWidget)
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
        self._raw_range = max_value > 1  # e.g. filter cutoff 0-127
        if max_value > 1:
            self.factor = max_value
        self.create_parameter_slider = create_parameter_slider
        # When range is 0-127, value is already in that range; else value is 0-1
        if value is not None and self._raw_range:
            initial_value = int(value)
        else:
            initial_value = int(value * self.factor) if value is not None else 0
        self.slider = self.create_parameter_slider(
            param=param,
            label=label,
            vertical=True,
            initial_value=initial_value,
        )
        self.spinbox = create_double_spinbox(
            min_value=min_value, max_value=max_value, step=0.01, value=value
        )
        self.spinbox.setRange(min_value, max_value)
        self.factor = Midi.VALUE.MAX.SEVEN_BIT
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
            log.error(
                f"Parameter type for {self.param.name} is None, cannot convert to envelope"
            )
            return 0.0
        if param_type in [
            EnvelopeParameter.FILTER_CUTOFF,
            EnvelopeParameter.FILTER_RESONANCE,
        ]:
            return value
        if param_type == EnvelopeParameter.MOD_DEPTH:
            return value / self.factor
        if param_type == EnvelopeParameter.PULSE_WIDTH:
            return value / self.factor
        else:
            log.error(f"Unknown envelope parameter type: {param_type}")
            return 0.0  # or raise an error, depending on design

    def convert_from_envelope(self, value: float):
        param_type = self.param.get_envelope_param_type()
        if param_type is None:
            log.error(
                f"Parameter type for {self.param.name} is None, cannot convert from envelope"
            )
            return 0.0
        if param_type in [
            EnvelopeParameter.FILTER_CUTOFF,
            EnvelopeParameter.FILTER_RESONANCE,
        ]:
            return value
        if param_type in [EnvelopeParameter.MOD_DEPTH]:
            return int(value * self.factor)
        if param_type in [EnvelopeParameter.PULSE_WIDTH]:
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
        env_val = self.convert_to_envelope(value)
        self.envelope_changed.emit(
            {self.param.get_envelope_param_type(): env_val}
        )
        log.message(f"slider value now {value}", scope=self.__class__.__name__)
        self.value_changed.emit(value)

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
        self.value_changed.emit(self.slider.value())

    def setValue(self, value: float):
        """
        Set the value of the double spinbox and slider.
        When used for filter (0-127 range), value is 0-127; else 0-1.
        """
        if self._raw_range:
            # Value is already in 0..max (e.g. 0-127)
            v = int(value)
            self.slider.setValue(v)
            self.spinbox.setValue(v)
        else:
            self.slider.setValue(value * self.factor)
            self.spinbox.setValue(value)
        self.envelope_changed.emit({self.param.get_envelope_param_type(): value})

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
