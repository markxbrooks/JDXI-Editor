"""
MOD LFO section of the digital partial editor.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTabWidget
from typing import Callable

from jdxi_editor.jdxi.style import JDXiStyle
from jdxi_editor.midi.data.parameter.digital.partial import (
    AddressParameterDigitalPartial,
)
from jdxi_editor.ui.windows.jdxi.dimensions import JDXiDimensions


class DigitalModLFOSection(QWidget):
    """MOD LFO section for the digital partial editor."""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_combo_box: Callable,
        on_parameter_changed: Callable,
        controls: dict,
    ):
        super().__init__()
        """
        Initialize the DigitalModLFOSection

        :param create_parameter_slider: Callable
        :param create_parameter_combo_box: Callable
        :param on_parameter_changed: Callable
        :param controls: dict
        """
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self._on_parameter_changed = on_parameter_changed
        self.controls = controls
        self.setStyleSheet(JDXiStyle.ADSR)
        self._init_ui()

    def _init_ui(self):
        mod_lfo_layout = QVBoxLayout()

        self.setLayout(mod_lfo_layout)

        # Shape and sync controls
        shape_row_layout = QHBoxLayout()
        shape_row_layout.addStretch()
        self.mod_lfo_shape = self._create_parameter_combo_box(
            AddressParameterDigitalPartial.MOD_LFO_SHAPE,
            "Shape",
            ["TRI", "SIN", "SAW", "SQR", "S&H", "RND"],
        )
        shape_row_layout.addWidget(self.mod_lfo_shape)

        self.mod_lfo_sync = self._create_parameter_combo_box(
            AddressParameterDigitalPartial.MOD_LFO_TEMPO_SYNC_SWITCH,
            "Sync",
            ["OFF", "ON"],
        )
        shape_row_layout.addWidget(self.mod_lfo_sync)

        self.mod_lfo_note = self._create_parameter_combo_box(
            AddressParameterDigitalPartial.MOD_LFO_TEMPO_SYNC_NOTE,
            "Note",
            ["1/1", "1/2", "1/4", "1/8", "1/16"],
        )
        shape_row_layout.addWidget(self.mod_lfo_note)
        shape_row_layout.addStretch()
        mod_lfo_layout.addLayout(shape_row_layout)

        # Create tab widget for Rate/Rate Ctrl and Depths
        mod_lfo_controls_tab_widget = QTabWidget()
        mod_lfo_layout.addWidget(mod_lfo_controls_tab_widget)

        # --- Rate and Rate Ctrl Controls Tab ---
        rate_widget = QWidget()
        rate_layout = QHBoxLayout()
        rate_layout.addStretch()
        rate_widget.setLayout(rate_layout)
        rate_widget.setMinimumHeight(JDXiDimensions.EDITOR_MINIMUM_HEIGHT)
        
        # Rate and Rate Ctrl controls
        rate_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.MOD_LFO_RATE, "Rate", vertical=True
            )
        )
        rate_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.MOD_LFO_RATE_CTRL, "Rate Ctrl", vertical=True
            )
        )
        rate_layout.addStretch()

        mod_lfo_controls_tab_widget.addTab(rate_widget, "Rate and Rate Ctrl")

        # --- Depths Tab ---
        depths_widget = QWidget()
        depths_layout = QHBoxLayout()
        depths_layout.addStretch()
        depths_widget.setLayout(depths_layout)
        depths_widget.setMinimumHeight(JDXiDimensions.EDITOR_MINIMUM_HEIGHT)

        depths_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.MOD_LFO_PITCH_DEPTH, "Pitch", vertical=True
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.MOD_LFO_FILTER_DEPTH, "Filter", vertical=True
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.MOD_LFO_AMP_DEPTH, "Amp", vertical=True
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                AddressParameterDigitalPartial.MOD_LFO_PAN, "Pan", vertical=True
            )
        )
        depths_layout.addStretch()

        mod_lfo_controls_tab_widget.addTab(depths_widget, "Depths")

        mod_lfo_layout.addStretch()
