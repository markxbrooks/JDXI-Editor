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
from jdxi_editor.midi.data.parameter.digital.name import DigitalDisplayName
from jdxi_editor.midi.data.parameter.digital.option import DigitalDisplayOptions
from jdxi_editor.midi.data.parameter.digital.partial import (
    DigitalPartialParam,
)
from jdxi_editor.ui.editors.digital.partial.base_lfo import BaseLFOSection
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_button_with_icon,
    create_icon_from_qta,
    create_layout_with_widgets,
)


class DigitalLFOSection(BaseLFOSection):
    """LFO section for the digital partial editor."""

    def __init__(
        self,
        create_parameter_slider: Callable,
        create_parameter_switch: Callable,
        create_parameter_combo_box: Callable,
        controls: dict,
        send_midi_parameter: Callable = None,
        icon_type=IconType.ADSR, analog=False
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

        super().__init__(icon_type=icon_type,
                         analog=analog)
        self.setup_ui()

    def _create_switch_row_layout(self) -> QHBoxLayout:
        """Create Switch row"""
        self.lfo_tempo_sync_switch = self._create_parameter_switch(
            DigitalPartialParam.LFO_TEMPO_SYNC_SWITCH,
            DigitalDisplayName.LFO_TEMPO_SYNC_SWITCH,
            DigitalDisplayOptions.LFO_TEMPO_SYNC_SWITCH,
        )
        self.lfo_sync_note = self._create_parameter_combo_box(
            DigitalPartialParam.LFO_TEMPO_SYNC_NOTE,
            DigitalDisplayName.LFO_TEMPO_SYNC_NOTE,
            options=DigitalDisplayOptions.LFO_TEMPO_SYNC_NOTE,
        )
        # --- Key trigger switch
        self.lfo_trigger = self._create_parameter_switch(
            DigitalPartialParam.LFO_KEY_TRIGGER,
            DigitalDisplayName.LFO_KEY_TRIGGER,
            DigitalDisplayOptions.LFO_KEY_TRIGGER,
        )
        switch_row_layout = create_layout_with_widgets(
            [self.lfo_tempo_sync_switch, self.lfo_sync_note, self.lfo_trigger]
        )
        return switch_row_layout

    def _create_tab_widget(self) -> QTabWidget:
        """Create tab widget for Rate/Fade and Depths"""
        lfo_controls_tab_widget = QTabWidget()

        rate_fade_widget = self._create_rate_fade_controls()

        rate_fade_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.CLOCK, color=JDXi.UI.Style.GREY
        )
        lfo_controls_tab_widget.addTab(
            rate_fade_widget, rate_fade_icon, "Rate and Fade"
        )
        depths_widget = self._create_depths_controls()

        depths_icon = JDXi.UI.IconRegistry.get_icon(
            JDXi.UI.IconRegistry.WAVEFORM, color=JDXi.UI.Style.GREY
        )
        lfo_controls_tab_widget.addTab(depths_widget, depths_icon, "Depths")
        return lfo_controls_tab_widget

    def _create_depths_controls(self) -> QWidget:
        """Depths Tab"""
        depths_layout_widgets = [
            self._create_parameter_slider(
                DigitalPartialParam.LFO_PITCH_DEPTH,
                DigitalDisplayName.LFO_PITCH_DEPTH,
                vertical=True,
            ),
            self._create_parameter_slider(
                DigitalPartialParam.LFO_FILTER_DEPTH,
                DigitalDisplayName.LFO_FILTER_DEPTH,
                vertical=True,
            ),
            self._create_parameter_slider(
                DigitalPartialParam.LFO_AMP_DEPTH,
                DigitalDisplayName.LFO_AMP_DEPTH,
                vertical=True,
            ),
            self._create_parameter_slider(
                DigitalPartialParam.LFO_PAN_DEPTH,
                DigitalDisplayName.LFO_PAN_DEPTH,
                vertical=True,
            ),
        ]
        depths_widget = QWidget()
        depths_layout = create_layout_with_widgets(depths_layout_widgets)
        depths_widget.setLayout(depths_layout)
        depths_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)
        return depths_widget

    def _create_rate_fade_controls(self) -> QWidget:
        """Rate and Fade Controls Tab"""
        rate_fade_layout_widgets = [
            self._create_parameter_slider(
                DigitalPartialParam.LFO_RATE, DigitalDisplayName.LFO_RATE, vertical=True
            ),
            self._create_parameter_slider(
                DigitalPartialParam.LFO_FADE_TIME,
                DigitalDisplayName.LFO_FADE_TIME,
                vertical=True,
            ),
        ]
        rate_fade_widget = QWidget()
        rate_fade_layout = create_layout_with_widgets(rate_fade_layout_widgets)
        rate_fade_widget.setLayout(rate_fade_layout)
        rate_fade_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MINIMUM_HEIGHT)
        return rate_fade_widget

    def _create_shape_row_layout(self) -> QHBoxLayout:
        """Shape and sync controls"""
        shape_row_layout = QHBoxLayout()
        shape_row_layout.addStretch()

        # --- Add label
        shape_label = QLabel("Shape")
        shape_row_layout.addWidget(shape_label)

        # --- Create buttons for each LFO shape
        lfo_shapes = [
            DigitalLFOShape.TRIANGLE,
            DigitalLFOShape.SINE,
            DigitalLFOShape.SAW,
            DigitalLFOShape.SQUARE,
            DigitalLFOShape.SAMPLE_HOLD,
            DigitalLFOShape.RANDOM,
        ]

        # --- Map LFO shapes to icon names
        shape_icon_map = {
            DigitalLFOShape.TRIANGLE: "mdi.triangle-wave",
            DigitalLFOShape.SINE: "mdi.sine-wave",
            DigitalLFOShape.SAW: "mdi.sawtooth-wave",
            DigitalLFOShape.SQUARE: "mdi.square-wave",
            DigitalLFOShape.SAMPLE_HOLD: "mdi.waveform",
            DigitalLFOShape.RANDOM: "mdi.wave",
        }

        for lfo_shape in lfo_shapes:
            # --- Add icon
            icon_name = shape_icon_map.get(lfo_shape, "mdi.waveform")
            icon = create_icon_from_qta(icon_name=icon_name)
            btn = create_button_with_icon(
                icon_name=lfo_shape.display_name,
                icon=icon,
                button_dimensions=JDXi.UI.Dimensions.LFOIcon,
                icon_dimensions=JDXi.UI.Dimensions.WAVEFORM_ICON,
            )
            btn.clicked.connect(
                lambda checked, shape=lfo_shape: self._on_lfo_shape_selected(shape)
            )
            self.lfo_shape_buttons[lfo_shape] = btn
            shape_row_layout.addWidget(btn)
        return shape_row_layout

    def _on_lfo_shape_selected(self, lfo_shape: DigitalLFOShape):
        """
        Handle LFO shape button clicks

        :param lfo_shape: DigitalLFOShape enum value
        """
        # --- Reset all buttons to default style
        for btn in self.lfo_shape_buttons.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

        # --- Apply active style to the selected LFO shape button
        selected_btn = self.lfo_shape_buttons.get(lfo_shape)
        if selected_btn:
            selected_btn.setChecked(True)
            selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)

        # --- Send MIDI message
        if self.send_midi_parameter:
            if not self.send_midi_parameter(
                DigitalPartialParam.LFO_SHAPE, lfo_shape.value
            ):
                log.warning(f"Failed to set LFO shape to {lfo_shape.name}")
