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

import re
from typing import Any, Callable

from decologr import Decologr as log
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.midi.data.drum.data import rm_waves
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.ui.widgets.wmt.envelope import WMTEnvelopeWidget
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


class DrumWMTSection(QWidget):
    """Drum TVF Section for the JDXI Editor"""

    def __init__(
        self,
        controls,
        create_parameter_combo_box,
        create_parameter_slider,
        create_parameter_switch,
        midi_helper,
        address=None,
    ):
        super().__init__()
        """
        Initialize the DrumWMTSection

        :param controls: dict
        :param create_parameter_combo_box: Callable
        :param create_parameter_slider: Callable
        :param midi_helper: MidiIOHelper
        """
        self.l_wave_combos = {}
        self.l_wave_search_boxes = {}
        self.l_wave_selectors = {}
        self.r_wave_combos = {}
        self.r_wave_search_boxes = {}
        self.r_wave_selectors = {}
        self.wmt_tab_widget = None
        self.controls = controls
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self._create_parameter_switch = create_parameter_switch
        self.midi_helper = midi_helper
        self.address = address
        self.setup_ui()

    def setup_ui(self):
        """setup UI"""
        self.setMinimumWidth(JDXiDimensions.DRUM_PARTIAL_TAB_MIN_WIDTH)
        layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setMinimumHeight(JDXiDimensions.SCROLL_AREA_HEIGHT)
        scroll_area.setWidgetResizable(True)  # Important for resizing behavior
        layout.addWidget(scroll_area)

        scrolled_widget = QWidget()
        scrolled_layout = QVBoxLayout(scrolled_widget)

        # Add widgets to scrolled_layout here if needed

        scroll_area.setWidget(scrolled_widget)

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
            "Velocity control",
            ["OFF", "ON", "RANDOM"],
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
        self.wmt_controls_tab_widget.addTab(
            self._create_wmt_controls_group(p), "Controls"
        )
        self.wmt_controls_tab_widget.addTab(
            self._create_wave_combo_group(p, wmt_index), "Waves"
        )
        self.wmt_controls_tab_widget.addTab(self._create_fxm_group(p), "FXM")
        self.wmt_controls_tab_widget.addTab(self._create_tuning_group(p), "Tuning")
        self.wmt_controls_tab_widget.addTab(self._create_wmt_pan_group(p), "Pan")
        self.wmt_controls_tab_widget.addTab(
            self._create_adsr_widget(p), "ADSR Envelope"
        )
        return main_row_hlayout

    def _create_wmt_controls_group(self, p: Callable[[Any], Any]):
        wmt_controls_group = QGroupBox()
        form_layout = QFormLayout()
        wmt_controls_group.setLayout(form_layout)
        self.wave_switch = self._create_parameter_switch(
            p("WAVE_SWITCH"), "Wave Switch", ["OFF", "ON"]
        )
        form_layout.addWidget(self.wave_switch)
        form_layout.addRow(
            self._create_parameter_combo_box(
                p("WAVE_GAIN"), "Wave Gain", ["-6", "0", "6", "12"], [0, 1, 2, 3]
            )
        )
        form_layout.addRow(
            self._create_parameter_slider(p("WAVE_TEMPO_SYNC"), "Wave Tempo Sync")
        )
        return wmt_controls_group

    def _create_wave_combo_group(self, p: Callable[[Any], Any], wmt_index: int):
        """create wave combo"""
        wmt_wave_group = QGroupBox()
        form_layout = QFormLayout()
        wmt_wave_group.setLayout(form_layout)
        rm_wave_groups = [
            "",  # Empty string for the first item
            # === Drum Machine Sources ===
            "Drum Machines",
            "    606",
            "    626",
            "    707",
            "    808",
            "    909",
            "    78",
            "    106",
            "    TM-2",
            # === Musical Genres & Styles ===
            "Genres/Styles",
            "    Ballad",
            "    Break",
            "    Dance",
            "    DanceHall",
            "    Hip-Hop",
            "    HipHop",
            "    Jazz",
            "    Jungle",
            "    Ragga",
            "    Reggae",
            "    Rock",
            # === Sound Character & Texture ===
            "Character",
            "    Analog",
            "    Bright",
            "    Dry",
            "    Hard",
            "    Lite",
            "    Lo-Bit",
            "    Lo-Fi",
            "    Old",
            "    Plastic",
            "    Power",
            "    Tight",
            "    Turbo",
            "    Vint",
            "    Warm",
            "    Wet",
            "    Wide",
            "    Wild",
            # === Instrument Types ===
            "Instruments" "    Kick",
            "    Snare",
            "    Tom",
            "    Clap",
            "    Cymbal",
            "    Crash",
            # === Percussion Types ===
            "Percussion",
            "    Bongo",
            "    Brush",
            "    Brsh",
            "    Conga",
            "    Cowbell",
            "    Piccolo",
            "    Rim",
            "    Rimshot",
            "    Stick",
            "    Cstick",
            "    Swish",
            "    Swish&Trn",
            # === Hi-Hats ===
            "Hi-Hats",
            "    CHH",
            "    OHH",
            "    PHH",
            "    C&OHH",
            "    Tip",
            # === Layer/Expression/Technique Tags ===
            "Layer Tags",
            "    Jazz Rim",
            "    Jazz Snare",
            "    Jz",
            "    HphpJazz",
            # === Synthesis & Processing ===
            "Synthesis",
            "    Dst",
            "    Hush",
            "    Hash",
            "    LD",
            "    MG",
            "    Mix",
            "    PurePhat",
            "    SF",
            "    Sim",
            "    SimV",
            "    Synth",
            "    TY",
            "    WD",
        ]

        # --- Combo and Search Controls for L Wave ---
        form_layout.addRow(QLabel("Search L waves:"))

        # Search box
        l_wave_search_box = QLineEdit()
        l_wave_search_box.setPlaceholderText("Search L waves...")
        self.l_wave_search_boxes[wmt_index] = l_wave_search_box

        # Group selector
        l_wave_selector = QComboBox()
        l_wave_selector.addItems(rm_wave_groups)
        self.l_wave_selectors[wmt_index] = l_wave_selector

        # Combo box (wave list)
        l_wave_combo = self._create_parameter_combo_box(
            p("WAVE_NUMBER_L"), "Wave Number L/Mono", rm_waves, list(range(453))
        )
        self.l_wave_combos[wmt_index] = l_wave_combo

        # Connect both search & selector to populate method
        l_wave_search_box.textChanged.connect(
            lambda _, i=wmt_index: self._populate_l_waves(i)
        )
        l_wave_selector.currentTextChanged.connect(
            lambda _, i=wmt_index: self._populate_l_waves(i)
        )

        # Add widgets to layout
        search_row = QHBoxLayout()
        search_row.addStretch()
        search_row.addWidget(QLabel("Group:"))
        search_row.addWidget(l_wave_selector)
        search_row.addWidget(QLabel("Search:"))
        search_row.addWidget(l_wave_search_box)
        search_row.addStretch()
        form_layout.addRow(search_row)
        form_layout.addRow(l_wave_combo)

        self.l_wave_combos[wmt_index] = l_wave_combo
        self.l_wave_search_boxes[wmt_index] = l_wave_search_box
        self.l_wave_selectors[wmt_index] = l_wave_selector

        # --- Combo and Search Controls for R Wave ---
        form_layout.addRow(QLabel("Search R waves:"))

        # Search box
        r_wave_search_box = QLineEdit()
        r_wave_search_box.setPlaceholderText("Search R waves...")
        self.r_wave_search_boxes[wmt_index] = r_wave_search_box

        # Group selector
        r_wave_selector = QComboBox()
        r_wave_selector.addItems(rm_wave_groups)
        self.r_wave_selectors[wmt_index] = r_wave_selector

        # Combo box (wave list)
        r_wave_combo = self._create_parameter_combo_box(
            p("WAVE_NUMBER_R"), "Wave Number R", rm_waves, list(range(453))
        )
        self.r_wave_combos[wmt_index] = r_wave_combo

        # Connect both search & selector to populate method
        r_wave_search_box.textChanged.connect(
            lambda _, i=wmt_index: self._populate_r_waves(i)
        )
        r_wave_selector.currentTextChanged.connect(
            lambda _, i=wmt_index: self._populate_r_waves(i)
        )

        # Add widgets to layout
        r_search_row = QHBoxLayout()
        r_search_row.addStretch()
        r_search_row.addWidget(QLabel("Group:"))
        r_search_row.addWidget(r_wave_selector)
        r_search_row.addWidget(QLabel("Search:"))
        r_search_row.addWidget(r_wave_search_box)
        r_search_row.addStretch()
        form_layout.addRow(r_search_row)
        form_layout.addRow(r_wave_combo)
        return wmt_wave_group

    def _create_fxm_group(self, p: Callable[[Any], Any]):
        """create fxm group"""
        wmt_fxm_group = QGroupBox("FXM")
        form_layout = QFormLayout()
        wmt_fxm_group.setLayout(form_layout)
        form_layout.addRow(
            self._create_parameter_combo_box(
                p("WAVE_FXM_SWITCH"), "Wave FXM Switch", ["OFF", "ON"], [0, 1]
            )
        )  # If this is correct — maybe it’s a typo?
        form_layout.addRow(
            self._create_parameter_slider(p("WAVE_FXM_COLOR"), "Wave FXM Color")
        )
        form_layout.addRow(
            self._create_parameter_slider(p("WAVE_FXM_DEPTH"), "Wave FXM Depth")
        )
        return wmt_fxm_group

    def _create_wmt_pan_group(self, p: Callable[[Any], Any]):
        """create wmt pan"""
        wmt_pan_group = QGroupBox("Pan")
        form_layout = QFormLayout()
        wmt_pan_group.setLayout(form_layout)
        form_layout.addRow(self._create_parameter_slider(p("WAVE_PAN"), "Wave Pan"))

        # More combo boxes
        form_layout.addRow(
            self._create_parameter_combo_box(
                p("WAVE_RANDOM_PAN_SWITCH"),
                "Wave Random Pan Switch",
                ["OFF", "ON"],
                [0, 1],
            )
        )
        form_layout.addRow(
            self._create_parameter_combo_box(
                p("WAVE_ALTERNATE_PAN_SWITCH"),
                "Wave Alternate Pan Switch",
                ["OFF", "ON", "REVERSE"],
                [0, 1, 2],
            )
        )
        return wmt_pan_group

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
        adsr_widget.setStyleSheet(JDXiStyle.ADSR)
        return adsr_widget

    def _create_tuning_group(self, p: Callable[[Any], Any]):
        """Tuning Group"""
        tuning_group = QGroupBox("Tuning")
        form_layout = QFormLayout()
        tuning_group.setLayout(form_layout)
        form_layout.addRow(
            self._create_parameter_slider(p("WAVE_COARSE_TUNE"), "Wave Coarse Tune")
        )
        form_layout.addRow(
            self._create_parameter_slider(p("WAVE_FINE_TUNE"), "Wave Fine Tune")
        )
        return tuning_group

    def _populate_l_waves(self, wmt_index):
        try:
            search_box = self.l_wave_search_boxes[wmt_index]
            selector = self.l_wave_selectors[wmt_index]
            combo = self.l_wave_combos[wmt_index]

            search_text = search_box.text().strip()
            group_filter = selector.currentText().strip()

            filtered = rm_waves
            if search_text:
                filtered = [w for w in filtered if re.search(search_text, w, re.I)]
            if group_filter:
                filtered = [w for w in filtered if group_filter.lower() in w.lower()]

            combo.combo_box.clear()
            for wave in filtered:
                index_in_rm_waves = rm_waves.index(wave)
                combo.combo_box.addItem(wave, index_in_rm_waves)

            log.message(
                f"WMT{wmt_index}: Showing {len(filtered)} results for group '{group_filter}' + search '{search_text}'"
            )
        except Exception as ex:
            log.error(f"WMT{wmt_index}: Error filtering L waves:", exception=ex)

    def _populate_r_waves(self, wmt_index):
        try:
            search_box = self.r_wave_search_boxes[wmt_index]
            selector = self.r_wave_selectors[wmt_index]
            combo = self.r_wave_combos[wmt_index]

            search_text = search_box.text().strip()
            group_filter = selector.currentText().strip()

            filtered = rm_waves
            if search_text:
                filtered = [w for w in filtered if re.search(search_text, w, re.I)]
            if group_filter:
                filtered = [w for w in filtered if group_filter.lower() in w.lower()]

            combo.combo_box.clear()
            for wave in filtered:
                index_in_rm_waves = rm_waves.index(wave)
                combo.combo_box.addItem(wave, index_in_rm_waves)
            log.message(
                f"WMT{wmt_index}: Showing {len(filtered)} R wave results for "
                f"group '{group_filter}' + search '{search_text}'"
            )
        except Exception as ex:
            log.error(f"WMT{wmt_index}: Error filtering R waves: {ex}")

    def _create_wmt1_layout(self):
        return self._create_wmt_layout(1)

    def _create_wmt2_layout(self):
        return self._create_wmt_layout(2)

    def _create_wmt3_layout(self):
        return self._create_wmt_layout(3)

    def _create_wmt4_layout(self):
        return self._create_wmt_layout(4)
