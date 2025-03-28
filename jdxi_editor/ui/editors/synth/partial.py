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
from jdxi_editor.ui.editors.synth.base import SynthBase


class PartialEditor(SynthBase):
    """Editor for address single partial"""

    def __init__(self, midi_helper=None, partial_number=1, part=PART_1, parent=None):
        super().__init__(midi_helper, parent)
        self.bipolar_parameters = []
        self.midi_helper = midi_helper
        self.area = None
        self.part = part
        self.group = 0x00
        self.partial_number = partial_number  # This is now the numerical index
        self.partial_name = None  # More for Drums eg. 'BD1'
        self.preset_handler = None

        # Store parameter controls for easy access
        self.controls: Dict[SynthParameter, QWidget] = {}

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
            if hasattr(param, "get_nibbled_size"):
                size = param.get_nibbled_size()
            else:
                size = 1

            sysex_message = RolandSysEx(
                area=self.area,
                section=self.part,
                group=group,
                param=param.address,
                value=value,
                size=size,
            )
            result = self.midi_helper.send_midi_message(sysex_message)

            return bool(result)
        except Exception as ex:
            logging.error(f"MIDI error setting {param.name}: {ex}")
            return False
