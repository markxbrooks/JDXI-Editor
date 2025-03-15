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
    - jdxi_manager.midi.data.parameter.synth (SynthParameter)
    - jdxi_manager.midi.data.constants (PART_1)
    - jdxi_manager.ui.widgets.slider (Slider)
    - jdxi_manager.ui.widgets.combo_box.combo_box (ComboBox)
    - jdxi_manager.ui.widgets.spin_box.spin_box (SpinBox)

"""

import logging
from typing import Dict

from PySide6.QtWidgets import (
    QWidget,
)

from jdxi_editor.midi.data.parameter.synth import SynthParameter
from jdxi_editor.midi.data.constants.constants import PART_1
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.ui.widgets.slider import Slider
from jdxi_editor.ui.widgets.combo_box.combo_box import ComboBox
from jdxi_editor.ui.widgets.spin_box.spin_box import SpinBox
from jdxi_editor.ui.widgets.switch.switch import Switch


class PartialEditor(QWidget):
    """Editor for address single partial"""

    def __init__(self, midi_helper=None, partial_num=1, part=PART_1, parent=None):
        super().__init__(parent)
        self.bipolar_parameters = []
        self.midi_helper = midi_helper
        self.area = None
        self.part = part
        self.group = 0x00
        self.partial_number = partial_num  # This is now the numerical index
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

        slider = Slider(label, display_min, display_max, is_bipolar=param.is_bipolar)
        # Set up bipolar parameters
        if param in self.bipolar_parameters or param.is_bipolar:
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

    def _create_parameter_switch(
        self,
        param: SynthParameter,
        label: str,
        values: list[str],
    ) -> Switch:
        """Create address switch for address parameter with proper display conversion"""
        switch = Switch(label, values)
        switch.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        self.controls[param] = switch
        return switch

    def send_midi_parameter(self, param: SynthParameter, value: int) -> bool:
        """Send MIDI parameter with error handling."""
        try:
            # Get parameter area and address with partial offset
            group, _ = getattr(
                param, "get_address_for_partial", lambda _: (self.group, None)
            )(self.partial_number)

            logging.info(
                f"Sending param={param.name}, partial={self.part}, group={group}, value={value}"
            )

            sysex_message = RolandSysEx(
                area=self.area,
                section=self.part,
                group=group,
                param=param.address,
                value=value,
            )
            result = self.midi_helper.send_midi_message(sysex_message)

            return bool(result)
        except Exception as ex:
            logging.error(f"MIDI error setting {param.name}: {ex}")
            return False

    def _on_parameter_changed(self, param: SynthParameter, display_value: int):
        """Handle parameter value changes from UI controls."""
        try:
            # Convert display value to MIDI value
            midi_value = (
                param.convert_from_display(display_value)
                if hasattr(param, "convert_from_display")
                else param.validate_value(display_value)
            )

            # Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")
        except Exception as ex:
            logging.error(f"Error handling parameter {param.name}: {ex}")
