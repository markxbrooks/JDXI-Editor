"""
LFO section of the digital partial editor.
"""

from typing import Callable, Literal

from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.editors.base.lfo import BaseLFOSection
from jdxi_editor.ui.widgets.spec import SliderSpec, SwitchSpec
from jdxi_editor.ui.widgets.editor import IconType


class DigitalLFOSection(BaseLFOSection):
    """LFO section for the digital partial editor."""

    rate_tab_label = "Rate and Fade"

    DEPTH_SLIDERS = [
        SliderSpec(
            Digital.Param.LFO_PITCH_DEPTH,
            Digital.Display.Name.LFO_PITCH_DEPTH,
        ),
        SliderSpec(
            Digital.Param.LFO_FILTER_DEPTH,
            Digital.Display.Name.LFO_FILTER_DEPTH,
        ),
        SliderSpec(
            Digital.Param.LFO_AMP_DEPTH,
            Digital.Display.Name.LFO_AMP_DEPTH,
        ),
        SliderSpec(
            Digital.Param.LFO_PAN_DEPTH,
            Digital.Display.Name.LFO_PAN_DEPTH,
        ),
    ]
    SWITCH_SPECS = [
        SwitchSpec(
            Digital.Param.LFO_TEMPO_SYNC_SWITCH,
            Digital.Display.Name.LFO_TEMPO_SYNC_SWITCH,
            Digital.Display.Options.LFO_TEMPO_SYNC_SWITCH,
        ),
        SwitchSpec(
            Digital.Param.LFO_TEMPO_SYNC_NOTE,
            Digital.Display.Name.LFO_TEMPO_SYNC_NOTE,
            Digital.Display.Options.LFO_TEMPO_SYNC_NOTE,
        ),
        SwitchSpec(
            Digital.Param.LFO_KEY_TRIGGER,
            Digital.Display.Name.LFO_KEY_TRIGGER,
            Digital.Display.Options.LFO_KEY_TRIGGER,
        ),
    ]
    RATE_FADE_SLIDERS = [
        SliderSpec(
            Digital.Param.LFO_RATE, Digital.Display.Name.LFO_RATE
        ),
        SliderSpec(
            Digital.Param.LFO_FADE_TIME,
            Digital.Display.Name.LFO_FADE_TIME,
        ),
    ]

    def __init__(
        self,
        controls: dict,
        send_midi_parameter: Callable = None,
        icons_row_type=IconType.ADSR,
        analog=False,
    ):
        """
        Initialize the DigitalLFOSection

        :param controls: dict
        :param send_midi_parameter: Callable to send MIDI parameter updates
        """
        self.controls = controls

        super().__init__(
            icons_row_type=icons_row_type, analog=analog, send_midi_parameter=send_midi_parameter
        )
        self.send_midi_parameter = send_midi_parameter
        self.wave_shape_param: Literal[Digital.Param.LFO_SHAPE] = (
            Digital.Param.LFO_SHAPE
        )
        self.build_widgets()
        self.setup_ui()
