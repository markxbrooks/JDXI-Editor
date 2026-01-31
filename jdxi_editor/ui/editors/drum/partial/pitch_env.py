"""
Module: drum_pitch_env
================

This module defines the `DrumPitchEnvSection` class, which provides a PySide6-based
user interface for editing drum pitch envelope parameters in the Roland JD-Xi synthesizer.
It extends the `QWidget` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying drum pitch envelope parameters, including
  pitch env depth, pitch env velocity sens, pitch env time1 velocity sens, pitch env time4 velocity sens,
  pitch env time1, pitch env time2, pitch env time3, pitch env time4, pitch env level0, pitch env level1,
  pitch env level2, pitch env level3, and pitch env level4.
- Includes a visual envelope plot showing the 5-level, 4-time-segment envelope curve.

Dependencies:
-------------
- PySide6 (for UI components and event handling)
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

Usage:
------
The `DrumPitchEnvSection` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MIDIHelper()
    editor = DrumPitchEnvSection(midi_helper)
    editor.show()
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.drum.partial.base import DrumBaseSection
from jdxi_editor.ui.widgets.spec import SliderSpec
from jdxi_editor.ui.widgets.editor.helper import create_group_and_grid_layout
from jdxi_editor.ui.widgets.plot.drum import DrumPitchEnvPlot


class DrumPitchEnvSection(DrumBaseSection):
    """Drum Pitch Env Section for the JDXI Editor"""

    PARAM_SPECS = [
        # Row 0: Depth, V-Sens, T1 V-Sens, T4 V-Sens
        SliderSpec(DrumPartialParam.PITCH_ENV_DEPTH, "Depth", vertical=True),
        SliderSpec(DrumPartialParam.PITCH_ENV_VELOCITY_SENS, "V-Sens", vertical=True),
        SliderSpec(DrumPartialParam.PITCH_ENV_TIME_1_VELOCITY_SENS, "T1 V-Sens", vertical=True),
        SliderSpec(DrumPartialParam.PITCH_ENV_TIME_4_VELOCITY_SENS, "T4 V-Sens", vertical=True),
        # Row 1: Time 1, Time 2, Time 3, Time 4
        SliderSpec(DrumPartialParam.PITCH_ENV_TIME_1, "Time 1", vertical=True),
        SliderSpec(DrumPartialParam.PITCH_ENV_TIME_2, "Time 2", vertical=True),
        SliderSpec(DrumPartialParam.PITCH_ENV_TIME_3, "Time 3", vertical=True),
        SliderSpec(DrumPartialParam.PITCH_ENV_TIME_4, "Time 4", vertical=True),
        # Row 2: Level 0, Level 1, Level 2, Level 3, Level 4
        SliderSpec(DrumPartialParam.PITCH_ENV_LEVEL_0, "Level 0", vertical=True),
        SliderSpec(DrumPartialParam.PITCH_ENV_LEVEL_1, "Level 1", vertical=True),
        SliderSpec(DrumPartialParam.PITCH_ENV_LEVEL_2, "Level 2", vertical=True),
        SliderSpec(DrumPartialParam.PITCH_ENV_LEVEL_3, "Level 3", vertical=True),
        SliderSpec(DrumPartialParam.PITCH_ENV_LEVEL_4, "Level 4", vertical=True),
    ]

    envelope_changed = Signal(dict)

    def __init__(
        self,
        controls: dict[DrumPartialParam, QWidget],
        midi_helper: MidiIOHelper,
    ):
        """
        Initialize the DrumPitchEnvSection

        :param controls: dict
        :param create_parameter_combo_box: Callable
        :param create_parameter_slider: Callable
        :param midi_helper: MidiIOHelper
        """
        # Initialize envelope before super().__init__() because setup_ui() will be called
        # during super().__init__() and it needs envelope
        self.envelope = {
            "depth": 64,
            "v_sens": 64,
            "t1_v_sens": 64,
            "t4_v_sens": 64,
            "time_1": 10,
            "time_2": 10,
            "time_3": 34,
            "time_4": 9,
            "level_0": 0,
            "level_1": 64,
            "level_2": 16,
            "level_3": 15,
            "level_4": -25,
        }

        # Pass controls to super().__init__() so widgets created from PARAM_SPECS
        # are stored in the same dict
        super().__init__(controls=controls or {}, midi_helper=midi_helper)
        # Widgets from PARAM_SPECS are already in self.controls from build_widgets()
        # Note: _setup_ui() is overridden in DrumBaseSection to do nothing, so we need to call setup_ui() explicitly
        self.setup_ui()

    def setup_ui(self) -> None:
        """setup UI"""
        # Get layout (this will create scrolled_layout via DrumBaseSection.get_layout() if needed)
        layout = self.get_layout()

        # --- Main container with controls and plot
        main_container = QWidget()
        main_layout = QHBoxLayout(main_container)
        main_layout.addStretch()
        layout.addWidget(main_container)

        controls_group, controls_layout = create_group_and_grid_layout(
            group_name="Pitch Envelope Controls"
        )
        JDXi.UI.Theme.apply_adsr_style(widget=controls_group, analog=self.analog)
        main_layout.addWidget(controls_group)
        self.create_sliders(controls_layout)

        self.setup_plot()
        main_layout.addWidget(self.plot)
        main_layout.addStretch()

    def setup_plot(self):
        # Right side: Envelope plot
        self.plot = DrumPitchEnvPlot(
            width=JDXi.UI.Style.ADSR_PLOT_WIDTH,
            height=JDXi.UI.Style.ADSR_PLOT_HEIGHT,
            envelope=self.envelope,
            parent=self,
        )

    def create_sliders(self, controls_layout: QGridLayout):
        """Create sliders and connect them - widgets are created from PARAM_SPECS"""
        # Widgets are created automatically from PARAM_SPECS in build_widgets()
        # Access them from self.controls and add to grid layout in the same order
        
        # Row 0: Depth, V-Sens, T1 V-Sens, T4 V-Sens
        row = 0
        depth_slider = self.controls[DrumPartialParam.PITCH_ENV_DEPTH]
        self.depth_slider = depth_slider  # Keep reference for compatibility
        controls_layout.addWidget(depth_slider, row, 0)
        depth_slider.valueChanged.connect(
            lambda v: self._update_envelope("depth", v, DrumPartialParam.PITCH_ENV_DEPTH)
        )

        v_sens_slider = self.controls[DrumPartialParam.PITCH_ENV_VELOCITY_SENS]
        self.v_sens_slider = v_sens_slider
        controls_layout.addWidget(v_sens_slider, row, 1)
        v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope("v_sens", v, DrumPartialParam.PITCH_ENV_VELOCITY_SENS)
        )

        t1_v_sens_slider = self.controls[DrumPartialParam.PITCH_ENV_TIME_1_VELOCITY_SENS]
        self.t1_v_sens_slider = t1_v_sens_slider
        controls_layout.addWidget(t1_v_sens_slider, row, 2)
        t1_v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope("t1_v_sens", v, DrumPartialParam.PITCH_ENV_TIME_1_VELOCITY_SENS)
        )

        t4_v_sens_slider = self.controls[DrumPartialParam.PITCH_ENV_TIME_4_VELOCITY_SENS]
        self.t4_v_sens_slider = t4_v_sens_slider
        controls_layout.addWidget(t4_v_sens_slider, row, 3)
        t4_v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope("t4_v_sens", v, DrumPartialParam.PITCH_ENV_TIME_4_VELOCITY_SENS)
        )

        # Row 1: Time 1, Time 2, Time 3, Time 4
        row += 1
        time_1_slider = self.controls[DrumPartialParam.PITCH_ENV_TIME_1]
        self.time_1_slider = time_1_slider
        controls_layout.addWidget(time_1_slider, row, 0)
        time_1_slider.valueChanged.connect(
            lambda v: self._update_envelope("time_1", v, DrumPartialParam.PITCH_ENV_TIME_1)
        )

        time_2_slider = self.controls[DrumPartialParam.PITCH_ENV_TIME_2]
        self.time_2_slider = time_2_slider
        controls_layout.addWidget(time_2_slider, row, 1)
        time_2_slider.valueChanged.connect(
            lambda v: self._update_envelope("time_2", v, DrumPartialParam.PITCH_ENV_TIME_2)
        )

        time_3_slider = self.controls[DrumPartialParam.PITCH_ENV_TIME_3]
        self.time_3_slider = time_3_slider
        controls_layout.addWidget(time_3_slider, row, 2)
        time_3_slider.valueChanged.connect(
            lambda v: self._update_envelope("time_3", v, DrumPartialParam.PITCH_ENV_TIME_3)
        )

        time_4_slider = self.controls[DrumPartialParam.PITCH_ENV_TIME_4]
        self.time_4_slider = time_4_slider
        controls_layout.addWidget(time_4_slider, row, 3)
        time_4_slider.valueChanged.connect(
            lambda v: self._update_envelope("time_4", v, DrumPartialParam.PITCH_ENV_TIME_4)
        )

        # Row 2: Level 0, Level 1, Level 2, Level 3, Level 4
        row += 1
        level_0_slider = self.controls[DrumPartialParam.PITCH_ENV_LEVEL_0]
        self.level_0_slider = level_0_slider
        controls_layout.addWidget(level_0_slider, row, 0)
        level_0_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_0", v, DrumPartialParam.PITCH_ENV_LEVEL_0)
        )

        level_1_slider = self.controls[DrumPartialParam.PITCH_ENV_LEVEL_1]
        self.level_1_slider = level_1_slider
        controls_layout.addWidget(level_1_slider, row, 1)
        level_1_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_1", v, DrumPartialParam.PITCH_ENV_LEVEL_1)
        )

        level_2_slider = self.controls[DrumPartialParam.PITCH_ENV_LEVEL_2]
        self.level_2_slider = level_2_slider
        controls_layout.addWidget(level_2_slider, row, 2)
        level_2_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_2", v, DrumPartialParam.PITCH_ENV_LEVEL_2)
        )

        level_3_slider = self.controls[DrumPartialParam.PITCH_ENV_LEVEL_3]
        self.level_3_slider = level_3_slider
        controls_layout.addWidget(level_3_slider, row, 3)
        level_3_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_3", v, DrumPartialParam.PITCH_ENV_LEVEL_3)
        )

        level_4_slider = self.controls[DrumPartialParam.PITCH_ENV_LEVEL_4]
        self.level_4_slider = level_4_slider
        controls_layout.addWidget(level_4_slider, row, 4)
        level_4_slider.valueChanged.connect(
            lambda v: self._update_envelope("level_4", v, DrumPartialParam.PITCH_ENV_LEVEL_4)
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
