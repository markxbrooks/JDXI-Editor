"""
Analog LFO Section
"""

from typing import Callable, Dict, Literal

from PySide6.QtWidgets import (
    QPushButton,
)

from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.base.lfo import BaseLFOSection
from jdxi_editor.ui.widgets.editor import IconType


class AnalogLFOSection(BaseLFOSection):
    SYNTH_SPEC = Analog

    def __init__(
        self,
        on_lfo_shape_changed: Callable,
        lfo_shape_buttons: Dict[int, QPushButton],
        send_midi_parameter: Callable = None,
        midi_helper: MidiIOHelper = None,
        controls: dict = None,
    ):
        self._on_lfo_shape_changed = on_lfo_shape_changed
        self.lfo_shape_buttons = lfo_shape_buttons
        self.midi_helper = midi_helper

        # configure BEFORE base UI build
        from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
        self.lfo_shape_param: Literal[AnalogParam.LFO_SHAPE] = AnalogParam.LFO_SHAPE
        self.wave_shape_param: Literal[AnalogParam.LFO_SHAPE] = AnalogParam.LFO_SHAPE
        self.controls = controls or {}

        super().__init__(
            icons_row_type=IconType.ADSR,
            analog=True,
            send_midi_parameter=send_midi_parameter,
        )
        # Base skips _setup_ui() when analog=True, so build the layout here
        self._setup_ui()
