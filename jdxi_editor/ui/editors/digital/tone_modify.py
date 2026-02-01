"""
Digital Tone Modify Section
"""

from typing import Callable, Dict, Optional, Union

from PySide6.QtWidgets import QWidget

from jdxi_editor.midi.data.lfo.lfo import LFOSyncNote
from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.style import JDXiUIStyle
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets, create_group_with_layout
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


class DigitalToneModifySection(SectionBaseWidget):
    SLIDER_GROUPS = {
        "interval_sens": [
            SliderSpec(
                Digital.ModifyParam.ATTACK_TIME_INTERVAL_SENS,
                Digital.ModifyDisplay.Names.ATTACK_TIME_INTERVAL_SENS,
                vertical=True,
            ),
            SliderSpec(
                Digital.ModifyParam.RELEASE_TIME_INTERVAL_SENS,
                Digital.ModifyDisplay.Names.RELEASE_TIME_INTERVAL_SENS,
                vertical=True,
            ),
            SliderSpec(
                Digital.ModifyParam.PORTAMENTO_TIME_INTERVAL_SENS,
                Digital.ModifyDisplay.Names.PORTAMENTO_TIME_INTERVAL_SENS,
                vertical=True,
            ),
        ],
    }
    COMBO_BOX_GROUPS = {
        "envelope_loop_mode": [
            ComboBoxSpec(
                Digital.ModifyParam.ENVELOPE_LOOP_MODE,
                Digital.ModifyDisplay.Names.ENVELOPE_LOOP_MODE,
                Digital.ModifyDisplay.Options.ENVELOPE_LOOP_MODE,
            ),
        ],
        "envelope_loop_sync_note": [
            ComboBoxSpec(
                Digital.ModifyParam.ENVELOPE_LOOP_SYNC_NOTE,
                Digital.ModifyDisplay.Names.ENVELOPE_LOOP_SYNC_NOTE,
                LFOSyncNote.get_all_display_names(),
            ),
        ],
    }
    SWITCH_GROUPS = {
        "chromatic_portamento": [
            SwitchSpec(
                Digital.ModifyParam.CHROMATIC_PORTAMENTO,
                Digital.ModifyDisplay.Names.CHROMATIC_PORTAMENTO,
                Digital.ModifyDisplay.Options.CHROMATIC_PORTAMENTO,
            ),
        ],
    }

    def __init__(
        self,
        controls: dict,
        send_midi_parameter: Optional[Callable] = None,
        midi_helper: Optional[MidiIOHelper] = None,
    ):
        """
        Initialize the DigitalToneModifySection

        :param controls: dict
        """

        super().__init__(
            icons_row_type=IconType.ADSR,
            analog=False,
            send_midi_parameter=send_midi_parameter,
            midi_helper=midi_helper,
        )
        self.controls: Dict[Union[DigitalPartialParam], QWidget] = controls or {}

        self.build_widgets()
        self.setup_ui()

    def _setup_ui(self):
        pass  # override so as to not provide a Tab Widget

    # ------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------

    def build_widgets(self) -> None:
        self.interval_sens_sliders = self._build_sliders(
            self.SLIDER_GROUPS["interval_sens"]
        )
        self.envelope_loop_mode_combo_boxes = self._build_combo_boxes(
            self.COMBO_BOX_GROUPS["envelope_loop_mode"]
        )
        self.envelope_loop_sync_note_combo_boxes = self._build_combo_boxes(
            self.COMBO_BOX_GROUPS["envelope_loop_sync_note"]
        )
        self.chromatic_portamento_switches = self._build_switches(
            self.SWITCH_GROUPS["chromatic_portamento"]
        )

    # ------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------

    def setup_ui(self) -> None:
        """setup ui"""
        layout = self.get_layout()
        group, sub_layout = create_group_with_layout(label="Tone Modify")
        layout.addWidget(group)
        group.setStyleSheet(JDXiUIStyle.ADSR)
        sub_layout.addLayout(create_layout_with_widgets(self.envelope_loop_mode_combo_boxes))
        sub_layout.addLayout(create_layout_with_widgets(self.envelope_loop_sync_note_combo_boxes))
        sub_layout.addLayout(create_layout_with_widgets(self.chromatic_portamento_switches))
        sub_layout.addLayout(
            create_layout_with_widgets(
                self.interval_sens_sliders
            )
        )
        sub_layout.addStretch()
        layout.addStretch()
