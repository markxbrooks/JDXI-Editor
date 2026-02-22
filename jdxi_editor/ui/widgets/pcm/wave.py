"""
PCM Wave Widget
"""

from typing import Callable

from PySide6.QtWidgets import QWidget
from decologr import Decologr as log
from jdxi_editor.midi.data.parameter.digital.spec import DigitalGroupBox
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.midi.data.pcm.waves import PCM_WAVES_CATEGORIZED
from jdxi_editor.ui.widgets.combo_box import SearchableFilterableComboBox
from jdxi_editor.ui.widgets.editor.helper import (
    create_centered_layout_with_widgets,
    create_group_from_definition,
)


class PCMWaveWidget(QWidget):

    def __init__(
        self,
        groupbox_spec: type[DigitalGroupBox],
        create_parameter_combo_box: Callable,
        send_param: Callable,
    ):
        super().__init__()
        self._send_param = send_param
        self.pcm_wave_number: QWidget | None = None
        self.pcm_wave_gain: QWidget | None = None
        self.groupbox_spec = groupbox_spec
        self._create_parameter_combo_box = create_parameter_combo_box
        self.build_widgets()
        self.setup_ui()

    def build_widgets(self):
        """Create PCM Wave controls (Gain and Number) after parent builds widgets
        These will be added to a separate "PCM" tab, not the Controls tab
        PCM Wave Gain: combo box with -6, 0, +6, +12 dB options"""
        self.pcm_wave_gain = self._create_parameter_combo_box(
            Digital.Param.PCM_WAVE_GAIN,
            Digital.Display.Name.PCM_WAVE_GAIN,
            options=Digital.Display.Options.PCM_WAVE_GAIN,
            values=Digital.Display.Values.PCM_WAVE_GAIN,  # MIDI values for -6, 0, +6, +12 dB
        )
        # --- Don't add to control_widgets - it will be in the PCM tab

        # --- Build options, values, and categories from PCM_WAVES_CATEGORIZED
        pcm_options = [
            f"{w['Wave Number']:03d}: {w['Wave Name']}" for w in PCM_WAVES_CATEGORIZED
        ]
        pcm_values = [w["Wave Number"] for w in PCM_WAVES_CATEGORIZED]
        pcm_categories = sorted(
            set(w["Category"] for w in PCM_WAVES_CATEGORIZED if w["Category"] != "None")
        )

        # --- Category filter function
        def pcm_category_filter(wave_name: str, category: str) -> bool:
            """Check if a PCM wave matches a category."""
            if not category:
                return True
            # --- Find the wave in PCM_WAVES_CATEGORIZED and check its category
            wave_num_str = wave_name.split(":")[0].strip()
            try:
                wave_num = int(wave_num_str)
                for w in PCM_WAVES_CATEGORIZED:
                    if w["Wave Number"] == wave_num:
                        return w["Category"] == category
            except ValueError:
                pass
            return False

        self.pcm_wave_number = SearchableFilterableComboBox(
            label=Digital.Display.Name.PCM_WAVE_NUMBER,
            options=pcm_options,
            values=pcm_values,
            categories=pcm_categories,
            category_filter_func=pcm_category_filter,
            show_label=True,
            show_search=True,
            show_category=True,
            show_bank=False,
            search_placeholder="Search PCM waves...",
            category_label="Category:",
        )
        # --- Connect to MIDI parameter sending
        if self._send_param:
            self.pcm_wave_number.valueChanged.connect(
                lambda v: self._send_param(Digital.Param.PCM_WAVE_NUMBER, v)
            )
        # --- Don't add to control_widgets - it will be in the PCM tab

    def setup_ui(self):
        try:
            centered_layout = create_centered_layout_with_widgets(
                widgets=[self.pcm_wave_gain, self.pcm_wave_number]
            )
            self.setLayout(centered_layout)
            pcm_group = create_group_from_definition(
                key=self.groupbox_spec.PCM_WAVE,
                layout_or_widget=self,
                set_attr=self,
            )
        except Exception as ex:
            log.error(f"Error {ex} occurred")
