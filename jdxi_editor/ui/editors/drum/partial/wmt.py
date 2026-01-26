"""
Module: drum_wmt
================

This module defines the `DrumWMTSection` class, which provides a PySide6-based
user interface for editing drum WMT parameters in the Roland JD-Xi synthesizer.
It extends the `QWidget` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying drum WMT parameters, including
  wave selection, gain, FXM color, depth, tempo sync, coarse tune, fine tune, pan,
  random pan switch, alternate pan switch, velocity range lower, velocity range upper,
  velocity fade width lower, velocity fade width upper, and wave level.

Dependencies:
-------------
- PySide6 (for UI components and event handling)
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

Usage:
------
The `DrumWMTSection` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MIDIHelper()
    editor = DrumWMTSection(midi_helper)
    editor.show()
"""

from typing import Any, Callable

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.drum.data import rm_waves
from jdxi_editor.midi.data.parameter.drum.name import DrumDisplayName
from jdxi_editor.midi.data.parameter.drum.option import DrumDisplayOptions
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.param_section import ParameterSectionBase
from jdxi_editor.ui.widgets.combo_box.searchable_filterable import (
    SearchableFilterableComboBox,
)
from jdxi_editor.ui.widgets.editor.helper import (
    create_adsr_icon,
    create_group_with_form_layout,
    create_scrolled_area_with_layout,
    transfer_layout_items,
)
from jdxi_editor.ui.widgets.wmt.envelope import WMTEnvelopeWidget


class DrumWMTSection(ParameterSectionBase):
    """Drum TVF Section for the JDXI Editor"""

    def __init__(
            self,
            controls: dict,
            midi_helper: MidiIOHelper,
            address: RolandSysExAddress = None,
            on_parameter_changed: Callable = None,
    ):
        super().__init__()
        """
        Initialize the DrumWMTSection

        :param controls: dict
        :param midi_helper: MidiIOHelper
        :param address: RolandSysExAddress
        :param on_parameter_changed: Callable to handle parameter changes
        """
        self.l_wave_combos = {}
        self.r_wave_combos = {}
        self.wmt_tab_widget = None
        self.controls = controls
        self.midi_helper = midi_helper
        self.address = address
        self._on_parameter_changed = on_parameter_changed
        self.setup_ui()

    def _setup_ui(self):
        pass

    def setup_ui(self):
        """setup UI"""
        self.setMinimumWidth(JDXi.UI.Dimensions.EDITOR_DRUM.PARTIAL_TAB_MIN_WIDTH)
        # Set size policy to allow vertical expansion
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll_area, scrolled_layout = create_scrolled_area_with_layout()
        scrolled_widget = scroll_area.widget()
        scrolled_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        scrolled_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)

        # Icons row (standardized across editor tabs) - transfer items to avoid "already has a parent" errors
        icon_row_container = QHBoxLayout()
        icon_hlayout = JDXi.UI.Icon.create_adsr_icons_row()

        transfer_layout_items(icon_hlayout, icon_row_container)
        scrolled_layout.addLayout(icon_row_container)

        # WMT Group
        wmt_group = QGroupBox("WMT")
        wmt_layout = QVBoxLayout()
        wmt_group.setLayout(wmt_layout)

        # WMT Velocity Control
        wmt_velocity_control_combo_row_layout = QHBoxLayout()
        wmt_layout.addLayout(wmt_velocity_control_combo_row_layout)
        wmt_velocity_control_combo_row_layout.addStretch()
        wmt_velocity_control_combo = self._create_parameter_switch(
            DrumPartialParam.WMT_VELOCITY_CONTROL,
            DrumDisplayName.WMT_VELOCITY_CONTROL,
            DrumDisplayOptions.WMT_VELOCITY_CONTROL,
        )
        wmt_velocity_control_combo_row_layout.addWidget(wmt_velocity_control_combo)
        wmt_velocity_control_combo_row_layout.addStretch()

        # WMT Tabbed Widget
        self.wmt_tab_widget = QTabWidget()
        wmt_tabs = ["WMT1", "WMT2", "WMT3", "WMT4"]
        for wmt_tab in wmt_tabs:
            self.wmt_tab_widget.addTab(QWidget(), wmt_tab)
        wmt_layout.addWidget(self.wmt_tab_widget)
        wmt1_tab = self.wmt_tab_widget.widget(0)
        wmt1_layout = self._create_wmt1_layout()
        wmt1_tab.setLayout(wmt1_layout)

        # Add controls to WMT2 tab
        wmt2_tab = self.wmt_tab_widget.widget(1)
        wmt2_layout = self._create_wmt2_layout()
        wmt2_tab.setLayout(wmt2_layout)

        # Add controls to WMT2 tab
        wmt3_tab = self.wmt_tab_widget.widget(2)
        wmt3_layout = self._create_wmt3_layout()
        wmt3_tab.setLayout(wmt3_layout)

        # Add controls to WMT2 tab
        wmt4_tab = self.wmt_tab_widget.widget(3)
        wmt4_layout = self._create_wmt4_layout()
        wmt4_tab.setLayout(wmt4_layout)
        scrolled_layout.addWidget(wmt_group)

    def _create_wmt_layout(self, wmt_index: int) -> QHBoxLayout:
        """
        _create_wmt_layout

        :param wmt_index: int
        :return: QFormLayout
        """
        main_row_hlayout = QHBoxLayout()
        prefix = f"WMT{wmt_index}_"

        def p(name):  # helper to get DrumPartialParameter by name
            return getattr(DrumPartialParam, prefix + name)

        self.wmt_controls_tab_widget = QTabWidget()
        main_row_hlayout.addWidget(self.wmt_controls_tab_widget)

        controls_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.TUNE, color=JDXi.UI.Style.GREY
        )
        self.wmt_controls_tab_widget.addTab(
            self._create_wmt_controls_group(p), controls_icon, "Controls"
        )
        waves_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.WAVEFORM, color=JDXi.UI.Style.GREY
        )
        self.wmt_controls_tab_widget.addTab(
            self._create_wave_combo_group(p, wmt_index), waves_icon, "Waves"
        )
        fxm_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.EQUALIZER, color=JDXi.UI.Style.GREY
        )
        self.wmt_controls_tab_widget.addTab(self._create_fxm_group(p), fxm_icon, "FXM")
        tuning_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.MUSIC_NOTE, color=JDXi.UI.Style.GREY
        )
        self.wmt_controls_tab_widget.addTab(
            self._create_tuning_group(p), tuning_icon, "Tuning"
        )
        pan_icon = JDXi.UI.Icon.get_icon(
            JDXi.UI.Icon.PAN_HORIZONTAL, color=JDXi.UI.Style.GREY
        )
        self.wmt_controls_tab_widget.addTab(
            self._create_wmt_pan_group(p), pan_icon, "Pan"
        )
        adsr_icon = create_adsr_icon()
        self.wmt_controls_tab_widget.addTab(
            self._create_adsr_widget(p), adsr_icon, "ADSR Envelope"
        )
        return main_row_hlayout

    def _create_wmt_controls_group(self, p: Callable[[Any], Any]):
        self.wave_switch = self._create_parameter_switch(
            p("WAVE_SWITCH"),
            DrumDisplayName.WMT_WAVE_SWITCH,
            values=DrumDisplayOptions.WMT_WAVE_SWITCH,
        )
        widgets = [
            self.wave_switch,
            self._create_parameter_combo_box(
                p("WAVE_GAIN"),
                DrumDisplayName.WMT_WAVE_GAIN,
                options=DrumDisplayOptions.WMT_WAVE_GAIN,
                values=[0, 1, 2, 3],
            ),
            self._create_parameter_slider(
                p("WAVE_TEMPO_SYNC"), DrumDisplayName.WMT_WAVE_TEMPO_SYNC
            ),
        ]
        group, _ = create_group_with_form_layout(widgets)
        return group

    def _create_wave_combo_group(self, p: Callable[[Any], Any], wmt_index: int):
        """create wave combo using SearchableFilterableComboBox"""
        # Extract categories from rm_wave_groups (non-empty, non-indented items)
        rm_wave_categories = [
            "Drum Machines",
            "Genres/Styles",
            "Character",
            "Instruments",
            "Percussion",
            "Hi-Hats",
            "Layer Tags",
            "Synthesis",
        ]

        # Category filter function for wave groups
        def wave_category_filter(wave_name: str, category: str) -> bool:
            """Check if a wave name matches a category."""
            if not category:
                return True
            # Map category to search terms
            category_terms = {
                "Drum Machines": [
                    "606",
                    "626",
                    "707",
                    "808",
                    "909",
                    "78",
                    "106",
                    "TM-2",
                ],
                "Genres/Styles": [
                    "Ballad",
                    "Break",
                    "Dance",
                    "DanceHall",
                    "Hip-Hop",
                    "HipHop",
                    "Jazz",
                    "Jungle",
                    "Ragga",
                    "Reggae",
                    "Rock",
                ],
                "Character": [
                    "Analog",
                    "Bright",
                    "Dry",
                    "Hard",
                    "Lite",
                    "Lo-Bit",
                    "Lo-Fi",
                    "Old",
                    "Plastic",
                    "Power",
                    "Tight",
                    "Turbo",
                    "Vint",
                    "Warm",
                    "Wet",
                    "Wide",
                    "Wild",
                ],
                "Instruments": ["Kick", "Snare", "Tom", "Clap", "Cymbal", "Crash"],
                "Percussion": [
                    "Bongo",
                    "Brush",
                    "Brsh",
                    "Conga",
                    "Cowbell",
                    "Piccolo",
                    "Rim",
                    "Rimshot",
                    "Stick",
                    "Cstick",
                    "Swish",
                ],
                "Hi-Hats": ["CHH", "OHH", "PHH", "C&OHH", "Tip"],
                "Layer Tags": ["Jazz Rim", "Jazz Snare", "Jz", "HphpJazz"],
                "Synthesis": [
                    "Dst",
                    "Hush",
                    "Hash",
                    "LD",
                    "MG",
                    "Mix",
                    "PurePhat",
                    "SF",
                    "Sim",
                    "SimV",
                    "Synth",
                    "TY",
                    "WD",
                ],
            }
            terms = category_terms.get(category, [])
            return any(term.lower() in wave_name.lower() for term in terms)

        # --- L Wave Combo Box ---
        l_wave_param = p("WAVE_NUMBER_L")
        l_wave_combo = SearchableFilterableComboBox(
            label="Wave Number L/Mono",
            options=rm_waves,
            values=list(range(len(rm_waves))),
            categories=rm_wave_categories,
            category_filter_func=wave_category_filter,
            show_label=True,
            show_search=True,
            show_category=True,
            search_placeholder="Search L waves...",
            category_label="Group:",
            search_label="Search:",
        )
        # Connect to parameter change handler using the same pattern as _create_parameter_combo_box
        # The valueChanged signal emits the original value (not filtered index), which is correct
        l_wave_combo.valueChanged.connect(
            lambda v: self._on_wave_parameter_changed(l_wave_param, v)
        )
        self.l_wave_combos[wmt_index] = l_wave_combo
        self.controls[l_wave_param] = l_wave_combo

        # --- R Wave Combo Box ---
        r_wave_param = p("WAVE_NUMBER_R")
        r_wave_combo = SearchableFilterableComboBox(
            label="Wave Number R",
            options=rm_waves,
            values=list(range(len(rm_waves))),
            categories=rm_wave_categories,
            category_filter_func=wave_category_filter,
            show_label=True,
            show_search=True,
            show_category=True,
            search_placeholder="Search R waves...",
            category_label="Group:",
            search_label="Search:",
        )
        # Connect to parameter change handler using the same pattern as _create_parameter_combo_box
        r_wave_combo.valueChanged.connect(
            lambda v: self._on_wave_parameter_changed(r_wave_param, v)
        )
        self.r_wave_combos[wmt_index] = r_wave_combo
        self.controls[r_wave_param] = r_wave_combo

        widgets = [l_wave_combo, r_wave_combo]
        group, _ = create_group_with_form_layout(widgets)
        return group

    def _create_fxm_group(self, p: Callable[[Any], Any]):
        """create fxm group"""
        widgets = [
            self._create_parameter_combo_box(
                p("WAVE_FXM_SWITCH"), "Wave FXM Switch", ["OFF", "ON"], [0, 1]
            ),
            self._create_parameter_slider(p("WAVE_FXM_COLOR"), "Wave FXM Color"),
            self._create_parameter_slider(p("WAVE_FXM_DEPTH"), "Wave FXM Depth"),
        ]
        group, _ = create_group_with_form_layout(widgets, label="FXM")
        return group

    def _create_wmt_pan_group(self, p: Callable[[Any], Any]):
        """create wmt pan"""
        widgets = [
            self._create_parameter_slider(p("WAVE_PAN"), "Wave Pan"),
            self._create_parameter_combo_box(
                p("WAVE_RANDOM_PAN_SWITCH"),
                "Wave Random Pan Switch",
                ["OFF", "ON"],
                [0, 1],
            ),
            self._create_parameter_combo_box(
                p("WAVE_ALTERNATE_PAN_SWITCH"),
                "Wave Alternate Pan Switch",
                ["OFF", "ON", "REVERSE"],
                [0, 1, 2],
            ),
        ]
        group, _ = create_group_with_form_layout(widgets, label="Pan")
        return group

    def _create_adsr_widget(self, p: Callable[[Any], Any]) -> WMTEnvelopeWidget:
        adsr_widget = WMTEnvelopeWidget(
            fade_lower_param=p("VELOCITY_FADE_WIDTH_LOWER"),
            range_lower_param=p("VELOCITY_RANGE_LOWER"),
            range_upper_param=p("VELOCITY_RANGE_UPPER"),
            depth_param=p("WAVE_LEVEL"),
            fade_upper_param=p("VELOCITY_FADE_WIDTH_UPPER"),
            create_parameter_slider=self._create_parameter_slider,
            controls=self.controls,
            midi_helper=self.midi_helper,
            address=self.address,
        )
        adsr_widget.setStyleSheet(JDXi.UI.Style.ADSR)
        return adsr_widget

    def _create_tuning_group(self, p: Callable[[Any], Any]):
        """Tuning Group"""
        widgets = [
            self._create_parameter_slider(p("WAVE_COARSE_TUNE"), "Wave Coarse Tune"),
            self._create_parameter_slider(p("WAVE_FINE_TUNE"), "Wave Fine Tune"),
        ]
        group, _ = create_group_with_form_layout(widgets, label="Tuning")
        return group

    def _on_wave_parameter_changed(self, param: DrumPartialParam, value: int) -> None:
        """
        Handle wave parameter change.

        This method is called when a wave combo box value changes.
        It sends the MIDI command with the correct value (original index, not filtered index).

        The new SearchableFilterableComboBox widget maintains proper value mapping,
        so the value parameter is already the correct original index.

        :param param: The parameter that changed
        :param value: The original value (wave index in rm_waves)
        """
        # Use the parent editor's _on_parameter_changed if available, otherwise use direct MIDI sending
        if self._on_parameter_changed:
            self._on_parameter_changed(param, value, self.address)
        elif hasattr(self, "midi_helper") and self.midi_helper and self.address:
            try:
                from jdxi_editor.midi.sysex.composer import JDXiSysExComposer

                sysex_composer = JDXiSysExComposer()
                sysex_message = sysex_composer.compose_message(
                    address=self.address, param=param, value=value
                )
                self.midi_helper.send_midi_message(sysex_message)
                log.debug(f"Sent MIDI for {param.name} with value {value}")
            except Exception as ex:
                log.error(f"Error sending MIDI for {param.name}: {ex}")

    def _create_wmt1_layout(self):
        return self._create_wmt_layout(1)

    def _create_wmt2_layout(self):
        return self._create_wmt_layout(2)

    def _create_wmt3_layout(self):
        return self._create_wmt_layout(3)

    def _create_wmt4_layout(self):
        return self._create_wmt_layout(4)
