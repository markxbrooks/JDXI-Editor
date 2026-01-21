"""
MOD LFO section of the digital partial editor.
"""

from typing import Callable

from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.partial import (
    DigitalPartialParam,
)
from jdxi_editor.ui.editors.digital.partial.base_lfo import BaseLFOSection, SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.editor import IconType


class DigitalModLFOSection(BaseLFOSection):
    """MOD LFO section for the digital partial editor."""

    rate_tab_label = "Rate and Rate Ctrl"

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_combo_box: Callable,
        create_parameter_switch: Callable,
        on_parameter_changed: Callable,
        controls: dict,
        send_midi_parameter: Callable = None,
        icon_type: str = IconType.ADSR,
        analog: bool = False
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

        super().__init__(icon_type=icon_type,
                         analog=analog,
                         send_midi_parameter=send_midi_parameter)
        self.lfo_shape_param = DigitalPartialParam.MOD_LFO_SHAPE
        self.RATE_FADE_SLIDERS = [
            SliderSpec(DigitalPartialParam.MOD_LFO_RATE, DigitalDisplayName.MOD_LFO_RATE),
            SliderSpec(DigitalPartialParam.MOD_LFO_RATE_CTRL, DigitalDisplayName.MOD_LFO_RATE_CTRL),
        ]
        self.DEPTH_SLIDERS = [
            SliderSpec(DigitalPartialParam.LFO_PITCH_DEPTH, DigitalDisplayName.MOD_LFO_PITCH_DEPTH),
            SliderSpec(DigitalPartialParam.LFO_FILTER_DEPTH, DigitalDisplayName.MOD_LFO_FILTER_DEPTH),
            SliderSpec(DigitalPartialParam.LFO_AMP_DEPTH, DigitalDisplayName.MOD_LFO_AMP_DEPTH),
            SliderSpec(DigitalPartialParam.LFO_PAN_DEPTH, DigitalDisplayName.MOD_LFO_PAN),
        ]
        self.SWITCH_SPECS = [
            SwitchSpec(
                DigitalPartialParam.MOD_LFO_TEMPO_SYNC_SWITCH,
                DigitalDisplayName.MOD_LFO_TEMPO_SYNC_SWITCH,
                DigitalDisplayOptions.MOD_LFO_TEMPO_SYNC_SWITCH,
            ),
            SwitchSpec(
                DigitalPartialParam.MOD_LFO_TEMPO_SYNC_NOTE,
                DigitalDisplayName.MOD_LFO_TEMPO_SYNC_NOTE,
                DigitalDisplayOptions.MOD_LFO_TEMPO_SYNC_NOTE,
            ),
        ]
        self.build_widgets()
        self.setup_ui()
