"""
Module for the PartialEditor widget, which provides a UI for editing individual partial parameters of a synthesizer.

This module defines the `PartialEditor` class, which extends `QWidget` to offer an interface for modifying
synth parameters through sliders, combo boxes, and spin boxes. It integrates with a MIDI helper to send parameter
changes to the synthesizer in real-time.

Classes:
    PartialEditor: A QWidget-based editor for modifying individual partial parameters.

Dependencies:
    - PySide6.QtWidgets (QWidget)
    - logging
    - typing (Dict)
    - jdxi_manager.data.parameter.synth (SynthParameter)
    - jdxi_manager.midi.constants (PART_1)
    - jdxi_manager.ui.widgets.slider (Slider)
    - jdxi_manager.ui.widgets.combo_box.combo_box (ComboBox)
    - jdxi_manager.ui.widgets.spin_box.spin_box (SpinBox)

"""

import logging
from typing import Dict

from PySide6.QtWidgets import (
    QWidget,
)
from jdxi_manager.data.parameter.synth import SynthParameter
from jdxi_manager.midi.constants import PART_1
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.combo_box.combo_box import ComboBox
from jdxi_manager.ui.widgets.spin_box.spin_box import SpinBox


class PartialEditor(QWidget):
    """Editor for address single partial"""

    def __init__(self, midi_helper=None, partial_num=1, part=PART_1, parent=None):
        super().__init__(parent)
        self.bipolar_parameters = []
        self.four_byte_params = None
        self.midi_helper = midi_helper
        self.area = None
        self.part = part
        self.group = None
        self.partial_num = partial_num  # This is now the numerical index
        self.partial_name = None  # More for Drums eg. 'BD1'
        self.preset_handler = None

        # Store parameter controls for easy access
        self.controls: Dict[SynthParameter, QWidget] = {}

    def _create_parameter_slider(
        self, param: SynthParameter, label: str = None
    ) -> Slider:
        """Create address slider for address parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        slider = Slider(label, display_min, display_max)
        # Set up bipolar parameters
        if param in self.bipolar_parameters:
            # Set format string to show + sign for positive values
            slider.setValueDisplayFormat(lambda v: f"{v:+d}" if v != 0 else "0")
            # Set center tick
            slider.setCenterMark(0)
            # Add more prominent tick at center
            slider.setTickPosition(Slider.TickPosition.TicksBothSides)
            slider.setTickInterval((display_max - display_min) // 4)

        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        # Store control reference
        self.controls[param] = slider
        return slider

    def _create_parameter_combo_box(
        self,
        param: SynthParameter,
        label: str = None,
        options: list = None,
        values: list = None,
    ) -> ComboBox:
        """Create address combo box for address parameter with proper display conversion"""

        combo_box = ComboBox(label, options, values)

        # Connect value changed signal
        combo_box.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = combo_box
        return combo_box

    def _create_parameter_spin_box(
        self, param: SynthParameter, label: str = None
    ) -> SpinBox:
        """Create address spin box for address parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        spin_box = SpinBox(label, display_min, display_max)

        # Connect value changed signal
        spin_box.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = spin_box
        return spin_box

    def _on_parameter_changed(self, param: SynthParameter, display_value: int):
        """Handle parameter value changes from UI controls"""
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(display_value)
            else:
                midi_value = param.validate_value(display_value)
            logging.info(
                f"parameter: {param} display {display_value} midi value {midi_value}"
            )
            if param in self.four_byte_params:
                size = 4
            else:
                size = 1
            logging.info(
                f"parameter param {param} value {display_value} size {size} sent"
            )
            try:
                # Ensure value is included in the MIDI message
                return self.midi_helper.send_parameter(
                    area=self.area,
                    part=self.part,
                    group=self.group,
                    param=param.address,
                    value=midi_value,  # Make sure this value is being sent
                    size=size,
                )
            except Exception as ex:
                logging.error(f"MIDI error setting {param}: {str(ex)}")
                return False

        except Exception as ex:
            logging.error(f"Error handling parameter {param.name}: {str(ex)}")
            return False
