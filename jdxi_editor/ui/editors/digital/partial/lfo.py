"""
LFO section of the digital partial editor.
"""

from typing import Callable

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from jdxi_editor.jdxi.style import JDXiStyle, JDXiThemeManager
from jdxi_editor.midi.data.parameter.digital.partial import (
    DigitalPartialParam,
)
from jdxi_editor.ui.widgets.editor.section_base import IconType, SectionBaseWidget
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


class DigitalLFOSection(SectionBaseWidget):
    """LFO section for the digital partial editor."""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        controls: dict,
    ):
        self.lfo_shape = None
        """
        Initialize the DigitalLFOSection

        :param create_parameter_slider: Callable
        :param create_parameter_switch: Callable
        :param controls: dict
        """
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self.controls = controls
        
        super().__init__(icon_type=IconType.ADSR, analog=False)
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI for the LFO section."""
        layout = self.get_layout()

        # Shape and sync controls
        shape_row_layout = QHBoxLayout()
        shape_row_layout.addStretch()
        self.lfo_shape = self._create_parameter_switch(
            DigitalPartialParam.LFO_SHAPE,
            "Shape",
            ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"],
        )
        shape_row_layout.addWidget(self.lfo_shape)

        self.lfo_tempo_sync_switch = self._create_parameter_switch(
            DigitalPartialParam.LFO_TEMPO_SYNC_SWITCH,
            "Tempo Sync",
            ["OFF", "ON"],
        )
        shape_row_layout.addWidget(self.lfo_tempo_sync_switch)
        self.lfo_sync_note = self._create_parameter_combo_box(
            DigitalPartialParam.LFO_TEMPO_SYNC_NOTE,
            "Sync Note",
            options=["1/1", "1/2", "1/4", "1/8", "1/16"],
        )
        shape_row_layout.addWidget(self.lfo_sync_note)

        # Key trigger switch
        self.lfo_trigger = self._create_parameter_switch(
            DigitalPartialParam.LFO_KEY_TRIGGER, "Key Trigger", ["OFF", "ON"]
        )
        shape_row_layout.addWidget(self.lfo_trigger)
        shape_row_layout.addStretch()
        layout.addLayout(shape_row_layout)

        # Create tab widget for Rate/Fade and Depths
        lfo_controls_tab_widget = QTabWidget()
        layout.addWidget(lfo_controls_tab_widget)

        # --- Rate and Fade Controls Tab ---
        rate_fade_widget = QWidget()
        rate_fade_layout = QHBoxLayout()
        rate_fade_layout.addStretch()
        rate_fade_widget.setLayout(rate_fade_layout)
        rate_fade_widget.setMinimumHeight(JDXiDimensions.EDITOR_MINIMUM_HEIGHT)

        # Rate and fade controls
        rate_fade_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.LFO_RATE, "Rate", vertical=True
            )
        )
        rate_fade_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.LFO_FADE_TIME, "Fade", vertical=True
            )
        )
        rate_fade_layout.addStretch()

        lfo_controls_tab_widget.addTab(rate_fade_widget, "Rate and Fade")

        # --- Depths Tab ---
        depths_widget = QWidget()
        depths_layout = QHBoxLayout()
        depths_layout.addStretch()
        depths_widget.setLayout(depths_layout)
        depths_widget.setMinimumHeight(JDXiDimensions.EDITOR_MINIMUM_HEIGHT)

        depths_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.LFO_PITCH_DEPTH, "Pitch", vertical=True
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.LFO_FILTER_DEPTH, "Filter", vertical=True
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.LFO_AMP_DEPTH, "Amp", vertical=True
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.LFO_PAN_DEPTH, "Pan", vertical=True
            )
        )
        depths_layout.addStretch()

        lfo_controls_tab_widget.addTab(depths_widget, "Depths")

        layout.addStretch()
