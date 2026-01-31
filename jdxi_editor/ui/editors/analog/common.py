"""
Common Section
"""

from typing import Dict, Union

from PySide6.QtWidgets import QWidget

from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


class AnalogCommonSection(SectionBaseWidget):
    """Common section for analog synth parameters."""

    SLIDER_GROUPS = {
        "all": [
            SliderSpec(Analog.Param.PITCH_BEND_UP, Analog.Display.Name.PITCH_BEND_UP, vertical=True),
            SliderSpec(Analog.Param.PITCH_BEND_DOWN,
                       Analog.Display.Name.PITCH_BEND_DOWN,
                       vertical=True),
            SliderSpec(Analog.Param.PORTAMENTO_TIME,
                       Analog.Display.Name.PORTAMENTO_TIME,
                       vertical=True)
        ]
    }
    SWITCH_SPECS = [
        SwitchSpec(
            Analog.Param.LEGATO_SWITCH,
            Analog.Display.Name.LEGATO_SWITCH,
            Analog.Display.Options.LEGATO_SWITCH
        ),
        SwitchSpec(
            Analog.Param.PORTAMENTO_SWITCH,
            Analog.Display.Name.PORTAMENTO_SWITCH,
            Analog.Display.Options.PORTAMENTO_SWITCH,
        ),
    ]
    COMBO_BOXES = [
        ComboBoxSpec(Analog.Param.OCTAVE_SHIFT,
                     Analog.Display.Name.OCTAVE_SHIFT,
                     Analog.Display.Options.OCTAVE_SHIFT,
                     Analog.Display.Values.OCTAVE_SHIFT, )
    ]

    def __init__(
            self,
            controls: dict,
    ):
        """
        Initialize the AnalogCommonSection
        :param controls: dict
        """

        super().__init__(icons_row_type=IconType.GENERIC, analog=True)
        self.controls: Dict[Union[Analog.Param], QWidget] = controls or {}
        self.build_widgets()
        self.setup_ui()

    def setup_ui(self):
        """
        setup ui
        """
        layout = self.get_layout()

        # --- Octave Switch row
        octave_shift_switch_row = create_layout_with_widgets([self.octave_shift_switch])
        layout.addLayout(octave_shift_switch_row)

        # --- Legato Switch row
        legato_row = create_layout_with_widgets([self.legato_switch])
        layout.addLayout(legato_row)

        # --- Portamento row
        portamento_switch_row = create_layout_with_widgets([self.portamento_switch])
        layout.addLayout(portamento_switch_row)

        # --- Pitch Bend etc
        pitch_bend_row = create_layout_with_widgets(
            [self.pitch_bend_up, self.pitch_bend_down, self.portamento_time]
        )
        layout.addLayout(pitch_bend_row)
        layout.addStretch()

    def build_widgets(self):
        """Create Sliders"""
        #  --- Octave Switch
        (self.octave_shift_switch,) = self._build_combo_boxes(self.COMBO_BOXES)

        (self.legato_switch, self.portamento_switch) = self._build_switches(self.SWITCH_SPECS)

        (self.pitch_bend_up, self.pitch_bend_down, self.portamento_time) = self._build_sliders(self.SLIDER_GROUPS["all"])
