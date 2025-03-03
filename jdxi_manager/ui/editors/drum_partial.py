import logging
from typing import Dict

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QGridLayout,
    QGroupBox,
    QFormLayout,
    QSpinBox,
    QComboBox,
    QTabWidget,
)
from jdxi_manager.data.drums import get_address_for_partial, DRUM_ADDRESSES, rm_waves
from jdxi_manager.data.parameter.drums import DrumParameter
from jdxi_manager.midi.constants import (
    TEMPORARY_DRUM_KIT_AREA)
from jdxi_manager.midi.constants.sysex import (
    TEMPORARY_TONE_AREA, DRUM_KIT_AREA
)
from jdxi_manager.data.parameter.drums import get_address_for_partial_name
from jdxi_manager.ui.widgets.slider import Slider
from jdxi_manager.ui.widgets.combo_box.combo_box import ComboBox
from jdxi_manager.ui.widgets.spin_box.spin_box import SpinBox

instrument_icon_folder = "drum_kits"

"""
For reference:
|-------------+-----------+----------------------------------------------------|
| 00 20 | 0000 00aa |                             WMT Velocity Control (0 - 2) |
|       |                                                    | OFF, ON, RANDOM |
|-------------+-----------+----------------------------------------------------|
| 00 21 | 0000 000a | WMT1 Wave Switch (0 - 1) |
| | | OFF, ON |
| 00 22 | 0000 00aa | WMT1 Wave Group Type (0) |
|# 00 23 | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | WMT1 Wave Group ID (0 - 16384) |
| | | OFF, 1 - 16384 |
|# 00 27 | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | WMT1 Wave Number L (Mono) (0 - 16384) |
| | | OFF, 1 - 16384 |
|# 00 2B | 0000 aaaa | |
| | 0000 bbbb | |
| | 0000 cccc | |
| | 0000 dddd | WMT1 Wave Number R (0 - 16384) |
| | | OFF, 1 - 16384 |
| 00 2F | 0000 00aa | WMT1 Wave Gain (0 - 3) |
| | | -6, 0, +6, +12 [dB] |
| 00 30 | 0000 000a | WMT1 Wave FXM Switch (0 - 1) |
| | | OFF, ON |
| 00 31 | 0000 00aa | WMT1 Wave FXM Color (0 - 3) |
| | | 1 - 4 |
| 00 32 | 000a aaaa | WMT1 Wave FXM Depth (0 - 16) |
| 00 33 | 0000 000a | WMT1 Wave Tempo Sync (0 - 1) |
| | | OFF, ON |
| 00 34 | 0aaa aaaa | WMT1 Wave Coarse Tune (16 - 112) |
| | | -48 - +48 |
| 00 35 | 0aaa aaaa | WMT1 Wave Fine Tune (14 - 114) |
| | | -50 - +50 |
| 00 36 | 0aaa aaaa | WMT1 Wave Pan (0 - 127) |
| | | L64 - 63R |
| 00 37 | 0000 000a | WMT1 Wave Random Pan Switch (0 - 1) |
| | | OFF, ON |
| 00 38 | 0000 00aa | WMT1 Wave Alternate Pan Switch (0 - 2) |
| | | OFF, ON, REVERSE |
| 00 39 | 0aaa aaaa | WMT1 Wave Level (0 - 127) |
| 00 3A | 0aaa aaaa | WMT1 Velocity Range Lower (1 - 127) |
| | | 1 - UPPER |
| 00 3B | 0aaa aaaa | WMT1 Velocity Range Upper (1 - 127) |
| | | LOWER - 127 |
| 00 3C | 0aaa aaaa | WMT1 Velocity Fade Width Lower (0 - 127) |
| 00 3D | 0aaa aaaa | WMT1 Velocity Fade Width Upper (0 - 127) |
|-------------+-----------+----------------------------------------------------|
"""


class DrumPartialEditor(QWidget):
    """Editor for address single partial"""

    def __init__(self, midi_helper=None, partial_num=0, partial_name=None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.partial_num = partial_num  # This is now the numerical index
        self.partial_name = partial_name  # This is now the numerical index
        self.preset_handler = None
        # Calculate the address for this partial
        try:
            from jdxi_manager.data.drums import get_address_for_partial

            self.partial_address = get_address_for_partial_name(self.partial_name)
            logging.info(
                f"Initialized partial {partial_num} with address: {hex(self.partial_address)}"
            )
        except Exception as e:
            logging.error(
                f"Error calculating address for partial {partial_num}: {str(e)}"
            )
            self.partial_address = 0x00

        # Store parameter controls for easy access
        self.controls: Dict[DrumParameter, QWidget] = {}

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)

        # Create grid layout for parameter groups
        grid_layout = QGridLayout()
        scroll_layout.addLayout(grid_layout)

        # Add parameter groups
        pitch_group = self._create_pitch_group()
        grid_layout.addWidget(pitch_group, 0, 0)

        output_group = self._create_output_group()
        grid_layout.addWidget(output_group, 0, 2)

        tvf_group = self._create_tvf_group()
        grid_layout.addWidget(tvf_group, 1, 2)

        pitch_env_group = self._create_pitch_env_group()
        grid_layout.addWidget(pitch_env_group, 0, 1)

        wmt_group = self._create_wmt_group()
        grid_layout.addWidget(wmt_group, 1, 0)

        tva_group = self._create_tva_group()
        grid_layout.addWidget(tva_group, 1, 1)

        # scroll_area.setLayout(scroll_layout)
        main_layout.addWidget(scroll_area)

    def _create_tva_group(self):
        """Create the TVA group."""

        # TVA Group
        tva_group = QGroupBox("TVA")
        tva_layout = QFormLayout()
        tva_group.setLayout(tva_layout)

        # Add TVA parameters
        tva_level_velocity_curve_spin = QSpinBox()
        tva_level_velocity_curve_spin.setRange(0, 7)
        tva_layout.addRow("Level Velocity Curve", tva_level_velocity_curve_spin)

        tva_level_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.TVA_LEVEL_VELOCITY_SENS, "Level Velocity Sens"
        )
        tva_layout.addRow(tva_level_velocity_sens_slider)

        tva_env_time1_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_TIME_1_VELOCITY_SENS, "Env Time 1 Velocity Sens"
        )
        tva_layout.addRow(tva_env_time1_velocity_sens_slider)

        tva_env_time4_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_TIME_4_VELOCITY_SENS, "Env Time 4 Velocity Sens"
        )
        tva_layout.addRow(tva_env_time4_velocity_sens_slider)

        tva_env_time1_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_TIME_1, "Env Time 1"
        )
        tva_layout.addRow(tva_env_time1_slider)

        tva_env_time2_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_TIME_2, "Env Time 2"
        )
        tva_layout.addRow(tva_env_time2_slider)

        tva_env_time3_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_TIME_3, "Env Time 3"
        )
        tva_layout.addRow(tva_env_time3_slider)

        tva_env_time4_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_TIME_4, "Env Time 4"
        )
        tva_layout.addRow(tva_env_time4_slider)

        tva_env_level1_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_LEVEL_1, "Env Level 1"
        )
        tva_layout.addRow(tva_env_level1_slider)

        tva_env_level2_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_LEVEL_2, "Env Level 2"
        )
        tva_layout.addRow(tva_env_level2_slider)

        tva_env_level3_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_LEVEL_3, "Env Level 3"
        )
        tva_layout.addRow(tva_env_level3_slider)
        return tva_group

    def _create_wmt_group(self):
        """Create the WMT group."""

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
        return wmt_group

    def _create_wmt1_layout(self):
        # Add controls to WMT1 tab
        wmt1_layout = QFormLayout()

        wmt1_wave_switch_combo = QComboBox()
        wmt1_wave_switch_combo.addItems(["OFF", "ON"])
        wmt1_layout.addRow("WMT1 Wave Switch", wmt1_wave_switch_combo)
        wmt1_wave_switch_combo.currentIndexChanged.connect(self._on_wmt1_wave_switch_changed)

        wmt1_wave_number_l_combo = QComboBox()
        wmt1_wave_number_l_combo.addItems(rm_waves)
        wmt1_layout.addRow("WMT1 Wave Number L", wmt1_wave_number_l_combo)
        wmt1_wave_number_l_combo.currentIndexChanged.connect(self._on_wmt1_wave_number_l_changed)

        wmt1_wave_number_r_combo = QComboBox()
        wmt1_wave_number_r_combo.addItems(rm_waves)
        wmt1_layout.addRow("WMT1 Wave Number R", wmt1_wave_number_r_combo)
        wmt1_wave_number_r_combo.currentIndexChanged.connect(self._on_wmt1_wave_number_r_changed)

        wmt1_wave_gain_combo = QComboBox()
        wmt1_wave_gain_combo.addItems(["-6", "0", "+6", "+12"])
        wmt1_layout.addRow("WMT1 Wave Gain", wmt1_wave_gain_combo)
        wmt1_wave_gain_combo.currentIndexChanged.connect(self._on_wmt1_wave_gain_changed)

        wmt1_wave_fxm_switch_combo = QComboBox()
        wmt1_wave_fxm_switch_combo.addItems(["OFF", "ON"])
        wmt1_layout.addRow("WMT1 Wave FXM Switch", wmt1_wave_fxm_switch_combo)
        wmt1_wave_fxm_switch_combo.currentIndexChanged.connect(self._on_wmt1_wave_fxm_switch_changed)

        wmt1_wave_fxm_color_spin = QSpinBox()
        wmt1_wave_fxm_color_spin.setRange(0, 3)
        wmt1_layout.addRow("WMT1 Wave FXM Color", wmt1_wave_fxm_color_spin)
        wmt1_wave_fxm_color_spin.valueChanged.connect(self._on_wmt1_wave_fxm_color_changed)

        wmt1_wave_fxm_depth_spin = QSpinBox()
        wmt1_wave_fxm_depth_spin.setRange(0, 16)
        wmt1_layout.addRow("WMT1 Wave FXM Depth", wmt1_wave_fxm_depth_spin)

        wmt1_wave_tempo_sync_combo = QComboBox()
        wmt1_wave_tempo_sync_combo.addItems(["OFF", "ON"])
        wmt1_layout.addRow("WMT1 Wave Tempo Sync", wmt1_wave_tempo_sync_combo)
        wmt1_wave_tempo_sync_combo.currentIndexChanged.connect(self._on_wmt1_wave_tempo_sync_changed)

        wmt1_wave_coarse_tune_spin = QSpinBox()
        wmt1_wave_coarse_tune_spin.setRange(16, 112)
        wmt1_layout.addRow("WMT1 Wave Coarse Tune", wmt1_wave_coarse_tune_spin)
        wmt1_wave_coarse_tune_spin.valueChanged.connect(self._on_wmt1_wave_coarse_tune_changed)

        wmt1_wave_fine_tune_spin = QSpinBox()
        wmt1_wave_fine_tune_spin.setRange(14, 114)
        wmt1_layout.addRow("WMT1 Wave Fine Tune", wmt1_wave_fine_tune_spin)
        wmt1_wave_fine_tune_spin.valueChanged.connect(self._on_wmt1_wave_fine_tune_changed)

        wmt1_wave_pan_spin = QSpinBox()
        wmt1_wave_pan_spin.setRange(0, 127)
        wmt1_layout.addRow("WMT1 Wave Pan", wmt1_wave_pan_spin)
        wmt1_wave_pan_spin.valueChanged.connect(self._on_wmt1_wave_pan_changed)

        wmt1_wave_random_pan_switch_combo = QComboBox()
        wmt1_wave_random_pan_switch_combo.addItems(["OFF", "ON"])
        wmt1_layout.addRow(
            "WMT1 Wave Random Pan Switch", wmt1_wave_random_pan_switch_combo
        )
        wmt1_wave_random_pan_switch_combo.currentIndexChanged.connect(self._on_wmt1_wave_random_pan_switch_changed)

        wmt1_wave_alternate_pan_switch_combo = QComboBox()
        wmt1_wave_alternate_pan_switch_combo.addItems(["OFF", "ON", "REVERSE"])
        wmt1_layout.addRow(
            "WMT1 Wave Alternate Pan Switch", wmt1_wave_alternate_pan_switch_combo
        )
        wmt1_wave_alternate_pan_switch_combo.currentIndexChanged.connect(
            self._on_wmt1_wave_alternate_pan_switch_changed)

        wmt1_wave_level_spin = QSpinBox()
        wmt1_wave_level_spin.setRange(0, 127)
        wmt1_layout.addRow("WMT1 Wave Level", wmt1_wave_level_spin)
        wmt1_wave_level_spin.valueChanged.connect(self._on_wmt1_wave_level_changed)

        wmt1_velocity_range_lower_spin = QSpinBox()
        wmt1_velocity_range_lower_spin.setRange(1, 127)
        wmt1_layout.addRow("WMT1 Velocity Range Lower", wmt1_velocity_range_lower_spin)
        wmt1_velocity_range_lower_spin.valueChanged.connect(self._on_wmt1_velocity_range_lower_changed)

        wmt1_velocity_range_upper_spin = QSpinBox()
        wmt1_velocity_range_upper_spin.setRange(1, 127)
        wmt1_layout.addRow("WMT1 Velocity Range Upper", wmt1_velocity_range_upper_spin)
        wmt1_velocity_range_upper_spin.valueChanged.connect(self._on_wmt1_velocity_range_upper_changed)

        wmt1_velocity_fade_width_lower_spin = QSpinBox()
        wmt1_velocity_fade_width_lower_spin.setRange(0, 127)
        wmt1_layout.addRow(
            "WMT1 Velocity Fade Width Lower", wmt1_velocity_fade_width_lower_spin
        )
        wmt1_velocity_fade_width_lower_spin.valueChanged.connect(self._on_wmt1_velocity_fade_width_lower_changed)

        wmt1_velocity_fade_width_upper_spin = QSpinBox()
        wmt1_velocity_fade_width_upper_spin.setRange(0, 127)
        wmt1_layout.addRow(
            "WMT1 Velocity Fade Width Upper", wmt1_velocity_fade_width_upper_spin
        )
        wmt1_velocity_fade_width_upper_spin.valueChanged.connect(self._on_wmt1_velocity_fade_width_upper_changed)
        return wmt1_layout

    def _create_wmt2_layout(self):
        wmt2_layout = QFormLayout()
        wmt2_wave_switch_combo = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_SWITCH, "WMT2 Wave Switch",
                                                                  ["OFF", "ON"], [0, 1])

        wmt2_layout.addRow("WMT2 Wave Switch", wmt2_wave_switch_combo)

        wmt2_wave_number_l_spin = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_NUMBER_L,
                                                                   "WMT2 Wave Number L/Mono",
                                                                   options=rm_waves,
                                                                   values=list(range(1, 456)))

        wmt2_layout.addRow("WMT2 Wave Number L", wmt2_wave_number_l_spin)

        wmt2_wave_number_r_spin = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_NUMBER_R,
                                                                   "WMT2 Wave Number R",
                                                                   options=rm_waves,
                                                                   values=list(range(1, 456)))

        wmt2_layout.addRow("WMT2 Wave Number R", wmt2_wave_number_r_spin)

        wmt2_wave_gain_combo = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_GAIN,
                                                                "Wave Gain",
                                                                options=["-6", "0", "6", "12"],
                                                                values=[0, 1, 2, 3]
                                                                )

        wmt2_layout.addRow("WMT2 Wave Gain", wmt2_wave_gain_combo)

        wmt2_wave_fxm_switch_combo = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_GAIN,
                                                                      "Wave FXM Switch",
                                                                      options=["OFF", "ON"],
                                                                      values=[0, 1]
                                                                      )
        wmt2_layout.addRow("WMT2 Wave FXM Switch", wmt2_wave_fxm_switch_combo)

        wmt2_wave_fxm_color_combo = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_FXM_COLOR,
                                                                   "Wave FXM Color",
                                                                   options=["OFF", "ON"],
                                                                   values=[0, 1]
                                                                   )
        wmt2_layout.addRow("WMT2 Wave FXM Color", wmt2_wave_fxm_color_combo)

        wmt2_wave_fxm_depth_combo = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_FXM_DEPTH,
                                                                   "Wave FXM Depth",
                                                                   options=["OFF", "ON"],
                                                                   values=[0, 1]
                                                                   )
        wmt2_layout.addRow("WMT2 Wave FXM Depth", wmt2_wave_fxm_depth_combo)

        wmt2_wave_tempo_sync_combo = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_TEMPO_SYNC,
                                                                      "Wave Tempo Sync",
                                                                      options=["OFF", "ON"],
                                                                      values=[0, 1]
                                                                      )
        wmt2_layout.addRow("WMT2 Wave Tempo Sync", wmt2_wave_tempo_sync_combo)

        wmt2_wave_coarse_tune_combo = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_COARSE_TUNE,
                                                                      "Wave Coarse Tune",
                                                                      options=["OFF", "ON"],
                                                                      values=[0, 1]
                                                                      )
        wmt2_layout.addRow("WMT2 Wave Coarse Tune", wmt2_wave_coarse_tune_combo)

        wmt2_wave_fine_tune_combo = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_FINE_TUNE,
                                                                      "Wave Fine Tune",
                                                                      options=["OFF", "ON"],
                                                                      values=[0, 1]
                                                                      )
        wmt2_layout.addRow("WMT2 Wave Fine Tune", wmt2_wave_fine_tune_combo)

        wmt2_wave_pan_combo = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_PAN,
                                                              "Wave Pan",
                                                              options=["OFF", "ON"],
                                                              values=[0, 1]
                                                              )
        wmt2_layout.addRow("WMT2 Wave Pan", wmt2_wave_pan_combo)

        wmt2_wave_random_pan_switch_combo = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_RANDOM_PAN_SWITCH,
                                                                            "Wave Random Pan Switch",
                                                                            options=["OFF", "ON"],
                                                                            values=[0, 1]
                                                                            )
        wmt2_layout.addRow(
            "WMT2 Wave Random Pan Switch", wmt2_wave_random_pan_switch_combo
        )

        wmt2_wave_alternate_pan_switch_combo = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_ALTERNATE_PAN_SWITCH,
                                                                                "Wave Alternate Pan Switch",
                                                                                options=["OFF", "ON", "REVERSE"],
                                                                                values=[0, 1, 2]
                                                                                )
        wmt2_layout.addRow(
            "WMT2 Wave Alternate Pan Switch", wmt2_wave_alternate_pan_switch_combo
        )

        wmt2_wave_level_combo = self._create_parameter_combo_box(DrumParameter.WMT2_WAVE_LEVEL,
                                                                "Wave Level",
                                                                options=["OFF", "ON"],
                                                                values=[0, 1]
                                                                )
        wmt2_layout.addRow("WMT2 Wave Level", wmt2_wave_level_combo)

        wmt2_velocity_range_lower_combo = self._create_parameter_combo_box(DrumParameter.WMT2_VELOCITY_RANGE_LOWER,
                                                                          "Velocity Range Lower",
                                                                          options=["OFF", "ON"],
                                                                          values=[0, 1]
                                                                          )
        wmt2_layout.addRow("WMT2 Velocity Range Lower", wmt2_velocity_range_lower_combo)

        wmt2_velocity_range_upper_combo = self._create_parameter_combo_box(DrumParameter.WMT2_VELOCITY_RANGE_UPPER,
                                                                          "Velocity Range Upper",
                                                                          options=["OFF", "ON"],
                                                                          values=[0, 1]
                                                                          )
        wmt2_layout.addRow("WMT2 Velocity Range Upper", wmt2_velocity_range_upper_combo)

        wmt2_velocity_fade_width_lower_combo = self._create_parameter_slider(DrumParameter.WMT2_VELOCITY_FADE_WIDTH_LOWER,
                                                                                "Velocity Fade Width Lower",
                                                                                )
        wmt2_layout.addRow(
            wmt2_velocity_fade_width_lower_combo
        )

        wmt2_velocity_fade_width_upper_combo = self._create_parameter_slider(DrumParameter.WMT2_VELOCITY_FADE_WIDTH_UPPER,
                                                                                "Velocity Fade Width Upper",
                                                                                )
        wmt2_layout.addRow(
            wmt2_velocity_fade_width_upper_combo
        )
        return wmt2_layout

    def _create_wmt3_layout(self):
        # Add controls to WMT3 tab
        wmt3_layout = QFormLayout()

        wmt3_wave_switch_combo = QComboBox()
        wmt3_wave_switch_combo.addItems(["OFF", "ON"])
        wmt3_layout.addRow("WMT3 Wave Switch", wmt3_wave_switch_combo)
        wmt3_wave_switch_combo.currentIndexChanged.connect(self._on_wmt3_wave_switch_changed)

        wmt3_wave_group_type_spin = QSpinBox()
        wmt3_wave_group_type_spin.setRange(0, 0)
        wmt3_layout.addRow("WMT3 Wave Group Type", wmt3_wave_group_type_spin)
        wmt3_wave_group_type_spin.valueChanged.connect(self._on_wmt3_wave_group_type_changed)

        wmt3_wave_group_id_spin = QSpinBox()
        wmt3_wave_group_id_spin.setRange(0, 16384)
        wmt3_layout.addRow("WMT3 Wave Group ID", wmt3_wave_group_id_spin)
        wmt3_wave_group_id_spin.valueChanged.connect(self._on_wmt3_wave_group_id_changed)

        wmt3_wave_number_l_spin = QSpinBox()
        wmt3_wave_number_l_spin.setRange(0, 16384)
        wmt3_layout.addRow("WMT3 Wave Number L", wmt3_wave_number_l_spin)
        wmt3_wave_number_l_spin.valueChanged.connect(self._on_wmt3_wave_number_l_changed)

        wmt3_wave_number_r_spin = QSpinBox()
        wmt3_wave_number_r_spin.setRange(0, 16384)
        wmt3_layout.addRow("WMT3 Wave Number R", wmt3_wave_number_r_spin)
        wmt3_wave_number_r_spin.valueChanged.connect(self._on_wmt3_wave_number_r_changed)

        wmt3_wave_gain_spin = QSpinBox()
        wmt3_wave_gain_spin.setRange(0, 3)
        wmt3_layout.addRow("WMT3 Wave Gain", wmt3_wave_gain_spin)
        wmt3_wave_gain_spin.valueChanged.connect(self._on_wmt3_wave_gain_changed)

        wmt3_wave_fxm_switch_combo = QComboBox()
        wmt3_wave_fxm_switch_combo.addItems(["OFF", "ON"])
        wmt3_layout.addRow("WMT3 Wave FXM Switch", wmt3_wave_fxm_switch_combo)
        wmt3_wave_fxm_switch_combo.currentIndexChanged.connect(self._on_wmt3_wave_fxm_switch_changed)

        wmt3_wave_fxm_color_spin = QSpinBox()
        wmt3_wave_fxm_color_spin.setRange(0, 3)
        wmt3_layout.addRow("WMT3 Wave FXM Color", wmt3_wave_fxm_color_spin)
        wmt3_wave_fxm_color_spin.valueChanged.connect(self._on_wmt3_wave_fxm_color_changed)

        wmt3_wave_fxm_depth_spin = QSpinBox()
        wmt3_wave_fxm_depth_spin.setRange(0, 16)
        wmt3_layout.addRow("WMT3 Wave FXM Depth", wmt3_wave_fxm_depth_spin)

        wmt3_wave_tempo_sync_combo = QComboBox()
        wmt3_wave_tempo_sync_combo.addItems(["OFF", "ON"])
        wmt3_layout.addRow("WMT3 Wave Tempo Sync", wmt3_wave_tempo_sync_combo)
        # wmt3_wave_tempo_sync_combo.currentIndexChanged.connect(self._on_wmt3_wave_tempo_sync_changed)

        wmt3_wave_coarse_tune_spin = QSpinBox()
        wmt3_wave_coarse_tune_spin.setRange(16, 112)
        wmt3_layout.addRow("WMT3 Wave Coarse Tune", wmt3_wave_coarse_tune_spin)
        wmt3_wave_coarse_tune_spin.valueChanged.connect(self._on_wmt3_wave_coarse_tune_changed)

        wmt3_wave_fine_tune_spin = QSpinBox()
        wmt3_wave_fine_tune_spin.setRange(14, 114)
        wmt3_layout.addRow("WMT3 Wave Fine Tune", wmt3_wave_fine_tune_spin)
        wmt3_wave_fine_tune_spin.valueChanged.connect(self._on_wmt3_wave_fine_tune_changed)

        wmt3_wave_pan_spin = QSpinBox()
        wmt3_wave_pan_spin.setRange(0, 127)
        wmt3_layout.addRow("WMT3 Wave Pan", wmt3_wave_pan_spin)
        wmt3_wave_pan_spin.valueChanged.connect(self._on_wmt3_wave_pan_changed)

        wmt3_wave_random_pan_switch_combo = QComboBox()
        wmt3_wave_random_pan_switch_combo.addItems(["OFF", "ON"])
        wmt3_layout.addRow(
            "WMT3 Wave Random Pan Switch", wmt3_wave_random_pan_switch_combo
        )

        wmt3_wave_alternate_pan_switch_combo = QComboBox()
        wmt3_wave_alternate_pan_switch_combo.addItems(["OFF", "ON", "REVERSE"])
        wmt3_layout.addRow(
            "WMT3 Wave Alternate Pan Switch", wmt3_wave_alternate_pan_switch_combo
        )
        wmt3_wave_alternate_pan_switch_combo.currentIndexChanged.connect(
            self._on_wmt3_wave_alternate_pan_switch_changed)

        wmt3_wave_level_spin = QSpinBox()
        wmt3_wave_level_spin.setRange(0, 127)
        wmt3_layout.addRow("WMT3 Wave Level", wmt3_wave_level_spin)
        wmt3_wave_level_spin.valueChanged.connect(self._on_wmt3_wave_level_changed)

        wmt3_velocity_range_lower_spin = QSpinBox()
        wmt3_velocity_range_lower_spin.setRange(1, 127)
        wmt3_layout.addRow("WMT3 Velocity Range Lower", wmt3_velocity_range_lower_spin)
        wmt3_velocity_range_lower_spin.valueChanged.connect(self._on_wmt3_velocity_range_lower_changed)

        wmt3_velocity_range_upper_spin = QSpinBox()
        wmt3_velocity_range_upper_spin.setRange(1, 127)
        wmt3_layout.addRow("WMT3 Velocity Range Upper", wmt3_velocity_range_upper_spin)
        wmt3_velocity_range_upper_spin.valueChanged.connect(self._on_wmt3_velocity_range_upper_changed)

        wmt3_velocity_fade_width_lower_spin = QSpinBox()
        wmt3_velocity_fade_width_lower_spin.setRange(0, 127)
        wmt3_layout.addRow(
            "WMT3 Velocity Fade Width Lower", wmt3_velocity_fade_width_lower_spin
        )
        wmt3_velocity_fade_width_lower_spin.valueChanged.connect(self._on_wmt3_velocity_fade_width_lower_changed)

        wmt3_velocity_fade_width_upper_spin = QSpinBox()
        wmt3_velocity_fade_width_upper_spin.setRange(0, 127)
        wmt3_layout.addRow(
            "WMT3 Velocity Fade Width Upper", wmt3_velocity_fade_width_upper_spin
        )
        wmt3_velocity_fade_width_upper_spin.valueChanged.connect(self._on_wmt3_velocity_fade_width_upper_changed)
        return wmt3_layout

    def _create_wmt4_layout(self):
        # Add controls to WMT4 tab
        # wmt4_tab = self.wmt_tab_widget.widget(3)
        wmt4_layout = QFormLayout()
        # wmt4_tab.setLayout(wmt4_layout)

        wmt4_wave_switch_combo = QComboBox()
        wmt4_wave_switch_combo.addItems(["OFF", "ON"])
        wmt4_layout.addRow("WMT4 Wave Switch", wmt4_wave_switch_combo)
        wmt4_wave_switch_combo.currentIndexChanged.connect(self._on_wmt4_wave_switch_changed)

        wmt4_wave_group_type_spin = QSpinBox()
        wmt4_wave_group_type_spin.setRange(0, 0)
        wmt4_layout.addRow("WMT4 Wave Group Type", wmt4_wave_group_type_spin)
        wmt4_wave_group_type_spin.valueChanged.connect(self._on_wmt4_wave_group_type_changed)

        wmt4_wave_group_id_spin = QSpinBox()
        wmt4_wave_group_id_spin.setRange(0, 16384)
        wmt4_layout.addRow("WMT4 Wave Group ID", wmt4_wave_group_id_spin)
        wmt4_wave_group_id_spin.valueChanged.connect(self._on_wmt4_wave_group_id_changed)

        wmt4_wave_number_l_spin = QSpinBox()
        wmt4_wave_number_l_spin.setRange(0, 16384)
        wmt4_layout.addRow("WMT4 Wave Number L", wmt4_wave_number_l_spin)
        wmt4_wave_number_l_spin.valueChanged.connect(self._on_wmt4_wave_number_l_changed)

        wmt4_wave_number_r_spin = QSpinBox()
        wmt4_wave_number_r_spin.setRange(0, 16384)
        wmt4_layout.addRow("WMT4 Wave Number R", wmt4_wave_number_r_spin)
        wmt4_wave_number_r_spin.valueChanged.connect(self._on_wmt4_wave_number_r_changed)

        wmt4_wave_gain_combo = QComboBox()
        wmt4_wave_gain_combo.addItems(["-6", "0", "+6", "+12"])
        wmt4_layout.addRow("WMT4 Wave Gain", wmt4_wave_gain_combo)
        wmt4_wave_gain_combo.currentIndexChanged.connect(self._on_wmt4_wave_gain_changed)

        wmt4_wave_fxm_switch_combo = QComboBox()
        wmt4_wave_fxm_switch_combo.addItems(["OFF", "ON"])
        wmt4_layout.addRow("WMT4 Wave FXM Switch", wmt4_wave_fxm_switch_combo)
        wmt4_wave_fxm_switch_combo.currentIndexChanged.connect(self._on_wmt4_wave_fxm_switch_changed)

        wmt4_wave_fxm_color_spin = QSpinBox()
        wmt4_wave_fxm_color_spin.setRange(0, 3)
        wmt4_layout.addRow("WMT4 Wave FXM Color", wmt4_wave_fxm_color_spin)
        wmt4_wave_fxm_color_spin.valueChanged.connect(self._on_wmt4_wave_fxm_color_changed)

        wmt4_wave_fxm_depth_spin = QSpinBox()
        wmt4_wave_fxm_depth_spin.setRange(0, 16)
        wmt4_layout.addRow("WMT4 Wave FXM Depth", wmt4_wave_fxm_depth_spin)

        wmt4_wave_tempo_sync_combo = QComboBox()
        wmt4_wave_tempo_sync_combo.addItems(["OFF", "ON"])
        wmt4_layout.addRow("WMT4 Wave Tempo Sync", wmt4_wave_tempo_sync_combo)
        wmt4_wave_tempo_sync_combo.currentIndexChanged.connect(self._on_wmt4_wave_tempo_sync_changed)

        wmt4_wave_coarse_tune_spin = QSpinBox()
        wmt4_wave_coarse_tune_spin.setRange(16, 112)
        wmt4_layout.addRow("WMT4 Wave Coarse Tune", wmt4_wave_coarse_tune_spin)

        wmt4_wave_fine_tune_spin = QSpinBox()
        wmt4_wave_fine_tune_spin.setRange(14, 114)
        wmt4_layout.addRow("WMT4 Wave Fine Tune", wmt4_wave_fine_tune_spin)
        wmt4_wave_fine_tune_spin.valueChanged.connect(self._on_wmt4_wave_fine_tune_changed)

        wmt4_wave_pan_spin = QSpinBox()
        wmt4_wave_pan_spin.setRange(0, 127)
        wmt4_layout.addRow("WMT4 Wave Pan", wmt4_wave_pan_spin)
        wmt4_wave_pan_spin.valueChanged.connect(self._on_wmt4_wave_pan_changed)

        wmt4_wave_random_pan_switch_combo = QComboBox()
        wmt4_wave_random_pan_switch_combo.addItems(["OFF", "ON"])
        wmt4_layout.addRow(
            "WMT4 Wave Random Pan Switch", wmt4_wave_random_pan_switch_combo
        )
        wmt4_wave_random_pan_switch_combo.currentIndexChanged.connect(self._on_wmt4_wave_random_pan_switch_changed)
        wmt4_wave_alternate_pan_switch_combo = QComboBox()
        wmt4_wave_alternate_pan_switch_combo.addItems(["OFF", "ON", "REVERSE"])
        wmt4_layout.addRow(
            "WMT4 Wave Alternate Pan Switch", wmt4_wave_alternate_pan_switch_combo
        )
        wmt4_wave_alternate_pan_switch_combo.currentIndexChanged.connect(
            self._on_wmt4_wave_alternate_pan_switch_changed)

        wmt4_wave_level_spin = QSpinBox()
        wmt4_wave_level_spin.setRange(0, 127)
        wmt4_layout.addRow("WMT4 Wave Level", wmt4_wave_level_spin)
        wmt4_wave_level_spin.valueChanged.connect(self._on_wmt4_wave_level_changed)

        wmt4_velocity_range_lower_spin = QSpinBox()
        wmt4_velocity_range_lower_spin.setRange(1, 127)
        wmt4_layout.addRow("WMT4 Velocity Range Lower", wmt4_velocity_range_lower_spin)
        wmt4_velocity_range_lower_spin.valueChanged.connect(self._on_wmt4_velocity_range_lower_changed)

        wmt4_velocity_range_upper_spin = QSpinBox()
        wmt4_velocity_range_upper_spin.setRange(1, 127)
        wmt4_layout.addRow("WMT4 Velocity Range Upper", wmt4_velocity_range_upper_spin)
        wmt4_velocity_range_upper_spin.valueChanged.connect(self._on_wmt4_velocity_range_upper_changed)

        wmt4_velocity_fade_width_lower_spin = QSpinBox()
        wmt4_velocity_fade_width_lower_spin.setRange(0, 127)
        wmt4_layout.addRow(
            "WMT4 Velocity Fade Width Lower", wmt4_velocity_fade_width_lower_spin
        )
        wmt4_velocity_fade_width_lower_spin.valueChanged.connect(self._on_wmt4_velocity_fade_width_lower_changed)

        wmt4_velocity_fade_width_upper_spin = QSpinBox()
        wmt4_velocity_fade_width_upper_spin.setRange(0, 127)
        wmt4_layout.addRow(
            "WMT4 Velocity Fade Width Upper", wmt4_velocity_fade_width_upper_spin
        )
        wmt4_velocity_fade_width_upper_spin.valueChanged.connect(self._on_wmt4_velocity_fade_width_upper_changed)
        return wmt4_layout

    def _on_wmt1_wave_switch_changed(self, value: int):
        """ change wmt1 wave switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_SWITCH.value[0],
            value=value
        )



    def _on_wmt1_wave_group_type_changed(self, value: int):
        """ change wmt1 wave group preset_type value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GROUP_TYPE.value[0],
            value=value
        )

    def _on_wmt1_wave_group_id_changed(self, value: int):
        """ change wmt1 wave group id value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GROUP_ID.value[0],
            value=value
        )

    def _on_wmt1_wave_number_l_changed(self, value: int):
        """ change wmt1 wave number l value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_NUMBER_L.value[0],
            value=value,
            size=4
        )

    def _on_wmt1_wave_number_r_changed(self, value: int):
        """ change wmt1 wave number r value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )

    def _on_wmt1_wave_gain_changed(self, value: int):
        """ change wmt1 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_GAIN.value[0],
            value=value
        )

    def _on_wmt1_wave_fxm_switch_changed(self, value: int):
        """ change wmt1 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_SWITCH.value[0],
            value=value
        )

    def _on_wmt1_wave_fxm_color_changed(self, value: int):
        """ change wmt1 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_COLOR.value[0],
            value=value
        )

    def _on_wmt1_wave_fxm_depth_changed(self, value: int):
        """ change wmt1 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FXM_DEPTH.value[0],
            value=value
        )

    def _on_wmt1_wave_coarse_tune_changed(self, value: int):
        """ change wmt1 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_COARSE_TUNE.value[0],
            value=value
        )

    def _on_wmt1_wave_tempo_sync_changed(self, value: int):
        """ change wmt1 wave tempo sync value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_TEMPO_SYNC.value[0],
            value=value
        )

    def _on_wmt1_wave_fine_tune_changed(self, value: int):
        """ change wmt1 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_FINE_TUNE.value[0],
            value=value
        )

    def _on_wmt1_wave_pan_changed(self, value: int):
        """ change wmt1 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_PAN.value[0],
            value=value
        )

    def _on_wmt1_wave_random_pan_switch_changed(self, value: int):
        """ change wmt1 wave random pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )

    def _on_wmt1_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt1 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )

    def _on_wmt1_wave_level_changed(self, value: int):
        """ change wmt1 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_WAVE_LEVEL.value[0],
            value=value
        )

    def _on_wmt1_velocity_range_lower_changed(self, value: int):
        """ change wmt1 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )

    def _on_wmt1_velocity_range_upper_changed(self, value: int):
        """ change wmt1 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )

    def _on_wmt1_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt1 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )

    def _on_wmt1_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt1 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )

    def _on_wmt1_wave_r_changed(self, value: int):
        """Handle WMT1 Wave R parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_TONE_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,  # Use self.partial_address instead of partial_address
            param=DrumParameter.WMT1_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )

    def _create_pitch_group(self):
        """Create the pitch group."""
        # Pitch Group
        pitch_group = QGroupBox("Pitch")
        pitch_layout = QFormLayout()
        pitch_group.setLayout(pitch_layout)
        # grid_layout.addWidget(pitch_group, 0, 0)

        # Add pitch parameters
        partial_level_slider = self._create_parameter_slider(
            DrumParameter.PARTIAL_LEVEL, "Partial Level"
        )
        pitch_layout.addRow(partial_level_slider)

        partial_coarse_tune_slider = self._create_parameter_slider(
            DrumParameter.PARTIAL_COARSE_TUNE, "Partial Coarse Tune"
        )
        pitch_layout.addRow(partial_coarse_tune_slider)

        partial_fine_tune_slider = self._create_parameter_slider(
            DrumParameter.PARTIAL_FINE_TUNE, "Partial Fine Tune"
        )
        pitch_layout.addRow(partial_fine_tune_slider)

        partial_random_pitch_depth_slider = self._create_parameter_slider(
            DrumParameter.PARTIAL_RANDOM_PITCH_DEPTH, "Partial Random Pitch Depth"
        )
        pitch_layout.addRow(partial_random_pitch_depth_slider)

        partial_pan_slider = self._create_parameter_slider(
            DrumParameter.PARTIAL_PAN, "Partial Pan"
        )
        pitch_layout.addRow(partial_pan_slider)

        partial_random_pan_depth_slider = self._create_parameter_slider(
            DrumParameter.PARTIAL_RANDOM_PAN_DEPTH, "Partial Random Pan Depth"
        )
        pitch_layout.addRow(partial_random_pan_depth_slider)

        partial_alternate_pan_depth_slider = self._create_parameter_slider(
            DrumParameter.PARTIAL_ALTERNATE_PAN_DEPTH, "Partial Alternate Pan Depth"
        )
        pitch_layout.addRow(partial_alternate_pan_depth_slider)

        partial_env_mode_combo = QComboBox()
        partial_env_mode_combo.addItems(["0", "1"])
        pitch_layout.addRow("Partial Env Mode", partial_env_mode_combo)
        partial_env_mode_combo.currentIndexChanged.connect(
            self.on_partial_env_mode_changed
        )

        return pitch_group

    def _create_output_group(self):
        # Output Group
        output_group = QGroupBox("Output")
        output_layout = QFormLayout()
        output_group.setLayout(output_layout)

        # Add output parameters
        partial_output_level_slider = self._create_parameter_slider(
            DrumParameter.PARTIAL_OUTPUT_LEVEL, "Partial Output Level"
        )
        output_layout.addRow(partial_output_level_slider)

        partial_chorus_send_level_slider = self._create_parameter_slider(
            DrumParameter.PARTIAL_CHORUS_SEND_LEVEL, "Partial Chorus Send Level"
        )
        output_layout.addRow(partial_chorus_send_level_slider)

        partial_reverb_send_level_slider = self._create_parameter_slider(
            DrumParameter.PARTIAL_REVERB_SEND_LEVEL, "Partial Reverb Send Level"
        )
        output_layout.addRow(partial_reverb_send_level_slider)

        partial_output_assign_combo = QComboBox()
        partial_output_assign_combo.addItems(["EFX1", "EFX2", "DLY", "REV", "DIR"])
        output_layout.addRow("Partial Output Assign", partial_output_assign_combo)

        return output_group

    def _create_tvf_group(self):
        """create tvf group"""
        # TVF Group
        tvf_group = QGroupBox("TVF")
        tvf_layout = QFormLayout()
        tvf_group.setLayout(tvf_layout)

        # Add TVF parameters
        tvf_filter_type_combo = QComboBox()
        tvf_filter_type_combo.addItems(
            ["OFF", "LPF", "BPF", "HPF", "PKG", "LPF2", "LPF3"]
        )
        tvf_filter_type_combo.currentIndexChanged.connect(
            self._on_tvf_filter_type_combo_changed
        )
        tvf_layout.addRow("Filter Type", tvf_filter_type_combo)

        tvf_cutoff_frequency_slider = self._create_parameter_slider(
            DrumParameter.TVF_CUTOFF_FREQUENCY, "TVF Cutoff"
        )
        tvf_layout.addRow(tvf_cutoff_frequency_slider)

        tvf_cutoff_velocity_curve_spin = QSpinBox()
        tvf_cutoff_velocity_curve_spin.setRange(0, 7)
        tvf_cutoff_velocity_curve_spin.valueChanged.connect(
            self._on_tvf_cutoff_velocity_curve_spin_changed
        )
        tvf_layout.addRow("Cutoff Velocity Curve", tvf_cutoff_velocity_curve_spin)

        tvf_env_depth_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_DEPTH, "Env Depth"
        )
        tvf_layout.addRow(tvf_env_depth_slider)

        tvf_env_velocity_curve_type_spin = QSpinBox()
        tvf_env_velocity_curve_type_spin.setRange(0, 7)
        tvf_env_velocity_curve_type_spin.valueChanged.connect(
            self._on_tvf_env_velocity_curve_type_spin_changed
        )
        tvf_layout.addRow(
            "Env Velocity Curve Type", tvf_env_velocity_curve_type_spin
        )

        tvf_env_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_VELOCITY_SENS, "Env Velocity Sens"
        )
        tvf_layout.addRow(tvf_env_velocity_sens_slider)

        tvf_env_time1_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_TIME_1_VELOCITY_SENS, "Env Time 1 Velocity Sens"
        )
        tvf_layout.addRow(tvf_env_time1_velocity_sens_slider)

        tvf_env_time4_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_TIME_4_VELOCITY_SENS, "Env Time 4 Velocity Sens"
        )
        tvf_layout.addRow(tvf_env_time4_velocity_sens_slider)

        tvf_env_time1_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_TIME_1, "Env Time 1"
        )
        tvf_layout.addRow(tvf_env_time1_slider)

        tvf_env_time2_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_TIME_2, "Env Time 2"
        )
        tvf_layout.addRow(tvf_env_time2_slider)

        tvf_env_time3_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_TIME_3, "Env Time 3"
        )
        tvf_layout.addRow(tvf_env_time3_slider)

        tvf_env_time4_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_TIME_4, "Env Time 4"
        )
        tvf_layout.addRow(tvf_env_time4_slider)

        tvf_env_level0_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_LEVEL_0, "Env Level 0"
        )
        tvf_layout.addRow(tvf_env_level0_slider)

        tvf_env_level1_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_LEVEL_1, "Env Level 1"
        )
        tvf_layout.addRow(tvf_env_level1_slider)

        tvf_env_level2_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_LEVEL_2, "Env Level 2"
        )
        tvf_layout.addRow(tvf_env_level2_slider)

        tvf_env_level3_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_LEVEL_3, "Env Level 3"
        )
        tvf_layout.addRow(tvf_env_level3_slider)

        tvf_env_level4_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_LEVEL_4, "Env Level 4"
        )
        tvf_layout.addRow(tvf_env_level4_slider)
        return tvf_group

    def _create_pitch_env_group(self):
        """create pitch env group"""
        # Pitch Env Group
        pitch_env_group = QGroupBox("Pitch Env")
        pitch_env_layout = QFormLayout()
        pitch_env_group.setLayout(pitch_env_layout)

        # Add pitch env parameters
        pitch_env_depth_slider = self._create_parameter_slider(
            DrumParameter.PITCH_ENV_DEPTH, "Pitch Env Depth"
        )
        pitch_env_layout.addRow(pitch_env_depth_slider)

        pitch_env_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.PITCH_ENV_VELOCITY_SENS, "Pitch Env Velocity Sens"
        )
        pitch_env_layout.addRow(pitch_env_velocity_sens_slider)

        pitch_env_time1_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.PITCH_ENV_TIME_1_VELOCITY_SENS,
            "Pitch Env Time 1 Velocity Sens",
        )
        pitch_env_layout.addRow(pitch_env_time1_velocity_sens_slider)

        pitch_env_time4_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.PITCH_ENV_TIME_4_VELOCITY_SENS,
            "Pitch Env Time 4 Velocity Sens",
        )
        pitch_env_layout.addRow(pitch_env_time4_velocity_sens_slider)

        pitch_env_time1_slider = self._create_parameter_slider(
            DrumParameter.PITCH_ENV_TIME_1, "Pitch Env Time 1"
        )
        pitch_env_layout.addRow(pitch_env_time1_slider)

        pitch_env_time2_slider = self._create_parameter_slider(
            DrumParameter.PITCH_ENV_TIME_2, "Pitch Env Time 2"
        )
        pitch_env_layout.addRow(pitch_env_time2_slider)

        pitch_env_time3_slider = self._create_parameter_slider(
            DrumParameter.PITCH_ENV_TIME_3, "Pitch Env Time 3"
        )
        pitch_env_layout.addRow(pitch_env_time3_slider)

        pitch_env_time4_slider = self._create_parameter_slider(
            DrumParameter.PITCH_ENV_TIME_4, "Pitch Env Time 4"
        )
        pitch_env_layout.addRow(pitch_env_time4_slider)

        pitch_env_level0_slider = self._create_parameter_slider(
            DrumParameter.PITCH_ENV_LEVEL_0, "Pitch Env Level 0"
        )
        pitch_env_layout.addRow(pitch_env_level0_slider)

        pitch_env_level1_slider = self._create_parameter_slider(
            DrumParameter.PITCH_ENV_LEVEL_1, "Pitch Env Level 1"
        )
        pitch_env_layout.addRow(pitch_env_level1_slider)

        pitch_env_level2_slider = self._create_parameter_slider(
            DrumParameter.PITCH_ENV_LEVEL_2, "Pitch Env Level 2"
        )
        pitch_env_layout.addRow(pitch_env_level2_slider)

        pitch_env_level3_slider = self._create_parameter_slider(
            DrumParameter.PITCH_ENV_LEVEL_3, "Pitch Env Level 3"
        )
        pitch_env_layout.addRow(pitch_env_level3_slider)

        pitch_env_level4_slider = self._create_parameter_slider(
            DrumParameter.PITCH_ENV_LEVEL_4, "Pitch Env Level 4"
        )
        pitch_env_layout.addRow(pitch_env_level4_slider)
        return pitch_env_group

    def on_partial_env_mode_changed(self, value):
        """Handle partial envelope mode combo box value change"""
        # Use the helper function to send the SysEx message @@ FIXME
        self.send_sysex_message(0x0B, value)

    def send_sysex_message(self, address: int, value: int):
        """Helper function to send address SysEx message with address given address and value."""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=group,
            param=address,
            value=value,  # Make sure this value is being sent
        )

    def _on_tva_level_velocity_sens_slider_changed(self, value: int):
        """Handle TVA Level Velocity Sens change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_LEVEL_VELOCITY_SENS.value[0],
                value=value,
            )
            print(f"TVA Level Velocity Sens changed to {value}")

    def _on_tva_env_time1_velocity_sens_slider_changed(self, value: int):
        """Handle TVA Env Time 1 Velocity Sens change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_TIME_1_VELOCITY_SENS.value[0],
                value=value,
            )
            print(f"TVA Env Time 1 Velocity Sens changed to {value}")

    def _on_tva_env_time4_velocity_sens_slider_changed(self, value: int):
        """Handle TVA Env Time 4 Velocity Sens change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_TIME_4_VELOCITY_SENS.value[0],
                value=value,
            )
            print(f"TVA Env Time 4 Velocity Sens changed to {value}")

    def _on_tva_env_time1_slider_changed(self, value: int):
        """Handle TVA Env Time 1 change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_TIME_1.value[0],
                value=value,
            )
            print(f"TVA Env Time 1 changed to {value}")

    def _on_tva_env_time2_slider_changed(self, value: int):
        """Handle TVA Env Time 2 change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_TIME_2.value[0],
                value=value,
            )
            print(f"TVA Env Time 2 changed to {value}")

    def _on_tva_env_time3_slider_changed(self, value: int):
        """Handle TVA Env Time 3 change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_TIME_3.value[0],
                value=value,
            )
            print(f"TVA Env Time 3 changed to {value}")

    def _on_tva_env_level1_slider_changed(self, value: int):
        """Handle TVA Env Level 1 change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_LEVEL_1.value[0],
                value=value,
            )
            print(f"TVA Env Level 1 changed to {value}")

    def _on_tva_env_level2_slider_changed(self, value: int):
        """Handle TVA Env Level 2 change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_LEVEL_2.value[0],
                value=value,
            )
            print(f"TVA Env Level 2 changed to {value}")

    def _on_tva_env_level3_slider_changed(self, value: int):
        """Handle TVA Env Level 3 change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVA_ENV_LEVEL_3.value[0],
                value=value,
            )
            print(f"TVA Env Level 3 changed to {value}")

    def _on_tvf_filter_type_combo_changed(self, index: int):
        """Handle TVF Filter Type change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_FILTER_TYPE.value[0],
                value=index,
            )
            print(f"TVF Filter Type changed to {index}")

    def _on_tvf_cutoff_frequency_slider_changed(self, value: int):
        """Handle TVF Cutoff Frequency change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_CUTOFF_FREQUENCY.value[0],
                value=value,
            )
            print(f"TVF Cutoff Frequency changed to {value}")

    def _on_tvf_cutoff_velocity_curve_spin_changed(self, value: int):
        """Handle TVF Cutoff Velocity Curve change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_CUTOFF_VELOCITY_CURVE.value[0],
                value=value,
            )
            print(f"TVF Cutoff Velocity Curve changed to {value}")

    def _on_tvf_cutoff_velocity_sens_slider_changed(self, value: int):
        """Handle TVF Cutoff Velocity Sens change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_CUTOFF_VELOCITY_SENS.value[0],
                value=value,
            )
            print(f"TVF Cutoff Velocity Sens changed to {value}")

    def _on_tvf_env_depth_slider_changed(self, value: int):
        """Handle TVF Env Depth change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_ENV_DEPTH.value[0],
                value=value,
            )
            print(f"TVF Env Depth changed to {value}")

    def _on_tvf_env_velocity_curve_type_spin_changed(self, value: int):
        """Handle TVF Env Velocity Curve Type change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_ENV_VELOCITY_CURVE_TYPE.value[0],
                value=value,
            )
            print(f"TVF Env Velocity Curve Type changed to {value}")

    def _on_tvf_env_velocity_sens_slider_changed(self, value: int):
        """Handle TVF Env Velocity Sens change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_ENV_VELOCITY_SENS.value[0],
                value=value,
            )
            print(f"TVF Env Velocity Sens changed to {value}")

    def _on_tvf_env_time1_velocity_sens_slider_changed(self, value: int):
        """Handle TVF Env Time 1 Velocity Sens change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_ENV_TIME_1_VELOCITY_SENS.value[0],
                value=value,
            )
            print(f"TVF Env Time 1 Velocity Sens changed to {value}")

    def _create_parameter_slider(
            self, param: DrumParameter, label: str = None
    ) -> Slider:
        """Create address slider for address parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        slider = Slider(label, display_min, display_max)

        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = slider
        return slider

    def _create_parameter_combo_box(self, param: DrumParameter, label: str = None, options: list = None,
                                    values: list = None) -> ComboBox:
        """Create address combo box for address parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        combo_box = ComboBox(label, options, values)

        # Connect value changed signal
        combo_box.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = combo_box
        return combo_box

    def _create_parameter_spin_box(self, param: DrumParameter, label: str = None) -> SpinBox:
        """Create address spin box for address parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        spin_box = SpinBox(label, display_min, display_max)

        # Connect value changed signal
        spin_box.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = spin_box
        return spin_box

    def send_midi_parameter(self, param: DrumParameter, value: int) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False
        # @@ Length exceptions
        if param in [DrumParameter.WMT1_WAVE_NUMBER_L,
                     DrumParameter.WMT1_WAVE_NUMBER_R,
                     DrumParameter.WMT2_WAVE_NUMBER_L,
                     DrumParameter.WMT2_WAVE_NUMBER_R,
                     DrumParameter.WMT3_WAVE_NUMBER_L,
                     DrumParameter.WMT3_WAVE_NUMBER_R,
                     DrumParameter.WMT4_WAVE_NUMBER_L,
                     DrumParameter.WMT4_WAVE_NUMBER_R]:
            size = 4
        else:
            size = 1
        logging.info(f"parameter param {param} value {value} size {size} sent")
        try:
            # Ensure value is included in the MIDI message
            return self.midi_helper.send_parameter(
                area=TEMPORARY_TONE_AREA,
                part=DRUM_KIT_AREA,
                group=self.partial_address,
                param=param.address,
                value=value,  # Make sure this value is being sent
                size=size
            )
        except Exception as ex:
            logging.error(f"MIDI error setting {param}: {str(ex)}")
            return False

    def _on_parameter_changed(self, param: DrumParameter, display_value: int):
        """Handle parameter value changes from UI controls"""
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(display_value)
            else:
                midi_value = param.validate_value(display_value)
            logging.info(f"parameter: {param} display {display_value} midi value {midi_value}")
            # Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")

        except Exception as ex:
            logging.error(f"Error handling parameter {param.name}: {str(ex)}")

    def set_partial_num(self, partial_num: int):
        """Set the current partial number"""
        if 0 <= partial_num < len(DRUM_ADDRESSES):
            self.partial_num = partial_num
        else:
            raise ValueError(f"Invalid partial number: {partial_num}")

    def update_partial_num(self, index: int):
        """Update the partial number based on the current tab index"""
        self.set_partial_num(index)

        # Validate partial_name
        if self.partial_num < 0 or self.partial_num >= len(DRUM_ADDRESSES):
            logging.error(f"Invalid partial number: {self.partial_num}")
            return

        # Get the address for the current partial
        try:
            self.partial_address, self.partial_address = get_address_for_partial(self.partial_num)
            logging.info(
                f"Updated partial number to {self.partial_num}, group: {hex(self.partial_address)}, address: {hex(self.partial_address)}"
            )
            print(
                f"Updated partial number to {self.partial_num}, group: {hex(self.partial_address)}, address: {hex(self.partial_address)}"
            )
        except Exception as e:
            logging.error(
                f"Error getting address for partial {self.partial_num}: {str(e)}"
            )

            def _on_wmt1_wave_switch_changed(self, value: int):
                """ change wmt1 wave switch value """
                return self.midi_helper.send_parameter(
                    area=TEMPORARY_TONE_AREA,
                    part=DRUM_KIT_AREA,
                    group=self.partial_address,
                    param=DrumParameter.WMT1_WAVE_SWITCH.value[0],
                    value=value
                )

    def _on_wmt3_wave_switch_changed(self, value: int):
        """ change wmt3 wave switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_SWITCH.value[0],
            value=value
        )

    def _on_wmt3_wave_group_type_changed(self, value: int):
        """ change wmt3 wave group preset_type value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_GROUP_TYPE.value[0],
            value=value
        )

    def _on_wmt3_wave_group_id_changed(self, value: int):
        """ change wmt3 wave group id value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_GROUP_ID.value[0],
            value=value
        )

    def _on_wmt3_wave_number_l_changed(self, value: int):
        """ change wmt3 wave number l value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_NUMBER_L.value[0],
            value=value,
            size=4
        )

    def _on_wmt3_wave_number_r_changed(self, value: int):
        """ change wmt3 wave number r value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )

    def _on_wmt3_wave_gain_changed(self, value: int):
        """ change wmt3 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_GAIN.value[0],
            value=value
        )

    def _on_wmt3_wave_fxm_switch_changed(self, value: int):
        """ change wmt3 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_FXM_SWITCH.value[0],
            value=value
        )

    def _on_wmt3_wave_fxm_color_changed(self, value: int):
        """ change wmt3 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_FXM_COLOR.value[0],
            value=value
        )

    def _on_wmt3_wave_fxm_depth_changed(self, value: int):
        """ change wmt3 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_FXM_DEPTH.value[0],
            value=value
        )

    def _on_wmt3_wave_coarse_tune_changed(self, value: int):
        """ change wmt3 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_COARSE_TUNE.value[0],
            value=value
        )

    def _on_wmt3_wave_fine_tune_changed(self, value: int):
        """ change wmt3 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_FINE_TUNE.value[0],
            value=value
        )

    def _on_wmt3_wave_pan_changed(self, value: int):
        """ change wmt3 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_PAN.value[0],
            value=value
        )

    def _on_wmt3_wave_random_pan_switch_changed(self, value: int):
        """ change wmt3 wave random pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )

    def _on_wmt3_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt3 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )

    def _on_wmt3_wave_level_changed(self, value: int):
        """ change wmt3 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_WAVE_LEVEL.value[0],
            value=value
        )

    def _on_wmt3_velocity_range_lower_changed(self, value: int):
        """ change wmt3 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )

    def _on_wmt3_velocity_range_upper_changed(self, value: int):
        """ change wmt3 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )

    def _on_wmt3_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt3 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )

    def _on_wmt3_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt3 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT3_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )

    def _on_wmt4_wave_switch_changed(self, value: int):
        """ change wmt4 wave switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_SWITCH.value[0],
            value=value
        )

    def _on_wmt4_wave_group_type_changed(self, value: int):
        """ change wmt4 wave group preset_type value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_GROUP_TYPE.value[0],
            value=value
        )

    def _on_wmt4_wave_group_id_changed(self, value: int):
        """ change wmt4 wave group id value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_GROUP_ID.value[0],
            value=value
        )

    def _on_wmt4_wave_number_l_changed(self, value: int):
        """ change wmt4 wave number l value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_NUMBER_L.value[0],
            value=value,
            size=4
        )

    def _on_wmt4_wave_number_r_changed(self, value: int):
        """ change wmt4 wave number r value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_NUMBER_R.value[0],
            value=value,
            size=4
        )

    def _on_wmt4_wave_gain_changed(self, value: int):
        """ change wmt4 wave gain value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_GAIN.value[0],
            value=value
        )

    def _on_wmt4_wave_fxm_switch_changed(self, value: int):
        """ change wmt4 wave fxm switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_FXM_SWITCH.value[0],
            value=value
        )

    def _on_wmt4_wave_fxm_color_changed(self, value: int):
        """ change wmt4 wave fxm color value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_FXM_COLOR.value[0],
            value=value
        )

    def _on_wmt4_wave_fxm_depth_changed(self, value: int):
        """ change wmt4 wave fxm depth value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_FXM_DEPTH.value[0],
            value=value
        )

    def _on_wmt4_wave_tempo_sync_changed(self, value: int):
        """ change wmt4 wave tempo sync value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_TEMPO_SYNC.value[0],
            value=value
        )

    def _on_wmt4_wave_coarse_tune_changed(self, value: int):
        """ change wmt4 wave coarse tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_COARSE_TUNE.value[0],
            value=value
        )

    def _on_wmt4_wave_fine_tune_changed(self, value: int):
        """ change wmt4 wave fine tune value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_FINE_TUNE.value[0],
            value=value
        )

    def _on_wmt4_wave_pan_changed(self, value: int):
        """ change wmt4 wave pan value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_PAN.value[0],
            value=value
        )

    def _on_wmt4_wave_random_pan_switch_changed(self, value: int):
        """ change wmt4 wave random pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_RANDOM_PAN_SWITCH.value[0],
            value=value
        )

    def _on_wmt4_wave_alternate_pan_switch_changed(self, value: int):
        """ change wmt4 wave alternate pan switch value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_ALTERNATE_PAN_SWITCH.value[0],
            value=value
        )

    def _on_wmt4_wave_level_changed(self, value: int):
        """ change wmt4 wave level value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_WAVE_LEVEL.value[0],
            value=value
        )

    def _on_wmt4_velocity_range_lower_changed(self, value: int):
        """ change wmt4 velocity range lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_VELOCITY_RANGE_LOWER.value[0],
            value=value
        )

    def _on_wmt4_velocity_range_upper_changed(self, value: int):
        """ change wmt4 velocity range upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_VELOCITY_RANGE_UPPER.value[0],
            value=value
        )

    def _on_wmt4_velocity_fade_width_lower_changed(self, value: int):
        """ change wmt4 velocity fade width lower value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_VELOCITY_FADE_WIDTH_LOWER.value[0],
            value=value
        )

    def _on_wmt4_velocity_fade_width_upper_changed(self, value: int):
        """ change wmt4 velocity fade width upper value """
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.WMT4_VELOCITY_FADE_WIDTH_UPPER.value[0],
            value=value
        )

    def _on_coarse_tune_changed(self, value: int):
        """Handle Coarse Tune parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.COARSE_TUNE.value[0],
            value=value,
            size=1
        )

    def _on_fine_tune_changed(self, value: int):
        """Handle Fine Tune parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.FINE_TUNE.value[0],
            value=value,
            size=1
        )

    def _on_level_changed(self, value: int):
        """Handle Level parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.LEVEL.value[0],
            value=value,
            size=1
        )

    def _on_pan_changed(self, value: int):
        """Handle Pan parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.PAN.value[0],
            value=value,
            size=1
        )

    def _on_cutoff_changed(self, value: int):
        """Handle Cutoff parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.TVF_CUTOFF.value[0],
            value=value,
            size=1
        )

    def _on_resonance_changed(self, value: int):
        """Handle Resonance parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.TVF_RESONANCE.value[0],
            value=value,
            size=1
        )

    def _on_pitch_env_attack_changed(self, value: int):
        """Handle Pitch Envelope Attack parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.PITCH_ENV_ATTACK.value[0],
            value=value,
            size=1
        )

    def _on_pitch_env_decay_changed(self, value: int):
        """Handle Pitch Envelope Decay parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.PITCH_ENV_DECAY.value[0],
            value=value,
            size=1
        )

    def _on_tva_attack_changed(self, value: int):
        """Handle TVA Attack parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.TVA_ATTACK.value[0],
            value=value,
            size=1
        )

    def _on_tva_decay_changed(self, value: int):
        """Handle TVA Decay parameter change"""
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=DRUM_KIT_AREA,
            group=self.partial_address,
            param=DrumParameter.TVA_DECAY.value[0],
            value=value,
            size=1
        )