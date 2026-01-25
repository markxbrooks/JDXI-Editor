"""
Analog LFO Section
"""

from typing import Callable, Dict, Literal

from PySide6.QtWidgets import (
    QPushButton,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.ui.editors.digital.partial.lfo.base import BaseLFOSection
from jdxi_editor.ui.editors.widget_specs import SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.editor import IconType


class AnalogLFOSection(BaseLFOSection):
    """Analog LFO Section (responsive layout version)"""

    DEPTH_SLIDERS = [
        SliderSpec(
            JDXi.Midi.Analog.Param.LFO_PITCH_DEPTH,
            JDXi.Midi.Analog.Display.Name.LFO_PITCH_DEPTH,
        ),
        SliderSpec(
            JDXi.Midi.Analog.Param.LFO_FILTER_DEPTH,
            JDXi.Midi.Analog.Display.Name.LFO_FILTER_DEPTH,
        ),
        SliderSpec(
            JDXi.Midi.Analog.Param.LFO_AMP_DEPTH,
            JDXi.Midi.Analog.Display.Name.LFO_AMP_DEPTH,
        ),
    ]
    SWITCH_SPECS = [
        SwitchSpec(
            JDXi.Midi.Analog.Param.LFO_TEMPO_SYNC_SWITCH,
            JDXi.Midi.Analog.Display.Name.LFO_TEMPO_SYNC_SWITCH,
            JDXi.Midi.Analog.Display.Options.LFO_TEMPO_SYNC_SWITCH,
        ),
        SwitchSpec(
            JDXi.Midi.Analog.Param.LFO_TEMPO_SYNC_NOTE,
            JDXi.Midi.Analog.Display.Name.LFO_TEMPO_SYNC_NOTE,
            JDXi.Midi.Analog.Display.Options.LFO_TEMPO_SYNC_NOTE,
        ),
        SwitchSpec(
            JDXi.Midi.Analog.Param.LFO_KEY_TRIGGER,
            JDXi.Midi.Analog.Display.Name.LFO_KEY_TRIGGER,
            JDXi.Midi.Analog.Display.Options.LFO_KEY_TRIGGER,
        ),
    ]
    RATE_FADE_SLIDERS = [
        SliderSpec(
            JDXi.Midi.Analog.Param.LFO_RATE, JDXi.Midi.Analog.Display.Name.LFO_RATE
        ),
        SliderSpec(
            JDXi.Midi.Analog.Param.LFO_FADE_TIME,
            JDXi.Midi.Analog.Display.Name.LFO_FADE_TIME,
        ),
    ]

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        on_lfo_shape_changed: Callable,
        lfo_shape_buttons: Dict[int, QPushButton],
        send_midi_parameter: Callable = None,
    ):
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self._on_lfo_shape_changed = on_lfo_shape_changed
        self.lfo_shape_buttons = lfo_shape_buttons

        self.lfo_shapes = [
            JDXi.Midi.Analog.Wave.LFO.TRI,
            JDXi.Midi.Analog.Wave.LFO.SINE,
            JDXi.Midi.Analog.Wave.LFO.SAW,
            JDXi.Midi.Analog.Wave.LFO.SQUARE,
            JDXi.Midi.Analog.Wave.LFO.SAMPLE_HOLD,
            JDXi.Midi.Analog.Wave.LFO.RANDOM,
        ]
        self.shape_icon_map = {
            JDXi.Midi.Analog.Wave.LFO.TRI: JDXi.UI.Icon.WAVE_TRIANGLE,
            JDXi.Midi.Analog.Wave.LFO.SINE: JDXi.UI.Icon.WAVE_SINE,
            JDXi.Midi.Analog.Wave.LFO.SAW: JDXi.UI.Icon.WAVE_SAW,
            JDXi.Midi.Analog.Wave.LFO.SQUARE: JDXi.UI.Icon.WAVE_SQUARE,
            JDXi.Midi.Analog.Wave.LFO.SAMPLE_HOLD: JDXi.UI.Icon.WAVEFORM,
            JDXi.Midi.Analog.Wave.LFO.RANDOM: JDXi.UI.Icon.WAVE_RANDOM,
        }
        self.analog: bool = True
        super().__init__(
            icons_row_type=IconType.ADSR,
            analog=self.analog,
            send_midi_parameter=send_midi_parameter,
        )
        # --- Set LFO shape parameter for Analog
        from jdxi_editor.midi.data.parameter.analog.address import AnalogParam

        self.lfo_shape_param: Literal[AnalogParam.LFO_SHAPE] = AnalogParam.LFO_SHAPE
        self.build_widgets()
        self.setup_ui()
