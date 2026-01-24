"""
Digital Tone Modify Section
"""

from typing import Callable

from jdxi_editor.midi.data.lfo.lfo import LFOSyncNote
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.editors.widget_specs import SliderSpec
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class DigitalToneModifySection(SectionBaseWidget):
    SLIDER_GROUPS = {
        "interval_sens": [
            SliderSpec(Digital.ModifyParam.ATTACK_TIME_INTERVAL_SENS,
                       Digital.ModifyDisplay.Names.ATTACK_TIME_INTERVAL_SENS,
                       vertical=True),
            SliderSpec(Digital.ModifyParam.RELEASE_TIME_INTERVAL_SENS,
                       Digital.ModifyDisplay.Names.RELEASE_TIME_INTERVAL_SENS,
                       vertical=True),
            SliderSpec(Digital.ModifyParam.PORTAMENTO_TIME_INTERVAL_SENS,
                       Digital.ModifyDisplay.Names.PORTAMENTO_TIME_INTERVAL_SENS,
                       vertical=True),
        ]
    }

    def __init__(
            self,
            create_parameter_slider: Callable,
            create_parameter_combo_box: Callable,
            create_parameter_switch: Callable,
            controls: dict,
    ):
        """
            Initialize the DigitalToneModifySection

            :param create_parameter_slider: Callable
            :param create_parameter_combo_box: Callable
            :param create_parameter_switch: Callable
            :param controls: dict
            """
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self._create_parameter_switch = create_parameter_switch
        self.controls = controls

        super().__init__(icons_row_type=IconType.ADSR, analog=False)

        self._build_widgets()
        self.setup_ui()

    # ------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------

    def _build_widgets(self) -> None:
        self.interval_sens_sliders = self._build_sliders(
            self.SLIDER_GROUPS["interval_sens"]
        )

        self.envelope_loop_mode = self._create_parameter_combo_box(
            Digital.ModifyParam.ENVELOPE_LOOP_MODE,
            Digital.ModifyDisplay.Names.ENVELOPE_LOOP_MODE,
            Digital.ModifyDisplay.Options.ENVELOPE_LOOP_MODE,
        )

        self.envelope_loop_sync_note = self._create_parameter_combo_box(
            Digital.ModifyParam.ENVELOPE_LOOP_SYNC_NOTE,
            Digital.ModifyDisplay.Names.ENVELOPE_LOOP_SYNC_NOTE,
            LFOSyncNote.get_all_display_names(),
        )

        self.chromatic_portamento = self._create_parameter_switch(
            Digital.ModifyParam.CHROMATIC_PORTAMENTO,
            Digital.ModifyDisplay.Names.CHROMATIC_PORTAMENTO,
            Digital.ModifyDisplay.Options.CHROMATIC_PORTAMENTO,
        )

    # ------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------

    def setup_ui(self) -> None:
        layout = self.get_layout()

        self._add_centered_row(*self.interval_sens_sliders)
        self._add_centered_row(self.envelope_loop_mode)
        self._add_centered_row(self.envelope_loop_sync_note)
        self._add_centered_row(self.chromatic_portamento)

        layout.addStretch()
