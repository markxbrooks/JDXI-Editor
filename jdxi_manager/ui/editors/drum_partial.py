import logging
import os
import re
from typing import Dict

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
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
from jdxi_manager.data.drums import get_address_for_partial, DRUM_ADDRESSES
from jdxi_manager.data.parameter.drums import DrumParameter
from jdxi_manager.midi.constants import (
    TEMPORARY_DRUM_KIT_AREA,
    TEMPORARY_DIGITAL_SYNTH_1_AREA,
)
from jdxi_manager.data.parameter.drums import get_address_for_partial_name
from jdxi_manager.midi.preset.loader import PresetLoader
from jdxi_manager.ui.widgets.slider import Slider

instrument_icon_folder = "drum_kits"


class DrumPartialEditor(QWidget):
    """Editor for a single partial"""

    def __init__(self, midi_helper=None, partial_num=0, partial_name=None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.partial_num = partial_num  # This is now the numerical index
        self.partial_name = partial_name  # This is now the numerical index

        # Calculate the address for this partial
        try:
            from jdxi_manager.data.drums import get_address_for_partial

            self.address = get_address_for_partial_name(self.partial_name)
            logging.info(
                f"Initialized partial {partial_num} with address: {hex(self.address)}"
            )
        except Exception as e:
            logging.error(
                f"Error calculating address for partial {partial_num}: {str(e)}"
            )
            self.address = 0x00

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
        tva_layout.addRow("TVA Level Velocity Curve", tva_level_velocity_curve_spin)

        tva_level_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.TVA_LEVEL_VELOCITY_SENS, "TVA Level Velocity Sens"
        )
        tva_layout.addRow(tva_level_velocity_sens_slider)

        tva_env_time1_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_TIME_1_VELOCITY_SENS, "TVA Env Time 1 Velocity Sens"
        )
        tva_layout.addRow(tva_env_time1_velocity_sens_slider)

        tva_env_time4_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_TIME_4_VELOCITY_SENS, "TVA Env Time 4 Velocity Sens"
        )
        tva_layout.addRow(tva_env_time4_velocity_sens_slider)

        tva_env_time1_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_TIME_1, "TVA Env Time 1"
        )
        tva_layout.addRow(tva_env_time1_slider)

        tva_env_time2_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_TIME_2, "TVA Env Time 2"
        )
        tva_layout.addRow(tva_env_time2_slider)

        tva_env_time3_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_TIME_3, "TVA Env Time 3"
        )
        tva_layout.addRow(tva_env_time3_slider)

        tva_env_time4_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_TIME_4, "TVA Env Time 4"
        )
        tva_layout.addRow(tva_env_time4_slider)

        tva_env_level1_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_LEVEL_1, "TVA Env Level 1"
        )
        tva_layout.addRow(tva_env_level1_slider)

        tva_env_level2_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_LEVEL_2, "TVA Env Level 2"
        )
        tva_layout.addRow(tva_env_level2_slider)

        tva_env_level3_slider = self._create_parameter_slider(
            DrumParameter.TVA_ENV_LEVEL_3, "TVA Env Level 3"
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
        wmt_tab_widget = QTabWidget()
        wmt_tabs = ["WMT1", "WMT2", "WMT3", "WMT4"]
        for wmt_tab in wmt_tabs:
            wmt_tab_widget.addTab(QWidget(), wmt_tab)
        wmt_layout.addWidget(wmt_tab_widget)

        # Add controls to WMT1 tab
        wmt1_tab = wmt_tab_widget.widget(0)
        wmt1_layout = QFormLayout()
        wmt1_tab.setLayout(wmt1_layout)

        wmt1_wave_switch_combo = QComboBox()
        wmt1_wave_switch_combo.addItems(["OFF", "ON"])
        wmt1_layout.addRow("WMT1 Wave Switch", wmt1_wave_switch_combo)

        wmt1_wave_group_type_spin = QSpinBox()
        wmt1_wave_group_type_spin.setRange(0, 0)
        wmt1_layout.addRow("WMT1 Wave Group Type", wmt1_wave_group_type_spin)

        wmt1_wave_group_id_spin = QSpinBox()
        wmt1_wave_group_id_spin.setRange(0, 16384)
        wmt1_layout.addRow("WMT1 Wave Group ID", wmt1_wave_group_id_spin)

        wmt1_wave_number_l_spin = QSpinBox()
        wmt1_wave_number_l_spin.setRange(0, 16384)
        wmt1_layout.addRow("WMT1 Wave Number L", wmt1_wave_number_l_spin)

        wmt1_wave_number_r_spin = QSpinBox()
        wmt1_wave_number_r_spin.setRange(0, 16384)
        wmt1_layout.addRow("WMT1 Wave Number R", wmt1_wave_number_r_spin)

        wmt1_wave_gain_spin = QSpinBox()
        wmt1_wave_gain_spin.setRange(0, 3)
        wmt1_layout.addRow("WMT1 Wave Gain", wmt1_wave_gain_spin)

        wmt1_wave_fxm_switch_combo = QComboBox()
        wmt1_wave_fxm_switch_combo.addItems(["OFF", "ON"])
        wmt1_layout.addRow("WMT1 Wave FXM Switch", wmt1_wave_fxm_switch_combo)

        wmt1_wave_fxm_color_spin = QSpinBox()
        wmt1_wave_fxm_color_spin.setRange(0, 3)
        wmt1_layout.addRow("WMT1 Wave FXM Color", wmt1_wave_fxm_color_spin)

        wmt1_wave_fxm_depth_spin = QSpinBox()
        wmt1_wave_fxm_depth_spin.setRange(0, 16)
        wmt1_layout.addRow("WMT1 Wave FXM Depth", wmt1_wave_fxm_depth_spin)

        wmt1_wave_tempo_sync_combo = QComboBox()
        wmt1_wave_tempo_sync_combo.addItems(["OFF", "ON"])
        wmt1_layout.addRow("WMT1 Wave Tempo Sync", wmt1_wave_tempo_sync_combo)

        wmt1_wave_coarse_tune_spin = QSpinBox()
        wmt1_wave_coarse_tune_spin.setRange(16, 112)
        wmt1_layout.addRow("WMT1 Wave Coarse Tune", wmt1_wave_coarse_tune_spin)

        wmt1_wave_fine_tune_spin = QSpinBox()
        wmt1_wave_fine_tune_spin.setRange(14, 114)
        wmt1_layout.addRow("WMT1 Wave Fine Tune", wmt1_wave_fine_tune_spin)

        wmt1_wave_pan_spin = QSpinBox()
        wmt1_wave_pan_spin.setRange(0, 127)
        wmt1_layout.addRow("WMT1 Wave Pan", wmt1_wave_pan_spin)

        wmt1_wave_random_pan_switch_combo = QComboBox()
        wmt1_wave_random_pan_switch_combo.addItems(["OFF", "ON"])
        wmt1_layout.addRow(
            "WMT1 Wave Random Pan Switch", wmt1_wave_random_pan_switch_combo
        )

        wmt1_wave_alternate_pan_switch_combo = QComboBox()
        wmt1_wave_alternate_pan_switch_combo.addItems(["OFF", "ON", "REVERSE"])
        wmt1_layout.addRow(
            "WMT1 Wave Alternate Pan Switch", wmt1_wave_alternate_pan_switch_combo
        )

        wmt1_wave_level_spin = QSpinBox()
        wmt1_wave_level_spin.setRange(0, 127)
        wmt1_layout.addRow("WMT1 Wave Level", wmt1_wave_level_spin)

        wmt1_velocity_range_lower_spin = QSpinBox()
        wmt1_velocity_range_lower_spin.setRange(1, 127)
        wmt1_layout.addRow("WMT1 Velocity Range Lower", wmt1_velocity_range_lower_spin)

        wmt1_velocity_range_upper_spin = QSpinBox()
        wmt1_velocity_range_upper_spin.setRange(1, 127)
        wmt1_layout.addRow("WMT1 Velocity Range Upper", wmt1_velocity_range_upper_spin)

        wmt1_velocity_fade_width_lower_spin = QSpinBox()
        wmt1_velocity_fade_width_lower_spin.setRange(0, 127)
        wmt1_layout.addRow(
            "WMT1 Velocity Fade Width Lower", wmt1_velocity_fade_width_lower_spin
        )

        wmt1_velocity_fade_width_upper_spin = QSpinBox()
        wmt1_velocity_fade_width_upper_spin.setRange(0, 127)
        wmt1_layout.addRow(
            "WMT1 Velocity Fade Width Upper", wmt1_velocity_fade_width_upper_spin
        )
        # Add controls to WMT2 tab
        wmt2_tab = wmt_tab_widget.widget(1)
        wmt2_layout = QFormLayout()
        wmt2_tab.setLayout(wmt2_layout)

        wmt2_wave_switch_combo = QComboBox()
        wmt2_wave_switch_combo.addItems(["OFF", "ON"])
        wmt2_layout.addRow("WMT2 Wave Switch", wmt2_wave_switch_combo)

        wmt2_wave_group_type_spin = QSpinBox()
        wmt2_wave_group_type_spin.setRange(0, 0)
        wmt2_layout.addRow("WMT2 Wave Group Type", wmt2_wave_group_type_spin)

        wmt2_wave_group_id_spin = QSpinBox()
        wmt2_wave_group_id_spin.setRange(0, 16384)
        wmt2_layout.addRow("WMT2 Wave Group ID", wmt2_wave_group_id_spin)

        wmt2_wave_number_l_spin = QSpinBox()
        wmt2_wave_number_l_spin.setRange(0, 16384)
        wmt2_layout.addRow("WMT2 Wave Number L", wmt2_wave_number_l_spin)

        wmt2_wave_number_r_spin = QSpinBox()
        wmt2_wave_number_r_spin.setRange(0, 16384)
        wmt2_layout.addRow("WMT2 Wave Number R", wmt2_wave_number_r_spin)

        wmt2_wave_gain_spin = QSpinBox()
        wmt2_wave_gain_spin.setRange(0, 3)
        wmt2_layout.addRow("WMT2 Wave Gain", wmt2_wave_gain_spin)

        wmt2_wave_fxm_switch_combo = QComboBox()
        wmt2_wave_fxm_switch_combo.addItems(["OFF", "ON"])
        wmt2_layout.addRow("WMT2 Wave FXM Switch", wmt2_wave_fxm_switch_combo)

        wmt2_wave_fxm_color_spin = QSpinBox()
        wmt2_wave_fxm_color_spin.setRange(0, 3)
        wmt2_layout.addRow("WMT2 Wave FXM Color", wmt2_wave_fxm_color_spin)

        wmt2_wave_fxm_depth_spin = QSpinBox()
        wmt2_wave_fxm_depth_spin.setRange(0, 16)
        wmt2_layout.addRow("WMT2 Wave FXM Depth", wmt2_wave_fxm_depth_spin)

        wmt2_wave_tempo_sync_combo = QComboBox()
        wmt2_wave_tempo_sync_combo.addItems(["OFF", "ON"])
        wmt2_layout.addRow("WMT2 Wave Tempo Sync", wmt2_wave_tempo_sync_combo)

        wmt2_wave_coarse_tune_spin = QSpinBox()
        wmt2_wave_coarse_tune_spin.setRange(16, 112)
        wmt2_layout.addRow("WMT2 Wave Coarse Tune", wmt2_wave_coarse_tune_spin)

        wmt2_wave_fine_tune_spin = QSpinBox()
        wmt2_wave_fine_tune_spin.setRange(14, 114)
        wmt2_layout.addRow("WMT2 Wave Fine Tune", wmt2_wave_fine_tune_spin)

        wmt2_wave_pan_spin = QSpinBox()
        wmt2_wave_pan_spin.setRange(0, 127)
        wmt2_layout.addRow("WMT2 Wave Pan", wmt2_wave_pan_spin)

        wmt2_wave_random_pan_switch_combo = QComboBox()
        wmt2_wave_random_pan_switch_combo.addItems(["OFF", "ON"])
        wmt2_layout.addRow(
            "WMT2 Wave Random Pan Switch", wmt2_wave_random_pan_switch_combo
        )

        wmt2_wave_alternate_pan_switch_combo = QComboBox()
        wmt2_wave_alternate_pan_switch_combo.addItems(["OFF", "ON", "REVERSE"])
        wmt2_layout.addRow(
            "WMT2 Wave Alternate Pan Switch", wmt2_wave_alternate_pan_switch_combo
        )

        wmt2_wave_level_spin = QSpinBox()
        wmt2_wave_level_spin.setRange(0, 127)
        wmt2_layout.addRow("WMT2 Wave Level", wmt2_wave_level_spin)

        wmt2_velocity_range_lower_spin = QSpinBox()
        wmt2_velocity_range_lower_spin.setRange(1, 127)
        wmt2_layout.addRow("WMT2 Velocity Range Lower", wmt2_velocity_range_lower_spin)

        wmt2_velocity_range_upper_spin = QSpinBox()
        wmt2_velocity_range_upper_spin.setRange(1, 127)
        wmt2_layout.addRow("WMT2 Velocity Range Upper", wmt2_velocity_range_upper_spin)

        wmt2_velocity_fade_width_lower_spin = QSpinBox()
        wmt2_velocity_fade_width_lower_spin.setRange(0, 127)
        wmt2_layout.addRow(
            "WMT2 Velocity Fade Width Lower", wmt2_velocity_fade_width_lower_spin
        )

        wmt2_velocity_fade_width_upper_spin = QSpinBox()
        wmt2_velocity_fade_width_upper_spin.setRange(0, 127)
        wmt2_layout.addRow(
            "WMT2 Velocity Fade Width Upper", wmt2_velocity_fade_width_upper_spin
        )

        # Add controls to WMT3 tab
        wmt3_tab = wmt_tab_widget.widget(2)
        wmt3_layout = QFormLayout()
        wmt3_tab.setLayout(wmt3_layout)

        wmt3_wave_switch_combo = QComboBox()
        wmt3_wave_switch_combo.addItems(["OFF", "ON"])
        wmt3_layout.addRow("WMT3 Wave Switch", wmt3_wave_switch_combo)

        wmt3_wave_group_type_spin = QSpinBox()
        wmt3_wave_group_type_spin.setRange(0, 0)
        wmt3_layout.addRow("WMT3 Wave Group Type", wmt3_wave_group_type_spin)

        wmt3_wave_group_id_spin = QSpinBox()
        wmt3_wave_group_id_spin.setRange(0, 16384)
        wmt3_layout.addRow("WMT3 Wave Group ID", wmt3_wave_group_id_spin)

        wmt3_wave_number_l_spin = QSpinBox()
        wmt3_wave_number_l_spin.setRange(0, 16384)
        wmt3_layout.addRow("WMT3 Wave Number L", wmt3_wave_number_l_spin)

        wmt3_wave_number_r_spin = QSpinBox()
        wmt3_wave_number_r_spin.setRange(0, 16384)
        wmt3_layout.addRow("WMT3 Wave Number R", wmt3_wave_number_r_spin)

        wmt3_wave_gain_spin = QSpinBox()
        wmt3_wave_gain_spin.setRange(0, 3)
        wmt3_layout.addRow("WMT3 Wave Gain", wmt3_wave_gain_spin)

        wmt3_wave_fxm_switch_combo = QComboBox()
        wmt3_wave_fxm_switch_combo.addItems(["OFF", "ON"])
        wmt3_layout.addRow("WMT3 Wave FXM Switch", wmt3_wave_fxm_switch_combo)

        wmt3_wave_fxm_color_spin = QSpinBox()
        wmt3_wave_fxm_color_spin.setRange(0, 3)
        wmt3_layout.addRow("WMT3 Wave FXM Color", wmt3_wave_fxm_color_spin)

        wmt3_wave_fxm_depth_spin = QSpinBox()
        wmt3_wave_fxm_depth_spin.setRange(0, 16)
        wmt3_layout.addRow("WMT3 Wave FXM Depth", wmt3_wave_fxm_depth_spin)

        wmt3_wave_tempo_sync_combo = QComboBox()
        wmt3_wave_tempo_sync_combo.addItems(["OFF", "ON"])
        wmt3_layout.addRow("WMT3 Wave Tempo Sync", wmt3_wave_tempo_sync_combo)

        wmt3_wave_coarse_tune_spin = QSpinBox()
        wmt3_wave_coarse_tune_spin.setRange(16, 112)
        wmt3_layout.addRow("WMT3 Wave Coarse Tune", wmt3_wave_coarse_tune_spin)

        wmt3_wave_fine_tune_spin = QSpinBox()
        wmt3_wave_fine_tune_spin.setRange(14, 114)
        wmt3_layout.addRow("WMT3 Wave Fine Tune", wmt3_wave_fine_tune_spin)

        wmt3_wave_pan_spin = QSpinBox()
        wmt3_wave_pan_spin.setRange(0, 127)
        wmt3_layout.addRow("WMT3 Wave Pan", wmt3_wave_pan_spin)

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

        wmt3_wave_level_spin = QSpinBox()
        wmt3_wave_level_spin.setRange(0, 127)
        wmt3_layout.addRow("WMT3 Wave Level", wmt3_wave_level_spin)

        wmt3_velocity_range_lower_spin = QSpinBox()
        wmt3_velocity_range_lower_spin.setRange(1, 127)
        wmt3_layout.addRow("WMT3 Velocity Range Lower", wmt3_velocity_range_lower_spin)

        wmt3_velocity_range_upper_spin = QSpinBox()
        wmt3_velocity_range_upper_spin.setRange(1, 127)
        wmt3_layout.addRow("WMT3 Velocity Range Upper", wmt3_velocity_range_upper_spin)

        wmt3_velocity_fade_width_lower_spin = QSpinBox()
        wmt3_velocity_fade_width_lower_spin.setRange(0, 127)
        wmt3_layout.addRow(
            "WMT3 Velocity Fade Width Lower", wmt3_velocity_fade_width_lower_spin
        )

        wmt3_velocity_fade_width_upper_spin = QSpinBox()
        wmt3_velocity_fade_width_upper_spin.setRange(0, 127)
        wmt3_layout.addRow(
            "WMT3 Velocity Fade Width Upper", wmt3_velocity_fade_width_upper_spin
        )

        # Add controls to WMT4 tab
        wmt4_tab = wmt_tab_widget.widget(3)
        wmt4_layout = QFormLayout()
        wmt4_tab.setLayout(wmt4_layout)

        wmt4_wave_switch_combo = QComboBox()
        wmt4_wave_switch_combo.addItems(["OFF", "ON"])
        wmt4_layout.addRow("WMT4 Wave Switch", wmt4_wave_switch_combo)

        wmt4_wave_group_type_spin = QSpinBox()
        wmt4_wave_group_type_spin.setRange(0, 0)
        wmt4_layout.addRow("WMT4 Wave Group Type", wmt4_wave_group_type_spin)

        wmt4_wave_group_id_spin = QSpinBox()
        wmt4_wave_group_id_spin.setRange(0, 16384)
        wmt4_layout.addRow("WMT4 Wave Group ID", wmt4_wave_group_id_spin)

        wmt4_wave_number_l_spin = QSpinBox()
        wmt4_wave_number_l_spin.setRange(0, 16384)
        wmt4_layout.addRow("WMT4 Wave Number L", wmt4_wave_number_l_spin)

        wmt4_wave_number_r_spin = QSpinBox()
        wmt4_wave_number_r_spin.setRange(0, 16384)
        wmt4_layout.addRow("WMT4 Wave Number R", wmt4_wave_number_r_spin)

        wmt4_wave_gain_spin = QSpinBox()
        wmt4_wave_gain_spin.setRange(0, 3)
        wmt4_layout.addRow("WMT4 Wave Gain", wmt4_wave_gain_spin)

        wmt4_wave_fxm_switch_combo = QComboBox()
        wmt4_wave_fxm_switch_combo.addItems(["OFF", "ON"])
        wmt4_layout.addRow("WMT4 Wave FXM Switch", wmt4_wave_fxm_switch_combo)

        wmt4_wave_fxm_color_spin = QSpinBox()
        wmt4_wave_fxm_color_spin.setRange(0, 3)
        wmt4_layout.addRow("WMT4 Wave FXM Color", wmt4_wave_fxm_color_spin)

        wmt4_wave_fxm_depth_spin = QSpinBox()
        wmt4_wave_fxm_depth_spin.setRange(0, 16)
        wmt4_layout.addRow("WMT4 Wave FXM Depth", wmt4_wave_fxm_depth_spin)

        wmt4_wave_tempo_sync_combo = QComboBox()
        wmt4_wave_tempo_sync_combo.addItems(["OFF", "ON"])
        wmt4_layout.addRow("WMT4 Wave Tempo Sync", wmt4_wave_tempo_sync_combo)

        wmt4_wave_coarse_tune_spin = QSpinBox()
        wmt4_wave_coarse_tune_spin.setRange(16, 112)
        wmt4_layout.addRow("WMT4 Wave Coarse Tune", wmt4_wave_coarse_tune_spin)

        wmt4_wave_fine_tune_spin = QSpinBox()
        wmt4_wave_fine_tune_spin.setRange(14, 114)
        wmt4_layout.addRow("WMT4 Wave Fine Tune", wmt4_wave_fine_tune_spin)

        wmt4_wave_pan_spin = QSpinBox()
        wmt4_wave_pan_spin.setRange(0, 127)
        wmt4_layout.addRow("WMT4 Wave Pan", wmt4_wave_pan_spin)

        wmt4_wave_random_pan_switch_combo = QComboBox()
        wmt4_wave_random_pan_switch_combo.addItems(["OFF", "ON"])
        wmt4_layout.addRow(
            "WMT4 Wave Random Pan Switch", wmt4_wave_random_pan_switch_combo
        )

        wmt4_wave_alternate_pan_switch_combo = QComboBox()
        wmt4_wave_alternate_pan_switch_combo.addItems(["OFF", "ON", "REVERSE"])
        wmt4_layout.addRow(
            "WMT4 Wave Alternate Pan Switch", wmt4_wave_alternate_pan_switch_combo
        )

        wmt4_wave_level_spin = QSpinBox()
        wmt4_wave_level_spin.setRange(0, 127)
        wmt4_layout.addRow("WMT4 Wave Level", wmt4_wave_level_spin)

        wmt4_velocity_range_lower_spin = QSpinBox()
        wmt4_velocity_range_lower_spin.setRange(1, 127)
        wmt4_layout.addRow("WMT4 Velocity Range Lower", wmt4_velocity_range_lower_spin)

        wmt4_velocity_range_upper_spin = QSpinBox()
        wmt4_velocity_range_upper_spin.setRange(1, 127)
        wmt4_layout.addRow("WMT4 Velocity Range Upper", wmt4_velocity_range_upper_spin)

        wmt4_velocity_fade_width_lower_spin = QSpinBox()
        wmt4_velocity_fade_width_lower_spin.setRange(0, 127)
        wmt4_layout.addRow(
            "WMT4 Velocity Fade Width Lower", wmt4_velocity_fade_width_lower_spin
        )

        wmt4_velocity_fade_width_upper_spin = QSpinBox()
        wmt4_velocity_fade_width_upper_spin.setRange(0, 127)
        wmt4_layout.addRow(
            "WMT4 Velocity Fade Width Upper", wmt4_velocity_fade_width_upper_spin
        )
        return wmt_group

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
        tvf_layout.addRow("TVF Filter Type", tvf_filter_type_combo)

        tvf_cutoff_frequency_slider = self._create_parameter_slider(
            DrumParameter.TVF_CUTOFF_FREQUENCY, "TVF Cutoff"
        )
        tvf_layout.addRow(tvf_cutoff_frequency_slider)

        tvf_cutoff_velocity_curve_spin = QSpinBox()
        tvf_cutoff_velocity_curve_spin.setRange(0, 7)
        tvf_cutoff_velocity_curve_spin.valueChanged.connect(
            self._on_tvf_cutoff_velocity_curve_spin_changed
        )
        tvf_layout.addRow("TVF Cutoff Velocity Curve", tvf_cutoff_velocity_curve_spin)

        tvf_cutoff_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.TVF_CUTOFF_VELOCITY_SENS
        )
        tvf_layout.addRow(tvf_cutoff_velocity_sens_slider)

        tvf_env_depth_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_DEPTH
        )
        tvf_layout.addRow(tvf_env_depth_slider)

        tvf_env_velocity_curve_type_spin = QSpinBox()
        tvf_env_velocity_curve_type_spin.setRange(0, 7)
        tvf_env_velocity_curve_type_spin.valueChanged.connect(
            self._on_tvf_env_velocity_curve_type_spin_changed
        )
        tvf_layout.addRow(
            "TVF Env Velocity Curve Type", tvf_env_velocity_curve_type_spin
        )

        tvf_env_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_VELOCITY_SENS, "TVF Env Velocity Sens"
        )
        tvf_layout.addRow(tvf_env_velocity_sens_slider)

        tvf_env_time1_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_TIME_1_VELOCITY_SENS, "TVF Env Time 1 Velocity Sens"
        )
        tvf_layout.addRow(tvf_env_time1_velocity_sens_slider)

        tvf_env_time4_velocity_sens_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_TIME_4_VELOCITY_SENS, "TVF Env Time 4 Velocity Sens"
        )
        tvf_layout.addRow(tvf_env_time4_velocity_sens_slider)

        tvf_env_time1_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_TIME_1, "TVF Env Time 1"
        )
        tvf_layout.addRow(tvf_env_time1_slider)

        tvf_env_time2_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_TIME_2, "TVF Env Time 2"
        )
        tvf_layout.addRow(tvf_env_time2_slider)

        tvf_env_time3_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_TIME_3, "TVF Env Time 3"
        )
        tvf_layout.addRow(tvf_env_time3_slider)

        tvf_env_time4_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_TIME_4, "TVF Env Time 4"
        )
        tvf_layout.addRow(tvf_env_time4_slider)

        tvf_env_level0_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_LEVEL_0, "TVF Env Level 0"
        )
        tvf_layout.addRow(tvf_env_level0_slider)

        tvf_env_level1_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_LEVEL_1, "TVF Env Level 1"
        )
        tvf_layout.addRow(tvf_env_level1_slider)

        tvf_env_level2_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_LEVEL_2, "TVF Env Level 2"
        )
        tvf_layout.addRow(tvf_env_level2_slider)

        tvf_env_level3_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_LEVEL_3, "TVF Env Level 3"
        )
        tvf_layout.addRow(tvf_env_level3_slider)

        tvf_env_level4_slider = self._create_parameter_slider(
            DrumParameter.TVF_ENV_LEVEL_4, "TVF Env Level 4"
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

    def _on_parameter_changed(self, param: DrumParameter, display_value: int):
        """Handle parameter value changes from UI controls"""
        try:
            # Convert display value to MIDI value if needed
            if hasattr(param, "convert_from_display"):
                midi_value = param.convert_from_display(display_value)
            else:
                midi_value = param.validate_value(display_value)
            logging.info(f"parameter from widget midi_value: {midi_value}")
            # Send MIDI message
            if not self.send_midi_parameter(param, midi_value):
                logging.warning(f"Failed to send parameter {param.name}")

        except Exception as e:
            logging.error(f"Error handling parameter {param.name}: {str(e)}")

    def on_partial_env_mode_changed(self, value):
        """Handle partial envelope mode combo box value change"""
        # Use the helper function to send the SysEx message @@ FIXME
        self.send_sysex_message(0x0B, value)

    def _update_partial_sliders_from_sysex(self, json_sysex_data: str):
        """Update sliders and combo boxes based on parsed SysEx data."""
        logging.info("Updating UI components from SysEx data")
        debug_param_updates = True
        debug_stats = True

        try:
            sysex_data = json.loads(json_sysex_data)
            self.previous_data = self.current_data
            self.current_data = sysex_data
            self._log_changes(self.previous_data, sysex_data)
        except json.JSONDecodeError as ex:
            logging.error(f"Invalid JSON format: {ex}")
            return

        def _is_valid_sysex_area(sysex_data):
            """Check if SysEx data belongs to a supported digital synth area."""
            return sysex_data.get("TEMPORARY_AREA") in [
                "TEMPORARY_DIGITAL_SYNTH_1_AREA",
                "TEMPORARY_DIGITAL_SYNTH_2_AREA",
            ]

        def _get_partial_number(synth_tone):
            """Retrieve partial number from synth tone mapping."""
            return {"PARTIAL_1": 1, "PARTIAL_2": 2, "PARTIAL_3": 3}.get(
                synth_tone, None
            )

        # if not _is_valid_sysex_area(sysex_data):
        #    logging.warning(
        #        "SysEx data does not belong to TEMPORARY_DIGITAL_SYNTH_1_AREA or TEMPORARY_DIGITAL_SYNTH_2_AREA. Skipping update.")
        #    return

        synth_tone = sysex_data.get("SYNTH_TONE")
        partial_no = get_partial_number(synth_tone)

        ignored_keys = {"JD_XI_ID", "ADDRESS", "TEMPORARY_AREA", "TONE_NAME"}
        sysex_data = {k: v for k, v in sysex_data.items() if k not in ignored_keys}

        # osc_waveform_map = {wave.value: wave for wave in OscWave}

        failures, successes = [], []

        def _update_slider(param, value):
            """Helper function to update sliders safely."""
            slider = self.partial_editors[partial_no].controls.get(param)
            if slider:
                slider_value = param.convert_from_midi(value)
                logging.info(
                    f"midi value {value} converted to slider value {slider_value}"
                )
                slider.blockSignals(True)
                slider.setValue(slider_value)
                slider.blockSignals(False)
                successes.append(param.name)
                if debug_param_updates:
                    logging.info(f"Updated: {param.name:50} {value}")

        def _update_waveform(param_value):
            """Helper function to update waveform selection UI."""
            waveform = osc_waveform_map.get(param_value)
            if waveform and waveform in self.partial_editors[partial_no].wave_buttons:
                button = self.partial_editors[partial_no].wave_buttons[waveform]
                button.setChecked(True)
                self.partial_editors[partial_no]._on_waveform_selected(waveform)
                logging.debug(f"Updated waveform button for {waveform}")

        for param_name, param_value in sysex_data.items():
            param = DrumParameter.get_by_name(param_name)

            if param:
                _update_slider(param, param_value)
            else:
                failures.append(param_name)

        def _log_debug_info():
            """Helper function to log debugging statistics."""
            if debug_stats:
                success_rate = (
                    (len(successes) / len(sysex_data) * 100) if sysex_data else 0
                )
                logging.info(f"Successes: {successes}")
                logging.info(f"Failures: {failures}")
                logging.info(f"Success Rate: {success_rate:.1f}%")
                logging.info("--------------------------------")

        _log_debug_info()

    def update_instrument_title(self):
        selected_kit_text = self.instrument_selection_combo.combo_box.currentText()
        self.title_label.setText(f"Drum Kit:\n {selected_kit_text}")

    def update_instrument_preset(self):
        selected_kit_text = self.instrument_selection_combo.combo_box.currentText()
        if digital_synth_matches := re.search(
            r"(\d{3}): (\S+).+", selected_kit_text, re.IGNORECASE
        ):
            selected_synth_padded_number = (
                digital_synth_matches.group(1).lower().replace("&", "_").split("_")[0]
            )
            preset_index = int(selected_synth_padded_number)
            print(f"preset_index: {preset_index}")
            self.load_preset(preset_index)

    def load_preset(self, preset_index):
        preset_data = {
            "type": self.preset_type,  # Ensure this is a valid type
            "selpreset": preset_index,  # Convert to 1-based index
            "modified": 0,  # or 1, depending on your logic
        }
        if not self.preset_loader:
            self.preset_loader = PresetLoader(self.midi_helper)
        if self.preset_loader:
            self.preset_loader.load_preset(preset_data)

    def update_combo_box_index(self, preset_number):
        """Updates the QComboBox to reflect the loaded preset."""
        print(f"Updating combo to preset {preset_number}")
        self.instrument_selection_combo.combo_box.setCurrentIndex(preset_number)

    def send_sysex_message(self, address: int, value: int):
        """Helper function to send a SysEx message with a given address and value."""
        # 0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x19, 0x70, address, value, 0x6C, 0xF7
        """
        sysex_message = [
            START_OF_SYSEX,
            ROLAND_ID,
            DEVICE_ID,
            MODEL_ID_1,
            MODEL_ID_2,
            MODEL_ID_3,
            MODEL_ID_4,
            DT1_COMMAND,
            TEMPORARY_DIGITAL_SYNTH_1_AREA,  # Assuming this is a fixed address of the message
            0x70,  # Assuming this is a fixed address of the message
            address,
            value,
            0x6C,  # Assuming this is a fixed address of the message
        ]
        """
        # sysex_message = [
        #     0xF0, 0x41, 0x10, 0x00, 0x00, 0x00, 0x0E, 0x12, 0x19, 0x70, address, value, checksum, 0xF7
        # ]
        return self.midi_helper.send_parameter(
            area=TEMPORARY_DRUM_KIT_AREA,
            part=0x70,
            group=group,
            param=address,
            value=value,  # Make sure this value is being sent
        )
        # self.midi_helper.send_message(checksum_message)

    def _on_tva_level_velocity_sens_slider_changed(self, value: int):
        """Handle TVA Level Velocity Sens change"""
        if self.midi_helper:
            self.midi_helper.send_parameter(
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
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
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
                part=DrumParameter.DRUM_PART.value,
                group=DrumParameter.DRUM_GROUP.value,
                param=DrumParameter.TVF_ENV_TIME_1_VELOCITY_SENS.value[0],
                value=value,
            )
            print(f"TVF Env Time 1 Velocity Sens changed to {value}")

    def _create_parameter_slider(
        self, param: DrumParameter, label: str = None
    ) -> Slider:
        """Create a slider for a parameter with proper display conversion"""
        if hasattr(param, "get_display_value"):
            display_min, display_max = param.get_display_value()
        else:
            display_min, display_max = param.min_val, param.max_val

        # Create horizontal slider (removed vertical ADSR check)
        slider = Slider(label, display_min, display_max)

        if isinstance(param, DrumParameter) and param in [
            DrumParameter.PARTIAL_FINE_TUNE,
            # Add other bipolar parameters as needed
        ]:
            # Set format string to show + sign for positive values
            slider.setValueDisplayFormat(lambda v: f"{v:+d}" if v != 0 else "0")
            # Set center tick
            # slider.setCenterMark(0)
            # Add more prominent tick at center
            # slider.setTickPosition(Slider.TickPosition.TicksBothSides)
            # slider.setTickInterval((display_max - display_min) // 4)
            """ Set the slider to the center value """
            # Get initial MIDI value and convert to display value
            if self.midi_helper:
                self.address = get_address_for_partial(
                    self.partial_num
                )  # Get the current partial number
                group, param_address = get_address_for_partial(self.partial_num)
                midi_value = self.midi_helper.get_parameter(
                    area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
                    part=self.address,
                    group=group,
                    param=param_address,
                )
                if midi_value is not None:
                    display_value = param.convert_from_midi(midi_value)
                    slider.setValue(display_value)

        # Connect value changed signal
        slider.valueChanged.connect(lambda v: self._on_parameter_changed(param, v))

        # Store control reference
        self.controls[param] = slider
        return slider

    def send_midi_parameter(self, param, value) -> bool:
        """Send MIDI parameter with error handling"""
        if not self.midi_helper:
            logging.debug("No MIDI helper available - parameter change ignored")
            return False

        try:
            # Get parameter group and address with partial offset
            if isinstance(param, DrumParameter):
                partial_group, partial_address = get_address_for_partial(
                    self.partial_num
                )
            else:
                partial_group = 0x00  # Common parameters group
                partial_address = param.address

            # Ensure value is included in the MIDI message
            return self.midi_helper.send_parameter(
                area=TEMPORARY_DIGITAL_SYNTH_1_AREA,
                part=DrumParameter.DRUM_PART.value[0],
                group=partial_group,
                param=param.address,
                value=value,  # Make sure this value is being sent
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
            self.group, self.address = get_address_for_partial(self.partial_num)
            logging.info(
                f"Updated partial number to {self.partial_num}, group: {hex(self.group)}, address: {hex(self.address)}"
            )
            print(
                f"Updated partial number to {self.partial_num}, group: {hex(self.group)}, address: {hex(self.address)}"
            )
        except Exception as e:
            logging.error(
                f"Error getting address for partial {self.partial_num}: {str(e)}"
            )
