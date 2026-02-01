"""
Common Section
"""

from typing import Callable

from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.base.common import BaseCommonSection
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


class AnalogCommonSection(BaseCommonSection):
    """Common section for analog synth parameters."""

    SLIDER_GROUPS = {
        "all": [
            SliderSpec(
                Analog.Param.PITCH_BEND_UP,
                Analog.Display.Name.PITCH_BEND_UP,
                vertical=True,
            ),
            SliderSpec(
                Analog.Param.PITCH_BEND_DOWN,
                Analog.Display.Name.PITCH_BEND_DOWN,
                vertical=True,
            ),
            SliderSpec(
                Analog.Param.PORTAMENTO_TIME,
                Analog.Display.Name.PORTAMENTO_TIME,
                vertical=True,
            ),
        ]
    }
    SWITCH_SPECS = [
        SwitchSpec(
            Analog.Param.LEGATO_SWITCH,
            Analog.Display.Name.LEGATO_SWITCH,
            Analog.Display.Options.LEGATO_SWITCH,
        ),
        SwitchSpec(
            Analog.Param.PORTAMENTO_SWITCH,
            Analog.Display.Name.PORTAMENTO_SWITCH,
            Analog.Display.Options.PORTAMENTO_SWITCH,
        ),
    ]
    COMBO_BOXES = [
        ComboBoxSpec(
            Analog.Param.OCTAVE_SHIFT,
            Analog.Display.Name.OCTAVE_SHIFT,
            Analog.Display.Options.OCTAVE_SHIFT,
            Analog.Display.Values.OCTAVE_SHIFT,
        )
    ]

    def __init__(
        self,
        controls: dict,
        midi_helper: MidiIOHelper = None,
        send_midi_parameter: Callable = None,
    ):
        """
        Initialize the AnalogCommonSection
        :param controls: dict
        """
        super().__init__(
            icons_row_type=IconType.GENERIC,
            analog=True,
            midi_helper=midi_helper,
            send_midi_parameter=send_midi_parameter,
            controls=controls,
        )
        self.build_widgets()
        self.setup_ui()
