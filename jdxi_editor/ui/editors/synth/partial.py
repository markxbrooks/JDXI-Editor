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

from jdxi_editor.midi.data.address.address import TemporaryToneAddressOffset, ProgramAddressGroup
from jdxi_editor.midi.data.parameter.synth import SynthParameter
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.ui.editors.synth.base import SynthBase


class PartialEditor(SynthBase):
    """Editor for address single partial"""

    def __init__(self, midi_helper=None, partial_number=1,
                 part=TemporaryToneAddressOffset.DIGITAL_PART_1,
                 parent=None):
        super().__init__(midi_helper, parent)
        self.bipolar_parameters = []
        self.midi_helper = midi_helper
        self.address_msb = None
        self.address_umb = part
        self.address_lmb = ProgramAddressGroup.PROGRAM_COMMON
        self.partial_number = partial_number  # This is now the numerical index
        self.partial_name = None  # More for Drums eg. 'BD1'
        self.preset_helper = None

        # Store parameter controls for easy access
        self.controls: Dict[SynthParameter, QWidget] = {}

    def send_midi_parameter(self, param: SynthParameter, value: int) -> bool:
        """Send MIDI parameter with error handling."""
        try:
            # Get parameter area and address with partial offset
            group, _ = getattr(
                param, "get_address_for_partial", lambda _: (self.address_lmb, None)
            )(self.partial_number)

            logging.info(
                f"Sending param={param.name}, partial={self.address_umb}, group={group}, value={value}"
            )
            if hasattr(param, "get_nibbled_size"):
                size = param.get_nibbled_size()
            else:
                size = 1

            sysex_message = RolandSysEx(
                address_msb=self.address_msb,
                address_umb=self.address_umb,
                address_lmb=group,
                address_lsb=param.address,
                value=value,
                size=size,
            )
            result = self.midi_helper.send_midi_message(sysex_message)

            return bool(result)
        except Exception as ex:
            logging.error(f"MIDI error setting {param.name}: {ex}")
            return False
