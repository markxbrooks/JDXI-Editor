"""
Analog LFO Section
"""

from typing import Callable, Dict, Literal, Union

from PySide6.QtWidgets import (
    QPushButton,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.ui.editors.base.lfo import BaseLFOSection
from jdxi_editor.ui.widgets.spec import SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.editor import IconType


class AnalogLFOSection(BaseLFOSection):
    """Analog LFO Section (responsive layout version)"""

    DEPTH_SLIDERS = [
        SliderSpec(
            Analog.Param.LFO_PITCH_DEPTH,
            Analog.Display.Name.LFO_PITCH_DEPTH,
        ),
        SliderSpec(
            Analog.Param.LFO_FILTER_DEPTH,
            Analog.Display.Name.LFO_FILTER_DEPTH,
        ),
        SliderSpec(
            Analog.Param.LFO_AMP_DEPTH,
            Analog.Display.Name.LFO_AMP_DEPTH,
        ),
    ]
    SWITCH_SPECS = [
        SwitchSpec(
            Analog.Param.LFO_TEMPO_SYNC_SWITCH,
            Analog.Display.Name.LFO_TEMPO_SYNC_SWITCH,
            Analog.Display.Options.LFO_TEMPO_SYNC_SWITCH,
        ),
        SwitchSpec(
            Analog.Param.LFO_TEMPO_SYNC_NOTE,
            Analog.Display.Name.LFO_TEMPO_SYNC_NOTE,
            Analog.Display.Options.LFO_TEMPO_SYNC_NOTE,
        ),
        SwitchSpec(
            Analog.Param.LFO_KEY_TRIGGER,
            Analog.Display.Name.LFO_KEY_TRIGGER,
            Analog.Display.Options.LFO_KEY_TRIGGER,
        ),
    ]
    RATE_FADE_SLIDERS = [
        SliderSpec(
            Analog.Param.LFO_RATE, Analog.Display.Name.LFO_RATE
        ),
        SliderSpec(
            Analog.Param.LFO_FADE_TIME,
            Analog.Display.Name.LFO_FADE_TIME,
        ),
    ]

    def __init__(
        self,
        on_lfo_shape_changed: Callable,
        lfo_shape_buttons: Dict[int, QPushButton],
        send_midi_parameter: Callable = None,
        controls: dict = None,
    ):
        self._on_lfo_shape_changed = on_lfo_shape_changed
        self.lfo_shape_buttons = lfo_shape_buttons

        self.lfo_shapes = [
            Analog.Wave.LFO.TRI,
            Analog.Wave.LFO.SINE,
            Analog.Wave.LFO.SAW,
            Analog.Wave.LFO.SQUARE,
            Analog.Wave.LFO.SAMPLE_HOLD,
            Analog.Wave.LFO.RANDOM,
        ]
        self.shape_icon_map = {
            Analog.Wave.LFO.TRI: JDXi.UI.Icon.WAVE_TRIANGLE,
            Analog.Wave.LFO.SINE: JDXi.UI.Icon.WAVE_SINE,
            Analog.Wave.LFO.SAW: JDXi.UI.Icon.WAVE_SAW,
            Analog.Wave.LFO.SQUARE: JDXi.UI.Icon.WAVE_SQUARE,
            Analog.Wave.LFO.SAMPLE_HOLD: JDXi.UI.Icon.WAVEFORM,
            Analog.Wave.LFO.RANDOM: JDXi.UI.Icon.WAVE_RANDOM,
        }
        self.analog: bool = True
        super().__init__(
            icons_row_type=IconType.ADSR,
            analog=self.analog,
            send_midi_parameter=send_midi_parameter,
        )
        # --- Set controls after super().__init__() to avoid it being overwritten
        self.controls: Dict[Union[Analog.Param], QWidget] = controls or {}
        # --- Set LFO shape parameter for Analog
        from jdxi_editor.midi.data.parameter.analog.address import AnalogParam

        self.lfo_shape_param: Literal[AnalogParam.LFO_SHAPE] = AnalogParam.LFO_SHAPE
        # Also set wave_shape_param for BaseLFOSection._on_wave_shape_selected
        self.wave_shape_param = AnalogParam.LFO_SHAPE
        self.build_widgets()
        self.setup_ui()
