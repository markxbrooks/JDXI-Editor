import sys
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QGroupBox, QHBoxLayout, QGridLayout
)
from PySide6.QtCore import Qt, Signal

from jdxi_editor.jdxi.midi.constant import MidiConstant
from jdxi_editor.log.logger import Logger as logger
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.address.helpers import apply_address_offset
from jdxi_editor.midi.data.parameter import AddressParameter
from jdxi_editor.midi.data.parameter.digital import AddressParameterDigitalPartial
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.midi.utils.conversions import midi_value_to_ms, ms_to_midi_value
from jdxi_editor.ui.widgets.pitch.pwm_plot import PWMPlot
from jdxi_editor.ui.widgets.pulse_width.slider_spinbox import PWMSliderSpinbox
from jdxi_editor.ui.widgets.slider import Slider
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


class PWMWidget(QWidget):

    mod_depth_changed = Signal(dict)
    pulse_width_changed = Signal(dict)
    envelopeChanged = Signal(dict)

    def __init__(self,
                 width_param: AddressParameter,
                 mod_depth_param: AddressParameter,
                 midi_helper: Optional[MidiIOHelper] = None,
                 controls: dict[AddressParameter, QWidget] = None,
                 address: Optional[RolandSysExAddress] = None,
                 parent: Optional[QWidget] = None,
                 ):
        super().__init__(parent)
        self.plot = None
        self.setWindowTitle("PWM Widget")
        self.address = address
        self.midi_helper = midi_helper
        if controls:
            self.controls = controls
        else:
            self.controls = {}
        self.envelope = {"pulse_width": 0.5,
                         "mod_depth": 0.5}
        self.width_control = PWMSliderSpinbox(
            width_param,
            min_value=0,
            max_value=127,
            suffix=" %",
            label="Width",
            value=int(self.envelope["pulse_width"] * MidiConstant.VALUE_MAX_SEVEN_BIT),  # Convert from 0.0–1.0 to 0–100
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.mod_depth_control = PWMSliderSpinbox(
            mod_depth_param,
            min_value=0,
            max_value=127,
            suffix=" %",
            label="Mod Depth",
            value=int(self.envelope["mod_depth"] * MidiConstant.VALUE_MAX_SEVEN_BIT),  # Convert from 0.0–1.0 to 0–100
            create_parameter_slider=self._create_parameter_slider,
            parent=self,
        )
        self.pitch_envelope_controls = [
            self.width_control,
            self.mod_depth_control,
        ]
        self.layout = QGridLayout()
        self.layout.addWidget(self.mod_depth_control, 0, 0)
        self.layout.addWidget(self.width_control, 0, 1)
        self.setLayout(self.layout)
        self.plot = PWMPlot(width=300,
                            height=250,
                            parent=self,
                            envelope=self.envelope)
        self.layout.addWidget(self.plot, 0, 4, 3, 1)
        self.setGeometry(JDXiDimensions.PWM_WIDGET_X,
                         JDXiDimensions.PWM_WIDGET_Y,
                         JDXiDimensions.PWM_WIDGET_WIDTH,
                         JDXiDimensions.PWM_WIDGET_HEIGHT)
        # self.mod_depth_control.envelopeChanged.connect(self.on_envelope_changed)
        self.width_control.slider.valueChanged.connect(self.on_pulse_width_changed)
        self.mod_depth_control.slider.valueChanged.connect(self.on_mod_depth_changed)
        self.init_ui()

    def on_envelope_changed(self, envelope: dict) -> None:
        """
        Handle envelope changes from controls
        :param envelope: dict
        :return: None
        """
        self.envelope = envelope
        print(f"Envelope changed: {self.envelope}")
        self.update()  # Trigger repaint if needed

    def on_pulse_width_changed(self, val: int) -> None:
        """
        Handle pulse width changes from slider
        :param val: int
        :return: None
        """
        self.envelope["pulse_width"] = val / MidiConstant.VALUE_MAX_SEVEN_BIT  # Convert from 0–100 to 0.0–1.0
        self.update()  # Trigger repaint if needed

    def on_mod_depth_changed(self, val: int) -> None:
        """
        Handle modulation depth changes from slider
        :param val: int
        :return: None
        """
        self.envelope["mod_depth"] = val / MidiConstant.VALUE_MAX_SEVEN_BIT   # Convert from 0–100 to 0.0–1.0
        self.update()  # Trigger repaint if needed

    def init_ui(self):
        layout = QVBoxLayout()

        # Group box for PWM controls
        group_box = QGroupBox("PWM Controls")
        group_layout = QHBoxLayout()

        # Width slider
        self.width_label = QLabel("Width (% of cycle): 50")
        self.width_slider = QSlider(Qt.Vertical)
        self.width_slider.setRange(0, 100)
        self.width_slider.setValue(50)
        self.width_slider.valueChanged.connect(
            lambda val: self.width_label.setText(f"Width (% of cycle): {val}")
        )
        self.width_slider.valueChanged.connect(self.on_pulse_width_changed)

        # Mod Depth slider
        self.mod_depth_label = QLabel("Mod Depth (of LFO applied): 50")
        self.mod_depth_slider = QSlider(Qt.Vertical)
        self.mod_depth_slider.setRange(0, 100)
        self.mod_depth_slider.setValue(50)
        self.mod_depth_slider.valueChanged.connect(
            lambda val: self.mod_depth_label.setText(f"Mod Depth (of LFO applied): {val}")
        )
        self.mod_depth_slider.valueChanged.connect(self.on_mod_depth_changed)

        # Add widgets to layout
        for label, slider in [
            (self.width_label, self.width_slider),
            (self.mod_depth_label, self.mod_depth_slider),
        ]:
            group_layout.addWidget(label)
            group_layout.addWidget(slider)

        # group_layout.addWidget(self.plot)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        # self.setLayout(layout)
        
    def _create_parameter_slider(self,
                                 param: AddressParameter,
                                 label: str,
                                 value: int = None) -> Slider:
        """
        Create address slider for address parameter with proper display conversion
        :param param: AddressParameter
        :param label: str
        :param value: int
        :return: Slider
        """
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val
        # Create vertical slider
        slider = Slider(
            label,
            min_value=display_min,
            max_value=display_max,
            midi_helper=self.midi_helper,
            vertical=True,
            show_value_label=False,
            is_bipolar=param.is_bipolar,
        )
        slider.setValue(value)
        # Connect value changed signal
        slider.valueChanged.connect(
            lambda v, s=slider: self.update_envelope_from_slider(s)
        )
        slider.valueChanged.connect(lambda v: self.send_parameter_message(param, v))
        self.controls[param] = slider
        return slider

    def update_envelope_from_slider(self, slider: QSlider) -> None:
        """Update envelope with value from a single slider"""
        for param, ctrl in self.controls.items():
            if ctrl is slider:
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "mod_depth":
                    self.envelope["mod_depth"] = slider.value() / MidiConstant.VALUE_MAX_SEVEN_BIT
                elif envelope_param_type == "pulse_width":
                    self.envelope["pulse_width"] = slider.value() / MidiConstant.VALUE_MAX_SEVEN_BIT
                else:
                    pass
                break

    def send_parameter_message(self, param: AddressParameter, value: int) -> None:
        """
        Handle slider value changes and send midi message
        :param param: AddressParameter
        :param value: int
        :return: None
        Convert display value to MIDI value if needed then send message
        """
        try:
            if hasattr(param, "convert_to_midi"):
                midi_value = param.convert_to_midi(value)
            elif hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(value)
            else:
                midi_value = param.validate_value(value)
            if not self.send_midi_parameter(param, midi_value):
                logger.parameter("Failed to send parameter", param)
        except ValueError as ex:
            logger.error(f"Error updating parameter: {ex}")

    def _on_parameter_changed(self, param: AddressParameter, value: int) -> None:
        """
        Handle parameter value changes and update envelope accordingly
        :param param: AddressParameter
        :param value: int
        :return: None
        """
        # Update envelope based on slider values
        self.update_envelope_from_controls()
        self.pulse_width_changed.emit(self.envelope)
        # self._update_spin_box(param)
        self.send_parameter_message(param, value)
        self.plot.set_values(self.envelope)
        self.pulse_width_changed.emit(self.envelope)

    def update_envelope_from_controls(self) -> None:
        """Update envelope values from slider controls"""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                logger.message(f"envelope_param_type = {envelope_param_type}")
                if envelope_param_type == "mod_depth":
                    self.envelope["mod_depth"] = slider.value() / MidiConstant.VALUE_MAX_SEVEN_BIT
                if envelope_param_type == "pulse_width":
                    self.envelope["pulse_width"] = slider.value() / MidiConstant.VALUE_MAX_SEVEN_BIT
                else:
                    self.envelope[envelope_param_type] = midi_value_to_ms(
                        slider.value()
                    )
            logger.message(f"{self.envelope}")
        except Exception as ex:
            logger.error(f"Error updating envelope from controls: {ex}")
        self.plot.set_values(self.envelope)

    def update_controls_from_envelope(self) -> None:
        """Update slider controls from envelope values."""
        try:
            for param, slider in self.controls.items():
                envelope_param_type = param.get_envelope_param_type()
                if envelope_param_type == "mod_depth":
                    slider.setValue(int(self.envelope["mod_depth"] * MidiConstant.VALUE_MAX_SEVEN_BIT))
                if envelope_param_type == "pulse_width":
                    slider.setValue(int(self.envelope["pulse_width"] * MidiConstant.VALUE_MAX_SEVEN_BIT))
                else:
                    slider.setValue(
                        int(ms_to_midi_value(self.envelope[envelope_param_type]))
                    )
        except Exception as ex:
            logging.error(f"Error updating controls from envelope: {ex}")
        self.plot.set_values(self.envelope)

    def send_midi_parameter(self, param: AddressParameter, value: int) -> bool:
        """
        Send MIDI parameter with error handling
        :param param: AddressParameter
        :param value: int
        :return: bool True on success, false otherwise
        """
        if not self.midi_helper:
            logger.message("No MIDI helper available - parameter change ignored")
            return False
        address = apply_address_offset(self.address, param)

        try:
            sysex_message = RolandSysEx(
                msb=address.msb,
                umb=address.umb,
                lmb=address.lmb,
                lsb=address.lsb,
                value=value,
            )
            return self.midi_helper.send_midi_message(sysex_message)
        except Exception as ex:
            logger.error(f"MIDI error setting {param}: {str(ex)}")
            return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    midi_helper = MidiIOHelper()
    address = RolandSysExAddress(msb=0x41, umb=0x00, lmb=0x00, lsb=0x00)
    window = PWMWidget(width_param=AddressParameterDigitalPartial.OSC_PULSE_WIDTH_MOD_DEPTH,
                       mod_depth_param=AddressParameterDigitalPartial.OSC_PULSE_WIDTH_MOD_DEPTH,
                       midi_helper=midi_helper,
                       address=address)

    window.show()
    sys.exit(app.exec())
