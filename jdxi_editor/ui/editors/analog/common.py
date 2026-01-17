"""
Common Section
"""

from typing import Callable

from jdxi_editor.midi.data.parameter.analog import AnalogParam
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class AnalogCommonSection(SectionBaseWidget):
    """Common section for analog synth parameters."""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        controls: dict,
    ):
        """
        Initialize the AnalogCommonSection

        :param create_parameter_slider: Callable
        :param create_parameter_switch: Callable
        :param create_parameter_combo_box: Callable
        :param controls: dict
        """
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self.controls = controls

        super().__init__(icon_type=IconType.GENERIC, analog=True)
        self.init_ui()

    def init_ui(self):
        """
        init ui
        """
        main_rows_vlayout = self.get_layout()

        # Mono Switch
        self.octave_shift_switch = self._create_parameter_combo_box(
            AnalogParam.OCTAVE_SHIFT,
            "Octave shift",
            ["-3", "-2", "-1", "0", "+1", "+2", "+3"],
            [61, 62, 63, 64, 65, 66, 67],
        )
        octave_shift_switch_row = create_layout_with_widgets([self.octave_shift_switch])
        main_rows_vlayout.addLayout(octave_shift_switch_row)

        self.legato_switch = self._create_parameter_switch(
            AnalogParam.LEGATO_SWITCH, "Legato", ["OFF", "ON"]
        )

        legato_row = create_layout_with_widgets([self.legato_switch])
        main_rows_vlayout.addLayout(legato_row)

        # Portamento Switch
        self.portamento_switch = self._create_parameter_switch(
            AnalogParam.PORTAMENTO_SWITCH, "Portamento", ["OFF", "ON"]
        )
        portamento_switch_row = create_layout_with_widgets([self.portamento_switch])
        main_rows_vlayout.addLayout(portamento_switch_row)

        self.pitch_bend_up = self._create_parameter_slider(
            AnalogParam.PITCH_BEND_UP, "Pitch Bend Up", vertical=True
        )
        self.pitch_bend_down = self._create_parameter_slider(
            AnalogParam.PITCH_BEND_DOWN, "Pitch Bend Down", vertical=True
        )

        # Portamento Time
        self.portamento_time = self._create_parameter_slider(
            AnalogParam.PORTAMENTO_TIME, "Portamento Time", vertical=True
        )
        # Pitch Bend
        pitch_bend_row = create_layout_with_widgets(
            [self.pitch_bend_up, self.pitch_bend_down, self.portamento_time]
        )
        main_rows_vlayout.addLayout(pitch_bend_row)
        main_rows_vlayout.addStretch()
