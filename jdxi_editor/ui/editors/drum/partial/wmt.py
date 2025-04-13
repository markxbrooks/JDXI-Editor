from PySide6.QtWidgets import QGroupBox, QFormLayout, QWidget, QVBoxLayout, QScrollArea, QTabWidget, QComboBox

from jdxi_editor.midi.data.drum.data import rm_waves
from jdxi_editor.midi.data.parameter.drum.common import DrumCommonParameter
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParameter
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
            return getattr(DrumPartialParameter, prefix + name)

        # Combo boxes
        layout.addRow(self._create_parameter_combo_box(p("WAVE_SWITCH"), f"{prefix}Wave Switch", ["OFF", "ON"], [0, 1]))
        layout.addRow(self._create_parameter_combo_box(p("WAVE_NUMBER_L"), f"{prefix}Wave Number L/Mono", rm_waves,
                                                       list(range(453))))
        layout.addRow(
            self._create_parameter_combo_box(p("WAVE_NUMBER_R"), f"{prefix}Wave Number R", rm_waves, list(range(453))))
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

    def _create_wmt1_layout(self):
        return self._create_wmt_layout(1)

    def _create_wmt2_layout(self):
        return self._create_wmt_layout(2)

    def _create_wmt3_layout(self):
        return self._create_wmt_layout(3)

    def _create_wmt4_layout(self):
        return self._create_wmt_layout(4)
