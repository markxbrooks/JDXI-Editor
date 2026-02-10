"""
Common Section
"""

from typing import Callable

from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.base.common.section import BaseCommonSection
from jdxi_editor.ui.editors.base.layout.spec import LayoutSpec
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


class AnalogCommonSection(BaseCommonSection):
    """Common section for analog synth parameters."""

    SYNTH_SPEC = Analog

    def __init__(
        self,
        midi_helper: MidiIOHelper = None,
        send_midi_parameter: Callable = None,
    ):
        """
        Initialize the AnalogCommonSection
        :param midi_helper: MidiIOHelper
        :param send_midi_parameter: Callable
        """
        self.spec: LayoutSpec = self._build_layout_spec()
        self.SWITCH_SPECS = self.spec.switches
        self.COMBO_BOXES = self.spec.combos
        super().__init__(
            icons_row_type=IconType.GENERIC,
            analog=True,
            midi_helper=midi_helper,
            send_midi_parameter=send_midi_parameter,
        )
        self.build_widgets()
        self.setup_ui()

    def _build_layout_spec(self) -> LayoutSpec:
        """build Analog Oscillator Layout Spec"""
        S = self.SYNTH_SPEC
        controls = [
            SliderSpec(
                S.Param.PITCH_BEND_UP,
                S.Param.PITCH_BEND_UP.display_name,
                vertical=True,
            ),
            SliderSpec(
                S.Param.PITCH_BEND_DOWN,
                S.Param.PITCH_BEND_DOWN.display_name,
                vertical=True,
            ),
            SliderSpec(
                S.Param.PORTAMENTO_TIME,
                S.Param.PORTAMENTO_TIME.display_name,
                vertical=True,
            ),
        ]
        switches = [
            SwitchSpec(
                S.Param.LEGATO_SWITCH,
                S.Param.LEGATO_SWITCH.display_name,
                S.Display.Options.LEGATO_SWITCH,
            ),
            SwitchSpec(
                S.Param.PORTAMENTO_SWITCH,
                S.Param.PORTAMENTO_SWITCH.display_name,
                S.Display.Options.PORTAMENTO_SWITCH,
            ),
        ]
        combos = [
            ComboBoxSpec(
                S.Param.OCTAVE_SHIFT,
                S.Param.OCTAVE_SHIFT.display_name,
                S.Display.Options.OCTAVE_SHIFT,
                S.Display.Values.OCTAVE_SHIFT,
            )
        ]
        return LayoutSpec(controls=controls, switches=switches, combos=combos)
