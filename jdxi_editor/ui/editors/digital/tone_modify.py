"""
Digital Tone Modify Section
"""

from typing import Callable, Dict, Optional, Union
from dataclasses import dataclass
from PySide6.QtWidgets import QWidget

from jdxi_editor.midi.data.lfo.lfo import LFOSyncNote
from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


@dataclass
class   DigitalToneModifyWidgets:
    """Digital Tone Modify"""
    interval_sens: list[QWidget] = None
    envelope_loop_mode: list[QWidget] = None
    envelope_loop_sync_note: list[QWidget] = None
    chromatic_portamento: list[QWidget] = None
    
        
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
        self.widgets: dict = {}
        self.build_widgets()
        self.setup_ui()

    def _setup_ui(self):
        pass  # override to not provide a Tab Widget

    # ------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------

    def build_widgets(self) -> None:
        """Build all the necessary widgets for the digital common section."""
        self.widgets = DigitalToneModifyWidgets(interval_sens_sliders=self._build_sliders(self.SLIDER_GROUPS["interval_sens"]),
            envelope_loop_mode_combo_boxes=self._build_combo_boxes(self.COMBO_BOX_GROUPS["envelope_loop_mode"]),
            envelope_loop_sync_note_combo_boxes=self._build_combo_boxes(self.COMBO_BOX_GROUPS["envelope_loop_sync_note"]),
            chromatic_portamento_switches=self._build_switches(self.SWITCH_GROUPS["chromatic_portamento"]),
        }

    # ------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------

    def setup_ui(self) -> None:
        """setup ui"""
        widget_rows = [
            self.widgets.interval_sens_sliders,
            self.widgets.envelope_loop_mode_combo_boxes,
            self.widgets.envelope_loop_sync_note_combo_boxes,
            self.widgets["chromatic_portamento_switches,
        ]
        self._add_group_with_widget_rows(label="Tone Modify", rows=widget_rows)
