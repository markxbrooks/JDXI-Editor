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
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.partial import (
    DigitalPartialParam,
)
from jdxi_editor.ui.widgets.editor.helper import create_layout_with_widgets, create_button_with_icon, create_icon_from_qta
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
        """init the ui"""
        mod_lfo_layout = self.get_layout()
        shape_row_layout = self._create_shape_row_layout()
        switch_row_layout = self._create_switch_row_layout()
        mod_lfo_controls_tab_widget = self._create_mod_lfo_controls_tab_widget()
        mod_lfo_layout.addLayout(shape_row_layout)
        mod_lfo_layout.addLayout(switch_row_layout)
        mod_lfo_layout.addWidget(mod_lfo_controls_tab_widget)
        mod_lfo_layout.addStretch()

    def _create_shape_row_layout(self):
        """Shape and sync controls"""
        # --- Create buttons for each Mod LFO shape
        mod_lfo_shapes = [
            DigitalLFOShape.TRIANGLE,
            DigitalLFOShape.SINE,
            DigitalLFOShape.SAW,
            DigitalLFOShape.SQUARE,
            DigitalLFOShape.SAMPLE_HOLD,
            DigitalLFOShape.RANDOM,
        ]

        # --- Map Mod LFO shapes to icon names
        shape_icon_map = {
            DigitalLFOShape.TRIANGLE: "mdi.triangle-wave",
            DigitalLFOShape.SINE: "mdi.sine-wave",
            DigitalLFOShape.SAW: "mdi.sawtooth-wave",
            DigitalLFOShape.SQUARE: "mdi.square-wave",
            DigitalLFOShape.SAMPLE_HOLD: "mdi.waveform",
            DigitalLFOShape.RANDOM: "mdi.wave",
        }
        # --- Add label
        shape_label = QLabel("Shape")
        shape_row_layout_widgets = [shape_label]
        for mod_lfo_shape in mod_lfo_shapes:
            icon_name = shape_icon_map.get(mod_lfo_shape, "mdi.waveform")
            icon = create_icon_from_qta(icon_name)
            btn = create_button_with_icon(icon_name=mod_lfo_shape.display_name, icon=icon, button_dimensions=JDXi.UI.Dimensions.WAVEFORM_ICON, icon_dimensions=JDXi.UI.Dimensions.LFOIcon)
            btn.clicked.connect(
                lambda checked, shape=mod_lfo_shape: self._on_mod_lfo_shape_selected(
                    shape
                )
            )
            self.mod_lfo_shape_buttons[mod_lfo_shape] = btn
            shape_row_layout_widgets.append(btn)
            
        shape_row_layout = create_layout_with_widgets(shape_row_layout_widgets)
        return shape_row_layout
        
    def _create_switch_row_layout(self):
        """Switch Row layout"""
        self.mod_lfo_sync = self._create_parameter_combo_box(
            DigitalPartialParam.MOD_LFO_TEMPO_SYNC_SWITCH,
            DigitalDisplayName.MOD_LFO_TEMPO_SYNC_SWITCH,
            options=DigitalDisplayOptions.MOD_LFO_TEMPO_SYNC_SWITCH,
        )
        self.mod_lfo_note = self._create_parameter_combo_box(
            DigitalPartialParam.MOD_LFO_TEMPO_SYNC_NOTE,
            DigitalDisplayName.MOD_LFO_TEMPO_SYNC_NOTE,
            options=DigitalDisplayOptions.MOD_LFO_TEMPO_SYNC_NOTE,
        )
        switch_row_layout = create_layout_with_widgets([self.mod_lfo_sync, self.mod_lfo_note])
        return switch_row_layout

    def _create_mod_lfo_controls_tab_widget(self):
        """Create tab widget for Rate/Rate Ctrl and Depths"""
        mod_lfo_controls_tab_widget = QTabWidget()

        rate_widget = self._create_rate_widget()
        rate_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.CLOCK, color=JDXi.UI.Style.GREY
        )
        mod_lfo_controls_tab_widget.addTab(rate_widget, rate_icon, "Rate and Rate Ctrl")

        depths_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.WAVEFORM, color=JDXi.UI.Style.GREY
        )
        depths_widget = self._create_depths_widget()
        mod_lfo_controls_tab_widget.addTab(depths_widget, depths_icon, "Depths")
        return mod_lfo_controls_tab_widget
    
    def _create_rate_widget(self):
        """Rate and Rate Ctrl Controls Tab"""
        # --- Create the Rate and Rate Ctrl controls
        rate_layout_widgets = [
            self._create_parameter_slider(
                DigitalPartialParam.MOD_LFO_RATE,
                DigitalDisplayName.MOD_LFO_RATE,
                vertical=True,
            ),
            self._create_parameter_slider(
                DigitalPartialParam.MOD_LFO_RATE_CTRL,
                DigitalDisplayName.MOD_LFO_RATE_CTRL,
                vertical=True,
            )]
        # --- Create the layout with the list of widgets
        rate_layout = create_layout_with_widgets(rate_layout_widgets)
        # --- Create the widget to add the controls to
        rate_widget = QWidget()
        rate_widget.setLayout(rate_layout)
        rate_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)
        return rate_widget

    def _create_depths_widget(self):
        """Depths Tab"""
        # --- First create a list of widgets
        depths_layout_widgets = [
            self._create_parameter_slider(
                DigitalPartialParam.MOD_LFO_PITCH_DEPTH,
                DigitalDisplayName.MOD_LFO_PITCH_DEPTH,
                vertical=True,
            ),
            self._create_parameter_slider(
                DigitalPartialParam.MOD_LFO_FILTER_DEPTH,
                DigitalDisplayName.MOD_LFO_FILTER_DEPTH,
                vertical=True,
            ),
            self._create_parameter_slider(
                DigitalPartialParam.MOD_LFO_AMP_DEPTH,
                DigitalDisplayName.MOD_LFO_AMP_DEPTH,
                vertical=True,
            ),
            self._create_parameter_slider(
                DigitalPartialParam.MOD_LFO_PAN,
                DigitalDisplayName.MOD_LFO_PAN,
                vertical=True,
            )]
        # --- Second add the list to a new hlayout 
        depths_layout = create_layout_with_widgets(depths_layout_widgets)
        # --- Third create the widget to put these on
        depths_widget = QWidget()
        depths_widget.setLayout(depths_layout)
        depths_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)
        return depths_widget

    def _on_mod_lfo_shape_selected(self, mod_lfo_shape: DigitalLFOShape):
        """
        Handle Mod LFO shape button clicks

        :param mod_lfo_shape: DigitalLFOShape enum value
        """
        # --- Reset all buttons to default style
        for btn in self.mod_lfo_shape_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

        # --- Apply active style to the selected Mod LFO shape button
        selected_btn = self.mod_lfo_shape_buttons.get(mod_lfo_shape)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)

        # --- Send MIDI message
        if self.send_midi_parameter:
            if not self.send_midi_parameter(
                DigitalPartialParam.MOD_LFO_SHAPE, mod_lfo_shape.value
            ):
                log.warning(f"Failed to set Mod LFO shape to {mod_lfo_shape.name}")
