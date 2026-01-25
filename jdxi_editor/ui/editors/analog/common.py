"""
Common Section
"""

from typing import Callable, Union, Dict

from PySide6.QtWidgets import QWidget

from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.midi.data.parameter.analog.address import AnalogParam
from jdxi_editor.midi.data.parameter.analog.name import AnalogDisplayName
from jdxi_editor.midi.data.parameter.analog.option import AnalogDisplayOptions
from jdxi_editor.midi.data.parameter.analog.values import AnalogDisplayValues
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class AnalogCommonSection(SectionBaseWidget):
    """Common section for analog synth parameters."""

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
        self.init_ui()

    def init_ui(self):
        """
        init ui
        """
        main_rows_vlayout = self.get_layout()

        self.create_sliders()

        # --- Octave Switch
        octave_shift_switch_row = create_layout_with_widgets([self.octave_shift_switch])
        main_rows_vlayout.addLayout(octave_shift_switch_row)

        # --- Legato Switch
        legato_row = create_layout_with_widgets([self.legato_switch])
        main_rows_vlayout.addLayout(legato_row)

        # --- Portamento Switch
        portamento_switch_row = create_layout_with_widgets([self.portamento_switch])
        main_rows_vlayout.addLayout(portamento_switch_row)

        # --- Pitch Bend
        pitch_bend_row = create_layout_with_widgets(
            [self.pitch_bend_up, self.pitch_bend_down, self.portamento_time]
        )
        main_rows_vlayout.addLayout(pitch_bend_row)
        main_rows_vlayout.addStretch()

    def create_sliders(self):
        """Create Sliders"""
        #  --- Octave Switch
        self.octave_shift_switch = self._create_parameter_combo_box(
            Analog.Param.OCTAVE_SHIFT,
            Analog.Display.Name.OCTAVE_SHIFT,
            Analog.Display.Options.OCTAVE_SHIFT,
            Analog.Display.Values.OCTAVE_SHIFT,
        )
        self.legato_switch = self._create_parameter_switch(
            Analog.Param.LEGATO_SWITCH,
            Analog.Display.Name.LEGATO_SWITCH,
            Analog.Display.Options.LEGATO_SWITCH,
        )
        # --- Portamento Switch
        self.portamento_switch = self._create_parameter_switch(
            Analog.Param.PORTAMENTO_SWITCH,
            Analog.Display.Name.PORTAMENTO_SWITCH,
            Analog.Display.Options.PORTAMENTO_SWITCH,
        )

        self.pitch_bend_up = self._create_parameter_slider(
            Analog.Param.PITCH_BEND_UP, Analog.Display.Name.PITCH_BEND_UP, vertical=True
        )
        self.pitch_bend_down = self._create_parameter_slider(
            Analog.Param.PITCH_BEND_DOWN,
            Analog.Display.Name.PITCH_BEND_DOWN,
            vertical=True,
        )

        # --- Portamento Time
        self.portamento_time = self._create_parameter_slider(
            Analog.Param.PORTAMENTO_TIME,
            Analog.Display.Name.PORTAMENTO_TIME,
            vertical=True,
        )
