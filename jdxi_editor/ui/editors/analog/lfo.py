"""
Analog LFO Section
"""

from typing import Callable, Dict, Literal, Union

from PySide6.QtWidgets import (
    QPushButton,
    QWidget,
)

from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.base.lfo import BaseLFOSection, LFOGroup
from jdxi_editor.ui.widgets.editor import IconType


class AnalogLFOSection(BaseLFOSection):
    """Analog LFO Section (responsive layout version)"""

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
        self.analog: bool = True
        self.midi_helper = midi_helper
        super().__init__(
            icons_row_type=IconType.ADSR,
            analog=self.analog,
            send_midi_parameter=send_midi_parameter,
        )
        # --- Force analog so slider/theme styling is correct (base may default to False)
        self.analog = True
        # --- Set controls after super().__init__() to avoid it being overwritten
        self.controls: Dict[Union[Analog.Param], QWidget] = controls or {}
        # --- Set LFO shape parameter for Analog
        from jdxi_editor.midi.data.parameter.analog.address import AnalogParam

        self.lfo_shape_param: Literal[AnalogParam.LFO_SHAPE] = AnalogParam.LFO_SHAPE
        # Also set wave_shape_param for BaseLFOSection._on_wave_shape_selected
        self.wave_shape_param: Literal[AnalogParam.LFO_SHAPE] = AnalogParam.LFO_SHAPE
        self.build_widgets()
        self.setup_ui()

    def setup_ui(self) -> None:
        """setup ui"""
        widget_rows = [
            self.widgets[LFOGroup.switch.SWITCH_ROW],
            self.widgets[LFOGroup.slider.DEPTH],
            self.widgets[LFOGroup.slider.RATE_FADE],
        ]
        self._add_group_with_widget_rows(label=LFOGroup.label, rows=widget_rows)

