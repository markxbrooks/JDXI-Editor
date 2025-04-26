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


import logging
import threading
import time
from typing import Dict
from PySide6.QtWidgets import QWidget

from jdxi_editor.midi.data.address.helpers import apply_address_offset, construct_address
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.io import MidiIOHelper
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
        self.sysex_address = None
        self.partial_number = None
        self.bipolar_parameters = []
        self.address_lmb = None
        self.address_msb = None
        self.address_umb = None
        self.controls: Dict[AddressParameter, QWidget] = {}
        self.midi_helper = midi_helper
        self.midi_requests = []

    def set_midi_helper(self, midi_helper: MidiIOHelper):
        """Set MIDI helper instance"""
        self.midi_helper = midi_helper

    def send_raw_message(self, message: bytes):
        """Send address SysEx message using the MIDI helper"""
        if not self.midi_helper:
            logging.error("MIDI helper not initialized")
            return
        self.midi_helper.send_raw_message(message)

    def data_request(self):
        def send_with_delay(midi_requests):
            for midi_request in midi_requests:
                byte_list_message = bytes.fromhex(midi_request)
                self.midi_helper.send_raw_message(byte_list_message)
                time.sleep(0.075)  # Blocking delay in a separate thread

        # Run the function in a separate thread
        threading.Thread(target=send_with_delay, args=(self.midi_requests,)).start()

    def _on_midi_message_received(self, message):
        """Handle incoming MIDI messages"""
        if not message.type == "clock":
            logging.info(f"MIDI message: {message}")
            self.blockSignals(True)
            self.data_request()
            self.blockSignals(False)

    def send_midi_parameter_new(self, param: AddressParameter, value: int) -> bool:
        """Send MIDI parameter with error handling."""
        try:
            logging.info(self._format_logging_message(param, value))
            size = self._get_parameter_size(param)
            full_address = self._construct_full_address(param)
            sysex_message = self._create_sysex_message(full_address, value, size)
            result = self.midi_helper.send_midi_message(sysex_message)
            return bool(result)
        except Exception as ex:
            logging.error(f"MIDI error setting {param.name}: {ex}")
            return False

    def send_midi_parameter(self, param: AddressParameter, value: int) -> bool:
        """Send MIDI parameter with error handling."""
        try:
            logging.info(self._format_logging_message(param, value))
            size = self._get_parameter_size(param)
            base_address, full_address, offset = self._construct_full_address(param)
            sysex_message = self._create_sysex_message(full_address, value, size)
            result = self.midi_helper.send_midi_message(sysex_message)
            return bool(result)
        except Exception as ex:
            logging.error(f"MIDI error setting {param.name}: {ex}")
            return False

    def _format_logging_message(self, param: AddressParameter, value: int) -> str:
        return (
            f"Sending {self.partial_number} param={param.name}, "
            f"partial={self.address_umb}, group={self.address_lmb}, value={value}"
        )

    def _get_parameter_size(self, param: AddressParameter) -> int:
        return param.get_nibbled_size() if hasattr(param, "get_nibbled_size") else 1

    def _construct_full_address_new(self, param: AddressParameter):
        return apply_address_offset(self.sysex_data.address, param)

    def _create_sysex_message_new(self, full_address, value: int, size: int) -> RolandSysEx:
        sysex_message = RolandSysEx(
            address=full_address,
            value=value,
            size=size,
        )
        return sysex_message

    def _construct_full_address(self, param: AddressParameter):
        return construct_address(self.address_msb, self.address_umb, self.address_lmb, param)

    def _create_sysex_message(self, full_address, value: int, size: int) -> RolandSysEx:
        address_msb, address_umb, address_lmb, address_lsb = full_address
        sysex_message = RolandSysEx(
            msb=address_msb,
            umb=address_umb,
            lmb=address_lmb,
            lsb=address_lsb,
            value=value,
            size=size,
        )
        return sysex_message

    def send_midi_parameter_new(self, param: AddressParameter, value: int) -> bool:
        """Send MIDI parameter with error handling."""
        try:
            logging.info(
                f"Sending {self.partial_number} param={param.name}, partial={self.address_umb}, group={self.address_lmb}, value={value}"
            )
            if hasattr(param, "get_nibbled_size"):
                size = param.get_nibbled_size()
            else:
                size = 1
            base_address, full_address, offset = apply_address_offset(self.address_msb,
                                                                      self.address_umb,
                                                                      self.address_lmb,
                                                                      param
                                                                      )
            address_msb, address_umb, address_lmb, address_lsb = full_address
            logging.info(f"base address: \t{base_address.to_sysex_address()}")
            logging.info(f"offset: \t{offset}")
            logging.info(f"full address \t{full_address}")

            sysex_message = RolandSysEx(
                msb=address_msb,
                umb=address_umb,
                lmb=address_lmb,
                lsb=address_lsb,
                value=value,
                size=size,
            )
            result = self.midi_helper.send_midi_message(sysex_message)
            return bool(result)
        except Exception as ex:
            logging.error(f"MIDI error setting {param.name}: {ex}")
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
                logging.warning(f"Failed to send parameter {param.name}")
        except Exception as ex:
            logging.error(f"Error handling parameter {param.name}: {ex}")

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
