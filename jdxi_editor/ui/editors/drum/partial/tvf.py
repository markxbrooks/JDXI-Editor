"""
Module: drum_tvf
==============

This module defines the `DrumTVFSection` class, which provides a PySide6-based
user interface for editing drum TVF parameters in the Roland JD-Xi synthesizer.
It extends the `QWidget` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying drum TVF parameters, including
  filter type, cutoff frequency, cutoff velocity curve, env depth, env velocity curve type,
  env velocity sens, env time1 velocity sens, env time4 velocity sens, env time1, env time2,
  env time3, env time4, env level0, env level1, env level2, env level3, and env level4.
- Includes a visual envelope plot showing the 5-level, 4-time-segment TVF envelope curve.

Dependencies:
-------------
- PySide6 (for UI components and event handling)
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

Usage:
------
The `DrumTVFSection` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MidiIOHelper()
    editor = DrumTVFSection(midi_helper)
    editor.show()
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import (
    QIcon,
)
from PySide6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.drum.name import DrumDisplayName
from jdxi_editor.midi.data.parameter.drum.option import DrumDisplayOptions
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.drum.partial.base import DrumBaseSection
from jdxi_editor.ui.image.utils import base64_to_pixmap
from jdxi_editor.ui.image.waveform import generate_waveform_icon
from jdxi_editor.ui.style import JDXiUIStyle
from jdxi_editor.ui.widgets.editor.helper import (
    create_layout_with_widgets, create_centered_layout_with_child,
)
from jdxi_editor.ui.widgets.plot.drum import DrumTVFEnvPlot
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec


class DrumTVFSection(DrumBaseSection):
    """Drum TVF Section for the JDXI Editor"""

    SLIDER_GROUPS = {
        "controls": [
            ComboBoxSpec(
                DrumPartialParam.TVF_FILTER_TYPE,
                DrumDisplayName.TVF_FILTER_TYPE,
                options=DrumDisplayOptions.TVF_FILTER_TYPE,
                values=[0, 1, 2, 3, 4, 5, 6],
            ),
            SliderSpec(
                DrumPartialParam.TVF_CUTOFF_FREQUENCY,
                DrumDisplayName.TVF_CUTOFF_FREQUENCY,
            ),
            ComboBoxSpec(
                DrumPartialParam.TVF_CUTOFF_VELOCITY_CURVE,
                DrumDisplayName.TVF_CUTOFF_VELOCITY_CURVE,
                options=DrumDisplayOptions.TVF_CUTOFF_VELOCITY_CURVE,
                values=[0, 1, 2, 3, 4, 5, 6, 7],
            ),
            ComboBoxSpec(
                DrumPartialParam.TVF_ENV_VELOCITY_CURVE_TYPE,
                DrumDisplayName.TVF_ENV_VELOCITY_CURVE_TYPE,
                options=DrumDisplayOptions.TVF_ENV_VELOCITY_CURVE_TYPE,
                values=[0, 1, 2, 3, 4, 5, 6, 7],
            ),
            SliderSpec(
                DrumPartialParam.TVF_ENV_DEPTH, DrumDisplayName.TVF_DEPTH, vertical=True
            ),
            SliderSpec(
                DrumPartialParam.TVF_ENV_VELOCITY_SENS,
                DrumDisplayName.TVF_V_SENS,
                vertical=True,
            ),
            SliderSpec(
                DrumPartialParam.TVF_ENV_TIME_1_VELOCITY_SENS,
                DrumDisplayName.TVF_T1_V_SENS,
                vertical=True,
            ),
            SliderSpec(
                DrumPartialParam.TVF_ENV_TIME_4_VELOCITY_SENS,
                DrumDisplayName.TVF_T4_V_SENS,
                vertical=True,
            ),
            SliderSpec(
                DrumPartialParam.TVF_ENV_TIME_1, DrumDisplayName.TVF_TIME_1, vertical=True
            ),
            SliderSpec(
                DrumPartialParam.TVF_ENV_TIME_2, DrumDisplayName.TVF_TIME_2, vertical=True
            ),
            SliderSpec(
                DrumPartialParam.TVF_ENV_TIME_3, DrumDisplayName.TVF_TIME_3, vertical=True
            ),
            SliderSpec(
                DrumPartialParam.TVF_ENV_TIME_4, DrumDisplayName.TVF_TIME_4, vertical=True
            ),
            SliderSpec(
                DrumPartialParam.TVF_ENV_LEVEL_0, DrumDisplayName.TVF_LEVEL_0, vertical=True
            ),
            SliderSpec(
                DrumPartialParam.TVF_ENV_LEVEL_1, DrumDisplayName.TVF_LEVEL_1, vertical=True
            ),
            SliderSpec(
                DrumPartialParam.TVF_ENV_LEVEL_2, DrumDisplayName.TVF_LEVEL_2, vertical=True
            ),
            SliderSpec(
                DrumPartialParam.TVF_ENV_LEVEL_3, DrumDisplayName.TVF_LEVEL_3, vertical=True
            ),
            SliderSpec(
                DrumPartialParam.TVF_ENV_LEVEL_4, DrumDisplayName.TVF_LEVEL_4, vertical=True
            ),
        ],
    }

    envelope_changed = Signal(dict)

    def __init__(
        self,
        controls: dict[DrumPartialParam, QWidget],
        midi_helper: MidiIOHelper,
    ):
        """
        Initialize the DrumTVFSection

        :param controls: dict
        :param midi_helper: MidiIOHelper
        """
        self.envelope = {
            "depth": 64,
            "v_sens": 64,
            "t1_v_sens": 64,
            "t4_v_sens": 64,
            "time_1": 21,
            "time_2": 16,
            "time_3": 40,
            "time_4": 25,
            "level_0": 0,
            "level_1": 127,
            "level_2": 70,
            "level_3": 70,
            "level_4": 0,
        }
        super().__init__(controls=controls or {}, midi_helper=midi_helper)
        self.setup_ui()

    def setup_ui(self):
        """setup UI"""
        # Get layout (this will create scrolled_layout via DrumBaseSection.get_layout() if needed)
        layout = self.get_layout()

        # Create plot first (needed by envelope group)
        self._create_tvf_plot()

        # --- Main container with controls and plot
        main_container = QWidget()
        main_layout = QHBoxLayout(main_container)
        main_layout.addStretch()
        layout.addWidget(main_container)

        self.tvf_tab_widget = QTabWidget()

        # --- Basic TVF controls and envelope controls ---
        controls_icon = JDXi.UI.Icon.get_icon("mdi.tune", color=JDXi.UI.Style.GREY)
        self.tvf_tab_widget.addTab(
            self._create_tvf_basic_group(), controls_icon, "Controls"
        )

        # --- TVF Envelope Controls
        envelope_icon_base64 = generate_waveform_icon("adsr", "#FFFFFF", 1.0)
        envelope_icon = QIcon(base64_to_pixmap(envelope_icon_base64))
        self.tvf_tab_widget.addTab(
            self._create_tvf_env_group(), envelope_icon, "Envelope"
        )

        main_layout.addWidget(self.tvf_tab_widget)
        main_layout.addStretch()

    def _create_tvf_env_group(self) -> QGroupBox:
        """Envelope controls group"""
        envelope_group = QGroupBox("Envelope")
        envelope_group_layout = QHBoxLayout()
        #  --- Left side: Envelope sliders  ---
        envelope_slider_layout = QGridLayout()
        envelope_group.setLayout(envelope_group_layout)

        envelope_group.setStyleSheet(JDXi.UI.Style.ADSR)

        #  --- Use widgets from SLIDER_GROUPS["controls"] and connect them ---
        row = 0
        depth_slider = self.controls[DrumPartialParam.TVF_ENV_DEPTH]
        self.depth_slider = depth_slider  # Keep reference for compatibility
        envelope_slider_layout.addWidget(depth_slider, row, 0)
        depth_slider.valueChanged.connect(
            lambda v: self._update_envelope("depth", v, DrumPartialParam.TVF_ENV_DEPTH)
        )

        v_sens_slider = self.controls[DrumPartialParam.TVF_ENV_VELOCITY_SENS]
        self.v_sens_slider = v_sens_slider
        envelope_slider_layout.addWidget(v_sens_slider, row, 1)
        v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                "v_sens", v, DrumPartialParam.TVF_ENV_VELOCITY_SENS
            )
        )

        t1_v_sens_slider = self.controls[DrumPartialParam.TVF_ENV_TIME_1_VELOCITY_SENS]
        self.t1_v_sens_slider = t1_v_sens_slider
        envelope_slider_layout.addWidget(t1_v_sens_slider, row, 2)
        t1_v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                "t1_v_sens", v, DrumPartialParam.TVF_ENV_TIME_1_VELOCITY_SENS
            )
        )

        t4_v_sens_slider = self.controls[DrumPartialParam.TVF_ENV_TIME_4_VELOCITY_SENS]
        self.t4_v_sens_slider = t4_v_sens_slider
        envelope_slider_layout.addWidget(t4_v_sens_slider, row, 3)
        t4_v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                "t4_v_sens", v, DrumPartialParam.TVF_ENV_TIME_4_VELOCITY_SENS
            )
        )

        row += 1
        #  --- Time controls  ---
        time_1_slider = self.controls[DrumPartialParam.TVF_ENV_TIME_1]
        self.time_1_slider = time_1_slider
        envelope_slider_layout.addWidget(time_1_slider, row, 0)
        time_1_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                "time_1", v, DrumPartialParam.TVF_ENV_TIME_1
            )
        )

        time_2_slider = self.controls[DrumPartialParam.TVF_ENV_TIME_2]
        self.time_2_slider = time_2_slider
        envelope_slider_layout.addWidget(time_2_slider, row, 1)
        time_2_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                "time_2", v, DrumPartialParam.TVF_ENV_TIME_2
            )
        )

        time_3_slider = self.controls[DrumPartialParam.TVF_ENV_TIME_3]
        self.time_3_slider = time_3_slider
        envelope_slider_layout.addWidget(time_3_slider, row, 2)
        time_3_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                "time_3", v, DrumPartialParam.TVF_ENV_TIME_3
            )
        )

        time_4_slider = self.controls[DrumPartialParam.TVF_ENV_TIME_4]
        self.time_4_slider = time_4_slider
        envelope_slider_layout.addWidget(time_4_slider, row, 3)
        time_4_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                "time_4", v, DrumPartialParam.TVF_ENV_TIME_4
            )
        )

        row += 1
        #  --- Level controls ---
        level_0_slider = self.controls[DrumPartialParam.TVF_ENV_LEVEL_0]
        self.level_0_slider = level_0_slider
        envelope_slider_layout.addWidget(level_0_slider, row, 0)
        level_0_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                "level_0", v, DrumPartialParam.TVF_ENV_LEVEL_0
            )
        )

        level_1_slider = self.controls[DrumPartialParam.TVF_ENV_LEVEL_1]
        self.level_1_slider = level_1_slider
        envelope_slider_layout.addWidget(level_1_slider, row, 1)
        level_1_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                "level_1", v, DrumPartialParam.TVF_ENV_LEVEL_1
            )
        )

        level_2_slider = self.controls[DrumPartialParam.TVF_ENV_LEVEL_2]
        self.level_2_slider = level_2_slider
        envelope_slider_layout.addWidget(level_2_slider, row, 2)
        level_2_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                "level_2", v, DrumPartialParam.TVF_ENV_LEVEL_2
            )
        )

        level_3_slider = self.controls[DrumPartialParam.TVF_ENV_LEVEL_3]
        self.level_3_slider = level_3_slider
        envelope_slider_layout.addWidget(level_3_slider, row, 3)
        level_3_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                "level_3", v, DrumPartialParam.TVF_ENV_LEVEL_3
            )
        )

        level_4_slider = self.controls[DrumPartialParam.TVF_ENV_LEVEL_4]
        self.level_4_slider = level_4_slider
        envelope_slider_layout.addWidget(level_4_slider, row, 4)
        level_4_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                "level_4", v, DrumPartialParam.TVF_ENV_LEVEL_4
            )
        )

        #  --- Right side: Envelope plot (created in setup_ui())  ---
        envelope_plot_layout = QVBoxLayout()
        envelope_plot_layout.addWidget(self.plot)

        envelope_group_layout.addLayout(envelope_slider_layout)
        envelope_group_layout.addLayout(envelope_plot_layout)

        return envelope_group

    def _create_tvf_basic_group(self) -> QGroupBox:
        """Basic TVF controls group - widgets from SLIDER_GROUPS['controls'] in build_widgets()."""
        group = QGroupBox("Controls")

        basic_tvf_layout = QFormLayout()
        centered_layout = create_centered_layout_with_child(basic_tvf_layout)
        group.setLayout(centered_layout)

        tvf_filter_type_combo = self.controls[DrumPartialParam.TVF_FILTER_TYPE]
        basic_tvf_layout.addRow(tvf_filter_type_combo)

        tvf_cutoff_velocity_curve_spin = self.controls[
            DrumPartialParam.TVF_CUTOFF_VELOCITY_CURVE
        ]
        basic_tvf_layout.addRow(tvf_cutoff_velocity_curve_spin)

        tvf_env_velocity_curve_type_spin = self.controls[
            DrumPartialParam.TVF_ENV_VELOCITY_CURVE_TYPE
        ]
        basic_tvf_layout.addRow(tvf_env_velocity_curve_type_spin)
        tvf_cutoff_frequency_slider = self.controls[
            DrumPartialParam.TVF_CUTOFF_FREQUENCY
        ]
        tvf_cutoff_frequency_layout = create_layout_with_widgets(
            widgets=[tvf_cutoff_frequency_slider], vertical=False
        )
        basic_tvf_layout.addRow(tvf_cutoff_frequency_layout)
        group.setStyleSheet(JDXiUIStyle.ADSR)
        group.setMinimumHeight(JDXi.UI.Dimensions.EDITOR_DRUM.MIN_HEIGHT)
        group.setMaximumHeight(JDXi.UI.Dimensions.EDITOR_DRUM.HEIGHT)
        return group

    def _create_tvf_plot(self):
        self.plot = DrumTVFEnvPlot(
            width=JDXi.UI.Style.ADSR_PLOT_WIDTH,
            height=JDXi.UI.Style.ADSR_PLOT_HEIGHT,
            envelope=self.envelope,
            parent=self,
        )

    def _update_envelope(
        self, key: str, value: int, param: DrumPartialParam = None
    ) -> None:
        """Update envelope value and refresh plot

        :param key: str Envelope parameter key
        :param value: int Display value from slider
        :param param: AddressParameterDrumPartial Parameter object for conversion
        """
        # Convert display value to MIDI value if parameter is provided
        if param and hasattr(param, "convert_from_display"):
            midi_value = param.convert_from_display(value)
        else:
            # For parameters without special conversion, assume value is already MIDI
            midi_value = value

        self.envelope[key] = midi_value
        self.plot.set_values(self.envelope)
        self.envelope_changed.emit(self.envelope)
