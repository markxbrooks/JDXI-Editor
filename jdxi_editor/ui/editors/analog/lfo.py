"""
Analog LFO Section
"""

from typing import Callable, Dict, Literal

from PySide6.QtWidgets import QPushButton

from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.base.lfo import BaseLFOSection
from jdxi_editor.ui.widgets.editor import IconType


class AnalogLFOSection(BaseLFOSection):

    SYNTH_SPEC = Analog

    def __init__(
        self,
        send_midi_parameter: Callable | None = None,
        midi_helper: MidiIOHelper = None,
        controls: dict = None,
    ):
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
        # Base overwrites wave_shape_param with None; restore for MIDI shape messages
        self.wave_shape_param = AnalogParam.LFO_SHAPE
        # Base skips _setup_ui() when analog=True, so build the layout here
        self._setup_ui()
        # Share shape buttons with editor so _update_lfo_shape_buttons (preset load) works
        self.lfo_shape_buttons.update(
            {shape.value: btn for shape, btn in self.wave_shape_buttons.items()}
        )
