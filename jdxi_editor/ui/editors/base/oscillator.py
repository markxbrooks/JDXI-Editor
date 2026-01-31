"""
LFO section of the digital partial editor.
"""

from typing import Callable

from decologr import Decologr as log
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QWidget,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_button_with_icon,
    create_icon_from_qta,
    create_layout_with_widgets,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


class BaseOscillatorSection(SectionBaseWidget):
    """Abstract base class for LFO sections."""
    
    controls_tab_label: str = "Controls"
    adsr_tab_label: str = "ADSR"

    def __init__(
        self,
        *,
        send_midi_parameter: Callable = None,
        midi_helper=None,
        controls: dict = None,
        address=None,
        icons_row_type: str = IconType.OSCILLATOR,
        analog: bool = False,
    ):
        """
        Initialize the BaseOscillatorSection
        :param send_midi_parameter: Callable to send MIDI parameters
        :param midi_helper: MIDI helper instance
        :param controls: Dictionary of controls
        :param address: Roland SysEx address
        :param icons_row_type: Type of icon
        :param analog: bool
        """
        self.wave_layout_widgets: list = []
        self.wave_shape_param: list | None = None
        self.switch_row_widgets: list | None = None
        self.rate_layout_widgets: list | None = None
        self.depths_layout_widgets: list | None = None
        self.send_midi_parameter: Callable | None = send_midi_parameter
        self.wave_shape_buttons = {}  # --- Dictionary to store LFO shape buttons

        super().__init__(
            send_midi_parameter=send_midi_parameter,
            midi_helper=midi_helper,
            controls=controls,
            address=address,
            icons_row_type=icons_row_type,
            analog=analog,
        )
        # ---  Set up waveform shapes
        self.wave_shapes = [
            JDXi.Midi.Digital.Wave.LFO.TRIANGLE,
            JDXi.Midi.Digital.Wave.LFO.SINE,
            JDXi.Midi.Digital.Wave.LFO.SAW,
            JDXi.Midi.Digital.Wave.LFO.SQUARE,
            JDXi.Midi.Digital.Wave.LFO.SAMPLE_HOLD,
            JDXi.Midi.Digital.Wave.LFO.RANDOM,
        ]
        # ---  Map waveform shapes to icon names
        self.shape_icon_map = {
            JDXi.Midi.Digital.Wave.LFO.TRIANGLE: JDXi.UI.Icon.WAVE_TRIANGLE,
            JDXi.Midi.Digital.Wave.LFO.SINE: JDXi.UI.Icon.WAVE_SINE,
            JDXi.Midi.Digital.Wave.LFO.SAW: JDXi.UI.Icon.WAVE_SAW,
            JDXi.Midi.Digital.Wave.LFO.SQUARE: JDXi.UI.Icon.WAVE_SQUARE,
            JDXi.Midi.Digital.Wave.LFO.SAMPLE_HOLD: JDXi.UI.Icon.WAVEFORM,
            JDXi.Midi.Digital.Wave.LFO.RANDOM: JDXi.UI.Icon.WAVE_RANDOM,
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
        # --- Call parent to create buttons and other widgets from specs
        super().build_widgets()
        # --- Then create LFO-specific widgets (only if attributes exist)
        if hasattr(self, 'RATE_FADE_SLIDERS'):
            self._create_rate_fade_layout_widgets()
        if hasattr(self, 'DEPTH_SLIDERS'):
            self._create_depths_layout_widgets()
        if hasattr(self, 'SWITCH_SPECS'):
            self._create_switch_layout_widgets()

    def _create_shape_row_layout(self):
        """Shape and sync controls"""
        shape_label = QLabel("Shape")
        shape_row_layout_widgets = [shape_label]
        for mod_lfo_shape in self.wave_shapes:
            icon_name = self.shape_icon_map.get(mod_lfo_shape, JDXi.UI.Icon.WAVEFORM)
            icon = create_icon_from_qta(icon_name)
            btn = create_button_with_icon(
                icon_name=mod_lfo_shape.display_name,
                icon=icon,
                button_dimensions=JDXi.UI.Dimensions.WaveformIcon,
                icon_dimensions=JDXi.UI.Dimensions.LFOIcon,
            )
            btn.clicked.connect(
                lambda checked, shape=mod_lfo_shape: self._on_wave_shape_selected(shape)
            )
            if self.analog:
                JDXi.UI.Theme.apply_button_rect_analog(btn)
            self.wave_shape_buttons[mod_lfo_shape] = btn
            shape_row_layout_widgets.append(btn)

        shape_row_layout = create_layout_with_widgets(shape_row_layout_widgets)
        return shape_row_layout

    def _create_tab_widget(self):
        """Create tab widget for Rate/Rate Ctrl and Depths"""
        
        tab_widget = QTabWidget()
        self.tab_widget = tab_widget  # --- Set for _add_tab to use
        
        rate_widget = self._create_rate_widget()
        depths_widget = self._create_depths_widget()
        
        # --- Use tab definitions - BaseOscillatorSection uses LFO-style tabs
        from jdxi_editor.midi.data.parameter.digital.spec import DigitalLFOTab
        
        self._add_tab(key=DigitalLFOTab.RATE, widget=rate_widget)
        # --- Update label if it differs from default (BaseOscillatorSection uses "Controls" instead of "Rate")
        if tab_widget.tabText(0) != self.controls_tab_label:
            tab_widget.setTabText(0, self.controls_tab_label)
        
        self._add_tab(key=DigitalLFOTab.DEPTHS, widget=depths_widget)
        # --- Update label if it differs from default (BaseOscillatorSection uses "ADSR" instead of "Depths")
        if tab_widget.tabText(1) != self.adsr_tab_label:
            tab_widget.setTabText(1, self.adsr_tab_label)
        JDXi.UI.Theme.apply_tabs_style(tab_widget, analog=self.analog)
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

    def _on_wave_shape_selected(self, lfo_shape: DigitalLFOShape):
        """
        Handle Mod LFO shape button clicks

        :param lfo_shape: DigitalLFOShape enum value
        """
        for btn in self.wave_shape_buttons.values():
            btn.setChecked(False)
            if self.analog:
                JDXi.UI.Theme.apply_button_rect_analog(btn)
            else:
                btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)
        selected_btn = self.wave_shape_buttons.get(lfo_shape)
        if selected_btn:
            selected_btn.setChecked(True)
            if self.analog:
                JDXi.UI.Theme.apply_button_analog_active(selected_btn)
            else:
                selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)
        if self.analog:
            JDXi.UI.Theme.apply_button_analog_active(selected_btn)

        # ---  Send MIDI message
        if self.send_midi_parameter:
            if not self.send_midi_parameter(self.wave_shape_param, lfo_shape.value):
                log.warning(f"Failed to set Mod LFO shape to {lfo_shape.name}")

    def _create_switch_row_layout(self) -> QHBoxLayout:
        """Create Switch row"""
        switch_row_layout = create_layout_with_widgets(self.switch_row_widgets)
        return switch_row_layout

    def _create_switch_layout_widgets(self):
        """Create switch layout widgets"""
        if hasattr(self, 'SWITCH_SPECS'):
            self.switch_row_widgets = self._build_switches(self.SWITCH_SPECS)
        else:
            self.switch_row_widgets = []

    def _create_rate_fade_layout_widgets(self):
        if hasattr(self, 'RATE_FADE_SLIDERS'):
            self.rate_layout_widgets = self._build_sliders(self.RATE_FADE_SLIDERS)
        else:
            self.rate_layout_widgets = []

    def _create_depths_layout_widgets(self):
        if hasattr(self, 'DEPTH_SLIDERS'):
            self.depths_layout_widgets = self._build_sliders(self.DEPTH_SLIDERS)
        else:
            self.depths_layout_widgets = []

    def _on_button_selected(self, button_param):
        """Override to handle waveform button selection with correct MIDI parameter"""
        # --- Reset all buttons
        for btn in self.button_widgets.values():
            btn.setChecked(False)
            btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT)

        # Set selected button
        selected_btn = self.button_widgets[button_param]
        selected_btn.setChecked(True)
        selected_btn.setStyleSheet(JDXi.UI.Style.BUTTON_RECT_ACTIVE)

        # Update enabled states
        self._update_button_enabled_states(button_param)

        # --- Send MIDI parameter - button_param is a Digital.Wave.Osc enum
        if self.send_midi_parameter:
            self.send_midi_parameter(self.SYNTH_SPEC.Param.OSC_WAVE, button_param.value)

    def _update_button_enabled_states(self, button_param):
        """Override to enable/disable widgets based on selected waveform.

        This is called after all widgets are created (in setup_ui), so widgets
        should exist. We still check for None as a safety measure.
        """
        # --- Disable all first
        for attrs in self.BUTTON_ENABLE_RULES.values():
            for attr in attrs:
                widget = getattr(self, attr, None)
                if widget is not None:
                    widget.setEnabled(False)
        # --- Enable per selected button
        for attr in self.BUTTON_ENABLE_RULES.get(button_param, []):
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.setEnabled(True)

    def _create_button_row_layout(self):
        """Override to create waveform button row layout"""

        # --- Create wave variation combo box
        self.wave_variation = self._create_parameter_combo_box(
            self.SYNTH_SPEC.Param.OSC_WAVE_VARIATION,
            self.SYNTH_SPEC.Display.Name.OSC_WAVE_VARIATION,
            options=self.SYNTH_SPEC.Display.Options.OSC_WAVE_VARIATION,
            values=[0, 1, 2],  # A, B, C
        )
        self.controls[self.SYNTH_SPEC.Param.OSC_WAVE_VARIATION] = self.wave_variation

        button_row = QHBoxLayout()
        button_row.addStretch()
        button_row.addLayout(create_layout_with_widgets(self.wave_layout_widgets))
        button_row.addWidget(self.wave_variation)  # Add wave variation switch
        button_row.addStretch()
        return button_row
