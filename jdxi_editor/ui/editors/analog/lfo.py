"""
Analog LFO Section
"""

from typing import Callable, Dict

from PySide6.QtWidgets import (
    QPushButton,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.analog.spec import Analog
from jdxi_editor.ui.editors.digital.partial.lfo.base import BaseLFOSection
from jdxi_editor.ui.editors.widget_specs import SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.editor import IconType


class AnalogLFOSection(BaseLFOSection):
    """Analog LFO Section (responsive layout version)"""

    DEPTH_SLIDERS = [
        SliderSpec(
            Analog.Param.LFO_PITCH_DEPTH, Analog.Display.Name.LFO_PITCH_DEPTH
        ),
        SliderSpec(
            Analog.Param.LFO_FILTER_DEPTH, Analog.Display.Name.LFO_FILTER_DEPTH
        ),
        SliderSpec(Analog.Param.LFO_AMP_DEPTH, Analog.Display.Name.LFO_AMP_DEPTH),
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
        SliderSpec(Analog.Param.LFO_RATE, Analog.Display.Name.LFO_RATE),
        SliderSpec(Analog.Param.LFO_FADE_TIME, Analog.Display.Name.LFO_FADE_TIME),
    ]

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        on_lfo_shape_changed: Callable,
        lfo_shape_buttons: Dict[int, QPushButton],
    ):
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
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
            Analog.Wave.LFO.TRI: JDXi.UI.IconRegistry.TRIANGLE_WAVE,
            Analog.Wave.LFO.SINE: JDXi.UI.IconRegistry.SINE_WAVE,
            Analog.Wave.LFO.SAW: JDXi.UI.IconRegistry.SAW_WAVE,
            Analog.Wave.LFO.SQUARE: JDXi.UI.IconRegistry.SQUARE_WAVE,
            Analog.Wave.LFO.SAMPLE_HOLD: JDXi.UI.IconRegistry.WAVEFORM,
            Analog.Wave.LFO.RANDOM: JDXi.UI.IconRegistry.RANDOM_WAVE,
        }
        self.analog: bool = True
        super().__init__(icon_type=IconType.ADSR, analog=self.analog)
        self.build_widgets()
        self.setup_ui()
