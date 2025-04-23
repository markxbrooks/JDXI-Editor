import re

from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea, QTabWidget, QComboBox, QLabel, \
    QLineEdit, QHBoxLayout
import logging
from jdxi_editor.midi.data.drum.data import rm_waves
from jdxi_editor.midi.data.parameter.drum.partial import AddressParameterDrumPartial
from jdxi_editor.ui.windows.jdxi.dimensions import JDXIDimensions


class DrumWMTSection(QWidget):
    """Drum TVF Section for the JDXI Editor"""

    def __init__(
            self,
            controls,
            create_parameter_combo_box,
            create_parameter_slider,
            midi_helper,
    ):
        super().__init__()
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
        self.midi_helper = midi_helper
        self.setup_ui()

    def setup_ui(self):
        """setup UI"""
        layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setMinimumHeight(JDXIDimensions.SCROLL_AREA_HEIGHT)
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
        wmt_velocity_control_combo = QComboBox()
        wmt_velocity_control_combo.addItems(["OFF", "ON", "RANDOM"])
        wmt_layout.addWidget(wmt_velocity_control_combo)

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

    def _create_wmt_layout(self, wmt_index: int):
        layout = QFormLayout()
        prefix = f"WMT{wmt_index}_"

        def p(name):  # helper to get DrumPartialParameter by name
            return getattr(AddressParameterDrumPartial, prefix + name)

        self.wave_switch = self._create_parameter_combo_box(p("WAVE_SWITCH"), "Wave Switch", ["OFF", "ON"], [0, 1])
        layout.addRow(self.wave_switch)

        rm_wave_groups = [

            "",  # Empty string for the first item

            # === Drum Machine Sources ===
            "Drum Machines", "    606", "    626", "    707", "    808", "    909", "    78", "    106", "    TM-2",

            # === Musical Genres & Styles ===
            "Genres/Styles", "    Ballad", "    Break", "    Dance", "    DanceHall", "    Hip-Hop", "    HipHop", "    Jazz",
            "    Jungle", "    Ragga", "    Reggae", "    Rock",

            # === Sound Character & Texture ===
            "Character", "    Analog", "    Bright", "    Dry", "    Hard", "    Lite", "    Lo-Bit", "    Lo-Fi", "    Old",
            "    Plastic", "    Power", "    Tight", "    Turbo", "    Vint", "    Warm", "    Wet", "    Wide", "    Wild",

            # === Instrument Types ===
            "Instruments" "    Kick", "    Snare", "    Tom", "    Clap", "    Cymbal", "    Crash",

            # === Percussion Types ===
            "Percussion", "    Bongo", "    Brush", "    Brsh", "    Conga", "    Cowbell", "    Piccolo", "    Rim", "    Rimshot",
            "    Stick", "    Cstick", "    Swish", "    Swish&Trn",

            # === Hi-Hats ===
            "Hi-Hats", "    CHH", "    OHH", "    PHH", "    C&OHH", "    Tip",

            # === Layer/Expression/Technique Tags ===
            "Layer Tags", "    Jazz Rim", "    Jazz Snare", "    Jz", "    HphpJazz",

            # === Synthesis & Processing ===
            "Synthesis",  "    Dst", "    Hush", "    Hash", "    LD", "    MG", "    Mix", "    PurePhat", "    SF", "    Sim", "    SimV",
            "    Synth", "    TY", "    WD"
        ]

        # --- Combo and Search Controls for L Wave ---
        layout.addRow(QLabel("Search L waves:"))

        # Search box
        l_wave_search_box = QLineEdit()
        l_wave_search_box.setPlaceholderText("Search L waves...")
        self.l_wave_search_boxes[wmt_index] = l_wave_search_box

        # Group selector
        l_wave_selector = QComboBox()
        l_wave_selector.addItems(rm_wave_groups)
        self.l_wave_selectors[wmt_index] = l_wave_selector

        # Combo box (wave list)
        l_wave_combo = self._create_parameter_combo_box(p("WAVE_NUMBER_L"), "Wave Number L/Mono",
                                                        rm_waves,
                                                        list(range(453)))
        self.l_wave_combos[wmt_index] = l_wave_combo

        # Connect both search & selector to populate method
        l_wave_search_box.textChanged.connect(lambda _, i=wmt_index: self._populate_l_waves(i))
        l_wave_selector.currentTextChanged.connect(lambda _, i=wmt_index: self._populate_l_waves(i))

        # Add widgets to layout
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Group:"))
        search_row.addWidget(l_wave_selector)
        search_row.addWidget(QLabel("Search:"))
        search_row.addWidget(l_wave_search_box)
        layout.addRow(search_row)
        layout.addRow(l_wave_combo)

        self.l_wave_combos[wmt_index] = l_wave_combo
        self.l_wave_search_boxes[wmt_index] = l_wave_search_box
        self.l_wave_selectors[wmt_index] = l_wave_selector

        # --- Combo and Search Controls for R Wave ---
        layout.addRow(QLabel("Search R waves:"))

        # Search box
        r_wave_search_box = QLineEdit()
        r_wave_search_box.setPlaceholderText("Search R waves...")
        self.r_wave_search_boxes[wmt_index] = r_wave_search_box

        # Group selector
        r_wave_selector = QComboBox()
        r_wave_selector.addItems(rm_wave_groups)
        self.r_wave_selectors[wmt_index] = r_wave_selector

        # Combo box (wave list)
        r_wave_combo = self._create_parameter_combo_box(p("WAVE_NUMBER_R"), "Wave Number R",
                                                        rm_waves,
                                                        list(range(453)))
        self.r_wave_combos[wmt_index] = r_wave_combo

        # Connect both search & selector to populate method
        r_wave_search_box.textChanged.connect(lambda _, i=wmt_index: self._populate_r_waves(i))
        r_wave_selector.currentTextChanged.connect(lambda _, i=wmt_index: self._populate_r_waves(i))

        # Add widgets to layout
        r_search_row = QHBoxLayout()
        r_search_row.addWidget(QLabel("Group:"))
        r_search_row.addWidget(r_wave_selector)
        r_search_row.addWidget(QLabel("Search:"))
        r_search_row.addWidget(r_wave_search_box)
        layout.addRow(r_search_row)
        layout.addRow(r_wave_combo)

        layout.addRow(
            self._create_parameter_combo_box(p("WAVE_GAIN"), "Wave Gain", ["-6", "0", "6", "12"], [0, 1, 2, 3]))
        layout.addRow(self._create_parameter_combo_box(p("WAVE_GAIN"), "Wave FXM Switch", ["OFF", "ON"],
                                                       [0, 1]))  # If this is correct — maybe it’s a typo?

        # Sliders
        layout.addRow(self._create_parameter_slider(p("WAVE_FXM_COLOR"), "Wave FXM Color"))
        layout.addRow(self._create_parameter_slider(p("WAVE_FXM_DEPTH"), "Wave FXM Depth"))
        layout.addRow(self._create_parameter_slider(p("WAVE_TEMPO_SYNC"), "Wave Tempo Sync"))
        layout.addRow(self._create_parameter_slider(p("WAVE_COARSE_TUNE"), "Wave Coarse Tune"))
        layout.addRow(self._create_parameter_slider(p("WAVE_FINE_TUNE"), "Wave Fine Tune"))
        layout.addRow(self._create_parameter_slider(p("WAVE_PAN"), "Wave Pan"))

        # More combo boxes
        layout.addRow(
            self._create_parameter_combo_box(p("WAVE_RANDOM_PAN_SWITCH"), "Wave Random Pan Switch", ["OFF", "ON"],
                                             [0, 1]))
        layout.addRow(self._create_parameter_combo_box(p("WAVE_ALTERNATE_PAN_SWITCH"), "Wave Alternate Pan Switch",
                                                       ["OFF", "ON", "REVERSE"], [0, 1, 2]))

        # More sliders
        layout.addRow(self._create_parameter_slider(p("WAVE_LEVEL"), "Wave Level"))
        layout.addRow(self._create_parameter_slider(p("VELOCITY_RANGE_LOWER"), "Velocity Range Lower"))
        layout.addRow(self._create_parameter_slider(p("VELOCITY_RANGE_UPPER"), "Velocity Range Upper"))
        layout.addRow(self._create_parameter_slider(p("VELOCITY_FADE_WIDTH_LOWER"), "Velocity Fade Width Lower"))
        layout.addRow(self._create_parameter_slider(p("VELOCITY_FADE_WIDTH_UPPER"), "Velocity Fade Width Upper"))

        return layout

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

            logging.info(
                f"WMT{wmt_index}: Showing {len(filtered)} results for group '{group_filter}' + search '{search_text}'")
        except Exception as ex:
            logging.warning(f"WMT{wmt_index}: Error filtering L waves: {ex}")

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
            logging.info(
                f"WMT{wmt_index}: Showing {len(filtered)} R wave results for group '{group_filter}' + search '{search_text}'")
        except Exception as ex:
            logging.warning(f"WMT{wmt_index}: Error filtering R waves: {ex}")

    def _create_wmt1_layout(self):
        return self._create_wmt_layout(1)

    def _create_wmt2_layout(self):
        return self._create_wmt_layout(2)

    def _create_wmt3_layout(self):
        return self._create_wmt_layout(3)

    def _create_wmt4_layout(self):
        return self._create_wmt_layout(4)
