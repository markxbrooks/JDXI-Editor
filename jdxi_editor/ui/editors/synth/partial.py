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

from jdxi_editor.midi.data.address.address import (
    AddressOffsetTemporaryToneUMB,
    AddressOffsetProgramLMB, construct_address, Address,
)
from jdxi_editor.midi.data.parameter.synth import SynthParameter
from jdxi_editor.midi.message.roland import RolandSysEx
from jdxi_editor.ui.editors.synth.base import SynthBase


class PartialEditor(SynthBase):
    """Editor for address single partial"""

    def __init__(
        self,
        midi_helper=None,
        partial_number=1,
        part=AddressOffsetTemporaryToneUMB.DIGITAL_PART_1,
        parent=None,
    ):
        super().__init__(midi_helper, parent)
        self.synth_data = None
        self.partial_address_default = None
        self.partial_address_map = {}
        self.bipolar_parameters = []
        self.midi_helper = midi_helper
        self.address_msb = None
        self.address_umb = part
        self.address_lmb = AddressOffsetProgramLMB.COMMON
        self.partial_number = partial_number  # This is now the numerical index
        self.partial_name = None  # More for Drums eg. 'BD1'
        self.preset_helper = None

        # Store parameter controls for easy access
        self.controls: Dict[SynthParameter, QWidget] = {}

    def send_midi_parameter(self, param: SynthParameter, value: int) -> bool:
        """Send MIDI parameter with error handling."""
        try:
            address_lmb = self.address_lmb
            print(f"Type of address_lmb: {type(address_lmb)} {address_lmb}")
            logging.info(
                f"Sending partial number {self.partial_number} param={param}, address_umb={self.address_umb}, address_lmb={address_lmb}, value={value}"
            )
            if hasattr(param, "get_nibbled_size"):
                size = param.get_nibbled_size()
            else:
                size = 1
            base_address, full_address, offset = construct_address(self.address_msb,
                                                                   self.address_umb,
                                                                   self.address_lmb,
                                                                   param
            )

            # Step 5: Extract individual bytes
            address_msb, address_umb, address_lmb, address_lsb = full_address
            logging.info(f"base address: t\{base_address.to_sysex_address()}")
            logging.info(f"offset: \t{offset}")
            logging.info(f"full address \t{full_address}")
            sysex_message = RolandSysEx(
                address_msb=address_msb,
                address_umb=address_umb,
                address_lmb=address_lmb,
                address_lsb=address_lsb,
                value=value,
                size=size,
            )
            result = self.midi_helper.send_midi_message(sysex_message)

            return bool(result)
        except Exception as ex:
            logging.error(f"MIDI error setting {param.name}: {ex}")
            return False

    def get_partial_address(self) -> int:
        """Get parameter area and address adjusted for partial number."""
        address_lmb = self.partial_address_map.get(
            self.partial_number, self.partial_address_default
        )  # Default to 0x20 if partial_name is not 1, 2, or 3
        logging.info(f"address_lmb found: {address_lmb}")
        return address_lmb
