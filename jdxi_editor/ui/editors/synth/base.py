"""
Synth Control Base Module

This module defines the `SynthControlBase` class, a Qt-based widget that provides MIDI
control functionality for synthesizer parameters in the JD-Xi editor.

It facilitates:
- Sending and receiving MIDI SysEx messages.
- Handling parameter updates through UI elements (sliders, combo boxes, spin boxes, switches).
- Managing MIDI helper instances for communication.

Dependencies:
- PySide6 for GUI components.
- jdxi_editor.midi for MIDI communication.
- jdxi_editor.ui.widgets for UI elements.

Classes:
- SynthControlBase: A base widget for controlling synth parameters via MIDI.
"""


import threading
from typing import Dict

import mido
from PySide6.QtWidgets import QWidget

from jdxi_editor.log.error import log_error
from jdxi_editor.log.message import log_message
from jdxi_editor.log.parameter import log_parameter
from jdxi_editor.midi.data.address.helpers import apply_address_offset
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.io import MidiIOHelper
from jdxi_editor.midi.io.delay import send_with_delay
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.ui.widgets.combo_box.combo_box import ComboBox
from jdxi_editor.ui.widgets.slider import Slider
from jdxi_editor.ui.widgets.spin_box.spin_box import SpinBox
from jdxi_editor.ui.widgets.switch.switch import Switch


class SynthBase(QWidget):
    """base class for all synth editors"""

    def __init__(self, midi_helper, parent=None):
        super().__init__(parent)
        self.sysex_data = None
        self.address = None
        self.partial_number = None
        self.bipolar_parameters = []
        self.controls: Dict[AddressParameter, QWidget] = {}
        self._midi_helper = midi_helper
        self.midi_requests = []

    @property
    def midi_helper(self) -> MidiIOHelper:
        return self._midi_helper

    @midi_helper.setter
    def midi_helper(self, helper: MidiIOHelper) -> None:
        self._midi_helper = helper

    def send_raw_message(self, message: bytes) -> bool:
        """Send address SysEx message using the MIDI helper"""
        if not self._midi_helper:
            log_message("MIDI helper not initialized")
            return False
        return self._midi_helper.send_raw_message(message)

    def data_request(self):
        """
        Request the current value of the NRPN parameter from the device.
        """
        threading.Thread(
            target=send_with_delay,
            args=(
                self._midi_helper,
                self.midi_requests,
            ),
        ).start()

    def _on_midi_message_received(self, message: mido.Message) -> None:
        """
        Handle incoming MIDI messages
        :param message: mido.Message
        :return: None
        """
        if not message.type == "clock":
            log_message(f"MIDI message: {message}")
            self.blockSignals(True)
            self.data_request()
            self.blockSignals(False)

    def send_midi_parameter(self, param: AddressParameter, value: int) -> bool:
        """
        Send MIDI parameter with error handling
        :param param: AddressParameter
        :param value: int value
        :return: bool True on success, False otherwise
        """
        try:
            if hasattr(param, "get_nibbled_size"):
                size = param.get_nibbled_size()
            else:
                size = 1
            address = apply_address_offset(self.address, param)
            log_message("applying address offset ->")
            log_parameter("base address:", self.address)
            log_parameter("parameter offset to apply:", param)
            log_parameter("  -->  final address", address)
            log_parameter("parameter value:", value)
            sysex_message = RolandSysEx(
                msb=address.msb,
                umb=address.umb,
                lmb=address.lmb,
                lsb=address.lsb,
                value=value,
                size=size,
            )
            result = self._midi_helper.send_midi_message(sysex_message)
            return bool(result)
        except Exception as ex:
            log_error(f"MIDI error setting {param.name}: {ex}")
            return False

    def _on_parameter_changed(self, param: AddressParameter, display_value: int):
        """Handle parameter value changes from UI controls."""
        try:
            # Convert display value to MIDI value
            if hasattr(param, "convert_to_midi"):
                midi_value = param.convert_to_midi(display_value)
            else:
                midi_value = (
                    param.convert_from_display(display_value)
                    if hasattr(param, "convert_from_display")
                    else param.validate_value(display_value)
                )
            # Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                log_message(f"Failed to send parameter {param.name}")
        except Exception as ex:
            log_error(f"Error handling parameter {param.name}: {ex}")

    def _create_parameter_slider(
        self,
        param: AddressParameter,
        label: str,
        vertical=False,
        show_value_label=True,
    ) -> Slider:
        """Create a slider for a synth parameter with proper display conversion."""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        slider = Slider(
            label,
            display_min,
            display_max,
            vertical,
            show_value_label,
            is_bipolar=param.is_bipolar,
        )

        if param.name in self.bipolar_parameters or param.is_bipolar:
            slider.setValueDisplayFormat(lambda v: f"{v:+d}" if v != 0 else "0")
            slider.setCenterMark(0)
            slider.setTickPosition(Slider.TickPosition.TicksBothSides)
            slider.setTickInterval((display_max - display_min) // 4)

        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        self.controls[param] = slider
        return slider

    def _create_parameter_combo_box(
        self,
        param: AddressParameter,
        label: str = None,
        options: list = None,
        values: list = None,
        show_label=True,
    ) -> ComboBox:
        """Create a combo box for a parameter with proper display conversion"""
        combo_box = ComboBox(label, options, values, show_label=show_label)
        combo_box.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        self.controls[param] = combo_box
        return combo_box

    def _create_parameter_spin_box(
        self, param: AddressParameter, label: str = None
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
        param: AddressParameter,
        label: str,
        values: list[str],
    ) -> Switch:
        """Create address switch for address parameter with proper display conversion"""
        switch = Switch(label, values)
        switch.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))
        self.controls[param] = switch
        return switch
