"""
Analog Filter Section
"""

from typing import Callable, Dict, Optional, Union

from jdxi_editor.midi.data.parameter.digital.spec import JDXiMidiDigital
from jdxi_editor.midi.io.helper import MidiIOHelper
from jdxi_editor.ui.widgets.filter.filter import FilterWidget
from jdxi_editor.ui.widgets.spec import FilterWidgetSpec
from picomidi.sysex.parameter.address import AddressParameter
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QWidget,
)
from decologr import Decologr as log
from jdxi_editor.core.jdxi import JDXi
from jdxi_editor.midi.data.address.address import RolandSysExAddress
from jdxi_editor.midi.data.analog.filter import AnalogFilterType
from jdxi_editor.midi.data.parameter.analog.spec import JDXiMidiAnalog as Analog
from jdxi_editor.ui.widgets.editor.helper import (
    create_group_adsr_with_hlayout,
    create_icon_from_name,
    create_layout_with_widgets,
    set_button_style_and_dimensions,
)
from jdxi_editor.ui.widgets.editor.section_base import SectionBaseWidget
from jdxi_editor.ui.widgets.filter.analog_filter import AnalogFilterWidget


class BaseFilterSection(SectionBaseWidget):
    """Base Filter Section"""

    FILTER_SPECS: dict = {}
    FILTER_WIDGET_SPEC: FilterWidgetSpec = None
    SYNTH_SPEC = JDXiMidiDigital
    # Subclasses (e.g. DigitalFilterSection) override these; do not set in __init__
    FILTER_MODE_ENABLED_MAP: dict = {}
    FILTER_PARAMS_LIST: list = []
    FILTER_MODE_MIDI_MAP: dict = {}

    def __init__(
            self,
            controls: dict[AddressParameter, QWidget],
            address: RolandSysExAddress,
            on_filter_mode_changed: Callable = None,
            parent: Optional[QWidget] = None,
            icons_row_type: str = None,
            send_midi_parameter: Callable = None,
            midi_helper: MidiIOHelper = None,
            analog: bool = False
    ):
        """
        Initialize the AnalogFilterSection

        :param controls: dict[AddressParameter, QWidget] controls to add to
        :param address: RolandSysExAddress
        :param on_filter_mode_changed: Optional callback for filter mode changes
        """
        self.tab_widget: QTabWidget | None = None
        self.filter_resonance: QWidget | None = None
        self.filter_mode_buttons: dict = {}  # Dictionary to store filter mode buttons
        self._filter_mode_changed_callback: Callable = on_filter_mode_changed
        self.send_midi_parameter: Callable | None = send_midi_parameter

        super().__init__(send_midi_parameter=send_midi_parameter,
                         midi_helper=midi_helper,
                         controls=controls,
                         address=address,
                         icons_row_type=icons_row_type,
                         analog=analog)
        # Set attributes after super().__init__() to avoid them being overwritten
        self.controls: Dict[Union[Analog.Param], QWidget] = controls or {}
        self.address = address

    def build_widgets(self):
        """build widgets"""
        self.controls_group = self._create_controls_group()
        if self.BUTTON_SPECS:
            self._create_waveform_buttons()
            if self.analog:
                self.filter_mode_buttons = self.button_widgets
        self._create_adsr_group()
        self._create_tab_widget()

    def setup_ui(self):
        """Setup the UI (standardized method name matching Digital Filter)"""
        layout = self.get_layout()
        JDXi.UI.Theme.apply_tabs_style(self.tab_widget, analog=self.analog)
        if self.button_widgets:
            button_layout = self._create_button_row_layout()
            if button_layout is not None:
                layout.addLayout(button_layout)
        layout.addWidget(self.tab_widget)

        layout.addSpacing(JDXi.UI.Style.SPACING)
        layout.addStretch()
        if self.analog and self.BUTTON_SPECS:
            self._initialize_button_states()

    def _create_tab_widget(self):
        """Create tab widget. Idempotent: skip if already built (called from build_widgets and from SectionBaseWidget._setup_ui)."""
        if self.tab_widget is not None and self.tab_widget.count() > 0:
            return
        self.tab_widget = QTabWidget()
        # --- Filter Controls ---
        self._add_tab(key=self.SYNTH_SPEC.Filter.Tab.CONTROLS, widget=self.controls_group)
        # --- Filter ADSR ---
        self._add_tab(key=self.SYNTH_SPEC.Filter.Tab.ADSR, widget=self.adsr_group)

    def _create_filter_controls_row(self) -> QHBoxLayout:
        """Create the filter controls row with buttons for each filter mode."""
        self.filter_label = QLabel("Filter")

        self.filter_mode_control_button_widgets: list[QWidget] = [self.filter_label]
        # Create buttons dynamically based on the FilterSpec configurations
        for filter_mode, spec in self.FILTER_SPECS.items():
            button = QPushButton()
            icon = create_icon_from_name(spec.icon)
            button.setIcon(icon)
            button.setText(spec.name)
            button.setToolTip(spec.description)
            set_button_style_and_dimensions(button, JDXi.UI.Dimensions.WaveformIcon)
            button.clicked.connect(
                lambda checked, mode=filter_mode: self._on_filter_mode_selected(mode)
            )
            self.filter_mode_buttons[filter_mode] = button
            self.filter_mode_control_button_widgets.append(button)
        filter_row = create_layout_with_widgets(self.filter_mode_control_button_widgets, vertical=False)
        return filter_row

    def _on_button_selected_old(self, button_param):
        """Route Analog filter mode button clicks to _on_filter_mode_selected; Digital uses parent."""
        if self.analog and button_param is not None:
            # Match by key (Analog.Filter.Mode / AnalogFilterMode) or by value (0=BYPASS, 1=LPF)
            buttons = getattr(self, "filter_mode_buttons", None)
            if buttons and button_param in buttons:
                self._on_filter_mode_selected(button_param)
                return
            if hasattr(button_param, "value") and button_param.value in (0, 1):
                # AnalogFilterMode / filter-mode enum; handle here so we never pass it to send_midi_parameter
                self._on_filter_mode_selected(button_param)
                return
        super()._on_button_selected(button_param)

    def _on_filter_mode_selected(self, filter_mode: AnalogFilterType):
        """
        Handle filter mode button clicks

        :param filter_mode: Analog.Filter.FilterType enum value
        """
        log.message(
            f"[Filter] _on_filter_mode_selected: filter_mode={filter_mode!r} value={getattr(filter_mode, 'value', None)} analog={getattr(self, 'analog', None)}"
        )
        # --- Reset all buttons to default style
        for btn in self.filter_mode_buttons.values():
            btn.setChecked(False)
            JDXi.UI.Theme.apply_button_rect_analog(btn)

        # --- Apply active style to the selected filter mode button
        selected_btn = self.filter_mode_buttons.get(filter_mode)
        if selected_btn:
            selected_btn.setChecked(True)
            JDXi.UI.Theme.apply_button_analog_active(selected_btn)

        # --- Send MIDI message via SysEx (analog synth uses SysEx, not control changes)
        if self.midi_helper and self.address:
            sysex_message = self.sysex_composer.compose_message(
                address=self.address,
                param=Analog.Param.FILTER_MODE_SWITCH,
                value=filter_mode.value,
            )
            if sysex_message:
                self.midi_helper.send_midi_message(sysex_message)

        # --- Notify parent (Analog editor uses this to sync; Digital has no callback)
        if self._filter_mode_changed_callback:
            log.message(f"[Filter] Calling _filter_mode_changed_callback with value={filter_mode.value}")
            self._filter_mode_changed_callback(filter_mode.value)

        # --- Update enabled state here so Digital (no callback) still works; Analog callback does it too
        self.update_controls_state(filter_mode.value)

    def _create_controls_group(self) -> QGroupBox:
        """Controls Group - standardized order: FilterWidget, Resonance, KeyFollow, Velocity (harmonized with Digital)"""
        if self.analog:
            self.filter_widget = AnalogFilterWidget(
                cutoff_param=self.FILTER_WIDGET_SPEC.cutoff_param,
                midi_helper=self.midi_helper,
                create_parameter_slider=self._create_parameter_slider,
                controls=self.controls,
                address=self.address,
            )
        else:
            self.filter_widget = FilterWidget(
                cutoff_param=self.FILTER_WIDGET_SPEC.cutoff_param,
                slope_param=self.FILTER_WIDGET_SPEC.slope_param,
                midi_helper=self.midi_helper,
                create_parameter_slider=self._create_parameter_slider,
                create_parameter_switch=self._create_parameter_switch,
                controls=self.controls,
                address=self.address,
                analog=self.analog
            )
        if self.analog:
            (self.filter_resonance, self.filter_cutoff_keyfollow, self.filter_env_velocity_sens) = self._build_sliders(self.SLIDER_GROUPS["filter"])
        else:  # Digital has an extra slider
            (self.filter_resonance, self.filter_cutoff_keyfollow, self.filter_env_velocity_sens, self.filter_env_depth) = self._build_sliders(
                self.SLIDER_GROUPS["filter"])
        control_widgets = [
            self.filter_widget,
            self.filter_resonance,
            self.filter_cutoff_keyfollow,
            self.filter_env_velocity_sens,
        ]
        if not self.analog:
            control_widgets.append(self.filter_env_depth)
        controls_layout = create_layout_with_widgets(
            control_widgets
        )
        return create_group_adsr_with_hlayout(
            name="Controls", hlayout=controls_layout, analog=self.analog
        )

    def update_controls_state(self, value: int) -> None:
        """
        Update filter controls enabled state based on filter mode value.
        Called when filter mode changes from SysEx data.

        :param value: int - Filter mode value (0=BYPASS, 1=LPF, 2=HPF, etc.)
        :return: None
        """
        # --- Normalize to int (callers may pass enum or wrong type)
        if value is not None and not isinstance(value, int):
            if hasattr(value, "value"):
                value = value.value
            try:
                value = int(value) if isinstance(value, (int, float)) else 0
            except (ValueError, TypeError):
                value = 0
        if value is None:
            value = 0

        try:
            selected_filter_mode = self.FILTER_MODE_ENABLED_MAP.get(value)
            _map_keys = list(self.FILTER_MODE_ENABLED_MAP.keys()) if self.FILTER_MODE_ENABLED_MAP else []
            log.message(
                f"[Filter] update_controls_state: value={value} selected_filter_mode={selected_filter_mode!r} "
                f"FILTER_MODE_ENABLED_MAP keys={_map_keys}"
            )
            if selected_filter_mode is None:
                log.warning(f"[Filter] Unknown filter mode value: {value}, returning early")
                return

            # --- Enable/disable controls based on filter mode
            is_bypass = selected_filter_mode == self.SYNTH_SPEC.Filter.Mode.BYPASS
            enabled = not is_bypass
            self.controls_group.setEnabled(enabled)
            log.message(f"[Filter] Set controls_group.setEnabled({enabled})")
            if self.adsr_widget:
                self.adsr_widget.setEnabled(enabled)
                log.message(f"[Filter] Set adsr_widget.setEnabled({enabled})")
            if hasattr(self, "filter_widget"):
                self.filter_widget.setEnabled(enabled)
                log.message(f"[Filter] Set filter_widget.setEnabled({enabled})")
        except Exception as ex:
            log.error(f"Error {ex} occurred updating controls")

    def _on_button_selected(self, button_param):
        """Override to update filter mode in FilterWidget plot and enable/disable Controls sliders and ADSR"""
        # --- Call parent to handle button selection
        super()._on_button_selected(button_param)

        # --- Update enabled state of Controls sliders and filter widget (uses FILTER_MODE_* maps)
        if hasattr(button_param, "value"):
            self.update_controls_state(button_param.value)

        # --- Determine if bypass is selected
        is_bypass = button_param == self.SYNTH_SPEC.Filter.Mode.BYPASS
        enabled = not is_bypass

        # --- Update filter mode in FilterWidget plot
        if (
                hasattr(self, "filter_widget")
                and self.filter_widget
                and hasattr(self.filter_widget, "plot")
        ):
            filter_mode_str = self.FILTER_MODE_MIDI_MAP.get(
                button_param, self.SYNTH_SPEC.Filter.ModeType.LPF
            )
            self.filter_widget.filter_mode = filter_mode_str
            if hasattr(self.filter_widget.plot, "set_filter_mode"):
                self.filter_widget.plot.set_filter_mode(filter_mode_str)

            # --- Disable plot display when bypass is selected
            self.filter_widget.plot.enabled = enabled
            self.filter_widget.plot.update()  # Trigger redraw

        # --- Enable/disable ADSR widget based on filter mode (like PWM widget)
        if self.adsr_widget:
            self.adsr_widget.setEnabled(enabled)
