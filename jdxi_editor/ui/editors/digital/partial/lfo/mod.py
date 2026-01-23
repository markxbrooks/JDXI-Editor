"""
MOD LFO section of the digital partial editor.
"""

from typing import Callable

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
from jdxi_editor.ui.editors.digital.partial.lfo.base import BaseLFOSection
from jdxi_editor.ui.editors.widget_specs import SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.editor import IconType


class DigitalModLFOSection(BaseLFOSection):
    """MOD LFO section for the digital partial editor."""

    rate_tab_label = "Rate and Rate Ctrl"

    RATE_FADE_SLIDERS = [
        SliderSpec(JDXi.Midi.Digital.Param.MOD_LFO_RATE, JDXi.Midi.Digital.Display.Name.MOD_LFO_RATE),
        SliderSpec(
            JDXi.Midi.Digital.Param.MOD_LFO_RATE_CTRL, JDXi.Midi.Digital.Display.Name.MOD_LFO_RATE_CTRL
        ),
    ]
    DEPTH_SLIDERS = [
        SliderSpec(
            JDXi.Midi.Digital.Param.LFO_PITCH_DEPTH, JDXi.Midi.Digital.Display.Name.MOD_LFO_PITCH_DEPTH
        ),
        SliderSpec(
            JDXi.Midi.Digital.Param.LFO_FILTER_DEPTH,
            JDXi.Midi.Digital.Display.Name.MOD_LFO_FILTER_DEPTH,
        ),
        SliderSpec(
            JDXi.Midi.Digital.Param.LFO_AMP_DEPTH, JDXi.Midi.Digital.Display.Name.MOD_LFO_AMP_DEPTH
        ),
        SliderSpec(JDXi.Midi.Digital.Param.LFO_PAN_DEPTH, JDXi.Midi.Digital.Display.Name.MOD_LFO_PAN),
    ]
    SWITCH_SPECS = [
        SwitchSpec(
            JDXi.Midi.Digital.Param.MOD_LFO_TEMPO_SYNC_SWITCH,
            JDXi.Midi.Digital.Display.Name.MOD_LFO_TEMPO_SYNC_SWITCH,
            JDXi.Midi.Digital.Display.Options.MOD_LFO_TEMPO_SYNC_SWITCH,
        ),
        SwitchSpec(
            JDXi.Midi.Digital.Param.MOD_LFO_TEMPO_SYNC_NOTE,
            JDXi.Midi.Digital.Display.Name.MOD_LFO_TEMPO_SYNC_NOTE,
            JDXi.Midi.Digital.Display.Options.MOD_LFO_TEMPO_SYNC_NOTE,
        ),
    ]

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_combo_box: Callable,
        create_parameter_switch: Callable,
        on_parameter_changed: Callable,
        controls: dict,
        send_midi_parameter: Callable = None,
        icon_type: str = IconType.ADSR,
        analog: bool = False,
    ):
        """
        Initialize the DigitalModLFOSection

        :param create_parameter_slider: Callable
        :param create_parameter_combo_box: Callable
        :param on_parameter_changed: Callable
        :param controls: dict
        :param send_midi_parameter: Callable to send MIDI parameter updates
        """
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self._create_parameter_switch = create_parameter_switch
        self._on_parameter_changed = on_parameter_changed
        self.controls = controls
        self.lfo_shape_buttons = {}  # Dictionary to store Mod LFO shape buttons

        super().__init__(
            icon_type=icon_type, analog=analog, send_midi_parameter=send_midi_parameter
        )
        self.lfo_shape_param = DigitalPartialParam.MOD_LFO_SHAPE
        self.build_widgets()
        self.setup_ui()
