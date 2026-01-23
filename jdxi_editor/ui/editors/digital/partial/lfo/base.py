"""
LFO section of the digital partial editor.
"""

from typing import Callable

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QWidget,
)

from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_button_with_icon,
    create_icon_from_qta,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class BaseLFOSection(SectionBaseWidget):
    """LFO section for the digital partial editor."""

    rate_tab_label: str = "Rate"
    depths_tab_label: str = "Depths"

    def __init__(
        self,
        icon_type: str = IconType.ADSR,
        analog: bool = False,
        send_midi_parameter: Callable = None,
    ):
        """
        Initialize the DigitalLFOSection

        :param icon_type: Type of icon e.g
        :param analog: bool
        """
        self.lfo_shape_param: list | None = None
        self.switch_row_widgets: list | None = None
        self.rate_layout_widgets: list | None = None
        self.depths_layout_widgets: list | None = None
        self.send_midi_parameter: Callable | None = send_midi_parameter
        self.lfo_shape_buttons = {}  # Dictionary to store LFO shape buttons

        super().__init__(icon_type=icon_type, analog=analog)
        # -- Set up LFO shapes
        self.lfo_shapes = [
            DigitalLFOShape.TRIANGLE,
            DigitalLFOShape.SINE,
            DigitalLFOShape.SAW,
            DigitalLFOShape.SQUARE,
            DigitalLFOShape.SAMPLE_HOLD,
            DigitalLFOShape.RANDOM,
        ]
        # --- Map LFO shapes to icon names
        self.shape_icon_map = {
            DigitalLFOShape.TRIANGLE: JDXi.UI.IconRegistry.TRIANGLE_WAVE,
            DigitalLFOShape.SINE: JDXi.UI.IconRegistry.SINE_WAVE,
            DigitalLFOShape.SAW: JDXi.UI.IconRegistry.SAW_WAVE,
            DigitalLFOShape.SQUARE: JDXi.UI.IconRegistry.SQUARE_WAVE,
            DigitalLFOShape.SAMPLE_HOLD: JDXi.UI.IconRegistry.WAVEFORM,
            DigitalLFOShape.RANDOM: JDXi.UI.IconRegistry.RANDOM_WAVE,
        }

    def setup_ui(self):
        """Set up the UI for the LFO section."""
        layout = self.get_layout()
        shape_row_layout = self._create_shape_row_layout()
        switch_row_layout = self._create_switch_row_layout()
        tab_widget = self._create_tab_widget()
        layout.addLayout(shape_row_layout)
        layout.addLayout(switch_row_layout)
        layout.addWidget(tab_widget)
        layout.addStretch()

    def build_widgets(self):
        """Build the widgets"""
        self._create_rate_fade_layout_widgets()
        self._create_depths_layout_widgets()
        self._create_switch_layout_widgets()

    def _create_shape_row_layout(self):
        """Shape and sync controls"""
        shape_label = QLabel("Shape")
        shape_row_layout_widgets = [shape_label]
        for mod_lfo_shape in self.lfo_shapes:
            icon_name = self.shape_icon_map.get(mod_lfo_shape, JDXi.UI.IconRegistry.WAVEFORM)
            icon = create_icon_from_qta(icon_name)
            btn = create_button_with_icon(
                icon_name=mod_lfo_shape.display_name,
                icon=icon,
                button_dimensions=JDXi.UI.Dimensions.WAVEFORM_ICON,
                icon_dimensions=JDXi.UI.Dimensions.LFOIcon,
            )
            btn.clicked.connect(
                lambda checked, shape=mod_lfo_shape: self._on_lfo_shape_selected(shape)
            )
            if self.analog:
                JDXi.UI.ThemeManager.apply_button_rect_analog(btn)
            self.lfo_shape_buttons[mod_lfo_shape] = btn
            shape_row_layout_widgets.append(btn)

        shape_row_layout = create_layout_with_widgets(shape_row_layout_widgets)
        return shape_row_layout

    def _create_tab_widget(self):
        """Create tab widget for Rate/Rate Ctrl and Depths"""
        tab_widget = QTabWidget()

        rate_widget = self._create_rate_widget()
        # --- Create icons
        rate_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.CLOCK, color=JDXi.UI.Style.GREY
        )
        depths_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.WAVEFORM, color=JDXi.UI.Style.GREY
        )
        tab_widget.addTab(rate_widget, rate_icon, self.rate_tab_label)
        depths_widget = self._create_depths_widget()
        tab_widget.addTab(
            depths_widget, depths_icon, self.depths_tab_label
        )
        JDXi.UI.ThemeManager.apply_tabs_style(tab_widget, analog=self.analog)
        return tab_widget

    def _create_rate_widget(self):
        """Rate and Rate Ctrl Controls Tab"""
        rate_layout = create_layout_with_widgets(self.rate_layout_widgets)
        rate_widget = QWidget()
        rate_widget.setLayout(rate_layout)
        rate_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)
        return rate_widget

    def _create_depths_widget(self):
        """Depths Tab"""
        depths_layout = create_layout_with_widgets(self.depths_layout_widgets)
        depths_widget = QWidget()
        depths_widget.setLayout(depths_layout)
        depths_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)
        return depths_widget

    def _create_rate_fade_controls(self) -> QWidget:
        """Rate and Fade Controls Tab"""
        rate_fade_widget = QWidget()
        rate_fade_layout = create_layout_with_widgets(self.rate_layout_widgets)
        rate_fade_widget.setLayout(rate_fade_layout)
        rate_fade_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)
        return rate_fade_widget

    def _create_depths_controls(self) -> QWidget:
        """Depths Tab"""
        depths_widget = QWidget()
        depths_layout = create_layout_with_widgets(self.depths_layout_widgets)
        depths_widget.setLayout(depths_layout)
        depths_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)
        return depths_widget

    def _on_lfo_shape_selected(self, lfo_shape: DigitalLFOShape):
        """
        Handle Mod LFO shape button clicks

        :param lfo_shape: DigitalLFOShape enum value
        """
        for btn in self.lfo_shape_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
        selected_btn = self.lfo_shape_buttons.get(lfo_shape)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)

        # --- Send MIDI message
        if self.send_midi_parameter:
            if not self.send_midi_parameter(self.lfo_shape_param, lfo_shape.value):
                log.warning(f"Failed to set Mod LFO shape to {lfo_shape.name}")

    def _create_switch_row_layout(self) -> QHBoxLayout:
        """Create Switch row"""
        switch_row_layout = create_layout_with_widgets(self.switch_row_widgets)
        return switch_row_layout

    def _create_switch_layout_widgets(self):
        """Create switch layout widgets"""
        self.switch_row_widgets = self._build_switches(self.SWITCH_SPECS)

    def _create_rate_fade_layout_widgets(self):
        self.rate_layout_widgets = self._build_sliders(self.RATE_FADE_SLIDERS)

    def _create_depths_layout_widgets(self):
        self.depths_layout_widgets = self._build_sliders(self.DEPTH_SLIDERS)
