"""
LFO section of the digital partial editor.
"""

from typing import Callable

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.partial import (
    DigitalPartialParam,
)
from jdxi_editor.ui.editors.digital.partial.lfo.base import BaseLFOSection
from jdxi_editor.ui.editors.widget_specs import SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.editor import IconType


class DigitalLFOSection(BaseLFOSection):
    """LFO section for the digital partial editor."""

    rate_tab_label = "Rate and Fade"

    DEPTH_SLIDERS = [
        SliderSpec(
            JDXi.Midi.Digital.Param.LFO_PITCH_DEPTH, JDXi.Midi.Digital.Display.Name.LFO_PITCH_DEPTH
        ),
        SliderSpec(
            JDXi.Midi.Digital.Param.LFO_FILTER_DEPTH, JDXi.Midi.Digital.Display.Name.LFO_FILTER_DEPTH
        ),
        SliderSpec(JDXi.Midi.Digital.Param.LFO_AMP_DEPTH, JDXi.Midi.Digital.Display.Name.LFO_AMP_DEPTH),
        SliderSpec(JDXi.Midi.Digital.Param.LFO_PAN_DEPTH, DigitalDisplayName.LFO_PAN_DEPTH),
    ]
    SWITCH_SPECS = [
        SwitchSpec(
            JDXi.Midi.Digital.Param.LFO_TEMPO_SYNC_SWITCH,
            JDXi.Midi.Digital.Display.Name.LFO_TEMPO_SYNC_SWITCH,
            JDXi.Midi.Digital.Display.Options.LFO_TEMPO_SYNC_SWITCH,
        ),
        SwitchSpec(
            JDXi.Midi.Digital.Param.LFO_TEMPO_SYNC_NOTE,
            JDXi.Midi.Digital.Display.Name.LFO_TEMPO_SYNC_NOTE,
            JDXi.Midi.Digital.Display.Options.LFO_TEMPO_SYNC_NOTE,
        ),
        SwitchSpec(
            JDXi.Midi.Digital.Param.LFO_KEY_TRIGGER,
            JDXi.Midi.Digital.Display.Name.LFO_KEY_TRIGGER,
            JDXi.Midi.Digital.Display.Options.LFO_KEY_TRIGGER,
        ),
    ]
    RATE_FADE_SLIDERS = [
        SliderSpec(JDXi.Midi.Digital.Param.LFO_RATE, DigitalDisplayName.LFO_RATE),
        SliderSpec(JDXi.Midi.Digital.Param.LFO_FADE_TIME, JDXi.Midi.Digital.Display.Name.LFO_FADE_TIME),
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
        self.lfo_shape_param = JDXi.Midi.Digital.Param.LFO_SHAPE
        self.build_widgets()
        self.setup_ui()
