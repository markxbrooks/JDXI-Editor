"""
Digital Tone Modify Section
"""

from typing import Callable, Dict, Optional, Union

from PySide6.QtWidgets import QWidget

from jdxi_editor.midi.data.lfo.lfo import LFOSyncNote
from jdxi_editor.midi.data.parameter.digital import DigitalPartialParam
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.digital.tone_modify.spec import DigitalToneModifySpecs
from jdxi_editor.ui.editors.digital.tone_modify.widget import DigitalToneModifyWidgets
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec, SwitchSpec


class DigitalToneModifySection(SectionBaseWidget):
    """Digital Tone Modify"""

    def __init__(
        self,
        send_midi_parameter: Optional[Callable] = None,
        midi_helper: Optional[MidiIOHelper] = None,
    ):
        """
        Initialize the DigitalToneModifySection

        :param send_midi_parameter: Callable
        :param midi_helper: MidiIOHelper
        """
        self.spec: DigitalToneModifySpecs = self._build_layout_spec()
        super().__init__(
            icons_row_type=IconType.ADSR,
            analog=False,
            send_midi_parameter=send_midi_parameter,
            midi_helper=midi_helper,
        )
        self.widgets: DigitalToneModifyWidgets | None = None
        self.build_widgets()
        self.setup_ui()

    def _setup_ui(self):
        pass  # override to not provide a Tab Widget

    # ------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------

    def build_widgets(self) -> None:
        """Build all the necessary widgets for the digital common section."""
        self.widgets = DigitalToneModifyWidgets(
            interval_sens=self._build_sliders(self.spec.interval_sens),
            envelope_loop_mode=self._build_combo_boxes(self.spec.envelope_loop_mode),
            envelope_loop_sync_note=self._build_combo_boxes(
                self.spec.envelope_loop_sync_note
            ),
            chromatic_portamento=self._build_switches(self.spec.chromatic_portamento),
        )

    # ------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------

    def setup_ui(self) -> None:
        """setup ui"""
        widget_rows = [
            self.widgets.interval_sens,
            self.widgets.envelope_loop_mode,
            self.widgets.envelope_loop_sync_note,
            self.widgets.chromatic_portamento,
        ]
        self._add_group_with_widget_rows(label="Tone Modify", rows=widget_rows)

    def _build_layout_spec(self):
        """build layout spec"""
        interval_sens = [
            SliderSpec(
                Digital.ModifyParam.ATTACK_TIME_INTERVAL_SENS,
                Digital.ModifyParam.ATTACK_TIME_INTERVAL_SENS.display_name,
                vertical=True,
            ),
            SliderSpec(
                Digital.ModifyParam.RELEASE_TIME_INTERVAL_SENS,
                Digital.ModifyParam.RELEASE_TIME_INTERVAL_SENS.display_name,
                vertical=True,
            ),
            SliderSpec(
                Digital.ModifyParam.PORTAMENTO_TIME_INTERVAL_SENS,
                Digital.ModifyParam.PORTAMENTO_TIME_INTERVAL_SENS.display_name,
                vertical=True,
            ),
        ]
        envelope_loop_mode = [
            ComboBoxSpec(
                Digital.ModifyParam.ENVELOPE_LOOP_MODE,
                Digital.ModifyParam.ENVELOPE_LOOP_MODE.display_name,
                Digital.ModifyDisplay.Options.ENVELOPE_LOOP_MODE,
            ),
        ]
        envelope_loop_sync_note = [
            ComboBoxSpec(
                Digital.ModifyParam.ENVELOPE_LOOP_SYNC_NOTE,
                Digital.ModifyParam.ENVELOPE_LOOP_SYNC_NOTE.display_name,
                LFOSyncNote.get_all_display_names(),
            ),
        ]
        chromatic_portamento = [
            SwitchSpec(
                Digital.ModifyParam.CHROMATIC_PORTAMENTO,
                Digital.ModifyParam.CHROMATIC_PORTAMENTO.display_name,
                Digital.ModifyDisplay.Options.CHROMATIC_PORTAMENTO,
            ),
        ]
        return DigitalToneModifySpecs(
            interval_sens=interval_sens,
            envelope_loop_mode=envelope_loop_mode,
            envelope_loop_sync_note=envelope_loop_sync_note,
            chromatic_portamento=chromatic_portamento,
        )
