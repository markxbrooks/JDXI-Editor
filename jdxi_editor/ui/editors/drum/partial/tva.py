"""
Module: drum_tva
==============

This module defines the `DrumTVASection` class, which provides a PySide6-based
user interface for editing drum TVA parameters in the Roland JD-Xi synthesizer.
It extends the `QWidget` base class and integrates MIDI communication for real-time
parameter adjustments and preset management.

Key Features:
-------------
- Provides a graphical editor for modifying drum TVA parameters, including
  level velocity curve, level velocity sens, env time1 velocity sens, env time4 velocity sens,
  env time1, env time2, env time3, env time4, env level1, env level2, env level3, and env level4.

Dependencies:
-------------
- PySide6 (for UI components and event handling)
- MIDIHelper (for handling MIDI communication)
- PresetHandler (for managing synth presets)
- Various custom enums and helper classes (AnalogParameter, AnalogCommonParameter, etc.)

Usage:
------
The `DrumTVASection` class can be instantiated as part of a larger PySide6 application.
It requires a `MIDIHelper` instance for proper communication with the synthesizer.

Example:
--------
    midi_helper = MIDIHelper()
    editor = DrumTVASection(midi_helper)
    editor.show()
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.parameter.drum.option import DrumDisplayOptions, DrumDisplayValues
from jdxi_editor.midi.data.parameter.drum.partial import DrumPartialParam
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.editors.drum.partial.base import DrumBaseSection
from jdxi_editor.ui.widgets.editor.helper import (
    create_group_with_layout,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.envelope.parameter import EnvelopeParameter
from jdxi_editor.ui.widgets.plot.drum import DrumTVAEnvPlot
from jdxi_editor.ui.widgets.spec import ComboBoxSpec, SliderSpec


class DrumTVASection(DrumBaseSection):
    """Drum TVA Section for the JDXI Editor"""

    PARAM_SPECS = [
        # TVA Level Velocity Curve
        ComboBoxSpec(
            DrumPartialParam.TVA_LEVEL_VELOCITY_CURVE,
            DrumPartialParam.TVA_LEVEL_VELOCITY_CURVE.display_name,
            options=DrumDisplayOptions.TVA_LEVEL_VELOCITY_CURVE,
            values=DrumDisplayValues.TVA_LEVEL_VELOCITY_CURVE,
        ),
        # TVA Envelope Controls - Row 0: Level Velocity Sens, T1 V-Sens, T4 V-Sens
        SliderSpec(
            DrumPartialParam.TVA_LEVEL_VELOCITY_SENS,
            DrumPartialParam.TVA_LEVEL_VELOCITY_SENS.display_name,
            vertical=True,
        ),
        SliderSpec(
            DrumPartialParam.TVA_ENV_TIME_1_VELOCITY_SENS,
            DrumPartialParam.TVA_ENV_TIME_1_VELOCITY_SENS.display_name,
            vertical=True,
        ),
        SliderSpec(
            DrumPartialParam.TVA_ENV_TIME_4_VELOCITY_SENS,
            DrumPartialParam.TVA_ENV_TIME_4_VELOCITY_SENS.display_name,
            vertical=True,
        ),
        # Row 1: Time 1, Time 2, Time 3, Time 4
        SliderSpec(
            DrumPartialParam.TVA_ENV_TIME_1, DrumPartialParam.TVA_ENV_TIME_1.display_name, vertical=True
        ),
        SliderSpec(
            DrumPartialParam.TVA_ENV_TIME_2, DrumPartialParam.TVA_ENV_TIME_2.display_name, vertical=True
        ),
        SliderSpec(
            DrumPartialParam.TVA_ENV_TIME_3, DrumPartialParam.TVA_ENV_TIME_3.display_name, vertical=True
        ),
        SliderSpec(
            DrumPartialParam.TVA_ENV_TIME_4, DrumPartialParam.TVA_ENV_TIME_4.display_name, vertical=True
        ),
        # Row 2: Level 1, Level 2, Level 3
        SliderSpec(
            DrumPartialParam.TVA_ENV_LEVEL_1, DrumPartialParam.TVA_ENV_LEVEL_1.display_name, vertical=True
        ),
        SliderSpec(
            DrumPartialParam.TVA_ENV_LEVEL_2, DrumPartialParam.TVA_ENV_LEVEL_2.display_name, vertical=True
        ),
        SliderSpec(
            DrumPartialParam.TVA_ENV_LEVEL_3, DrumPartialParam.TVA_ENV_LEVEL_3.display_name, vertical=True
        ),
    ]

    envelope_changed = Signal(dict)

    def __init__(
        self,
        controls: dict[DrumPartialParam, QWidget],
        midi_helper: MidiIOHelper,
    ):
        """
        Initialize the DrumTVASection

        :param controls: dict
        :param midi_helper: MidiIOHelper
        """
        # Initialize envelope before super().__init__() because setup_ui() may need it
        self.envelope = {
            EnvelopeParameter.T1_V_SENS: 64,
            EnvelopeParameter.T4_V_SENS: 64,
            EnvelopeParameter.TIME_0: 0,
            EnvelopeParameter.TIME_1: 32,
            EnvelopeParameter.TIME_2: 32,
            EnvelopeParameter.TIME_3: 64,
            EnvelopeParameter.TIME_4: 64,
            EnvelopeParameter.LEVEL_0: 0,
            EnvelopeParameter.LEVEL_1: 120,
            EnvelopeParameter.LEVEL_2: 80,
            EnvelopeParameter.LEVEL_3: 70,
        }
        # Pass controls to super().__init__() so widgets created from PARAM_SPECS
        # are stored in the same dict
        super().__init__(controls=controls or {}, midi_helper=midi_helper)
        # Widgets from PARAM_SPECS are already in self.controls from build_widgets()
        # Note: _setup_ui() is overridden in DrumBaseSection to do nothing, so we need to call setup_ui() explicitly
        self.setup_ui()

    def setup_ui(self):
        """setup UI"""

        self.tva_level_velocity_curve_spin = self._create_tva_spin()
        self.tva_group = self._create_tva_group()
        self.plot = self._create_tva_plot()

        main_row_hlayout = create_layout_with_widgets(
            widgets=[self.tva_group, self.plot], vertical=False
        )

        # Get layout (this will create scrolled_layout via DrumBaseSection.get_layout() if needed)
        layout = self.get_layout()

        main_vbox_layout = create_layout_with_widgets(
            widgets=[self.tva_level_velocity_curve_spin], vertical=True
        )
        main_vbox_layout.addLayout(main_row_hlayout)
        layout.addLayout(main_vbox_layout)

    def _create_tva_spin(self) -> QWidget:
        # Widget is created automatically from PARAM_SPECS in build_widgets()
        return self.controls[DrumPartialParam.TVA_LEVEL_VELOCITY_CURVE]

    def _create_tva_group(self):
        """TVA Group"""
        envelope_slider_layout = QGridLayout()
        tva_group, _ = create_group_with_layout(
            label="TVA",
            child_layout=envelope_slider_layout,
            style_sheet=JDXi.UI.Style.ADSR,
        )

        # --- Add TVA Velocity Sensitivity controls - widgets are created from PARAM_SPECS
        row = 0
        tva_level_velocity_sens_slider = self.controls[
            DrumPartialParam.TVA_LEVEL_VELOCITY_SENS
        ]
        envelope_slider_layout.addWidget(tva_level_velocity_sens_slider, row, 0)

        t1_v_sens_slider = self.controls[DrumPartialParam.TVA_ENV_TIME_1_VELOCITY_SENS]
        self.t1_v_sens_slider = t1_v_sens_slider  # Keep reference for compatibility
        envelope_slider_layout.addWidget(t1_v_sens_slider, row, 1)
        t1_v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                EnvelopeParameter.T1_V_SENS, v, DrumPartialParam.TVA_ENV_TIME_1_VELOCITY_SENS
            )
        )

        t4_v_sens_slider = self.controls[DrumPartialParam.TVA_ENV_TIME_4_VELOCITY_SENS]
        self.t4_v_sens_slider = t4_v_sens_slider  # Keep reference for compatibility
        envelope_slider_layout.addWidget(t4_v_sens_slider, row, 2)
        t4_v_sens_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                EnvelopeParameter.T4_V_SENS, v, DrumPartialParam.TVA_ENV_TIME_4_VELOCITY_SENS
            )
        )

        # --- TVA Time Row ---
        row = 1
        time_1_slider = self.controls[DrumPartialParam.TVA_ENV_TIME_1]
        self.time_1_slider = time_1_slider
        envelope_slider_layout.addWidget(time_1_slider, row, 0)
        time_1_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                EnvelopeParameter.TIME_1, v, DrumPartialParam.TVA_ENV_TIME_1
            )
        )

        time_2_slider = self.controls[DrumPartialParam.TVA_ENV_TIME_2]
        self.time_2_slider = time_2_slider
        envelope_slider_layout.addWidget(time_2_slider, row, 1)
        time_2_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                EnvelopeParameter.TIME_2, v, DrumPartialParam.TVA_ENV_TIME_2
            )
        )

        time_3_slider = self.controls[DrumPartialParam.TVA_ENV_TIME_3]
        self.time_3_slider = time_3_slider
        envelope_slider_layout.addWidget(time_3_slider, row, 2)
        time_3_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                EnvelopeParameter.TIME_3, v, DrumPartialParam.TVA_ENV_TIME_3
            )
        )

        time_4_slider = self.controls[DrumPartialParam.TVA_ENV_TIME_4]
        self.time_4_slider = time_4_slider
        envelope_slider_layout.addWidget(time_4_slider, row, 3)
        time_4_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                EnvelopeParameter.TIME_4, v, DrumPartialParam.TVA_ENV_TIME_4
            )
        )

        # TVA ENV Level row
        row = 2
        level_1_slider = self.controls[DrumPartialParam.TVA_ENV_LEVEL_1]
        self.level_1_slider = level_1_slider
        envelope_slider_layout.addWidget(level_1_slider, row, 0)
        level_1_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                EnvelopeParameter.LEVEL_1, v, DrumPartialParam.TVA_ENV_LEVEL_1
            )
        )

        level_2_slider = self.controls[DrumPartialParam.TVA_ENV_LEVEL_2]
        self.level_2_slider = level_2_slider
        envelope_slider_layout.addWidget(level_2_slider, row, 1)
        level_2_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                EnvelopeParameter.LEVEL_2, v, DrumPartialParam.TVA_ENV_LEVEL_2
            )
        )

        level_3_slider = self.controls[DrumPartialParam.TVA_ENV_LEVEL_3]
        self.level_3_slider = level_3_slider
        envelope_slider_layout.addWidget(level_3_slider, row, 2)
        level_3_slider.valueChanged.connect(
            lambda v: self._update_envelope(
                EnvelopeParameter.LEVEL_3, v, DrumPartialParam.TVA_ENV_LEVEL_3
            )
        )
        return tva_group

    def _create_tva_plot(self):
        plot = DrumTVAEnvPlot(
            width=JDXi.UI.Style.ADSR_PLOT_WIDTH,
            height=JDXi.UI.Style.ADSR_PLOT_HEIGHT,
            envelope=self.envelope,
            parent=self,
        )
        return plot

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
