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
from typing import Dict, Optional

import mido
from PySide6.QtWidgets import QWidget

from jdxi_editor.jdxi.synth.factory import create_synth_data
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.log.logger import Logger as log
from jdxi_editor.log.slider_parameter import log_slider_parameters
from jdxi_editor.midi.data.address.address import AddressOffsetSuperNATURALLMB
from jdxi_editor.midi.data.parameter.digital.common import AddressParameterDigitalCommon
from jdxi_editor.midi.data.parameter.digital.modify import AddressParameterDigitalModify
from jdxi_editor.midi.data.parameter.synth import AddressParameter
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.midi.io.delay import send_with_delay
from jdxi_editor.midi.sysex.composer import JDXiSysExComposer
from jdxi_editor.ui.widgets.combo_box.combo_box import ComboBox
from jdxi_editor.ui.widgets.slider import Slider
from jdxi_editor.ui.widgets.spin_box.spin_box import SpinBox
from jdxi_editor.ui.widgets.switch.switch import Switch


class SynthBase(QWidget):
    """base class for all synth editors"""

    def __init__(self, midi_helper, parent=None):
        super().__init__(parent)
        self.partial_editors = []
        self.sysex_data = None
        self.address = None
        self.partial_number = None
        self.bipolar_parameters = []
        self.controls: Dict[AddressParameter, QWidget] = {}
        self._midi_helper = midi_helper
        self.midi_requests = []
        self.sysex_composer = JDXiSysExComposer()

    @property
    def midi_helper(self) -> MidiIOHelper:
        return self._midi_helper

    @midi_helper.setter
    def midi_helper(self, helper: MidiIOHelper) -> None:
        self._midi_helper = helper

    def send_raw_message(self, message: bytes) -> bool:
        """Send address SysEx message using the MIDI helper"""
        if not self._midi_helper:
            log.message("MIDI helper not initialized")
            return False
        return self._midi_helper.send_raw_message(message)

    def data_request(self, channel=None, program=None):
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
            log.message(f"MIDI message: {message}")
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
            if isinstance(param, AddressParameterDigitalCommon):
                self.address.lmb = AddressOffsetSuperNATURALLMB.COMMON
            if isinstance(param, AddressParameterDigitalModify):
                self.address.lmb = AddressOffsetSuperNATURALLMB.MODIFY
            sysex_message = self.sysex_composer.compose_message(
                address=self.address,
                param=param,
                value=value
            )
            result = self._midi_helper.send_midi_message(sysex_message)
            return bool(result)
        except Exception as ex:
            log.error(f"MIDI error setting {param.name}: {ex}")
            return False

    def send_midi_parameter_old(self, param: AddressParameter, value: int) -> bool:
        """
        Send MIDI parameter with error handling
        :param param: AddressParameter
        :param value: int value
        :return: bool True on success, False otherwise
        """
        try:
            sysex_message = self.sysex_composer.compose_message(address=target_address, param=param, value=value)
            result = self._midi_helper.send_midi_message(sysex_message)
            return bool(result)
        except Exception as ex:
            log.error(f"MIDI error setting {param.name}: {ex}")
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
                log.message(f"Failed to send parameter {param.name}")
        except Exception as ex:
            log.error(f"Error handling parameter {param.name}: {ex}")

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
            min_value=display_min,
            max_value=display_max,
            midi_helper=self.midi_helper,
            vertical=vertical,
            show_value_label=show_value_label,
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

    def _init_synth_data(self, synth_type: JDXiSynth = JDXiSynth.DIGITAL_SYNTH_1,
                         partial_number: Optional[int] = 0):
        """Initialize synth-specific data."""
        from jdxi_editor.jdxi.synth.factory import create_synth_data
        self.synth_data = create_synth_data(synth_type,
                                            partial_number=partial_number)

        # Dynamically assign attributes
        for attr in [
            "address",
            "preset_type",
            "instrument_default_image",
            "instrument_icon_folder",
            "presets",
            "preset_list",
            "midi_requests",
            "midi_channel",
        ]:
            setattr(self, attr, getattr(self.synth_data, attr))
            
    def _update_slider(
        self,
        param: AddressParameter,
        midi_value: int,
        successes: list = None,
        failures: list = None
    ) -> None:
        """
        Update slider based on parameter and value.
        :param param: AddressParameter
        :param midi_value: int value
        :param successes: list
        :param failures: list
        :return: None
        """
        slider = self.controls.get(param)
        if slider:
            if hasattr(param, "convert_from_midi"):
                slider_value = param.convert_from_midi(midi_value)
            else:
                slider_value = midi_value
            log_slider_parameters(
                self.address, param, midi_value, slider_value
            )
            slider.blockSignals(True)
            slider.setValue(midi_value)
            slider.blockSignals(False)
            successes.append(param.name)
        else:
            failures.append(param.name)

    def _update_switch(
        self,
        param: AddressParameter,
        midi_value: int,
        successes: list = None,
        failures: list = None,
        debug: bool = False,
    ) -> None:
        """
        Update switch based on parameter and value.
        :param param: AddressParameter
        :param midi_value: int value
        :param successes: list
        :param failures: list
        :param debug: bool
        :return: None
        """
        if not midi_value:
            return
        switch = self.controls.get(param)
        try:
            midi_value = int(midi_value)
            if switch:
                switch.blockSignals(True)
                switch.setValue(midi_value)
                switch.blockSignals(False)
                successes.append(param.name)
                log.parameter(f"Updated {midi_value} for", param)
            else:
                failures.append(param.name)
        except Exception as ex:
            log.error(f"Error {ex} occurred setting switch {param.name} to {midi_value}")
            failures.append(param.name)

    def _update_partial_slider(
        self,
        partial_no: int,
        param: AddressParameter,
        value: int,
        successes: list = None,
        failures: list = None,
    ) -> None:
        """
        Update the slider for a specific partial based on the parameter and value.
        :param partial_no: int
        :param param: AddressParameter
        :param value: int
        :param successes: list
        :return: None
        """
        if not value:
            return
        slider = self.partial_editors[partial_no].controls.get(param)
        if not slider:
            failures.append(param.name)
            return
        synth_data = create_synth_data(self.synth_data.preset_type, partial_no)
        self.address.lmb = synth_data.lmb
        slider_value = param.convert_from_midi(value)
        log_slider_parameters(
            self.address, param, value, slider_value
        )
        slider.blockSignals(True)
        slider.setValue(slider_value)
        slider.blockSignals(False)
        successes.append(param.name)
