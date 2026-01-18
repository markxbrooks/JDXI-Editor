"""
Drum partial editor for editing drum kit parameters.

The `DrumPartialEditor` class allows users to modify various parameters related to
drum sounds, including pitch, output, TVF (Time Variant Filter), pitch envelope,
WMT (Wave Modulation Time), and TVA (Time Variant Amplitude) settings.
"""

from typing import Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.jdxi import JDXi
from jdxi_editor.jdxi.synth.type import JDXiSynth
from jdxi_editor.midi.data.address.address import AddressOffsetProgramLMB
from jdxi_editor.midi.data.parameter.drum.addresses import DRUM_GROUP_MAP
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.drum.partial.output import DrumOutputSection
from jdxi_editor.ui.editors.drum.partial.partial import DrumPartialSection
from jdxi_editor.ui.editors.drum.partial.pitch_env import DrumPitchEnvSection
from jdxi_editor.ui.editors.drum.partial.tva import DrumTVASection
from jdxi_editor.ui.editors.drum.partial.tvf import DrumTVFSection
from jdxi_editor.ui.editors.drum.partial.wmt import DrumWMTSection
from jdxi_editor.ui.editors.synth.partial import PartialEditor
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon


class DrumPartialEditor(PartialEditor):
    """Editor for address single partial"""

    def __init__(
        self,
        midi_helper: Optional[MidiIOHelper] = None,
        partial_number: int = 0,
        partial_name: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.partial_number = partial_number  # This is now the numerical index
        self.partial_name = partial_name  # This is now the numerical index
        self.partial_address_default = AddressOffsetProgramLMB.DRUM_DEFAULT_PARTIAL
        self.partial_address_map = DRUM_GROUP_MAP
        self.preset_helper = None
        self._init_synth_data(
            synth_type=JDXiSynth.DRUM_KIT, partial_number=self.partial_number
        )
        # Store parameter controls for easy access
        self.controls: Dict[DrumPartialParam, QWidget] = {}

        # Main layout with no margins/spacing to maximize space
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create scroll area with hidden scrollbars and proper sizing
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        scroll_content = QWidget()
        scroll_content.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        scroll_area.setWidget(scroll_content)

        tab_widget = QTabWidget()
        tab_widget.setMinimumWidth(JDXi.UI.Dimensions.EDITOR_DRUM.PARTIAL_TAB_MIN_WIDTH)
        tab_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        scroll_layout.addWidget(tab_widget)

        tab_partial = QWidget()
        tab_partial_layout = QVBoxLayout(tab_partial)
        tab_partial_layout.setContentsMargins(0, 0, 0, 0)
        tab_partial_layout.setSpacing(0)
        partial_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.CIRCLE_OUTLINE, color=JDXi.UI.Style.GREY
        )
        tab_widget.addTab(tab_partial, partial_icon, "Partial")

        partial_group = DrumPartialSection(
            controls=self.controls,
            create_parameter_combo_box=self._create_parameter_combo_box,
            create_parameter_slider=self._create_parameter_slider,
            midi_helper=self.midi_helper,
        )
        tab_partial_layout.addWidget(partial_group)
        tab_partial_layout.addStretch()

        tab_wmt = QWidget()
        tab_wmt_layout = QVBoxLayout(tab_wmt)
        tab_wmt_layout.setContentsMargins(0, 0, 0, 0)
        tab_wmt_layout.setSpacing(0)
        wmt_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.WAVEFORM, color=JDXi.UI.Style.GREY
        )
        tab_widget.addTab(tab_wmt, wmt_icon, "WMT")

        wmt_group = DrumWMTSection(
            controls=self.controls,
            create_parameter_combo_box=self._create_parameter_combo_box,
            create_parameter_slider=self._create_parameter_slider,
            create_parameter_switch=self._create_parameter_switch,
            midi_helper=self.midi_helper,
            address=self.address,
            on_parameter_changed=self._on_parameter_changed,
        )
        tab_wmt_layout.addWidget(wmt_group)
        tab_wmt_layout.addStretch()

        tab_pitch_env = QWidget()
        tab_pitch_env_layout = QVBoxLayout(tab_pitch_env)
        tab_pitch_env_layout.setContentsMargins(0, 0, 0, 0)
        tab_pitch_env_layout.setSpacing(0)
        pitch_env_icon_base64 = generate_waveform_icon("adsr", "#FFFFFF", 1.0)
        pitch_env_icon = QIcon(base64_to_pixmap(pitch_env_icon_base64))
        tab_widget.addTab(tab_pitch_env, pitch_env_icon, "Pitch Env")

        pitch_env_group = DrumPitchEnvSection(
            controls=self.controls,
            create_parameter_combo_box=self._create_parameter_combo_box,
            create_parameter_slider=self._create_parameter_slider,
            midi_helper=self.midi_helper,
        )
        tab_pitch_env_layout.addWidget(pitch_env_group)
        tab_pitch_env_layout.addStretch()

        tab_output = QWidget()
        tab_output_layout = QVBoxLayout(tab_output)
        tab_output_layout.setContentsMargins(0, 0, 0, 0)
        tab_output_layout.setSpacing(0)
        output_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.VOLUME_HIGH, color=JDXi.UI.Style.GREY
        )
        tab_widget.addTab(tab_output, output_icon, "Output")

        output_group = DrumOutputSection(
            controls=self.controls,
            create_parameter_combo_box=self._create_parameter_combo_box,
            create_parameter_slider=self._create_parameter_slider,
            midi_helper=self.midi_helper,
        )
        tab_output_layout.addWidget(output_group)
        tab_output_layout.addStretch()

        tab_tvf = QWidget()
        tab_tvf_layout = QVBoxLayout(tab_tvf)
        tab_tvf_layout.setContentsMargins(0, 0, 0, 0)
        tab_tvf_layout.setSpacing(0)
        tvf_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.FILTER, color=JDXi.UI.Style.GREY
        )
        tab_widget.addTab(tab_tvf, tvf_icon, "TVF")

        tvf_group = DrumTVFSection(
            controls=self.controls,
            create_parameter_combo_box=self._create_parameter_combo_box,
            create_parameter_slider=self._create_parameter_slider,
            midi_helper=self.midi_helper,
        )
        tab_tvf_layout.addWidget(tvf_group)
        tab_tvf_layout.addStretch()

        tab_tva = QWidget()
        tab_tva_layout = QVBoxLayout(tab_tva)
        tab_tva_layout.setContentsMargins(0, 0, 0, 0)
        tab_tva_layout.setSpacing(0)
        tva_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.AMPLIFIER, color=JDXi.UI.Style.GREY
        )
        tab_widget.addTab(tab_tva, tva_icon, "TVA")

        tva_group = DrumTVASection(
            controls=self.controls,
            create_parameter_combo_box=self._create_parameter_combo_box,
            create_parameter_slider=self._create_parameter_slider,
            midi_helper=self.midi_helper,
        )
        tab_tva_layout.addWidget(tva_group)
        tab_tva_layout.addStretch()

        main_layout.addWidget(scroll_area)
        scroll_area.setMinimumHeight(1200)
