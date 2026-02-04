"""
LFO section of the digital partial editor.
"""

from typing import Callable, Protocol, runtime_checkable

from decologr import Decologr as log
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QWidget, QVBoxLayout,
)

from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.digital.lfo import DigitalLFOShape
from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital as Digital
from jdxi_editor.ui.widgets.editor import IconType
from jdxi_editor.ui.widgets.editor.helper import (
    create_button_with_icon,
    create_icon_from_qta,
    create_layout_with_widgets, add_sublayout_to_layout, add_widgets_to_layout,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget


@runtime_checkable
class LFOBehavior(Protocol):
    def build_widgets(self) -> None: ...
    def setup_ui(self) -> None: ...


class LFOSwitchGroup:
    """LFO Switch Group"""
    SWITCH_ROW: str = "switch_row_widgets"


class LFOSliderGroup:
    """Slider Group"""
    DEPTH: str = "depth"
    RATE_FADE: str = "rate_fade"


class LFOGroup:
    """LFO Groups"""
    label: str = "LFO"
    slider: LFOSliderGroup = LFOSliderGroup
    switch: LFOSwitchGroup = LFOSwitchGroup
    combo: None


class BaseLFOSection(SectionBaseWidget):
    """Abstract base class for LFO sections."""
    SLIDER_GROUPS = {}
    SWITCH_GROUPS = {}

    # Old Method (legacy; subclasses use SLIDER_GROUPS / SWITCH_GROUPS)
    DEPTH_SLIDERS = {}
    SWITCH_SPECS = {}
    RATE_FADE_SLIDERS = {}

    rate_tab_label: str = "Rate"
    depths_tab_label: str = "Depths"

    def __init__(
        self,
        icons_row_type: str = IconType.ADSR,
        analog: bool = False,
        send_midi_parameter: Callable = None,
    ):
        """
        Initialize the DigitalLFOSection

        :param icons_row_type: Type of icon e.g
        :param analog: bool
        """
        self.widgets: dict = {}
        self.wave_shape_param: list | None = None
        self.switch_row_widgets: list | None = None
        self.rate_layout_widgets: list | None = None
        self.depths_layout_widgets: list | None = None
        self.send_midi_parameter: Callable | None = send_midi_parameter
        self.wave_shape_buttons = {}  # Dictionary to store LFO shape buttons
        # --- Set up LFO shapes and icon map before super().__init__() so _setup_ui() can use them
        self.wave_shapes = [
            Digital.Wave.LFO.TRI,
            Digital.Wave.LFO.SINE,
            Digital.Wave.LFO.SAW,
            Digital.Wave.LFO.SQUARE,
            Digital.Wave.LFO.SAMPLE_HOLD,
            Digital.Wave.LFO.RANDOM,
        ]
        self.shape_icon_map = {
            Digital.Wave.LFO.TRI: JDXi.UI.Icon.WAVE_TRIANGLE,
            Digital.Wave.LFO.SINE: JDXi.UI.Icon.WAVE_SINE,
            Digital.Wave.LFO.SAW: JDXi.UI.Icon.WAVE_SAW,
            Digital.Wave.LFO.SQUARE: JDXi.UI.Icon.WAVE_SQUARE,
            Digital.Wave.LFO.SAMPLE_HOLD: JDXi.UI.Icon.WAVEFORM,
            Digital.Wave.LFO.RANDOM: JDXi.UI.Icon.WAVE_RANDOM,
        }

        super().__init__(icons_row_type=icons_row_type, analog=analog)
        # --- Set controls after super().__init__() to avoid it being overwritten
        if not hasattr(self, "controls") or self.controls is None:
            self.controls = {}

    def _setup_ui(self):
        """Assemble UI: icons row, switch row (right after icons), shape row, tab widget, stretch."""
        switch_row_layout = self._create_switch_row_layout()
        shape_row_layout = self._create_shape_row_layout()
        self._create_tab_widget()
        layout = self.create_layout()
        add_sublayout_to_layout(layout=layout, sub_layouts=[shape_row_layout, switch_row_layout])
        add_widgets_to_layout(layout=layout, widgets=[self.tab_widget])
        layout.addStretch()

    def setup_ui(self):
        """For analog: build layout here (_setup_ui is skipped). For digital: no-op, layout built in _setup_ui()."""
        if not self.analog:
            return  # Digital: already built in _setup_ui()
        layout = self.get_layout()
        shape_row_layout = self._create_shape_row_layout()
        switch_row_layout = self._create_switch_row_layout()
        add_sublayout_to_layout(layout=layout, sub_layouts=[shape_row_layout, switch_row_layout])
        # Create tab widget (Rate/Depths with sliders) — not created for analog since _setup_ui() is skipped
        self._create_tab_widget()
        add_widgets_to_layout(layout=layout, widgets=[self.tab_widget])
        layout.addStretch()

    def build_widgets(self):
        """Build from subclass SLIDER_GROUPS / SWITCH_GROUPS when present.
        Subclasses only need to define those class attributes; this fills
        self.widgets and self.switch_row_widgets.
        """
        slider_groups = getattr(self, "SLIDER_GROUPS", None)
        switch_groups = getattr(self, "SWITCH_GROUPS", None)
        if (
            slider_groups
            and LFOGroup.slider.DEPTH in slider_groups
            and LFOGroup.slider.RATE_FADE in slider_groups
            and switch_groups
            and LFOGroup.switch.SWITCH_ROW in switch_groups
        ):
            self.widgets = {
                LFOGroup.slider.DEPTH: self._build_sliders(
                    slider_groups[LFOGroup.slider.DEPTH]
                ),
                LFOGroup.slider.RATE_FADE: self._build_sliders(
                    slider_groups[LFOGroup.slider.RATE_FADE]
                ),
                LFOGroup.switch.SWITCH_ROW: self._build_switches(
                    switch_groups[LFOGroup.switch.SWITCH_ROW]
                ),
            }
            self.switch_row_widgets = self.widgets[LFOGroup.switch.SWITCH_ROW]
        else:
            self.switch_row_widgets = []

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
        self.tab_widget = tab_widget  # Set for _add_tab to use

        rate_widget = self._create_rate_widget()
        depths_widget = self._create_depths_widget()

        self._add_tab(key=self.SYNTH_SPEC.LFO.Tab.RATE, widget=rate_widget)
        # --- Update label if it differs from default
        if tab_widget.tabText(0) != self.rate_tab_label:
            tab_widget.setTabText(0, self.rate_tab_label)

        self._add_tab(key=self.SYNTH_SPEC.LFO.Tab.DEPTHS, widget=depths_widget)
        # --- Update label if it differs from default
        if tab_widget.tabText(1) != self.depths_tab_label:
            tab_widget.setTabText(1, self.depths_tab_label)

        JDXi.UI.Theme.apply_tabs_style(tab_widget, analog=self.analog)
        return tab_widget

    def _create_rate_widget(self):
        """Rate and Rate Ctrl Controls Tab"""
        rate_layout = create_layout_with_widgets(self.widgets[LFOGroup.slider.RATE_FADE])
        rate_widget = QWidget()
        rate_widget.setLayout(rate_layout)
        rate_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MIN_HEIGHT)
        return rate_widget

    def _create_depths_widget(self):
        """Depths Tab"""
        depths_layout = create_layout_with_widgets(self.widgets[LFOGroup.slider.DEPTH])
        depths_widget = QWidget()
        depths_widget.setLayout(depths_layout)
        depths_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MIN_HEIGHT)
        return depths_widget

    def _create_rate_fade_controls(self) -> QWidget:
        """Rate and Fade Controls Tab"""
        rate_fade_widget = QWidget()
        rate_fade_layout = create_layout_with_widgets(self.widgets[LFOGroup.slider.RATE_FADE])
        rate_fade_widget.setLayout(rate_fade_layout)
        rate_fade_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MIN_HEIGHT)
        return rate_fade_widget

    def _create_depths_controls(self) -> QWidget:
        """Depths Tab"""
        depths_widget = QWidget()
        depths_layout = create_layout_with_widgets(self.depths_layout_widgets)
        depths_widget.setLayout(depths_layout)
        depths_widget.setMinimumHeight(JDXi.UI.Dimensions.EDITOR.MIN_HEIGHT)
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

        # --- Send MIDI message
        if self.send_midi_parameter:
            if not self.send_midi_parameter(self.wave_shape_param, lfo_shape.value):
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
