"""
Common Section
"""

from typing import Callable

from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.editor.helper import (
    create_group_with_layout,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class BaseCommonSection(SectionBaseWidget):
    """Common section for analog synth parameters."""

    from jdxi_editor.ui.editors.base.layout.spec import LayoutSpec

    SLIDER_GROUPS: LayoutSpec = None
    SWITCH_SPECS = []
    COMBO_BOXES = []

    def __init__(
        self,
        icons_row_type: str,
        analog: bool = False,
        midi_helper: MidiIOHelper = None,
        send_midi_parameter: Callable = None,
        controls: dict = None,
    ):
        """
        Initialize the AnalogCommonSection
        :param icons_row_type: str
        :param analog: bool
        """
        super().__init__(
            icons_row_type=icons_row_type,
            analog=analog,
            midi_helper=midi_helper,
            send_midi_parameter=send_midi_parameter,
        )

    def setup_ui(self):
        """
        setup ui
        """
        layout = self.get_layout()
        group, sub_layout = create_group_with_layout(label="Common")
        layout.addWidget(group)
        # --- Octave Switch row
        octave_shift_switch_row = create_layout_with_widgets([self.octave_shift_switch])
        sub_layout.addLayout(octave_shift_switch_row)

        # --- Legato Switch row
        legato_row = create_layout_with_widgets([self.legato_switch])
        sub_layout.addLayout(legato_row)

        # --- Portamento row
        portamento_switch_row = create_layout_with_widgets([self.portamento_switch])
        sub_layout.addLayout(portamento_switch_row)

        # --- Pitch Bend etc
        pitch_bend_row = create_layout_with_widgets(
            [self.pitch_bend_up, self.pitch_bend_down, self.portamento_time]
        )
        sub_layout.addLayout(pitch_bend_row)
        sub_layout.addStretch()

    def build_widgets(self):
        """Create Sliders"""
        #  --- Octave Switch
        (self.octave_shift_switch,) = self._build_combo_boxes(self.COMBO_BOXES)

        (self.legato_switch, self.portamento_switch) = self._build_switches(
            self.SWITCH_SPECS
        )

        if hasattr(self.spec, "controls"):
            (self.pitch_bend_up, self.pitch_bend_down, self.portamento_time) = (
                self._build_sliders(self.spec.controls)
            )
        else:
            (self.pitch_bend_up, self.pitch_bend_down, self.portamento_time) = (
                self._build_sliders(self.spec["controls"])
            )
