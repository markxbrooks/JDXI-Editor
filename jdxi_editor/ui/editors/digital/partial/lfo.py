"""
LFO section of the digital partial editor.
"""

from typing import Callable

import qtawesome as qta
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QWidget,
)

from decologr import Decologr as log
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape
from jdxi_editor.midi.data.parameter.digital.partial import (
    DigitalPartialParam,
)
from jdxi_editor.ui.style import JDXiStyle
from jdxi_editor.ui.style.dimensions import JDXiDimensions
from jdxi_editor.ui.style.icons import JDXiIconRegistry
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class DigitalLFOSection(SectionBaseWidget):
    """LFO section for the digital partial editor."""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        controls: dict,
        send_midi_parameter: Callable = None,
    ):
        """
        Initialize the DigitalLFOSection

        :param create_parameter_slider: Callable
        :param create_parameter_switch: Callable
        :param create_parameter_combo_box: Callable
        :param controls: dict
        :param send_midi_parameter: Callable to send MIDI parameter updates
        """
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_switch = create_parameter_switch
        self._create_parameter_combo_box = create_parameter_combo_box
        self.controls = controls
        self.send_midi_parameter = send_midi_parameter
        self.lfo_shape_buttons = {}  # Dictionary to store LFO shape buttons

        super().__init__(icon_type=IconType.ADSR, analog=False)
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI for the LFO section."""
        layout = self.get_layout()

        # Shape and sync controls
        shape_row_layout = QHBoxLayout()
        shape_row_layout.addStretch()

        # Add label
        shape_label = QLabel("Shape")
        shape_row_layout.addWidget(shape_label)

        # Create buttons for each LFO shape
        lfo_shapes = [
            DigitalLFOShape.TRIANGLE,
            DigitalLFOShape.SINE,
            DigitalLFOShape.SAW,
            DigitalLFOShape.SQUARE,
            DigitalLFOShape.SAMPLE_HOLD,
            DigitalLFOShape.RANDOM,
        ]

        # Map LFO shapes to icon names
        shape_icon_map = {
            DigitalLFOShape.TRIANGLE: "mdi.triangle-wave",
            DigitalLFOShape.SINE: "mdi.sine-wave",
            DigitalLFOShape.SAW: "mdi.sawtooth-wave",
            DigitalLFOShape.SQUARE: "mdi.square-wave",
            DigitalLFOShape.SAMPLE_HOLD: "mdi.waveform",
            DigitalLFOShape.RANDOM: "mdi.wave",
        }

        for lfo_shape in lfo_shapes:
            btn = QPushButton(lfo_shape.display_name)
            btn.setCheckable(True)
            btn.setStyleSheet(JDXiStyle.BUTTON_RECT)
            # Add icon
            icon_name = shape_icon_map.get(lfo_shape, "mdi.waveform")
            icon = qta.icon(icon_name, color=JDXiStyle.WHITE, icon_size=0.7)
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))
            btn.setFixedSize(
                JDXiDimensions.WAVEFORM_ICON.WIDTH, JDXiDimensions.WAVEFORM_ICON.HEIGHT
            )
            btn.clicked.connect(
                lambda checked, shape=lfo_shape: self._on_lfo_shape_selected(shape)
            )
            self.lfo_shape_buttons[lfo_shape] = btn
            shape_row_layout.addWidget(btn)

        self.lfo_tempo_sync_switch = self._create_parameter_switch(
            DigitalPartialParam.LFO_TEMPO_SYNC_SWITCH,
            "Tempo Sync",
            ["OFF", "ON"],
        )
        switch_row_layout = QHBoxLayout()
        switch_row_layout.addStretch()
        switch_row_layout.addWidget(self.lfo_tempo_sync_switch)
        self.lfo_sync_note = self._create_parameter_combo_box(
            DigitalPartialParam.LFO_TEMPO_SYNC_NOTE,
            "Sync Note",
            options=["1/1", "1/2", "1/4", "1/8", "1/16"],
        )
        switch_row_layout.addWidget(self.lfo_sync_note)

        layout.addLayout(shape_row_layout)
        layout.addLayout(switch_row_layout)

        # Key trigger switch
        self.lfo_trigger = self._create_parameter_switch(
            DigitalPartialParam.LFO_KEY_TRIGGER, "Key Trigger", ["OFF", "ON"]
        )
        switch_row_layout.addWidget(self.lfo_trigger)
        switch_row_layout.addStretch()
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
        rate_fade_widget.setMinimumHeight(JDXiDimensions.EDITOR.MINIMUM_HEIGHT)

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

        rate_fade_icon = JDXiIconRegistry.get_icon(
            JDXiIconRegistry.CLOCK, color=JDXiStyle.GREY
        )
        lfo_controls_tab_widget.addTab(
            rate_fade_widget, rate_fade_icon, "Rate and Fade"
        )

        # --- Depths Tab ---
        depths_widget = QWidget()
        depths_layout = QHBoxLayout()
        depths_layout.addStretch()
        depths_widget.setLayout(depths_layout)
        depths_widget.setMinimumHeight(JDXiDimensions.EDITOR.MINIMUM_HEIGHT)

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

        depths_icon = JDXiIconRegistry.get_icon(
            JDXiIconRegistry.WAVEFORM, color=JDXiStyle.GREY
        )
        lfo_controls_tab_widget.addTab(depths_widget, depths_icon, "Depths")

        layout.addStretch()

    def _on_lfo_shape_selected(self, lfo_shape: DigitalLFOShape):
        """
        Handle LFO shape button clicks

        :param lfo_shape: DigitalLFOShape enum value
        """
        # Reset all buttons to default style
        for btn in self.lfo_shape_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXiStyle.BUTTON_RECT)

        # Apply active style to the selected LFO shape button
        selected_btn = self.lfo_shape_buttons.get(lfo_shape)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXiStyle.BUTTON_RECT_ACTIVE)

        # Send MIDI message
        if self.send_midi_parameter:
            if not self.send_midi_parameter(
                DigitalPartialParam.LFO_SHAPE, lfo_shape.value
            ):
                log.warning(f"Failed to set LFO shape to {lfo_shape.name}")
