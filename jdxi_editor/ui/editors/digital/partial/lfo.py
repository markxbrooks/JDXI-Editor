"""
LFO section of the digital partial editor.
"""

from typing import Callable

from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.partial import (
    DigitalPartialParam,
)
from jdxi_editor.ui.editors.digital.partial.base_lfo import BaseLFOSection
from jdxi_editor.ui.editors.widget_specs import SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.editor import IconType


class DigitalLFOSection(BaseLFOSection):
    """LFO section for the digital partial editor."""

    rate_tab_label = "Rate and Fade"

    DEPTH_SLIDERS = [
        SliderSpec(
            DigitalPartialParam.LFO_PITCH_DEPTH, DigitalDisplayName.LFO_PITCH_DEPTH
        ),
        SliderSpec(
            DigitalPartialParam.LFO_FILTER_DEPTH, DigitalDisplayName.LFO_FILTER_DEPTH
        ),
        SliderSpec(DigitalPartialParam.LFO_AMP_DEPTH, DigitalDisplayName.LFO_AMP_DEPTH),
        SliderSpec(DigitalPartialParam.LFO_PAN_DEPTH, DigitalDisplayName.LFO_PAN_DEPTH),
    ]
    SWITCH_SPECS = [
        SwitchSpec(
            DigitalPartialParam.LFO_TEMPO_SYNC_SWITCH,
            DigitalDisplayName.LFO_TEMPO_SYNC_SWITCH,
            DigitalDisplayOptions.LFO_TEMPO_SYNC_SWITCH,
        ),
        SwitchSpec(
            DigitalPartialParam.LFO_TEMPO_SYNC_NOTE,
            DigitalDisplayName.LFO_TEMPO_SYNC_NOTE,
            DigitalDisplayOptions.LFO_TEMPO_SYNC_NOTE,
        ),
        SwitchSpec(
            DigitalPartialParam.LFO_KEY_TRIGGER,
            DigitalDisplayName.LFO_KEY_TRIGGER,
            DigitalDisplayOptions.LFO_KEY_TRIGGER,
        ),
    ]
    RATE_FADE_SLIDERS = [
        SliderSpec(DigitalPartialParam.LFO_RATE, DigitalDisplayName.LFO_RATE),
        SliderSpec(DigitalPartialParam.LFO_FADE_TIME, DigitalDisplayName.LFO_FADE_TIME),
    ]

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        controls: dict,
        send_midi_parameter: Callable = None,
        icon_type=IconType.ADSR,
        analog=False,
    ):
        """
        Initialize the DigitalLFOSection

        :param create_parameter_slider: Callable
        :param create_parameter_switch: Callable
        :param create_parameter_combo_box: Callable
        :param controls: dict
        :param send_midi_parameter: Callable to send MIDI parameter updates
        """
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self.controls = controls
        self.lfo_shape_buttons = {}  # Dictionary to store LFO shape buttons

        super().__init__(
            icon_type=icon_type, analog=analog, send_midi_parameter=send_midi_parameter
        )
        self.send_midi_parameter = send_midi_parameter
        self.lfo_shape_param = DigitalPartialParam.LFO_SHAPE
        self.build_widgets()
        self.setup_ui()
