"""
This module defines the `DrumPartialEditor` class for editing drum kit parameters within a graphical user interface (GUI).

The `DrumPartialEditor` class allows users to modify various parameters related to drum sounds, including pitch, output, TVF (Time Variant Filter), pitch envelope, WMT (Wave Modulation Time), and TVA (Time Variant Amplifier) settings. The class provides a comprehensive layout with controls such as sliders, combo boxes, and spin boxes to adjust the parameters.

Key functionalities of the module include:
- Displaying parameter controls for a specific drum partial.
- Providing detailed access to different parameter groups such as pitch, output, and TVA.
- Handling MIDI and tone area settings for drum kit editing.
- Handling dynamic address assignment for each partial based on its name.

Dependencies:
- `logging`: For logging initialization and error handling.
- `PySide6.QtWidgets`: For GUI components such as `QWidget`, `QVBoxLayout`, `QScrollArea`, etc.
- `jdxi_manager.midi.data.drums`: For drum-related data and operations like retrieving drum waves.
- `jdxi_manager.midi.data.parameter.drums`: For specific drum parameter definitions and utilities.
- `jdxi_manager.midi.data.constants.sysex`: For MIDI-related constants like `TEMPORARY_TONE_AREA` and `DRUM_KIT_AREA`.
- `jdxi_manager.ui.widgets`: For custom UI widgets such as `Slider`, `ComboBox`, and `SpinBox`.

The `DrumPartialEditor` is designed to work within a larger system for managing drum kit tones, providing an intuitive interface for modifying various sound parameters.

"""

import logging
from typing import Dict

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QGridLayout,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QTabWidget,
)
from jdxi_editor.midi.data.drum import rm_waves
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParameter
from jdxi_editor.midi.data.constants.sysex import TEMPORARY_TONE_AREA, DRUM_KIT_AREA
from jdxi_editor.midi.data.parameter.drum.helper import get_address_for_partial_name
from jdxi_editor.ui.editors.partial import PartialEditor


class DrumPartialEditor(PartialEditor):
    """Editor for address single partial"""

    def __init__(self, midi_helper=None, partial_number=0, partial_name=None, parent=None):
        super().__init__(parent)
        self.midi_helper = midi_helper
        self.partial_num = partial_number  # This is now the numerical index
        self.partial_name = partial_name  # This is now the numerical index
        self.preset_handler = None
        self.area = TEMPORARY_TONE_AREA
        self.group = DRUM_KIT_AREA
        # Calculate the address for this partial
        try:
            self.partial_address = get_address_for_partial_name(self.partial_name)
            logging.info(
                f"Initialized partial {partial_number} with address: {hex(self.partial_address)}"
            )
        except Exception as ex:
            logging.error(
                f"Error calculating address for partial {partial_number}: {str(ex)}"
            )
            self.partial_address = 0x00

        # Store parameter controls for easy access
        self.controls: Dict[DrumPartialParameter, QWidget] = {}

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
        """Create the TVA area."""

        # TVA Group
        tva_group = QGroupBox("TVA")
        tva_layout = QFormLayout()
        tva_group.setLayout(tva_layout)

        # Add TVA parameters
        tva_level_velocity_curve_spin = self._create_parameter_combo_box(
            DrumPartialParameter.TVA_LEVEL_VELOCITY_CURVE,
            "Level Velocity Curve",
            ["FIXED", "1", "2", "3", "4", "5", "6", "7"],
            [0, 1, 2, 3, 4, 5, 6, 7],
        )

        tva_layout.addRow(tva_level_velocity_curve_spin)

        tva_level_velocity_sens_slider = self._create_parameter_slider(
            DrumPartialParameter.TVA_LEVEL_VELOCITY_SENS, "Level Velocity Sens"
        )
        tva_layout.addRow(tva_level_velocity_sens_slider)

        tva_env_time1_velocity_sens_slider = self._create_parameter_slider(
            DrumPartialParameter.TVA_ENV_TIME_1_VELOCITY_SENS, "Env Time 1 Velocity Sens"
        )
        tva_layout.addRow(tva_env_time1_velocity_sens_slider)

        tva_env_time4_velocity_sens_slider = self._create_parameter_slider(
            DrumPartialParameter.TVA_ENV_TIME_4_VELOCITY_SENS, "Env Time 4 Velocity Sens"
        )

        tva_layout.addRow(tva_env_time4_velocity_sens_slider)

        tva_env_time1_slider = self._create_parameter_slider(
            DrumPartialParameter.TVA_ENV_TIME_1, "Env Time 1"
        )
        tva_layout.addRow(tva_env_time1_slider)

        tva_env_time2_slider = self._create_parameter_slider(
            DrumPartialParameter.TVA_ENV_TIME_2, "Env Time 2"
        )
        tva_layout.addRow(tva_env_time2_slider)

        tva_env_time3_slider = self._create_parameter_slider(
            DrumPartialParameter.TVA_ENV_TIME_3, "Env Time 3"
        )
        tva_layout.addRow(tva_env_time3_slider)

        tva_env_time4_slider = self._create_parameter_slider(
            DrumPartialParameter.TVA_ENV_TIME_4, "Env Time 4"
        )
        tva_layout.addRow(tva_env_time4_slider)

        tva_env_level1_slider = self._create_parameter_slider(
            DrumPartialParameter.TVA_ENV_LEVEL_1, "Env Level 1"
        )
        tva_layout.addRow(tva_env_level1_slider)

        tva_env_level2_slider = self._create_parameter_slider(
            DrumPartialParameter.TVA_ENV_LEVEL_2, "Env Level 2"
        )
        tva_layout.addRow(tva_env_level2_slider)

        tva_env_level3_slider = self._create_parameter_slider(
            DrumPartialParameter.TVA_ENV_LEVEL_3, "Env Level 3"
        )
        tva_layout.addRow(tva_env_level3_slider)
        return tva_group

    def _create_wmt_group(self):
        """Create the WMT area."""

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
        wmt1_layout = QFormLayout()
        wmt1_wave_switch_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT1_WAVE_SWITCH, "WMT1 Wave Switch", ["OFF", "ON"], [0, 1]
        )

        wmt1_layout.addRow(wmt1_wave_switch_combo)

        wmt1_wave_number_l_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT1_WAVE_NUMBER_L,
            "WMT1 Wave Number L/Mono",
            options=rm_waves,
            values=list(range(0, 453)),
        )

        wmt1_layout.addRow(wmt1_wave_number_l_combo)

        wmt1_wave_number_r_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT1_WAVE_NUMBER_R,
            "WMT1 Wave Number R",
            options=rm_waves,
            values=list(range(0, 453)),
        )

        wmt1_layout.addRow(wmt1_wave_number_r_combo)

        wmt1_wave_gain_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT1_WAVE_GAIN,
            "Wave Gain",
            options=["-6", "0", "6", "12"],
            values=[0, 1, 2, 3],
        )

        wmt1_layout.addRow(wmt1_wave_gain_combo)

        wmt1_wave_fxm_switch_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT1_WAVE_GAIN,
            "Wave FXM Switch",
            options=["OFF", "ON"],
            values=[0, 1],
        )
        wmt1_layout.addRow(wmt1_wave_fxm_switch_combo)

        wmt1_wave_fxm_color_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT1_WAVE_FXM_COLOR,
            "Wave FXM Color",
        )
        wmt1_layout.addRow(wmt1_wave_fxm_color_slider)

        wmt1_wave_fxm_depth_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT1_WAVE_FXM_DEPTH,
            "Wave FXM Depth",
        )
        wmt1_layout.addRow(wmt1_wave_fxm_depth_slider)

        wmt1_wave_tempo_sync_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT1_WAVE_TEMPO_SYNC, "Wave Tempo Sync"
        )
        wmt1_layout.addRow(wmt1_wave_tempo_sync_slider)

        wmt1_wave_coarse_tune_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT1_WAVE_COARSE_TUNE,
            "Wave Coarse Tune",
        )
        wmt1_layout.addRow(wmt1_wave_coarse_tune_slider)

        wmt1_wave_fine_tune_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT1_WAVE_FINE_TUNE, "Wave Fine Tune"
        )
        wmt1_layout.addRow(wmt1_wave_fine_tune_slider)

        wmt1_wave_pan = self._create_parameter_slider(
            DrumPartialParameter.WMT1_WAVE_PAN,
            "Wave Pan",
        )
        wmt1_layout.addRow(wmt1_wave_pan)

        wmt1_wave_random_pan_switch = self._create_parameter_combo_box(
            DrumPartialParameter.WMT1_WAVE_RANDOM_PAN_SWITCH,
            "Wave Random Pan Switch",
            ["OFF", "ON"],
            [0, 1],
        )
        wmt1_layout.addRow(wmt1_wave_random_pan_switch)

        wmt1_wave_alternate_pan_switch = self._create_parameter_combo_box(
            DrumPartialParameter.WMT1_WAVE_ALTERNATE_PAN_SWITCH,
            "Wave Alternate Pan Switch",
            ["OFF", "ON", "REVERSE"],
            [0, 1, 2],
        )
        wmt1_layout.addRow(wmt1_wave_alternate_pan_switch)

        wmt1_wave_level_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT1_WAVE_LEVEL,
            "Wave Level",
        )
        wmt1_layout.addRow(wmt1_wave_level_slider)

        wmt1_velocity_range_lower_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT1_VELOCITY_RANGE_LOWER,
            "Velocity Range Lower",
        )
        wmt1_layout.addRow(wmt1_velocity_range_lower_slider)

        wmt1_velocity_range_upper_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT1_VELOCITY_RANGE_UPPER,
            "Velocity Range Upper",
        )
        wmt1_layout.addRow(wmt1_velocity_range_upper_slider)

        wmt1_velocity_fade_width_lower_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT1_VELOCITY_FADE_WIDTH_LOWER,
            "Velocity Fade Width Lower",
        )
        wmt1_layout.addRow(wmt1_velocity_fade_width_lower_slider)

        wmt1_velocity_fade_width_upper_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT1_VELOCITY_FADE_WIDTH_UPPER,
            "Velocity Fade Width Upper",
        )
        wmt1_layout.addRow(wmt1_velocity_fade_width_upper_slider)
        return wmt1_layout

    def _create_wmt2_layout(self):
        wmt2_layout = QFormLayout()
        wmt2_wave_switch_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT2_WAVE_SWITCH, "WMT2 Wave Switch", ["OFF", "ON"], [0, 1]
        )

        wmt2_layout.addRow(wmt2_wave_switch_combo)

        wmt2_wave_number_l_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT2_WAVE_NUMBER_L,
            "WMT2 Wave Number L/Mono",
            options=rm_waves,
            values=list(range(0, 453)),
        )

        wmt2_layout.addRow(wmt2_wave_number_l_combo)

        wmt2_wave_number_r_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT2_WAVE_NUMBER_R,
            "WMT2 Wave Number R",
            options=rm_waves,
            values=list(range(0, 453)),
        )

        wmt2_layout.addRow(wmt2_wave_number_r_combo)

        wmt2_wave_gain_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT2_WAVE_GAIN,
            "Wave Gain",
            options=["-6", "0", "6", "12"],
            values=[0, 1, 2, 3],
        )

        wmt2_layout.addRow(wmt2_wave_gain_combo)

        wmt2_wave_fxm_switch_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT2_WAVE_GAIN,
            "Wave FXM Switch",
            options=["OFF", "ON"],
            values=[0, 1],
        )
        wmt2_layout.addRow(wmt2_wave_fxm_switch_combo)

        wmt2_wave_fxm_color_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT2_WAVE_FXM_COLOR,
            "Wave FXM Color",
        )
        wmt2_layout.addRow(wmt2_wave_fxm_color_slider)

        wmt2_wave_fxm_depth_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT2_WAVE_FXM_DEPTH,
            "Wave FXM Depth",
        )
        wmt2_layout.addRow(wmt2_wave_fxm_depth_slider)

        wmt2_wave_tempo_sync_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT2_WAVE_TEMPO_SYNC, "Wave Tempo Sync"
        )
        wmt2_layout.addRow(wmt2_wave_tempo_sync_slider)

        wmt2_wave_coarse_tune_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT2_WAVE_COARSE_TUNE,
            "Wave Coarse Tune",
        )
        wmt2_layout.addRow(wmt2_wave_coarse_tune_slider)

        wmt2_wave_fine_tune_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT2_WAVE_FINE_TUNE, "Wave Fine Tune"
        )
        wmt2_layout.addRow(wmt2_wave_fine_tune_slider)

        wmt2_wave_pan = self._create_parameter_slider(
            DrumPartialParameter.WMT2_WAVE_PAN,
            "Wave Pan",
        )
        wmt2_layout.addRow(wmt2_wave_pan)

        wmt2_wave_random_pan_switch = self._create_parameter_combo_box(
            DrumPartialParameter.WMT2_WAVE_RANDOM_PAN_SWITCH,
            "Wave Random Pan Switch",
            ["OFF", "ON"],
            [0, 1],
        )
        wmt2_layout.addRow(wmt2_wave_random_pan_switch)

        wmt2_wave_alternate_pan_switch = self._create_parameter_combo_box(
            DrumPartialParameter.WMT2_WAVE_ALTERNATE_PAN_SWITCH,
            "Wave Alternate Pan Switch",
            ["OFF", "ON", "REVERSE"],
            [0, 1, 2],
        )
        wmt2_layout.addRow(wmt2_wave_alternate_pan_switch)

        wmt2_wave_level_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT2_WAVE_LEVEL,
            "Wave Level",
        )
        wmt2_layout.addRow(wmt2_wave_level_slider)

        wmt2_velocity_range_lower_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT2_VELOCITY_RANGE_LOWER,
            "Velocity Range Lower",
        )
        wmt2_layout.addRow(wmt2_velocity_range_lower_slider)

        wmt2_velocity_range_upper_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT2_VELOCITY_RANGE_UPPER,
            "Velocity Range Upper",
        )
        wmt2_layout.addRow(wmt2_velocity_range_upper_slider)

        wmt2_velocity_fade_width_lower_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT2_VELOCITY_FADE_WIDTH_LOWER,
            "Velocity Fade Width Lower",
        )
        wmt2_layout.addRow(wmt2_velocity_fade_width_lower_slider)

        wmt2_velocity_fade_width_upper_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT2_VELOCITY_FADE_WIDTH_UPPER,
            "Velocity Fade Width Upper",
        )
        wmt2_layout.addRow(wmt2_velocity_fade_width_upper_slider)
        return wmt2_layout

    def _create_wmt3_layout(self):
        wmt3_layout = QFormLayout()
        wmt3_wave_switch_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT3_WAVE_SWITCH, "WMT3 Wave Switch", ["OFF", "ON"], [0, 1]
        )

        wmt3_layout.addRow(wmt3_wave_switch_combo)

        wmt3_wave_number_l_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT3_WAVE_NUMBER_L,
            "WMT3 Wave Number L/Mono",
            options=rm_waves,
            values=list(range(0, 453)),
        )

        wmt3_layout.addRow(wmt3_wave_number_l_combo)

        wmt3_wave_number_r_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT3_WAVE_NUMBER_R,
            "WMT3 Wave Number R",
            options=rm_waves,
            values=list(range(0, 453)),
        )

        wmt3_layout.addRow(wmt3_wave_number_r_combo)

        wmt3_wave_gain_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT3_WAVE_GAIN,
            "Wave Gain",
            options=["-6", "0", "6", "12"],
            values=[0, 1, 2, 3],
        )

        wmt3_layout.addRow(wmt3_wave_gain_combo)

        wmt3_wave_fxm_switch_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT3_WAVE_GAIN,
            "Wave FXM Switch",
            options=["OFF", "ON"],
            values=[0, 1],
        )
        wmt3_layout.addRow(wmt3_wave_fxm_switch_combo)

        wmt3_wave_fxm_color_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT3_WAVE_FXM_COLOR,
            "Wave FXM Color",
            options=["OFF", "ON"],
            values=[0, 1],
        )
        wmt3_layout.addRow(wmt3_wave_fxm_color_combo)

        wmt3_wave_fxm_depth_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT3_WAVE_FXM_DEPTH,
            "Wave FXM Depth",
            options=["OFF", "ON"],
            values=[0, 1],
        )
        wmt3_layout.addRow(wmt3_wave_fxm_depth_combo)

        wmt3_wave_tempo_sync_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT3_WAVE_TEMPO_SYNC, "Wave Tempo Sync"
        )
        wmt3_layout.addRow(wmt3_wave_tempo_sync_slider)

        wmt3_wave_coarse_tune_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT3_WAVE_COARSE_TUNE,
            "Wave Coarse Tune",
        )
        wmt3_layout.addRow(wmt3_wave_coarse_tune_slider)

        wmt3_wave_fine_tune_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT3_WAVE_FINE_TUNE, "Wave Fine Tune"
        )
        wmt3_layout.addRow(wmt3_wave_fine_tune_slider)

        wmt3_wave_pan = self._create_parameter_slider(
            DrumPartialParameter.WMT3_WAVE_PAN,
            "Wave Pan",
        )
        wmt3_layout.addRow(wmt3_wave_pan)

        wmt3_wave_random_pan_switch = self._create_parameter_combo_box(
            DrumPartialParameter.WMT3_WAVE_RANDOM_PAN_SWITCH,
            "Wave Random Pan Switch",
            ["OFF", "ON"],
            [0, 1],
        )
        wmt3_layout.addRow(wmt3_wave_random_pan_switch)

        wmt3_wave_alternate_pan_switch = self._create_parameter_combo_box(
            DrumPartialParameter.WMT3_WAVE_ALTERNATE_PAN_SWITCH,
            "Wave Alternate Pan Switch",
            ["OFF", "ON", "REVERSE"],
            [0, 1, 2],
        )
        wmt3_layout.addRow(wmt3_wave_alternate_pan_switch)

        wmt3_wave_level_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT3_WAVE_LEVEL,
            "Wave Level",
        )
        wmt3_layout.addRow(wmt3_wave_level_slider)

        wmt3_velocity_range_lower_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT3_VELOCITY_RANGE_LOWER,
            "Velocity Range Lower",
        )
        wmt3_layout.addRow(wmt3_velocity_range_lower_slider)

        wmt3_velocity_range_upper_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT3_VELOCITY_RANGE_UPPER,
            "Velocity Range Upper",
        )
        wmt3_layout.addRow(wmt3_velocity_range_upper_slider)

        wmt3_velocity_fade_width_lower_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT3_VELOCITY_FADE_WIDTH_LOWER,
            "Velocity Fade Width Lower",
        )
        wmt3_layout.addRow(wmt3_velocity_fade_width_lower_slider)

        wmt3_velocity_fade_width_upper_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT3_VELOCITY_FADE_WIDTH_UPPER,
            "Velocity Fade Width Upper",
        )
        wmt3_layout.addRow(wmt3_velocity_fade_width_upper_slider)
        return wmt3_layout

    def _create_wmt4_layout(self):
        wmt4_layout = QFormLayout()
        wmt4_wave_switch_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT4_WAVE_SWITCH, "WMT4 Wave Switch", ["OFF", "ON"], [0, 1]
        )

        wmt4_layout.addRow(wmt4_wave_switch_combo)

        wmt4_wave_number_l_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT4_WAVE_NUMBER_L,
            "WMT4 Wave Number L/Mono",
            options=rm_waves,
            values=list(range(0, 453)),
        )

        wmt4_layout.addRow(wmt4_wave_number_l_combo)

        wmt4_wave_number_r_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT4_WAVE_NUMBER_R,
            "WMT4 Wave Number R",
            options=rm_waves,
            values=list(range(0, 453)),
        )

        wmt4_layout.addRow(wmt4_wave_number_r_combo)

        wmt4_wave_gain_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT4_WAVE_GAIN,
            "Wave Gain",
            options=["-6", "0", "6", "12"],
            values=[0, 1, 2, 3],
        )

        wmt4_layout.addRow(wmt4_wave_gain_combo)

        wmt4_wave_fxm_switch_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT4_WAVE_GAIN,
            "Wave FXM Switch",
            options=["OFF", "ON"],
            values=[0, 1],
        )
        wmt4_layout.addRow(wmt4_wave_fxm_switch_combo)

        wmt4_wave_fxm_color_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT4_WAVE_FXM_COLOR,
            "Wave FXM Color",
            options=["OFF", "ON"],
            values=[0, 1],
        )
        wmt4_layout.addRow(wmt4_wave_fxm_color_combo)

        wmt4_wave_fxm_depth_combo = self._create_parameter_combo_box(
            DrumPartialParameter.WMT4_WAVE_FXM_DEPTH,
            "Wave FXM Depth",
            options=["OFF", "ON"],
            values=[0, 1],
        )
        wmt4_layout.addRow(wmt4_wave_fxm_depth_combo)

        wmt4_wave_tempo_sync_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT4_WAVE_TEMPO_SYNC, "Wave Tempo Sync"
        )
        wmt4_layout.addRow(wmt4_wave_tempo_sync_slider)

        wmt4_wave_coarse_tune_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT4_WAVE_COARSE_TUNE,
            "Wave Coarse Tune",
        )
        wmt4_layout.addRow(wmt4_wave_coarse_tune_slider)

        wmt4_wave_fine_tune_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT4_WAVE_FINE_TUNE, "Wave Fine Tune"
        )
        wmt4_layout.addRow(wmt4_wave_fine_tune_slider)

        wmt4_wave_pan = self._create_parameter_slider(
            DrumPartialParameter.WMT4_WAVE_PAN,
            "Wave Pan",
        )
        wmt4_layout.addRow(wmt4_wave_pan)

        wmt4_wave_random_pan_switch = self._create_parameter_combo_box(
            DrumPartialParameter.WMT4_WAVE_RANDOM_PAN_SWITCH,
            "Wave Random Pan Switch",
            ["OFF", "ON"],
            [0, 1],
        )
        wmt4_layout.addRow(wmt4_wave_random_pan_switch)

        wmt4_wave_alternate_pan_switch = self._create_parameter_combo_box(
            DrumPartialParameter.WMT4_WAVE_ALTERNATE_PAN_SWITCH,
            "Wave Alternate Pan Switch",
            ["OFF", "ON", "REVERSE"],
            [0, 1, 2],
        )
        wmt4_layout.addRow(wmt4_wave_alternate_pan_switch)

        wmt4_wave_level_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT4_WAVE_LEVEL,
            "Wave Level",
        )
        wmt4_layout.addRow(wmt4_wave_level_slider)

        wmt4_velocity_range_lower_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT4_VELOCITY_RANGE_LOWER,
            "Velocity Range Lower",
        )
        wmt4_layout.addRow(wmt4_velocity_range_lower_slider)

        wmt4_velocity_range_upper_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT4_VELOCITY_RANGE_UPPER,
            "Velocity Range Upper",
        )
        wmt4_layout.addRow(wmt4_velocity_range_upper_slider)

        wmt4_velocity_fade_width_lower_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT4_VELOCITY_FADE_WIDTH_LOWER,
            "Velocity Fade Width Lower",
        )
        wmt4_layout.addRow(wmt4_velocity_fade_width_lower_slider)

        wmt4_velocity_fade_width_upper_slider = self._create_parameter_slider(
            DrumPartialParameter.WMT4_VELOCITY_FADE_WIDTH_UPPER,
            "Velocity Fade Width Upper",
        )
        wmt4_layout.addRow(wmt4_velocity_fade_width_upper_slider)
        return wmt4_layout

    def _create_pitch_group(self):
        """Create the pitch area."""
        # Pitch Group
        pitch_group = QGroupBox("Pitch")
        pitch_layout = QFormLayout()
        pitch_group.setLayout(pitch_layout)
        # grid_layout.addWidget(pitch_group, 0, 0)

        # Add pitch parameters
        partial_level_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_LEVEL, "Partial Level"
        )
        pitch_layout.addRow(partial_level_slider)

        partial_coarse_tune_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_COARSE_TUNE, "Partial Coarse Tune"
        )
        pitch_layout.addRow(partial_coarse_tune_slider)

        partial_fine_tune_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_FINE_TUNE, "Partial Fine Tune"
        )
        pitch_layout.addRow(partial_fine_tune_slider)

        partial_random_pitch_depth_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_RANDOM_PITCH_DEPTH, "Partial Random Pitch Depth"
        )
        pitch_layout.addRow(partial_random_pitch_depth_slider)

        partial_pan_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_PAN, "Partial Pan"
        )
        pitch_layout.addRow(partial_pan_slider)

        partial_random_pan_depth_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_RANDOM_PAN_DEPTH, "Partial Random Pan Depth"
        )
        pitch_layout.addRow(partial_random_pan_depth_slider)

        partial_alternate_pan_depth_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_ALTERNATE_PAN_DEPTH, "Partial Alternate Pan Depth"
        )
        pitch_layout.addRow(partial_alternate_pan_depth_slider)

        partial_env_mode_combo = self._create_parameter_combo_box(
            DrumPartialParameter.PARTIAL_ENV_MODE,
            "Partial Env Mode",
            ["NO-SUS", "SUSTAIN"],
            [0, 1],
        )
        pitch_layout.addRow(partial_env_mode_combo)

        return pitch_group

    def _create_output_group(self):
        # Output Group
        output_group = QGroupBox("Output")
        output_layout = QFormLayout()
        output_group.setLayout(output_layout)

        # Add output parameters
        partial_output_level_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_OUTPUT_LEVEL, "Partial Output Level"
        )
        output_layout.addRow(partial_output_level_slider)

        partial_chorus_send_level_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_CHORUS_SEND_LEVEL, "Partial Chorus Send Level"
        )
        output_layout.addRow(partial_chorus_send_level_slider)

        partial_reverb_send_level_slider = self._create_parameter_slider(
            DrumPartialParameter.PARTIAL_REVERB_SEND_LEVEL, "Partial Reverb Send Level"
        )
        output_layout.addRow(partial_reverb_send_level_slider)

        partial_output_assign_combo = self._create_parameter_combo_box(
            DrumPartialParameter.PARTIAL_OUTPUT_ASSIGN,
            "Partial Output Assign",
            ["EFX1", "EFX2", "DLY", "REV", "DIR"],
            [0, 1, 2, 3, 4],
        )
        output_layout.addRow(partial_output_assign_combo)

        return output_group

    def _create_tvf_group(self):
        """create tvf area"""
        # TVF Group
        tvf_group = QGroupBox("TVF")
        tvf_layout = QFormLayout()
        tvf_group.setLayout(tvf_layout)

        # Add TVF parameters
        tvf_filter_type_combo = self._create_parameter_combo_box(
            DrumPartialParameter.TVF_FILTER_TYPE,
            "Filter Type",
            ["OFF", "LPF", "BPF", "HPF", "PKG", "LPF2", "LPF3"],
            [0, 1, 2, 3, 4],
        )
        tvf_layout.addRow(tvf_filter_type_combo)

        tvf_cutoff_frequency_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_CUTOFF_FREQUENCY, "TVF Cutoff"
        )
        tvf_layout.addRow(tvf_cutoff_frequency_slider)

        tvf_cutoff_velocity_curve_spin = self._create_parameter_combo_box(
            DrumPartialParameter.TVF_CUTOFF_VELOCITY_CURVE,
            "Cutoff Velocity Curve",
            ["FIXED", "1", "2", "3", "4", "5", "6", "7"],
            [0, 1, 2, 3, 4, 5, 6, 7],
        )
        tvf_layout.addRow(tvf_cutoff_velocity_curve_spin)

        tvf_env_depth_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_ENV_DEPTH, "Env Depth"
        )
        tvf_layout.addRow(tvf_env_depth_slider)

        tvf_env_velocity_curve_type_spin = self._create_parameter_combo_box(
            DrumPartialParameter.TVF_ENV_VELOCITY_CURVE_TYPE,
            "Env Velocity Curve Type",
            ["FIXED", "1", "2", "3", "4", "5", "6", "7"],
            [0, 1, 2, 3, 4, 5, 6, 7],
        )
        tvf_layout.addRow(tvf_env_velocity_curve_type_spin)

        tvf_env_velocity_sens_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_ENV_VELOCITY_SENS, "Env Velocity Sens"
        )
        tvf_layout.addRow(tvf_env_velocity_sens_slider)

        tvf_env_time1_velocity_sens_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_ENV_TIME_1_VELOCITY_SENS, "Env Time 1 Velocity Sens"
        )
        tvf_layout.addRow(tvf_env_time1_velocity_sens_slider)

        tvf_env_time4_velocity_sens_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_ENV_TIME_4_VELOCITY_SENS, "Env Time 4 Velocity Sens"
        )
        tvf_layout.addRow(tvf_env_time4_velocity_sens_slider)

        tvf_env_time1_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_ENV_TIME_1, "Env Time 1"
        )
        tvf_layout.addRow(tvf_env_time1_slider)

        tvf_env_time2_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_ENV_TIME_2, "Env Time 2"
        )
        tvf_layout.addRow(tvf_env_time2_slider)

        tvf_env_time3_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_ENV_TIME_3, "Env Time 3"
        )
        tvf_layout.addRow(tvf_env_time3_slider)

        tvf_env_time4_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_ENV_TIME_4, "Env Time 4"
        )
        tvf_layout.addRow(tvf_env_time4_slider)

        tvf_env_level0_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_ENV_LEVEL_0, "Env Level 0"
        )
        tvf_layout.addRow(tvf_env_level0_slider)

        tvf_env_level1_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_ENV_LEVEL_1, "Env Level 1"
        )
        tvf_layout.addRow(tvf_env_level1_slider)

        tvf_env_level2_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_ENV_LEVEL_2, "Env Level 2"
        )
        tvf_layout.addRow(tvf_env_level2_slider)

        tvf_env_level3_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_ENV_LEVEL_3, "Env Level 3"
        )
        tvf_layout.addRow(tvf_env_level3_slider)

        tvf_env_level4_slider = self._create_parameter_slider(
            DrumPartialParameter.TVF_ENV_LEVEL_4, "Env Level 4"
        )
        tvf_layout.addRow(tvf_env_level4_slider)
        return tvf_group

    def _create_pitch_env_group(self):
        """create pitch env area"""
        # Pitch Env Group
        pitch_env_group = QGroupBox("Pitch Env")
        pitch_env_layout = QFormLayout()
        pitch_env_group.setLayout(pitch_env_layout)

        # Add pitch env parameters
        pitch_env_depth_slider = self._create_parameter_slider(
            DrumPartialParameter.PITCH_ENV_DEPTH, "Pitch Env Depth"
        )
        pitch_env_layout.addRow(pitch_env_depth_slider)

        pitch_env_velocity_sens_slider = self._create_parameter_slider(
            DrumPartialParameter.PITCH_ENV_VELOCITY_SENS, "Pitch Env Velocity Sens"
        )
        pitch_env_layout.addRow(pitch_env_velocity_sens_slider)

        pitch_env_time1_velocity_sens_slider = self._create_parameter_slider(
            DrumPartialParameter.PITCH_ENV_TIME_1_VELOCITY_SENS,
            "Pitch Env Time 1 Velocity Sens",
        )
        pitch_env_layout.addRow(pitch_env_time1_velocity_sens_slider)

        pitch_env_time4_velocity_sens_slider = self._create_parameter_slider(
            DrumPartialParameter.PITCH_ENV_TIME_4_VELOCITY_SENS,
            "Pitch Env Time 4 Velocity Sens",
        )
        pitch_env_layout.addRow(pitch_env_time4_velocity_sens_slider)

        pitch_env_time1_slider = self._create_parameter_slider(
            DrumPartialParameter.PITCH_ENV_TIME_1, "Pitch Env Time 1"
        )
        pitch_env_layout.addRow(pitch_env_time1_slider)

        pitch_env_time2_slider = self._create_parameter_slider(
            DrumPartialParameter.PITCH_ENV_TIME_2, "Pitch Env Time 2"
        )
        pitch_env_layout.addRow(pitch_env_time2_slider)

        pitch_env_time3_slider = self._create_parameter_slider(
            DrumPartialParameter.PITCH_ENV_TIME_3, "Pitch Env Time 3"
        )
        pitch_env_layout.addRow(pitch_env_time3_slider)

        pitch_env_time4_slider = self._create_parameter_slider(
            DrumPartialParameter.PITCH_ENV_TIME_4, "Pitch Env Time 4"
        )
        pitch_env_layout.addRow(pitch_env_time4_slider)

        pitch_env_level0_slider = self._create_parameter_slider(
            DrumPartialParameter.PITCH_ENV_LEVEL_0, "Pitch Env Level 0"
        )
        pitch_env_layout.addRow(pitch_env_level0_slider)

        pitch_env_level1_slider = self._create_parameter_slider(
            DrumPartialParameter.PITCH_ENV_LEVEL_1, "Pitch Env Level 1"
        )
        pitch_env_layout.addRow(pitch_env_level1_slider)

        pitch_env_level2_slider = self._create_parameter_slider(
            DrumPartialParameter.PITCH_ENV_LEVEL_2, "Pitch Env Level 2"
        )
        pitch_env_layout.addRow(pitch_env_level2_slider)

        pitch_env_level3_slider = self._create_parameter_slider(
            DrumPartialParameter.PITCH_ENV_LEVEL_3, "Pitch Env Level 3"
        )
        pitch_env_layout.addRow(pitch_env_level3_slider)

        pitch_env_level4_slider = self._create_parameter_slider(
            DrumPartialParameter.PITCH_ENV_LEVEL_4, "Pitch Env Level 4"
        )
        pitch_env_layout.addRow(pitch_env_level4_slider)
        return pitch_env_group
