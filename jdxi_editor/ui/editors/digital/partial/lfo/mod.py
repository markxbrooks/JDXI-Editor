"""
MOD LFO section of the digital partial editor.
"""

from typing import Callable, Literal

from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.editors.base.lfo import BaseLFOSection
from jdxi_editor.ui.widgets.spec import SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.editor import IconType


class DigitalModLFOSection(BaseLFOSection):
    """MOD LFO section for the digital partial editor."""

    rate_tab_label = "Rate and Rate Ctrl"

    RATE_FADE_SLIDERS = [
        SliderSpec(
            Digital.Param.MOD_LFO_RATE,
            Digital.Display.Name.MOD_LFO_RATE,
        ),
        SliderSpec(
            Digital.Param.MOD_LFO_RATE_CTRL,
            Digital.Display.Name.MOD_LFO_RATE_CTRL,
        ),
    ]
    DEPTH_SLIDERS = [
        SliderSpec(
            Digital.Param.LFO_PITCH_DEPTH,
            Digital.Display.Name.MOD_LFO_PITCH_DEPTH,
        ),
        SliderSpec(
            Digital.Param.LFO_FILTER_DEPTH,
            Digital.Display.Name.MOD_LFO_FILTER_DEPTH,
        ),
        SliderSpec(
            Digital.Param.LFO_AMP_DEPTH,
            Digital.Display.Name.MOD_LFO_AMP_DEPTH,
        ),
        SliderSpec(
            Digital.Param.LFO_PAN_DEPTH,
            Digital.Display.Name.MOD_LFO_PAN,
        ),
    ]
    SWITCH_SPECS = [
        SwitchSpec(
            Digital.Param.MOD_LFO_TEMPO_SYNC_SWITCH,
            Digital.Display.Name.MOD_LFO_TEMPO_SYNC_SWITCH,
            Digital.Display.Options.MOD_LFO_TEMPO_SYNC_SWITCH,
        ),
        SwitchSpec(
            Digital.Param.MOD_LFO_TEMPO_SYNC_NOTE,
            Digital.Display.Name.MOD_LFO_TEMPO_SYNC_NOTE,
            Digital.Display.Options.MOD_LFO_TEMPO_SYNC_NOTE,
        ),
    ]

    def __init__(
        self,
        on_parameter_changed: Callable,
        controls: dict,
        send_midi_parameter: Callable = None,
        icons_row_type: str = IconType.ADSR,
        analog: bool = False,
    ):
        """
        Initialize the DigitalModLFOSection

        :param on_parameter_changed: Callable
        :param controls: dict
        :param send_midi_parameter: Callable to send MIDI parameter updates
        """
        self._on_parameter_changed = on_parameter_changed
        self.controls = controls
        self.wave_shape_buttons = {}  # Dictionary to store Mod LFO shape buttons

        super().__init__(
            icons_row_type=icons_row_type, analog=analog, send_midi_parameter=send_midi_parameter
        )
        self.wave_shape_param: Literal[DigitalPartialParam.MOD_LFO_SHAPE] = (
            DigitalPartialParam.MOD_LFO_SHAPE
        )
        self.build_widgets()
        self.setup_ui()
