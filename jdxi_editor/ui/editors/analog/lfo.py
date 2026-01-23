"""
Analog LFO Section
"""

from typing import Callable, Dict

from PySide6.QtWidgets import (
    QPushButton,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.analog.lfo import AnalogLFOWaveShape
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.analog.name import AnalogDisplayName
from jdxi_editor.midi.data.parameter.analog.option import AnalogDisplayOptions
from jdxi_editor.ui.editors.digital.partial.lfo.base import BaseLFOSection
from jdxi_editor.ui.editors.widget_specs import SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.editor import IconType


class AnalogLFOSection(BaseLFOSection):
    """Analog LFO Section (responsive layout version)"""

    DEPTH_SLIDERS = [
        SliderSpec(
            AnalogParam.LFO_PITCH_DEPTH, AnalogDisplayName.LFO_PITCH_DEPTH
        ),
        SliderSpec(
            AnalogParam.LFO_FILTER_DEPTH, AnalogDisplayName.LFO_FILTER_DEPTH
        ),
        SliderSpec(AnalogParam.LFO_AMP_DEPTH, AnalogDisplayName.LFO_AMP_DEPTH),
    ]
    SWITCH_SPECS = [
        SwitchSpec(
            AnalogParam.LFO_TEMPO_SYNC_SWITCH,
            AnalogDisplayName.LFO_TEMPO_SYNC_SWITCH,
            AnalogDisplayOptions.LFO_TEMPO_SYNC_SWITCH,
        ),
        SwitchSpec(
            AnalogParam.LFO_TEMPO_SYNC_NOTE,
            AnalogDisplayName.LFO_TEMPO_SYNC_NOTE,
            AnalogDisplayOptions.LFO_TEMPO_SYNC_NOTE,
        ),
        SwitchSpec(
            AnalogParam.LFO_KEY_TRIGGER,
            AnalogDisplayName.LFO_KEY_TRIGGER,
            AnalogDisplayOptions.LFO_KEY_TRIGGER,
        ),
    ]
    RATE_FADE_SLIDERS = [
        SliderSpec(AnalogParam.LFO_RATE, AnalogDisplayName.LFO_RATE),
        SliderSpec(AnalogParam.LFO_FADE_TIME, AnalogDisplayName.LFO_FADE_TIME),
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
            AnalogLFOWaveShape.TRI,
            AnalogLFOWaveShape.SINE,
            AnalogLFOWaveShape.SAW,
            AnalogLFOWaveShape.SQUARE,
            AnalogLFOWaveShape.SAMPLE_HOLD,
            AnalogLFOWaveShape.RANDOM,
        ]
        self.shape_icon_map = {
            AnalogLFOWaveShape.TRI: JDXi.UI.IconRegistry.TRIANGLE_WAVE,
            AnalogLFOWaveShape.SINE: JDXi.UI.IconRegistry.SINE_WAVE,
            AnalogLFOWaveShape.SAW: JDXi.UI.IconRegistry.SAW_WAVE,
            AnalogLFOWaveShape.SQUARE: JDXi.UI.IconRegistry.SQUARE_WAVE,
            AnalogLFOWaveShape.SAMPLE_HOLD: JDXi.UI.IconRegistry.WAVEFORM,
            AnalogLFOWaveShape.RANDOM: JDXi.UI.IconRegistry.RANDOM_WAVE,
        }
        self.analog: bool = True
        super().__init__(icon_type=IconType.ADSR, analog=self.analog)
        self.build_widgets()
        self.setup_ui()
