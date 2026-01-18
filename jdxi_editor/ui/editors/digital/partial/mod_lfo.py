"""
MOD LFO section of the digital partial editor.
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
from jdxi_editor.jdxi.jdxi import JDXi
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.partial import (
    DigitalPartialParam,
)
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class DigitalModLFOSection(SectionBaseWidget):
    """MOD LFO section for the digital partial editor."""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_combo_box: Callable,
        on_parameter_changed: Callable,
        controls: dict,
        send_midi_parameter: Callable = None,
    ):
        """
        Initialize the DigitalModLFOSection

        :param create_parameter_slider: Callable
        :param create_parameter_combo_box: Callable
        :param on_parameter_changed: Callable
        :param controls: dict
        :param send_midi_parameter: Callable to send MIDI parameter updates
        """
        self._create_parameter_slider = create_parameter_slider
        self._create_parameter_combo_box = create_parameter_combo_box
        self._on_parameter_changed = on_parameter_changed
        self.controls = controls
        self.send_midi_parameter = send_midi_parameter
        self.mod_lfo_shape_buttons = {}  # Dictionary to store Mod LFO shape buttons

        super().__init__(icon_type=IconType.ADSR, analog=False)
        self._init_ui()

    def _init_ui(self):
        mod_lfo_layout = self.get_layout()

        # Shape and sync controls
        shape_row_layout = QHBoxLayout()
        shape_row_layout.addStretch()

        # Add label
        shape_label = QLabel("Shape")
        shape_row_layout.addWidget(shape_label)

        # Create buttons for each Mod LFO shape
        mod_lfo_shapes = [
            DigitalLFOShape.TRIANGLE,
            DigitalLFOShape.SINE,
            DigitalLFOShape.SAW,
            DigitalLFOShape.SQUARE,
            DigitalLFOShape.SAMPLE_HOLD,
            DigitalLFOShape.RANDOM,
        ]

        # Map Mod LFO shapes to icon names
        shape_icon_map = {
            DigitalLFOShape.TRIANGLE: "mdi.triangle-wave",
            DigitalLFOShape.SINE: "mdi.sine-wave",
            DigitalLFOShape.SAW: "mdi.sawtooth-wave",
            DigitalLFOShape.SQUARE: "mdi.square-wave",
            DigitalLFOShape.SAMPLE_HOLD: "mdi.waveform",
            DigitalLFOShape.RANDOM: "mdi.wave",
        }

        for mod_lfo_shape in mod_lfo_shapes:
            btn = QPushButton(mod_lfo_shape.display_name)
            btn.setCheckable(True)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
            # Add icon
            icon_name = shape_icon_map.get(mod_lfo_shape, "mdi.waveform")
            icon = qta.icon(icon_name, color=JDXi.UI.Style.WHITE, icon_size=0.7)
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))
            btn.setFixedSize(
                JDXi.UI.Dimensions.WAVEFORM_ICON.WIDTH,
                JDXi.UI.Dimensions.WAVEFORM_ICON.HEIGHT,
            )
            btn.clicked.connect(
                lambda checked, shape=mod_lfo_shape: self._on_mod_lfo_shape_selected(
                    shape
                )
            )
            self.mod_lfo_shape_buttons[mod_lfo_shape] = btn
            shape_row_layout.addWidget(btn)

        self.mod_lfo_sync = self._create_parameter_combo_box(
            DigitalPartialParam.MOD_LFO_TEMPO_SYNC_SWITCH,
            DigitalDisplayName.MOD_LFO_TEMPO_SYNC_SWITCH,
            options=DigitalDisplayOptions.MOD_LFO_TEMPO_SYNC_SWITCH,
        )
        switch_row_layout = QHBoxLayout()
        switch_row_layout.addStretch()
        switch_row_layout.addWidget(self.mod_lfo_sync)

        self.mod_lfo_note = self._create_parameter_combo_box(
            DigitalPartialParam.MOD_LFO_TEMPO_SYNC_NOTE,
            DigitalDisplayName.MOD_LFO_TEMPO_SYNC_NOTE,
            options=DigitalDisplayOptions.MOD_LFO_TEMPO_SYNC_NOTE,
        )
        switch_row_layout.addWidget(self.mod_lfo_note)
        shape_row_layout.addStretch()
        switch_row_layout.addStretch()
        mod_lfo_layout.addLayout(shape_row_layout)
        mod_lfo_layout.addLayout(switch_row_layout)

        # Create tab widget for Rate/Rate Ctrl and Depths
        mod_lfo_controls_tab_widget = QTabWidget()
        mod_lfo_layout.addWidget(mod_lfo_controls_tab_widget)

        # --- Rate and Rate Ctrl Controls Tab ---
        rate_widget = QWidget()
        rate_layout = QHBoxLayout()
        rate_layout.addStretch()
        rate_widget.setLayout(rate_layout)
        rate_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)

        # Rate and Rate Ctrl controls
        rate_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.MOD_LFO_RATE,
                DigitalDisplayName.MOD_LFO_RATE,
                vertical=True,
            )
        )
        rate_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.MOD_LFO_RATE_CTRL,
                DigitalDisplayName.MOD_LFO_RATE_CTRL,
                vertical=True,
            )
        )
        rate_layout.addStretch()

        rate_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.CLOCK, color=JDXi.UI.Style.GREY
        )
        mod_lfo_controls_tab_widget.addTab(rate_widget, rate_icon, "Rate and Rate Ctrl")

        # --- Depths Tab ---
        depths_widget = QWidget()
        depths_layout = QHBoxLayout()
        depths_layout.addStretch()
        depths_widget.setLayout(depths_layout)
        depths_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)

        depths_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.MOD_LFO_PITCH_DEPTH,
                DigitalDisplayName.MOD_LFO_PITCH_DEPTH,
                vertical=True,
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.MOD_LFO_FILTER_DEPTH,
                DigitalDisplayName.MOD_LFO_FILTER_DEPTH,
                vertical=True,
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.MOD_LFO_AMP_DEPTH,
                DigitalDisplayName.MOD_LFO_AMP_DEPTH,
                vertical=True,
            )
        )
        depths_layout.addWidget(
            self._create_parameter_slider(
                DigitalPartialParam.MOD_LFO_PAN,
                DigitalDisplayName.MOD_LFO_PAN,
                vertical=True,
            )
        )
        depths_layout.addStretch()

        depths_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.WAVEFORM, color=JDXi.UI.Style.GREY
        )
        mod_lfo_controls_tab_widget.addTab(depths_widget, depths_icon, "Depths")

        mod_lfo_layout.addStretch()

    def _on_mod_lfo_shape_selected(self, mod_lfo_shape: DigitalLFOShape):
        """
        Handle Mod LFO shape button clicks

        :param mod_lfo_shape: DigitalLFOShape enum value
        """
        # Reset all buttons to default style
        for btn in self.mod_lfo_shape_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

        # Apply active style to the selected Mod LFO shape button
        selected_btn = self.mod_lfo_shape_buttons.get(mod_lfo_shape)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)

        # Send MIDI message
        if self.send_midi_parameter:
            if not self.send_midi_parameter(
                DigitalPartialParam.MOD_LFO_SHAPE, mod_lfo_shape.value
            ):
                log.warning(f"Failed to set Mod LFO shape to {mod_lfo_shape.name}")
