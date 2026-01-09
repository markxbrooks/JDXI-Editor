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

from typing import Dict

from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtWidgets import (
    QWidget,
)

from jdxi_editor.ui.editors.synth.base import SynthBase


class PartialEditor(SynthBase):
    """Editor for address single partial"""

    def __init__(
        self,
        midi_helper=None,
        partial_number=1,
        parent=None,
    ):
        super().__init__(midi_helper, parent)
        self.synth_data = None
        self.partial_address_default = None
        self.partial_address_map = {}
        self.bipolar_parameters = []
        self.midi_helper = midi_helper
        self.partial_number = partial_number  # This is now the numerical index
        self.partial_name = None  # More for Drums eg. 'BD1'
        self.preset_helper = None
        # Store parameter controls for easy access
        self.controls: Dict[AddressParameter, QWidget] = {}

    def __str__(self):
        return f"{self.__class__.__name__} partial {self.partial_number}"

    def __repr__(self):
        return f"{self.__class__.__name__} partial {self.partial_number}"
